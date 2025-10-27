from flask import Flask, render_template, request, jsonify
from Alpaca.Scripts.alpaca_trading import start_trading, stop_trading
# from Alpaca.Scripts.script_controls import runScript, stopScript, checkScriptRunning
from Alpaca.Database.db_functions import getProcessId, nextPurchaseDate, getAccountValue, getLastOrderedStock, update_keys, checkFirstRun, initial_setup, getChartData, buildTables, createLog, createDBFile, getDbPath, getLogs
from datetime import datetime
from threading import Thread
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
    running = False
    trading_thread = None
    # bcknd_script_pid = getProcessId()
    
except:
    db_path = getDbPath()
    if not os.path.exists(db_path):
        createDBFile(db_path)
        print("Database file created at:", db_path)
    firstRun = True
    timestamps = []
    equities = []
    trading_thread = None
    # bcknd_script_pid = 0
    buildTables()
    running = False


@app.route("/")
def index():
    global timestamps, equities, running
    try: 
        timestamps, equities = getChartData()
        # bcknd_script_pid = getProcessId()
        firstRun = checkFirstRun()
    except:
        firstRun = True 
        running = False

    return render_template(
        "index.html",
        running = running,
        firstRun = firstRun
    )

@app.route('/api/status')
def status():
    global running

    try:
        return jsonify({
            "running": running,
            "stock": getLastOrderedStock(),
            "accountValue": getAccountValue(),
            "purchaseDate": nextPurchaseDate(),
            "firstRun": checkFirstRun(),
        })
    except:
        return jsonify({
            "running": running
        })
    
@app.route('/api/logTable')
def logTable():
    global running
    global startup
  
    if startup == True:
        initialRun = True
        startup = False
    else:
        initialRun = False

    try:
        return jsonify({
            "running": running,
            "logs": getLogs(),
            "initialRun": initialRun

        })
    except:
        return jsonify({
            "running": running
        })

@app.route('/toggle-running', methods=['POST'])
def toggle_running():
    global running, trading_thread

    data = request.get_json()
    running = data.get('running', False)

    if running == True:
        try:
            if trading_thread is None or not trading_thread.is_alive():
                trading_thread = Thread(target=start_trading, daemon=True)
                trading_thread.start()
                log = "Trading started."
            else:
                log = "Trading already running."

        except Exception as e:
            log = "Script did not successfully start running: " + e

    else:
        try:
            stop_trading()
            log = "Script successfully stopped running."


        except:
            log = "script did not successfully stop running."
            
    
    createLog(log)
    return jsonify(success=True, running=running)

@app.route('/update-info', methods=['POST'])
def update_info():
    data = request.get_json()
    api_key = data.get("API_KEY")
    secret_key = data.get("SECRET_KEY")
    paydate = data.get("PAY_DATE")

    paydate = datetime.strptime(paydate, "%Y-%m-%d")
    paydate = datetime.strftime(paydate, "%m/%d/%Y")

    print(paydate, api_key, secret_key)
    status = update_keys(api_key,secret_key, paydate)

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