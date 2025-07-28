import os
import sqlite3
from alpaca_trade_api.rest import REST
import json
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

db_path = r".\Alpaca\Database\12Auto.db"

BASE_URL = 'https://paper-api.alpaca.markets'

api_key = "PKO7ILCG3OLE42UQ2JYT"
secret = "cupqwDtkzIjqdAUSV6WMCXFLMOUhpmfiWFTbt40m"


api = REST(api_key, secret, BASE_URL)

# Get account value
account = api.get_account()
portfolio_value = account.portfolio_value
# print(f"Portfolio value: ${portfolio_value}")

# Start of new function "getChartData"

# End of new function "getChartData"

# Get last ordered stock
account = api.get_activities(page_size=1)
last_stock = account[0].symbol

#print(f"Last ordered stock: {last_stock}")

# pretty_json = json.dumps(account[0], indent=4, sort_keys=True)


conn = sqlite3.connect(db_path)
cursor = conn.cursor()
info =   cursor.execute("SELECT info, date FROM logs")
logs = cursor.fetchall()

conn.close()

paydate = "07/27/2025"

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

        print(paydate)

        print("Date updated successfully")
        conn.close()
    except Exception as e:
        print(f"Exception occured: {e}")