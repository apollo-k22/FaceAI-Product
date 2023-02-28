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
import ntplib
import time
from time import ctime
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import cpuinfo, wmi
from cryptophic.license import write_infomation_db, access_license_list

class LicenseBoxPage(QMainWindow):
    continue_app_signal = pyqtSignal()
    def __init__(self):
        super().__init__()

        self.window = uic.loadUi("./forms/Page_0.ui", self)
        self.btnConfirm.clicked.connect(self.procLicenseConfirm)   
        self.lblNotify = self.findChild(QLabel, "labelNotify")

    # The function for license process confirm
    def procLicenseConfirm(self):  
        # info = cpuinfo.get_cpu_info()
        # print(info)        

        lic = self.licenseBox.text()
        if len(lic) < 20:
            print("License length is not enough")
            self.lblNotify.setText("License length is not enough")
            return
        # Read license list file
        ret, expire_flag = access_license_list(lic)
        
        if not ret:
            self.lblNotify.setText("The license is not correct")
            return

        self.lblNotify.setText("The license is correct. One minutes...")
        expire_dt = None

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
        atpo_value = ""
        c = wmi.WMI()
        for s in c.Win32_Processor():
            fpo_value = s.ProcessorId
            atpo_value = s.Description

        write_infomation_db(True, expire_dt.strftime('%d/%m/%Y'), fpo_value, atpo_value) 

        ## Goto homepage  
        self.lblNotify.setText("Let's go to home page")
        self.continue_app_signal.emit()
        