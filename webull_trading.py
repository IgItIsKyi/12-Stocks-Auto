from webull import webull
import sqlite3
import json
from datetime import datetime, timedelta
import time
from cryptography.fernet import Fernet

wb = webull()

conn = sqlite3.connect("12Auto.db")
cursor = conn.cursor()





def getWebullAccountInfo():
    cursor.execute("SELECT key FROM user WHERE id = 1")
    key = cursor.fetchone()
    cipher = Fernet(key[0])

    cursor.execute("SELECT email, password FROM user WHERE id = 1")
    encrypted_row = cursor.fetchone()
    decrypted_email = cipher.decrypt(encrypted_row[0]).decode()
    decrypted_password = cipher.decrypt(encrypted_row[1]).decode()

    cursor.execute("SELECT did FROM user WHERE id = 1")
    device_id = cursor.fetchone()
    decrypted_did = cipher.decrypt(device_id[0]).decode()

    return decrypted_email, decrypted_password, decrypted_did


# Get account information
def submit_webull_order(sym):
    try:
        response = wb.place_order(stock=sym, orderType= "MKT", enforce='IOC', quant= 1)
        print(response)

    except:
        print("unable to place order.")

def getNextRunDate(old_date):
    data_OD = datetime.strptime(old_date, "%m/%d/%Y")
    days_14 = timedelta(days=14)
    next_run_date = data_OD + days_14
    
    next_run_date = next_run_date.strftime("%m/%d/%Y")
    print("New paydate: ", next_run_date)
    cursor.execute("UPDATE user SET pay_date = ? WHERE id = 1", (next_run_date,))
    conn.commit()

# while(True):

    login = False
    try:
        email, password, device_id = getWebullAccountInfo()
        wb._did = device_id 
        wb.login(email, password)
        login = True
    except:
        print("unable to login. Check email, password, or device ID for webull")
    
    if login == True:
        cursor.execute("SELECT pay_date FROM user WHERE id = 1")
        paydate = cursor.fetchone()[0]

        current_day = datetime.now().strftime("%m/%d/%Y")

        if current_day == paydate:
            print("It's payday!")
            getNextRunDate(paydate)
            submit_webull_order()
        else:
            print("Not payday... Sorry")
            time.sleep(82800)

email, password, device_id = getWebullAccountInfo()
wb._did = device_id 
now = wb.login(email, password)
wb.get_account_id()
wb.get_trade_token('080503')
submit_webull_order('KEY')

conn.close()
