import sqlite3


class DBConnection():
    def __init__(self):
        self.connection = sqlite3.connect()
        try:
            connection = sqlite3.connect("data.db")
            cursor = connection.cursor()
            cursor.execute("UPDATE appinfo SET isdst = ?, expire = ?, fpo = ?, atpo = ?",
                           (True, expire_dt.strftime('%d/%m/%Y'), fpo_value, "0"))
            connection.commit()

        except OperationalError:
            print("Database Error")

        finally:
            connection.close()