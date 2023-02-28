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
            query_string_targets = "create table if not exists targets (" \
                                   "id INTEGER PRIMARY KEY, " \
                                   "target_url TEXT," \
                                   "case_id INTEGER," \
                                   "similarity FLOAT);"
            self.connection = sqlite3.connect(self.connection_string)
            cursor = self.connection.cursor()
            cursor.execute(query_string_cases)
            cursor.execute(query_string_targets)
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())

        finally:
            if self.connection:
                self.connection.close()

    def count_row_number(self, table_name):
        try:
            query_string = "select count(id) from " + table_name + ";"
            self.connection = sqlite3.connect(self.connection_string)
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            row = cursor.fetchone()
            self.connection.commit()
            if row:
                return row[0]
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
        return 0

    def get_values(self):
        results = []
        try:
            query_string = "select " \
                           "id,probe_id,matched," \
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

    def get_last_inserted_id(self, table_name, id_field):
        try:
            query_string = "select " + id_field + " from " + table_name + " order by " + id_field + " desc;"
            self.connection = sqlite3.connect(self.connection_string)
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchone()
            self.connection.commit()
            if rows:
                for row in rows:
                    return row
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
        return 0

    # values : list of tuples
    def insert_values(self, table_name, fields, values):
        try:
            self.connection = sqlite3.connect(self.connection_string)
            cursor = self.connection.cursor()
            query_string = "insert into " + table_name + "("
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
        return self.get_last_inserted_id(table_name, "id")

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

    def get_case_info(self, image_path):
        case_no = ''
        ps = ''
        try:
            query_string = "select " \
                           "case_no,PS from cases " \
                           " where id=(select case_id from targets where target_url='" + image_path + "')"
            self.connection = sqlite3.connect(self.connection_string)
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchall()
            self.connection.commit()
            for row in rows:
                case_no = row[0]
                ps = row[1]
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
        return case_no, ps

    def get_pagination_results(self, param, current_page, number_per_page):
        results = []
        last_index = current_page * number_per_page
        query_string = ""
        if last_index:
            query_string = "select id,probe_id,matched," \
                           "case_no,PS,examiner_no,examiner_name,remarks" \
                           ",subject_url,json_result,created_date" \
                           " from " \
                           " (select * from cases order by created_date DESC) as a " \
                           " where a.id < (select min(id) from (select * from cases order by created_date DESC limit " \
                           + str(last_index) + "))"
        else:
            query_string = "select id,probe_id,matched," \
                           "case_no,PS,examiner_no,examiner_name,remarks" \
                           ",subject_url,json_result,created_date" \
                           " from cases order by created_date DESC limit " + str(number_per_page)

        try:
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
