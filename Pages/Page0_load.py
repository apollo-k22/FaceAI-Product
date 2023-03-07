import wmi
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from cryptophic.license import write_infomation_db, access_license_list
from commons.ntptime import ntp_get_time


class LicenseBoxPage(QWidget):
    continue_app_signal = pyqtSignal(str)

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
        today_dt = ntp_get_time()
        if today_dt is None:
            Common.show_message(QMessageBox.Warning, "NTP server was not connected", "",
                                "NTP Error.",
                                "")
            quit()

        if "1Year" in expire_flag:
            expire_dt = today_dt + relativedelta(months=+12)
        elif "1Month" in expire_flag:
            expire_dt = today_dt + relativedelta(months=+1)
        elif "1Day" in expire_flag:
            expire_dt = today_dt + timedelta(days=1)


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
        self.continue_app_signal.emit(expire_dt.strftime('%d/%m/%Y'))
