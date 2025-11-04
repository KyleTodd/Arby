# from contextlib import nullcontext
import requests
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API")
RACING_API_USER = os.getenv("RACING_API_USER")
RACING_API_PASSWORD = os.getenv("RACING_API_PASSWORD")



app = Flask(__name__)
CORS(app)




@app.route('/')
def serve_home():
    # return render_template('static', 'index.html', eport=os.getenv("PORT", 5000))
    return send_from_directory('static', 'index.html')


@app.route('/config')
def config():
    return jsonify({"port": os.getenv("PORT", 5000),"baseUrl": os.getenv("BASE_URL", "http://localhost")})

EXCLUDED_GROUPS = ['Soccer', 'Ice Hockey','Mixed Martial Arts','Politics','Golf']  # Exclude these until I integrate 3 option sports

@app.route('/get_racing_regions')
def get_racing_regions():
    """Get available racing regions from The Racing API"""
    # Define supported regions for horse racing
    racing_regions = {
        "Horse Racing": [
            {"key": "GB", "title": "Great Britain"},
            {"key": "IE", "title": "Ireland"},
            {"key": "AU", "title": "Australia"},
            {"key": "US", "title": "United States"},
            {"key": "FR", "title": "France"},
            {"key": "NZ", "title": "New Zealand"}
        ]
    }
    return jsonify(racing_regions)

@app.route('/get_sports')
def get_active_sports():
    response = requests.get("https://api.the-odds-api.com/v4/sports/?apiKey="+API_KEY)
    sports_data = response.json()

    sports_groups = {}
    for sport in sports_data:
        group = sport['group']
        if group in EXCLUDED_GROUPS:  # Skip the groups that are in the exclusion list
            continue
        if group not in sports_groups:
            sports_groups[group] = []
        sports_groups[group].append({"key": sport["key"], "title": sport["title"]})

    return jsonify(sports_groups)

# sport = ['cricket_big_bash']
completed_sports = []

def calculate_racing_bet(return_pct, odds_a, odds_b):
    """Calculate bet amounts and payouts for racing arbitrage"""
    bet_total = 100
    return_value = (1 + float(return_pct)/100) * bet_total
    bet_a = return_value / odds_a
    bet_b = return_value / odds_b
    payout_a = bet_a * odds_a
    payout_b = bet_b * odds_b
    
    return {
        'bet_a': f"{bet_a:.2f}",
        'bet_b': f"{bet_b:.2f}",
        'payout_a': f"{payout_a:.2f}",
        'payout_b': f"{payout_b:.2f}"
    }

