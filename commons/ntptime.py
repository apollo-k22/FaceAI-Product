import time
import ntplib
from datetime import datetime
from time import ctime

def ntp_get_time():
    try:
        NIST = 'pool.ntp.org'
        ntp = ntplib.NTPClient()
        ntpResponse = ntp.request(NIST)                        
        today_dt = datetime.strptime(ctime(ntpResponse.tx_time), "%a %b %d %H:%M:%S %Y")
        return today_dt
    except Exception as e:
        print("ntp_get_time: ", e)
        today_dt = datetime.strptime(ctime(time.time()), "%a %b %d %H:%M:%S %Y")
        return today_dt
        # return None