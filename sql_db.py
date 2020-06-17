import sqlite3
import os
import datetime
import json
from datetime import datetime, timedelta, timezone

from sqlite3 import Error


def create_db_connection():
    conn = None

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    try:
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'scrap.db'))
    except Error as e:
        print(e)

    return conn


def get_search_words():
    conn = create_db_connection()

    result_list = []

    sql_string = "SELECT * FROM search_words"

    try:
        with conn:
            sql_cursor = conn.cursor()
            sql_cursor.execute(sql_string)

            for row in sql_cursor.fetchall():
                result_list.append({
                    "id": row[0],
                    "word": row[1]
                })
    except Error as e:
        print(e)

    return json.dumps(result_list, ensure_ascii=False)


def get_exclude_words():
    conn = create_db_connection()

    result_list = []

    sql_string = "SELECT * FROM exclude_words"

    try:
        with conn:
            sql_cursor = conn.cursor()
            sql_cursor.execute(sql_string)

            for row in sql_cursor.fetchall():
                result_list.append({
                    "id": row[0],
                    "word": row[1]
                })
    except Error as e:
        print(e)

    return result_list


def get_regions():
    conn = create_db_connection()

    result_list = []

    sql_string = "SELECT * FROM regions"

    try:
        with conn:
            sql_cursor = conn.cursor()
            sql_cursor.execute(sql_string)

            for row in sql_cursor.fetchall():
                result_list.append({
                    "id_region": row[0],
                    "region_name": row[1],
                    "region_code": row[2]
                })
    except Error as e:
        print(e)

    return result_list


def get_search_platform():
    conn = create_db_connection()

    result_list = []

    sql_string = "SELECT * FROM search_platforms"

    try:
        with conn:
            sql_cursor = conn.cursor()
            sql_cursor.execute(sql_string)
            for row in sql_cursor.fetchall():
                result_list.append(
                    {
                        "id": row[0],
                        "platform_name": row[1],
                        "platform_url": row[2],
                        "last_update": row[3],
                        "exclude_from_search": row[4]
                    }
                )
    except Error as e:
        print(e)

    return json.dumps(result_list, ensure_ascii=False)


def create_row_object(platform, result_data):
    regions_list = get_regions()
    regions = []
    for region in regions_list:
        regions.append(region["region_name"])

    exclude_words = get_exclude_words()

    sql_result = 0
    for row in result_data:
        # print(row)
        ex = 0

        for ex_word in exclude_words:
            #print(row)
            #print(ex_word)
            #print(row["name"].find(ex_word["word"]))
            if row["name"].find(ex_word["word"]) > 0:
                ex = 1

        if row["place"] in regions and ex == 0:  # Если нужный регион и нет слов исключения
            print(row)
            sql_object = (platform["id"],
                          datetime.strptime(row["start_date"], "%d.%m.%Y").replace(
                              tzinfo=timezone.utc),
                          datetime.strptime(row["end_date"], "%d.%m.%Y").replace(
                              tzinfo=timezone.utc),
                          row["href"],
                          datetime.now(tz=timezone.utc),
                          row["number"],
                          row["type"],
                          row["name"],
                          row["place"],
                          row["number"]
                          )
            print(sql_object)
            ret_val = insert_row_object(sql_object)
            if ret_val == -1:
                sql_result = -1

    #if sql_result == 0:
    #    update_platform_date(platform["id"])


def insert_row_object(sql_object):
    #print(sql_object)
    conn = create_db_connection()

    sql_string = '''INSERT INTO search_result(id_platform,start_date,end_date,url_string,create_date,result_number,result_type,result_text,result_place)
                    SELECT ?,?,?,?,?,?,?,?,?
                    WHERE ? NOT IN (SELECT sr2.result_number FROM search_result sr2)'''

    try:
        with conn:
            print(sql_string)
            sql_cursor = conn.cursor()
            sql_cursor.execute(sql_string, sql_object)
        return 0
    except Error as e:
        print(e)
        return -1


def update_platform_date(platform_id):
    conn = create_db_connection()

    today = datetime.today() - timedelta(days=1)
    sql_string = "UPDATE search_platforms SET update_date = '" + \
        today.strftime('%d.%m.%Y') + "' WHERE id = " + str(platform_id).strip()

    try:
        with conn:
            sql_cursor = conn.cursor()
            sql_cursor.execute(sql_string)
            return 0
    except Error as e:
        print(e)
        return -1