@app.route('/racing_odds')
def get_racing_odds():
    """Get horse racing odds and calculate arbitrage opportunities"""
    from datetime import datetime
    
    region = request.args.get('region', 'AU')
    
    # Check if Racing API credentials are configured
    if not RACING_API_USER or not RACING_API_PASSWORD:
        return jsonify({
            "error": "Racing API credentials not configured. Please set RACING_API_USER and RACING_API_PASSWORD in .env file"
        }), 400
    
    try:
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Fetch racecards with odds from The Racing API
        url = f"https://api.theracingapi.com/v1/racecards?region={region}&date={today}"
        response = requests.get(url, auth=(RACING_API_USER, RACING_API_PASSWORD))
        
        if response.status_code == 401:
            return jsonify({"error": "Invalid Racing API credentials"}), 401
        elif response.status_code != 200:
            return jsonify({"error": f"Racing API error: {response.status_code}"}), 500
            
        racecards = response.json()
        
        if not racecards or len(racecards) == 0:
            return jsonify([])
        
        all_arb_ops = []
        
        # Process each race
        for race in racecards:
            try:
                # Skip if no odds data available
                if 'odds' not in race or not race['odds']:
                    continue
                
                race_name = race.get('course', 'Unknown Course')
                race_time = race.get('off_time', 'Unknown Time')
                runners = race.get('runners', [])
                
                if not runners or len(runners) < 2:
                    continue
                
                # Build odds matrix: for each runner, collect best odds from each bookmaker
                runner_odds = {}
                for runner in runners:
                    runner_name = runner.get('name', 'Unknown')
                    runner_odds[runner_name] = []
                
                # Extract odds from bookmakers
                if isinstance(race['odds'], dict):
                    for bookmaker_name, bookmaker_data in race['odds'].items():
                        if isinstance(bookmaker_data, list):
                            for runner_odds_data in bookmaker_data:
                                runner_name = runner_odds_data.get('runner', '')
                                odds_decimal = runner_odds_data.get('decimal', None)
                                if runner_name in runner_odds and odds_decimal:
                                    runner_odds[runner_name].append({
                                        'bookmaker': bookmaker_name,
                                        'odds': float(odds_decimal)
                                    })
                
                # Find arbitrage opportunities by selecting best odds for each runner
                # For simplicity, we'll check the top 2 runners with best odds
                runner_best_odds = {}
                for runner_name, odds_list in runner_odds.items():
                    if odds_list:
                        best = max(odds_list, key=lambda x: x['odds'])
                        runner_best_odds[runner_name] = best
                
                # Sort runners by best odds (lowest odds = favorite)
                sorted_runners = sorted(runner_best_odds.items(), key=lambda x: x[1]['odds'])
                
                if len(sorted_runners) < 2:
                    continue
                
                # Check arbitrage for top 2 favorites
                runner1_name, runner1_data = sorted_runners[0]
                runner2_name, runner2_data = sorted_runners[1]
                
                odds1 = runner1_data['odds']
                odds2 = runner2_data['odds']
                bookmaker1 = runner1_data['bookmaker']
                bookmaker2 = runner2_data['bookmaker']
                
                # Calculate arbitrage
                arb_value = (1/odds1 + 1/odds2) * 100
                arb_pct = 100 - arb_value
                arb_available = arb_value < 100
                
                bet_info = calculate_racing_bet(arb_pct, odds1, odds2)
                
                all_arb_ops.append({
                    'raceName': f"{race_name} - {race_time}",
                    'homeTeam': runner1_name,
                    'awayTeam': runner2_name,
                    'homePrice': odds1,
                    'awayPrice': odds2,
                    'homeBroker': bookmaker1,
                    'awayBroker': bookmaker2,
                    'combinedRatio': f"{arb_value:.2f}",
                    'returnPercent': f"{arb_pct:.2f}%",
                    'homeBet': f"${bet_info['bet_a']}",
                    'awayBet': f"${bet_info['bet_b']}",
                    'homePayout': f"${bet_info['payout_a']}",
                    'awayPayout': f"${bet_info['payout_b']}",
                    'arbopAvailable': arb_available
                })
                
            except Exception as e:
                print(f"Error processing race: {e}")
                continue
        
        # Return format matches /sports endpoint: [data, headers, reqcount]
        # This maintains consistency with existing frontend code
        return jsonify(all_arb_ops, [], None)
        
    except Exception as e:
        return jsonify({"error": f"Error fetching racing data: {str(e)}"}), 500

