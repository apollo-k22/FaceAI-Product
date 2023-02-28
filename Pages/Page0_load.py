from sqlite3 import OperationalError

from PyQt5 import uic
import sys
# from PyQt5 import QtWidgets
# from Page1 import Ui_MainWindow
# from page1_load import Start_Page
# import images
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sqlite3
from pyutil import filereplace
import ntplib
import time
from time import ctime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import cpuinfo, wmi

class LicenseBoxPage(QMainWindow):
    def __init__(self):
        super().__init__()

        self.window = uic.loadUi("./forms/Page_0.ui", self)
        self.btnConfirm.clicked.connect(self.procLicenseConfirm)   

    
    # The function for license process confirm
    def procLicenseConfirm(self):      

        info = cpuinfo.get_cpu_info()
        print(info)        

        lic = self.licenseBox.text()
        if len(lic) < 3:
            print("License length is not enough")
            return
        licenseFileName = "license.dat"
        # Read license list file
        try:
            listFile = open(licenseFileName, "r")
            if listFile:
                # Match inputed license and license list file
                matched = False
                expire_flag = ""
                for line in listFile:
                    if lic in line:
                        matched = True
                        expire_flag = line.split("&")[1]
                listFile.close()    

                # If Matched
                if matched == True:
                    print("Matched")
                    ## Delete matched license from list file                   
                    filereplace(licenseFileName, lic, "")
                    
                    expire_dt = None
                    ## Write FPO, ATPO, locked flag and validate date to Database   

                    ### getting validate date                 
                    try:
                        # NIST = 'pool.ntp.org'
                        # ntp = ntplib.NTPClient()
                        # ntpResponse = ntp.request(NIST)                        

                        today_dt = datetime.strptime(ctime(time.time()), "%a %b %d %H:%M:%S %Y")
                        # today_dt = datetime.strptime(ctime(ntpResponse.tx_time), "%a %b %d %H:%M:%S %Y")

                        if "1Year" in expire_flag:
                            expire_dt = today_dt + relativedelta(months=+12)
                        elif "1Month" in expire_flag:
                            expire_dt = today_dt + relativedelta(months=+1)
                        elif "1Day" in expire_flag:
                            expire_dt = today_dt + timedelta(days=1)

                    except:
                        print("ntp error")

                    ### getting processor batch number(FPO) and partial serial number(ATPO) date   
                    fpo_value = ""
                    c = wmi.WMI()
                    for s in c.Win32_Processor():
                        fpo_value = s.ProcessorId

                    try:
                        connection = sqlite3.connect("data.db")
                        cursor = connection.cursor()  
                        cursor.execute("UPDATE appinfo SET isdst = ?, expire = ?, fpo = ?, atpo = ?", (True, expire_dt.strftime('%d/%m/%Y'), fpo_value, "0"))
                        connection.commit()    

                    except OperationalError: 
                        print("Database Error")   

                    finally:
                        connection.close()  

                    ## Goto homepage      
                    

                # If Nonmatched
                else:
                    print("Nonmatched")
            
        except:
            print("File non exist")
        
        
        