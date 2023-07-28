import pandas as pd
# import matplotlib.dates as mpl_dates

import websocket, json, openpyxl
from datetime import datetime, timedelta

class XTB:
    def __init__(self, ID, PSW):
        self.ID = ID
        self.PSW = PSW
        self.ws = 0
        self.exec_start = self.get_time()
        self.connect()
        self.login()

    ################ XTB ####################
    
    def login(self):
        login ={
            "command": "login",
            "arguments": {
                "userId": self.ID,
                "password": self.PSW
            }
        }
        login_json = json.dumps(login)
        #Sending Login Request
        result = self.send(login_json)
        result = json.loads(result)
        status = result["status"]
        if str(status)=="True":
            #Success
            return True
        else:
            #Error
            return False

    def logout(self):
        logout ={
            "command": "logout"
        }
        logout_json = json.dumps(logout)
        #Sending Logout Request
        result = self.send(logout_json)
        result = json.loads(result)
        status = result["status"]
        self.disconnect()
        if str(status)=="True":
            #Success
            return True
        else:
            #Error
            return False

    def get_AllSymbols(self):
        allsymbols ={
            "command": "getAllSymbols"
        }
        allsymbols_json = json.dumps(allsymbols)
        result = self.send(allsymbols_json)
        result = json.loads(result)
        return result

    def get_Candles(self, period, symbol, days=0, hours=0, minutes=0, qty_candles=0):
        minutes = 0
        temporality = {'M1':1, 'M5':5, 'M15':15, 'M30':30, 'H1':60, 'H4':240, 'D1':1440, 'W1':10080,'MN1':43200}
        for clave, contenido in temporality.items():
            if period == clave:
                minutes += qty_candles*contenido
                period = contenido
        # if qty_candles!=0:
        #     minutes = minutes*2 
        start = self.get_ServerTime() - self.to_milliseconds(days=days, hours=hours, minutes=minutes)
        CHART_LAST_INFO_RECORD ={
            "period": period,
            "start": start,
            "symbol": symbol
        }
        candles ={
            "command": "getChartLastRequest",
            "arguments": {"info": CHART_LAST_INFO_RECORD}
        }
        candles_json = json.dumps(candles)
        result = self.send(candles_json)
        result = json.loads(result)
        result = pd.DataFrame()
        # candles=[]
        # candle={}
        # qty=len(result["returnData"]["rateInfos"])
        # candle["digits"]=result["returnData"]["digits"]    
        # if qty_candles==0:
        #     candle["qty_candles"]=qty
        # else:
        #     candle["qty_candles"]=qty_candles
        # candles.append(candle)
        # if qty_candles==0:
        #     start_qty = 0
        # else:
        #     start_qty = qty-qty_candles
        # if qty==0:
        #     start_qty=0
        
        # for i in range(start_qty, qty):
        #     candle={}
        #     candle["datetime"]=result["returnData"]["rateInfos"][i]["ctmString"]
        #     candle["open"]=result["returnData"]["rateInfos"][i]["open"]
        #     candle["close"]=result["returnData"]["rateInfos"][i]["close"]
        #     candle["high"]=result["returnData"]["rateInfos"][i]["high"]
        #     candle["low"]=result["returnData"]["rateInfos"][i]["low"]
        #     candles.append(candle)
        # if len(candles)==1:
        #     return False
        return result#candles
    
    def get_ServerTime(self):
        time ={
            "command": "getServerTime"
        }
        time_json = json.dumps(time)
        result = self.send(time_json)
        result = json.loads(result)
        time = result["returnData"]["time"]
        return time

    ################ TIME/DATE/CONVERSIONS ####################
    def get_time(self):
        time = datetime.today().strftime('%m/%d/%Y %H:%M:%S%f')
        time = datetime.strptime(time, '%m/%d/%Y %H:%M:%S%f')
        return time

    def to_milliseconds(self, days=0, hours=0, minutes=0):
        milliseconds = (days*24*60*60*1000)+(hours*60*60*1000)+(minutes*60*1000)
        return milliseconds

    def time_conversion(self, date):
        start = "01/01/1970 00:00:00"
        start = datetime.strptime(start, '%m/%d/%Y %H:%M:%S')
        date = datetime.strptime(date, '%m/%d/%Y %H:%M:%S')
        final_date = date-start
        temp = str(final_date)
        temp1, temp2 = temp.split(", ")
        hours, minutes, seconds = temp2.split(":")
        days = final_date.days
        days = int(days)
        hours = int(hours)
        hours+=2
        minutes = int(minutes)
        seconds = int(seconds)
        time = (days*24*60*60*1000)+(hours*60*60*1000)+(minutes*60*1000)+(seconds*1000)
        return time

    ################ CHECKS ####################

    def is_on(self):
        temp1 = self.exec_start
        temp2 = self.get_time()
        temp = temp2 - temp1
        temp = temp.total_seconds()
        temp = float(temp)
        if temp>=8.0:
            self.connect()
        self.exec_start = self.get_time()

    def is_open(self, symbol):
        candles = self.get_Candles("M1", symbol, qty_candles=1)
        if len(candles)==1:
            return False
        else:
            return True
        
    ################ WEBSOCKETS ####################
        
    def connect(self):
        try:
            self.ws=websocket.create_connection("wss://ws.xtb.com/demo")
            #Success
            return True
        except:
            #Error
            return False

    def disconnect(self):
        try:
            self.ws.close()
            #Success
            return True
        except:
            return False

    def send(self, msg):
        self.is_on()
        self.ws.send(msg)
        result = self.ws.recv()
        return result+"\n"

if __name__ == '__main__':
    user = '14636280'
    password = 'Cochino24$87'
    API = XTB(user, password)

    # divisas que se quieren analizar
    divisa = 'EURUSD'
    velas = API.get_Candles("M15", divisa, qty_candles=180)
    print(velas)

    API.logout()
