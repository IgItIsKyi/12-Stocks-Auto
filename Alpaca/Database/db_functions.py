import sqlite3
from cryptography.fernet import Fernet
from alpaca_trade_api.rest import REST
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
BASE_URL = 'https://paper-api.alpaca.markets'



db_path = r".\Alpaca\Database\12Auto.db"

def checkFirstRun():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key FROM user WHERE id = 1")
        return False
    except:
        # Create popup to get initial SQL information
        buildTables()
        return True
    

def buildTables():
    # SQL Connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the alpaca user table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        api_key BLOB,
        secret BLOB,
        key BLOB,
        pay_date TEXT,
        cur_stock TEXT, 
        process_pid TEXT
    )
    """)

        # Create "logs" Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (

            id INTEGER PRIMARY KEY,
            info TEXT,
            date TEXT               
        )
    """)
    # Create "stocks" Table and add all 12 stocks

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (

                id INTEGER PRIMARY KEY,
                stock_sym TEXT 
                    
            )
                    
        """)

        # Add all stocks to the table (each stock gives a dividend at some point)
    stocks = ['BDCX', 'NHPAP', 'CWPS', 'TWO', 'ABR', 'AB', 'ARLP', 'HTGC', 'SPQ', 'WHF', 'TRIN', 'CION']
    for stock in stocks: 
        cursor.execute("INSERT INTO stocks (stock_sym) VALUES (?)", (stock,))

    conn.commit()

    conn.close()

def getLogs():
    # SQL Connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    log_info = []
    log_date = []
    # Get all log information from SQL Table
    cursor.execute("SELECT info, date FROM logs")
    logs = cursor.fetchall()


    conn.close()

    for log in logs:
        log_info.append(log[0])
        log_date.append(log[1])

        print(f"Log: {log[0]} Timestamp: {log[1]}")

        
    return log_info, log_date


def createLog(log):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%H:%M %m/%d/%Y ")
    cursor.execute("INSERT INTO logs (info, date) VALUES (?,?)", (log, timestamp))
    print(f"Log: {log} \nTimestamp: {timestamp}")

    conn.commit()
    conn.close()
  

def getProcessId():
    # SQL Connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try: 
        cursor.execute("SELECT process_pid FROM user WHERE id = 1")
        pid = cursor.fetchone()

        conn.close()
        return pid[0]

    except:
        return 0
    
def updateProcessId(new_pid):
    # SQL Connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
                    UPDATE user
                    SET process_pid = ?
                    Where id = 1
                    """, (new_pid,)
                )
    
    conn.commit()
    conn.close()

def nextPurchaseDate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try: 
        cursor.execute("SELECT pay_date FROM user WHERE id = 1")
        purchaseDate = cursor.fetchone()

        return purchaseDate[0]

    except:
        print("No purchase date")

    conn.close()

# Alpaca Direct Values

def getAccountInfo():
    # SQL Connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT key FROM user WHERE id = 1")
    key = cursor.fetchone()
    cipher = Fernet(key[0])

    cursor.execute("SELECT api_key, secret FROM user WHERE id = 1")
    encrypted_row = cursor.fetchone()
    decrypted_apiKey = cipher.decrypt(encrypted_row[0]).decode()
    decrypted_secretKey = cipher.decrypt(encrypted_row[1]).decode()

    return decrypted_apiKey, decrypted_secretKey


def getAccountValue():
    API_KEY, SECRET_KEY = getAccountInfo()
    api = REST(API_KEY, SECRET_KEY, BASE_URL)

    account = api.get_account()
    portfolio_value = account.portfolio_value


    return portfolio_value

def getLastOrderedStock():
    API_KEY, SECRET_KEY = getAccountInfo()
    api = REST(API_KEY, SECRET_KEY, BASE_URL)

    account = api.get_activities(page_size=1)
    last_stock = account[0].symbol

    return last_stock

def getChartData():
    API_KEY, SECRET_KEY = getAccountInfo()
    api = REST(API_KEY, SECRET_KEY, BASE_URL)

    date_end = date.today().strftime("%Y-%m-01")
    date_start = (datetime.strptime(date_end, "%Y-%m-%d").date() - relativedelta(months=5)).strftime("%Y-%m-%d")

    portfolio_history = api.get_portfolio_history(
        date_start=date_start,
        date_end=date_end
    )

    # Extract first-of-month data
    first_by_month = {}
    for ts, eq in zip(portfolio_history.timestamp, portfolio_history.equity):
        month_key = datetime.fromtimestamp(ts).strftime("%Y-%m")
        if month_key not in first_by_month:
            readable_date = datetime.fromtimestamp(ts).strftime("%B %Y")
            first_by_month[month_key] = (readable_date, eq)

    # Separate into two lists
    timestamps = [item[0] for item in first_by_month.values()]
    equities = [item[1] for item in first_by_month.values()]

    return timestamps , equities


def update_keys(api_key, secret_key, paydate):
    if api_key == "" and secret_key == "" and paydate == "":
        return False
    
    try:
    # API and SECRET togethet
        if api_key != "" and secret_key != "":
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                if api_key == "" or secret_key == "":
                    return False
                else:
                    cursor.execute("SELECT key FROM user WHERE id = 1")
                    key = cursor.fetchone()
                    cipher = Fernet(key[0])
                
                    encrypted_api_key = cipher.encrypt(api_key.encode())
                    encrypted_secret_key = cipher.encrypt(secret_key.encode())

                    cursor.execute("""
                        UPDATE user
                        SET api_key = ?, secret = ?
                        Where id = 1
                        """, (encrypted_api_key, encrypted_secret_key )
                    )

                    conn.commit()
                    conn.close()

                    log = "Keys updated successfully."
                    createLog(log)

                return True

            except Exception as e:
                log = "Exception occured updating keys: " + e
                createLog(log)
                return False
        if paydate != "":
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                
                cursor.execute("""
                    UPDATE user
                    SET pay_date = ?
                    Where id = 1
                    """, (paydate, )
                )

                log = "Date updated successfully."
                createLog(log)

                conn.commit()
                conn.close()


            except Exception as e:
                log = "Exception occured updating paydate: " + e
                createLog(log)
    except:
        return False
    
def initial_setup(api, secret, payday, initial_stock):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try: 
        if api == "" or secret == "" or payday == "":
            return False

        print(f'Stock: {initial_stock}')
        try:
            cursor.execute("SELECT id FROM stocks WHERE stock_sym = ?", (initial_stock, ))
            stock = cursor.fetchone()[0]
        except:
            stock = 1
        print(f"Stock number: {stock}")

        key = Fernet.generate_key()
        print(f"Key: {key}")
        cipher = Fernet(key)

        encrypted_api_key = cipher.encrypt(api.encode())
        encrypted_secret_key = cipher.encrypt(secret.encode())

        cursor.execute("INSERT INTO user (api_key, secret, key, pay_date, cur_stock) VALUES (?,?,?,?,?)", (encrypted_api_key, encrypted_secret_key, key, payday, stock, ))
        print("Successful initial setup")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Unsuccessful initial setup: " + e)
        return False
    

getLogs()