@app.route('/sports')
def get_sports():
    
    sport = [request.args.get('type')]
    headers = []
    allArbOps = []
    for sportnum in range(len(sport)):
        allGames = requests.get('https://api.the-odds-api.com/v4/sports/'+str(sport[sportnum])+'/odds?regions=au&oddsFormat=decimal&apiKey='+str(API_KEY))
        json_res = allGames.json()
        # sport = [request.args.get('type')]
        # print(json_res)
        reqcount = allGames.headers['X-Requests-Remaining']
        
    # Loop through all matches
    catch=[]


    for i in range(len(json_res)):
        try:
            pricesOne=[]
            pricesTwo=[]
            brokerageList = []
            sideA = json_res[i]['home_team']
            sideB = json_res[i]['away_team']

            for odds in json_res[i]['bookmakers']:
                brokerage = odds['key']
                # updatedLast = odds['last_update']
                # market = odds['markets'][0]['key']
                sideOneName = odds['markets'][0]['outcomes'][0]['name']
                sideOnePrice = float(odds['markets'][0]['outcomes'][0]['price'])
                sideTwoName = odds['markets'][0]['outcomes'][1]['name']
                sideTwoPrice = float(odds['markets'][0]['outcomes'][1]['price'])

                pricesOne.append(sideOnePrice)
                pricesTwo.append(sideTwoPrice)
                brokerageList.append(brokerage)

                print(brokerage)
                print("- ", sideOneName, sideOnePrice)
                print("- ", sideTwoName, sideTwoPrice)
        except Exception:
            allArbOps.append({
            'homeTeam': 'sideA',
            'awayTeam': 'sideB',
            'homePrice': 'sideOneBestPrice',
            'awayPrice': 'sideTwoBestPrice',
            'homeBroker': 'sideOneInfo',
            'awayBroker': 'sideTwoInfo',
            'combinedRatio': 'arb_op',
            'arbOpAvailable': 'arb_opBinary'
        })

        #Best Arbitage Oppurtunity
        if pricesOne:
                sideOneInfo = brokerageList[pricesOne.index(max(pricesOne))]
        else:
            print("pricesOne is empty")

        if pricesTwo:
            sideTwoInfo = brokerageList[pricesTwo.index(max(pricesTwo))]
        else:
            print("pricesTwo is empty")

        sideOneBestPrice =  max(pricesOne) if pricesOne else None
        sideTwoBestPrice = max(pricesTwo) if pricesTwo else None

        # print('Largest Spread:')
        # print(sideA, sideOneInfo, sideOneBestPrice)
        # print(sideB, sideTwoInfo, sideTwoBestPrice)  

        # Calculate Arbitage Value
        arb_op = None

        if sideOneBestPrice and sideTwoBestPrice:
            arb_op = ((1/sideOneBestPrice + 1/sideTwoBestPrice) * 100)
            print('Arb value: ', arb_op)
            arbPct = "{:.2f}".format(100-arb_op)
        else:
            print("Cannot calculate arbitrage value because one or both price lists are empty")

        arb_opBinary = False

        if arb_op < 100:
            catch.append('BINGO'+'@'+str(i))
            arb_opBinary = True
        else:
            print('NO OP')

        def calculateBet(returnPercent):
            homeBet = None
            awayBet = None
            homePayout = None
            awayPayout = None

            bet = 100
            returnValue = (1+(float(returnPercent)/100))*bet
            if sideOneBestPrice is not None:
                homeBet = returnValue / sideOneBestPrice
            else:
                print("Cannot calculate homeBet because sideOneBestPrice is None")
            if sideTwoBestPrice is not None:
                awayBet = returnValue / sideTwoBestPrice
            else:
                print("Cannot calculate awayBet because sideTwoBestPrice is None")

            if homeBet is not None and sideOneBestPrice is not None:
                homePayout = homeBet * sideOneBestPrice
            else:
                print("Cannot calculate homePayout because homeBet or sideOneBestPrice is None")

            if awayBet is not None and sideTwoBestPrice is not None:
                awayPayout = awayBet * sideTwoBestPrice
            else:
                print("Cannot calculate awayPayout because awayBet or sideTwoBestPrice is None")
            homeBetf =  "{:.2f}".format(homeBet)
            awayBetf = "{:.2f}".format(awayBet)
            homePayoutf = "{:.2f}".format(homePayout)
            awayPayoutf =  "{:.2f}".format(awayPayout)

            return (homeBetf,awayBetf,homePayoutf,awayPayoutf)

        #Put all opputunities into list
        allArbOps.append({
            'homeTeam': sideA,
            'awayTeam': sideB,
            'homePrice': sideOneBestPrice,
            'awayPrice': sideTwoBestPrice,
            'homeBroker': sideOneInfo,
            'awayBroker': sideTwoInfo,
            'combinedRatio': "{:.2f}".format(arb_op),
            'returnPercent': str(arbPct)+"%",
            'homeBet':"$"+str(calculateBet(arbPct)[0]),
            'awayBet':"$"+str(calculateBet(arbPct)[1]),
             'homePayout':"$"+str(calculateBet(arbPct)[2]),
            'awayPayout':"$"+str(calculateBet(arbPct)[3]),
            'arbopAvailable': arb_opBinary
        })

        



        

        print(i)
    print(catch)
    print(json.dumps(allArbOps, sort_keys=False, indent= 4))
    completed_sports.append(sport)
    print(completed_sports)
    return jsonify(allArbOps,headers,reqcount)




if __name__ == "__main__":
    with app.app_context():
        print('App is about to start!')
    eport = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=eport, debug=False)

     