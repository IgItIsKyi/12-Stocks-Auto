from cryptography.fernet import Fernet
import sqlite3
import time
from datetime import datetime, timedelta
from alpaca_trade_api.rest import REST
import os
import sys
from threading import Thread, Event

def setup_paths():
    """
    Sets up sys.path so that the Database and Scripts folders
    are accessible both in development and in PyInstaller .exe.
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable
        base_path = sys._MEIPASS
    else:
        # Running in development (from source)
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Make sure the base path is first in sys.path
    if base_path not in sys.path:
        sys.path.insert(0, base_path)

    # Optional: debug print
    # print("Base path for imports:", base_path)
    # print("sys.path:", sys.path)

# Call the setup function
setup_paths()
    
from Database.db_functions import getDbPath, get_base_url, get_env_var
BASE_URL = get_base_url(get_env_var())  # Needed for Alpaca Account
db_path = getDbPath()
stop_event = Event()
trading_thread = None


running = False
is_running = False
# Calculate and update next run date
def getNextRunDate(old_date):

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    testing = False

    if testing == False:
        days_14 = timedelta(days=14)
        next_run_date = old_date + days_14
        
        next_run_date = next_run_date.strftime("%m/%d/%Y")
        print("New paydate: ", next_run_date)
        cursor.execute("UPDATE user SET pay_date = ? WHERE id = 1", (next_run_date,))
        conn.commit()
    else:
        days_14 = timedelta(seconds=3)
        next_run_date = old_date + days_14
        
        next_run_date = next_run_date.strftime("%m/%d/%Y")

    conn.close()

def getPayDate():

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT pay_date FROM user WHERE id = 1")
    paydate = cursor.fetchone()[0]
    conn.close()
    paydate = datetime.strptime(paydate, "%m/%d/%Y")

    print("Pay date: " + str(paydate))
    
    return paydate

# Retrieve and decrypt data
def getAccountInfo():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT key FROM user WHERE id = 1")
    key = cursor.fetchone()
    cipher = Fernet(key[0])

    cursor.execute("SELECT api_key, secret FROM user WHERE id = 1")
    encrypted_row = cursor.fetchone()
    conn.close()
    decrypted_apiKey = cipher.decrypt(encrypted_row[0]).decode()
    decrypted_secretKey = cipher.decrypt(encrypted_row[1]).decode()

    return decrypted_apiKey, decrypted_secretKey

def submitAlpacaOrder():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Figure out what stock id the user has
    cursor.execute("SELECT cur_stock FROM user WHERE id = 1")
    stock_id = cursor.fetchone()[0]

    # Search the id in the stocks table
    cursor.execute("SELECT stock_sym FROM stocks WHERE id = ?", (stock_id,))
    stock = cursor.fetchone()[0]
    order = False

    conn.close()

    while( order != True ):
        try:
            # Submit order to current stock
            api.submit_order(symbol=stock,type="market",qty=1)

            note = "Submitted order successfully for " + stock
            date = datetime.now().strftime("%m/%d/%Y")


            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("INSERT INTO logs (info, date) VALUES (?,?)", (note, date))
            order = True

            # Move to next stock in table
            cursor.execute("SELECT id FROM stocks WHERE stock_sym = ?", (stock,))
            current_stock = cursor.fetchone()[0]

            if current_stock == 12:
                next_stock = 1
            else:
                next_stock = current_stock + 1
                
            cursor.execute("UPDATE user SET cur_stock = ? WHERE id = 1", (next_stock,))
            conn.commit()
            conn.close()
            getNextRunDate(getPayDate())

        except Exception as e:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            date = datetime.now().strftime("%m/%d/%Y")
            note = "Unable to submit order. Trying again in 1 hour. Exception: " + str(e)
            cursor.execute("INSERT INTO logs (info, date) VALUES (?,?)", (note, date))
            conn.commit()
            conn.close()
            time.sleep(3600)  # Seconds converted to an hour

# Script Starts here #
try:
    API_KEY, SECRET_KEY = getAccountInfo()
    api = REST(API_KEY, SECRET_KEY, BASE_URL)
except:
    pass

def start_trading():

    global is_running
    if is_running == False:
        is_running = True


    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()

    while is_running:
        print("Running trading logic...")

        try:
            cursor.execute("SELECT pay_date FROM user WHERE id = 1")
            paydate = cursor.fetchone()[0]
            conn.close()
            current_day = datetime.now()
            paydate = datetime.strptime(paydate, "%m/%d/%Y")

            if not paydate:
                print("No pay date found.")
                stop_event.wait(10)
                continue

            if current_day >= paydate:
                print("It's payday!")
                submitAlpacaOrder()
                stop_event.wait(10)

            else:
                print("Not payday... Waiting 1 hour")
                time.sleep(3600) # Waits an hour
        except Exception as e:
            print("Error in trading logic: ", e)
            stop_event.wait(5)

def start_service():
    global is_running, trading_thread

    if not is_running:
        stop_event.clear()
        trading_thread = Thread(target=start_trading, daemon=True)
        trading_thread.start()
        is_running = True

    return is_running

def stop_service():
    global is_running


    stop_event.set()
    is_running = False
    return True
