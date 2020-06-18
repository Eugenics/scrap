import time
import os
import requests
import requests.exceptions as r_exc
import json

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta, time

import sql_db as sql

def search(platform: [], words: []) -> []:
    """
    Returns: List of search result strings

    Parameters:
        platform([]): Platform for search,
        word({}): Search word
    """
    result = []

    url = platform["platform_url"]
    ticks = (datetime.strptime(
        platform["last_update"], "%d.%m.%Y") - datetime(1970, 1, 1)).days * 24 * 60 * 60
    headers = {'Content-type': 'application/json'}

    #search_pages_result = []

    for word in words:
        print(word["word"])
        print('Seaching page count...')
        

        json_data = {
            "manager": "sphinx",
            "entity": "Procedure",
            "alias": "procedure",
            "fields": [
                "procedure.purchaseNumber",
                "procedure.purchaseObjectInfo",
                "procedure.status",
                "procedure.placerFullName",
                "procedure.maxSum",
                "procedure.type",
                "procedure.publicationDateTime",
                "procedure.startDateTime",
                "procedure.endDateTime",
                "procedure.substatus",
                "procedure.requestEndGiveDateTime"
            ],
            "conditions": {
                "procedure.id": ["gt", 0],
                "purchaseNumber,purchaseObjectInfo": ["match", word["word"]],
                "procedure.publicationDateTime": [["gte", ticks]],
                "region": ["match", ["04", "17", "19", "22", "24", "38", "42", "54", "55", "70"]]
            },
            "rules": ["Procedure.Registry", "Procedure.AdditionalInfo"],
            "limit": 10000
        }

        r = requests.post(url, data=json.dumps(json_data), headers=headers)

        #print(word)
        #print(ticks)
        response_json_data = r.json()
        #print(response_json_data['data']['entities'])
        
        if len(response_json_data['data']['entities']) > 0:
            for entity in response_json_data['data']['entities']:
                procedure_data = entity['procedure']
                print(procedure_data)

                row = {}

                row["start_date"] = procedure_data['publicationDateTime'].split()[0].strip()
                row["end_date"] = procedure_data['requestEndGiveDateTime'].split()[0].strip()
                row["number"] = procedure_data['purchaseNumber']
                row["type"] = procedure_data['type']
                row["href"] = ''.join(['https://gz.lot-online.ru/etp_front/procedure/view/procedure/common/',procedure_data['purchaseNumber']])
                row["name"] = procedure_data['purchaseObjectInfo']
                row["place"] = 'СФО'

                print(row)

                result.append(row)

    # Insert into db
    if len(result) > 0:
        print(''.join(["Запись в БД", platform["platform_name"], '...']))
        sql.create_row_object(platform, result)

    sql.update_platform_date(platform["id"])

    print(len(result))
    print(result)

    return result
