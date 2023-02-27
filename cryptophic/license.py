import sqlite3, os
from cryptophic.main import encrypt_file, decrypt_file, get_dec_file_path
from pyutil import filereplace
import cpuinfo, wmi

license_file_name = r"license.dat"
dec_secure_path = r"C:\\Users\\" + os.getlogin() + r"\\.secure\\.encfiles"

def access_license_list(license_str):
    expire_flag = ""
    decrypt_file(os.path.join(license_file_name))
    dec_secure_path = get_dec_file_path()

    try:
        listFile = open(os.path.join(dec_secure_path, license_file_name), "r")
        if listFile:
            # Match inputed license and license list file
            matched = False
            for line in listFile:
                if license_str in line:
                    matched = True
                    expire_flag = line.split("&")[1]
            listFile.close()   

            # If Matched
            if matched == True:
                print("Matched")
                ## Delete matched license from list file                   
                filereplace(os.path.join(dec_secure_path, license_file_name), license_str, "")
            else:
                print("Unmatched")
                encrypt_file(license_file_name)
                return (False, expire_flag)
        else:
            print("File non-exist")
            encrypt_file(license_file_name)
            return (False, expire_flag)
    except:
        print("File open error")
        encrypt_file(license_file_name)
        return (False, expire_flag)

    encrypt_file(license_file_name)
    return (True, expire_flag)
    

def read_information_db():
    try:
        connection = sqlite3.connect("./data.db")
        cursor = connection.cursor()
    
        (count,) = connection.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{}'".format("appinfo")).fetchone()
        if count == 0:
            cursor.execute("""CREATE TABLE appinfo (isdst, expire, fpo, atpo)""")
            cursor.execute("INSERT INTO appinfo VALUES (?,?,?,?)", (False, "expire", "fpo", "atpo"))
            connection.commit()
    
        cursor.execute("SELECT * FROM appinfo")
        result = cursor.fetchone()
        unlocked = result[0]
        expire_date = result[1]
        fpo_info = result[2]
    
    except OperationalError:
        print("Database Error")
    
    finally:
        connection.close()

    return (unlocked, expire_date, fpo_info)

def write_infomation_db(isdst, expire, fpo, atpo):
    try:
        connection = sqlite3.connect("./data.db")
        cursor = connection.cursor()  
        cursor.execute("UPDATE appinfo SET isdst = ?, expire = ?, fpo = ?, atpo = ?", (isdst, expire, fpo, atpo))
        connection.commit()    

    except: 
        print("Database Error")   

    finally:
        connection.close() 

def get_cpu_info():
    fpo_value = ""
    c = wmi.WMI()
    for s in c.Win32_Processor():
        fpo_value = s.ProcessorId

    return fpo_value