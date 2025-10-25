from flask import Flask, render_template, request, jsonify
from Alpaca.Scripts.script_controls import runScript, stopScript, checkScriptRunning
from Alpaca.Database.db_functions import getProcessId, nextPurchaseDate, getAccountValue, getLastOrderedStock, update_keys, checkFirstRun, initial_setup, getChartData, buildTables, createLog, createDBFile, getDbPath, getLogs
from datetime import datetime
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
    running = checkScriptRunning(getProcessId())
    bcknd_script_pid = getProcessId()
    
except:
    db_path = getDbPath()
    if not os.path.exists(db_path):
        createDBFile(db_path)
        print("Database file created at:", db_path)
    firstRun = True
    timestamps = []
    equities = []
    bcknd_script_pid = 0
    buildTables()
    running = False


@app.route("/")
def index():
    global bcknd_script_pid, timestamps, equities
    try: 
        timestamps, equities = getChartData()
        running = checkScriptRunning(getProcessId())
        bcknd_script_pid = getProcessId()
        firstRun = checkFirstRun()
    except:
        firstRun = True
        bcknd_script_pid = getProcessId()
        buildTables()
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
    global running, bcknd_script_pid

    data = request.get_json()
    running = data.get('running', False)

    if running == True:
        try:
            currentState = checkScriptRunning(bcknd_script_pid)
            if currentState == False:
                bcknd_script_pid = runScript()
                
                log = "Script successfully started running."
                createLog(log)

        except Exception as e:
            log = "Script did not successfully start running: " + e
            createLog(log)

    else:
        try:
            stopScript(bcknd_script_pid)
            log = "Script successfully stopped running PID " + bcknd_script_pid
            createLog(log)
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