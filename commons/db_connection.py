import json
import pathlib
import sqlite3
import traceback
from sqlite3 import OperationalError
from typing import Union

from commons.case_info import CaseInfo
from commons.common import Common
from commons.probing_result import ProbingResult


class DBConnection:
    def __init__(self):
        self.connection_string = "./" + Common.DATABASE_PATH + "/reports.db"
        self.connection = None
        self.create_table()

    def create_table(self):
        try:
            Common.create_path("./" + Common.DATABASE_PATH)
        except Union[FileExistsError, FileNotFoundError] as ex:
            print(ex)

        try:
            query_string_cases = "create table if not exists cases (" \
                                 "id INTEGER PRIMARY KEY, " \
                                 "case_no TEXT," \
                                 "ps TEXT," \
                                 "examiner_name TEXT," \
                                 "examiner_no TEXT," \
                                 "remarks TEXT," \
                                 "subject_url TEXT," \
                                 "created_date DATE," \
                                 "probe_id TEXT," \
                                 "matched TEXT," \
                                 "report_generation_time TEXT," \
                                 "json_result TEXT);"
            # query_string_targets = "create table if not exists targets (" \
            #                        "id INTEGER PRIMARY KEY, " \
            #                        "target_url TEXT," \
            #                        "case_id INTEGER," \
            #                        "similarity FLOAT);"
            self.connection = sqlite3.connect(self.connection_string)
            cursor = self.connection.cursor()
            cursor.execute(query_string_cases)
            # cursor.execute(query_string_targets)
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())

        finally:
            if self.connection:
                self.connection.close()

    def get_values(self):
        results = []
        try:
            query_string = "select " \
                           "cases.id,probe_id,matched," \
                           "case_no,PS,examiner_no,examiner_name,remarks" \
                           ",subject_url,json_result,created_date" \
                           " from cases " \
                           " order by created_date desc"
            self.connection = sqlite3.connect(self.connection_string)
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchall()
            self.connection.commit()
            for row in rows:
                probe_result = ProbingResult()
                case_info = CaseInfo()
                probe_result.probe_id = row[1]
                probe_result.matched = row[2]
                case_info.case_number = row[3]
                case_info.case_PS = row[4]
                case_info.examiner_no = row[5]
                case_info.examiner_name = row[6]
                case_info.remarks = row[7]
                case_info.subject_image_url = row[8]
                json_data = row[9]
                json_data = json.dumps(json_data)
                json_data = json.loads(json_data)
                probe_result.json_result = json_data
                probe_result.created_date = row[10]
                probe_result.case_info = case_info
                results.append(probe_result)
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
        return results

    # values : list of tuples
    def insert_values(self, table_name, fields, values):
        # data = [
        #     ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
        #     ("Monty Python's The Meaning of Life", 1983, 7.5),
        #     ("Monty Python's Life of Brian", 1979, 8.0),
        # ]
        # cur.executemany("INSERT INTO movie VALUES(?, ?, ?)", data)
        # con.commit()  # Remember to commit the transaction after executing INSERT.
        try:
            self.connection = sqlite3.connect(self.connection_string)
            cursor = self.connection.cursor()
            query_string = "insert into " + table_name + "(" #values("
            # add field names to query
            for field in fields:
                query_string += field
                query_string += ","
            # remove last comma
            len_query = len(query_string)
            query_string = query_string[0:len_query - 1]
            query_string += ") values("
            # add value field to query
            for i in range(len(values[0])):
                query_string += "?,"
            query_string = query_string[0:len([query_string]) - 2]
            query_string += ")"
            cursor.executemany(query_string, values)
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())

        finally:
            if self.connection:
                self.connection.close()

    def is_exist_value(self, table_name, field, value):
        try:
            query_string = "select * from " + table_name + " where " + field + "=" + value
            self.connection = sqlite3.connect(self.connection_string)
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchone()
            self.connection.commit()
            if rows:
                for row in rows:
                    return True
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
        return False
    # def update_table(self, table_name, fields, values):
    #     try:
    #         self.connection = sqlite3.connect("data.db")
    #         cursor = self.connection.cursor()
    #         cursor.execute("UPDATE appinfo SET isdst = ?, expire = ?, fpo = ?, atpo = ?",
    #                        (True, expire_dt.strftime('%d/%m/%Y'), fpo_value, "0"))
    #         self.connection.commit()
    #
    #     except OperationalError:
    #         print("Database Error")
    #
    #     finally:
    #         if self.connection:
    #            self.connection.close()
    #
    # def delete_value(self, table_name, field, value):
    #     try:
    #         self.connection = sqlite3.connect("data.db")
    #         cursor = self.connection.cursor()
    #         cursor.execute("UPDATE appinfo SET isdst = ?, expire = ?, fpo = ?, atpo = ?",
    #                        (True, expire_dt.strftime('%d/%m/%Y'), fpo_value, "0"))
    #         self.connection.commit()
    #
    #     except OperationalError:
    #         print("Database Error")
    #
    #     finally:
    #         if self.connection:
    #               self.connection.close()
