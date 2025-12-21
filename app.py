from flask import Flask, render_template, request, jsonify
from Alpaca.Scripts.alpaca_trading import start_service, stop_service
from Alpaca.Database.db_functions import nextPurchaseDate, getAccountValue, getLastOrderedStock, update_keys, checkFirstRun, initial_setup, getChartData, buildTables, createLog, createDBFile, getDbPath, getLogs
from datetime import datetime
from Alpaca.Scripts.updateChecker import check_for_update, getCurrentVersion
import os
import sys


base_path = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__,
            template_folder=os.path.join(base_path, 'templates'),
            static_folder=os.path.join(base_path, 'static'))

try:
    firstRun = checkFirstRun()
    startup = True
    timestamps, equities = getChartData()
    trading_thread = None
    
except:
    db_path = getDbPath()
    if not os.path.exists(db_path):
        createDBFile(db_path)
        print("Database file created at:", db_path)
    firstRun = True
    timestamps = []
    equities = []
    trading_thread = None
    buildTables()


@app.route("/")
def index():
    global timestamps, equities
    try: 
        timestamps, equities = getChartData()
        firstRun = checkFirstRun()
        isUpdateNeeded = check_for_update()
        currentVersion = getCurrentVersion()

    except:
        firstRun = True
        isUpdateNeeded = check_for_update()
        currentVersion = getCurrentVersion()

        print("update: ", isUpdateNeeded)
        print("Length: ", len(isUpdateNeeded))
        print("Version: ", currentVersion)

    from Alpaca.Scripts.alpaca_trading import is_running
    print("running:", is_running)
    return render_template(
        "index.html",
        is_running = is_running,
        firstRun = firstRun,
        isUpdateNeeded = isUpdateNeeded,
        currentVersion = currentVersion
    )

@app.route('/api/status')
def status():
    from Alpaca.Scripts.alpaca_trading import is_running

    try:
        return jsonify({
            "running": is_running,
            "stock": getLastOrderedStock(),
            "accountValue": getAccountValue(),
            "purchaseDate": nextPurchaseDate(),
            "firstRun": checkFirstRun(),
        })
    except:
        return jsonify({
            "running": is_running
        })
    
@app.route('/api/logTable')
def logTable():
    global startup


    from Alpaca.Scripts.alpaca_trading import is_running
  
    if startup == True:
        initialRun = True
        startup = False
    else:
        initialRun = False

    try:
        return jsonify({
            "running": is_running,
            "logs": getLogs(),
            "initialRun": initialRun

        })
    except:
        return jsonify({
            "running": is_running
        })

@app.route('/toggle-running', methods=['POST'])
def toggle_running():
    data = request.get_json()
    should_run = data.get('running', False)

    print("Received JSON:", data)


    if should_run:
        started = start_service()
    else:
        stop_service()

    from Alpaca.Scripts.alpaca_trading import is_running
    return jsonify({"success": True,"is_running": is_running})

@app.route('/update-info', methods=['POST'])
def update_info():
    data = request.get_json()
    api_key = data.get("API_KEY")
    secret_key = data.get("SECRET_KEY")
    paydate = data.get("PAY_DATE")
    stock = data.get("STOCK")

    try:
        paydate = datetime.strptime(paydate, "%Y-%m-%d")
        paydate = datetime.strftime(paydate, "%m/%d/%Y")
    except:
        ...
    print("Paydate: " + paydate + " API_KEY: " + api_key + "SECRET: " + secret_key + "STOCK: " + stock)
    status = update_keys(api_key,secret_key, paydate, stock)

    print(status)
    if status == False:
        return jsonify(success=False)
    else:
        return jsonify(success=True)

@app.route('/initial-info', methods=['POST'])
def initial_info():
    data = request.get_json()
    api_key = data.get("API_KEY")
    secret_key = data.get("SECRET_KEY")
    pay_date = data.get("PAY_DATE")
    stock = data.get("STOCK")
    
    try: 
        dateObj = datetime.strptime(pay_date, "%Y-%m-%d")
        pay_date = dateObj.strftime("%m/%d/%Y")
    except:
        print("Done testing...")

    status = initial_setup(api_key,secret_key, pay_date, stock)

    if status == False:
        return jsonify(success=False)
    else:
        return jsonify(success=True)

@app.route('/api/chart-data')
def chart_data():
    try:
        return jsonify({
            "labels": timestamps,
            "values": equities
        })
    except:
        return jsonify({
            "labels": ["No Data"],
            "values": [0]
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=49000, debug=False)