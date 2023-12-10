from contextlib import nullcontext
import requests
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# sport = ['tennis_wta_aus_open_singles'
#         #,'aussierules_afl','basketball_nba','cricket_big_bash'
#         ]
#completed_sports = []

@app.route('/sports')
def get_sports():
    sport = [request.args.get('type')]
    headers = []
    allArbOps = []
    for sportnum in range(len(sport)):
        allGames = requests.get('https://api.the-odds-api.com/v4/sports/'+sport[sportnum]+'/odds?regions=au&oddsFormat=decimal&apiKey=45924e9ea1424a4c74536a2de584d197')
        json_res = allGames.json()
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
                    updatedLast = odds['last_update']
                    market = odds['markets'][0]['key']
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
            sideOneInfo = brokerageList[pricesOne.index(max(pricesOne))]
            sideTwoInfo = brokerageList[pricesTwo.index(max(pricesTwo))]
            sideOneBestPrice =  max(pricesOne)
            sideTwoBestPrice = max(pricesTwo)

            print('Largest Spread:')
            print(sideA, sideOneInfo, sideOneBestPrice)
            print(sideB, sideTwoInfo, sideTwoBestPrice)  

            # Calculate Arbitage Value
            arb_op = ((1/max(pricesOne)+(1/max(pricesTwo)))*100)
            print('Arb value: ',arb_op)

            arb_opBinary = False

            if arb_op < 100:
                print('BINGOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
                catch.append('BINGO'+'@'+str(i))
                arb_opBinary = True
            else:
                print('NO OP')

            #Put all opputunities into list
            allArbOps.append({
                'homeTeam': sideA,
                'awayTeam': sideB,
                'homePrice': sideOneBestPrice,
                'awayPrice': sideTwoBestPrice,
                'homeBroker': sideOneInfo,
                'awayBroker': sideTwoInfo,
                'combinedRatio': "{:.2f}".format(arb_op),
                'arbOpAvailable': arb_opBinary
            })

            

            print(i)
        print(catch)
        print(json.dumps(allArbOps, sort_keys=False, indent= 4))
    #completed_sports.append(sport)
    #print(completed_sports)
    return jsonify(allArbOps,headers)


    