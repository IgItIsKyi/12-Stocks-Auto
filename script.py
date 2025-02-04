from cryptography.fernet import Fernet
import sqlite3
import time
from datetime import datetime, timedelta
from alpaca_trade_api.rest import REST

BASE_URL = 'https://paper-api.alpaca.markets'  # Needed for Alpaca Account
run = True   # Keep program running


# SQL Connection
conn = sqlite3.connect("12Auto.db")
cursor = conn.cursor()

# Calculate and update next run date
def getNextRunDate(old_date):
    data_OD = datetime.strptime(old_date, "%m/%d/%Y")
    days_14 = timedelta(days=14)
    next_run_date = data_OD + days_14
    
    next_run_date = next_run_date.strftime("%m/%d/%Y")
    print("New paydate: ", next_run_date)
    cursor.execute("UPDATE user SET pay_date = ? WHERE id = 1", (next_run_date,))
    conn.commit()

# Retrieve and decrypt data
def getAcctInfo():
    cursor.execute("SELECT key FROM user WHERE id = 1")
    key = cursor.fetchone()
    cipher = Fernet(key[0])

    cursor.execute("SELECT api_key, secret FROM user WHERE id = 1")
    encrypted_row = cursor.fetchone()
    decrypted_apiKey = cipher.decrypt(encrypted_row[0]).decode()
    decrypted_secretKey = cipher.decrypt(encrypted_row[1]).decode()

    return decrypted_apiKey, decrypted_secretKey

def submitOrder():
    # Figure out what stock id the user has
    cursor.execute("SELECT cur_stock FROM user WHERE id = 1")
    stock_id = cursor.fetchone()[0]

    # Search the id in the stocks table
    cursor.execute("SELECT stock_sym FROM stocks WHERE id = ?", (stock_id,))
    stock = cursor.fetchone()[0]
    print("Stock:", stock)
    order = False


    while( order != True ):
        try:
            # Submit order to current stock
            api.submit_order(symbol=stock,type="market",qty=1)

            note = "Submitted order for " + stock
            date = datetime.now().strftime("%m/%d/%Y")
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
            print("Next stock is #" + str(next_stock))

        except:
            date = datetime.now().strftime("%m/%d/%Y")
            note = "Unable to submit order. Trying again in 24 hours."
            cursor.execute("INSERT INTO logs (info, date) VALUES (?,?)", (note, date))
            conn.commit()
            time.sleep(86400)  # Seconds converted to a day

# Script Starts here #

API_KEY, SECRET_KEY = getAcctInfo()
api = REST(API_KEY, SECRET_KEY, BASE_URL)


while(run):

    cursor.execute("SELECT pay_date FROM user WHERE id = 1")
    paydate = cursor.fetchone()[0]

    current_day = datetime.now().strftime("%m/%d/%Y")

    if current_day == paydate:
        print("It's payday!")
        getNextRunDate(paydate)
        submitOrder()
    else:
        print("Not payday... Sorry")
        time.sleep(82800)

conn.close()
