# from contextlib import nullcontext
import requests
import json
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API")



app = Flask(__name__)
CORS(app)

@app.route('/')
def serve_home():
    return send_from_directory('static', 'index.html')


EXCLUDED_GROUPS = ['Soccer', 'Ice Hockey','Mixed Martial Arts','Politics','Golf']  # Exclude these until I integrate 3 option sports

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
        json_headers = allGames.headers['X-Requests-Remaining']
        headers.append(json_headers)
        print(json_headers)

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
    return jsonify(allArbOps,headers)




if __name__ == "__main__":
    with app.app_context():
        print('App is about to start!')
    app.run(host='localhost', port=5000, debug=False)

     