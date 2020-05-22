import json
import requests
import re
import sql_db as sql

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta
from multiprocessing import Queue


def get_scrap(url, params):
    result = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    html_page = requests.Response()

    try:
        html_page = requests.get(url, headers=headers, params=params)
    except:
        print('Error!')
        return -1

    if html_page.status_code != 200:
        return -1

    soup = BeautifulSoup(html_page.content, 'html.parser')

    cards = soup.find_all(attrs={'class': 'purchase-card'})

    # print(cards)

    if cards != None:
        for card in cards:
            # print(card)
            row = {}
            row["number"] = card.find(attrs={'class': 'number'}).string
            row["type"] = card.find(attrs={'class': 'tag__link'}).string
            name_lines = card.find(
                attrs={'class': 'spoiler'}).a.text.splitlines()
            if len(name_lines) > 2:
                row["name"] = name_lines[2]
            elif len(name_lines) > 1:
                row["name"] = name_lines[1]
            else:
                row["name"] = ""

            base_url = '{uri.scheme}://{uri.netloc}'.format(
                uri=urlparse(url))
            row["href"] = "{0}".format(card.find(
                attrs={'class': 'spoiler'}).a.get('href'))

            main_props = card.find_all(attrs={'class': 'prop'})

            if len(main_props) > 0:
                # print(main_props[4])

                if main_props[2].find(attrs={'class': 'value'}).string != None:
                    row["place"] = main_props[2].find(
                        attrs={'class': 'value'}).string.replace("\r\n", '').strip()

                if main_props[4].find(attrs={'class': 'value'}).text != None:
                    value_string = main_props[4].find(
                        attrs={'class': 'value'}).text.splitlines()
                    start_date = value_string[1].split()

                    if get_month(start_date) != None:
                        row["start_date"] = start_date[0] + "." + \
                            get_month(start_date) + "." + \
                            start_date[2].replace(',', '')
                    else:
                        row["start_date"] = datetime.now(
                            tz=timezone.utc).strftime("%d.%m.%Y")

                if main_props[5].find(attrs={'class': 'value'}).text != None:
                    value_string = main_props[5].find(
                        attrs={'class': 'value'}).text.splitlines()
                    end_date = value_string[1].split()

                    if get_month(end_date) != None:
                        row["end_date"] = end_date[0] + "." + \
                            get_month(end_date) + "." + \
                            end_date[2].replace(',', '')
                    else:
                        row["end_date"] = datetime.now(
                            tz=timezone.utc).strftime("%d.%m.%Y")
            result.append(row)

            # print(row)
    return result


def search(platform: [], words: []) -> []:
    url = platform["platform_url"]

    tommorrow = datetime.strptime(platform["last_update"], "%d.%m.%Y").replace(
        tzinfo=timezone.utc) + timedelta(days=1)
    search_date_from = tommorrow.strftime("%d.%m.%Y")

    result_list = []

    for word in words:
        params = {
            "fl": "True",
            "SearchForm.Keywords": word["word"],
            "SearchForm.DatePublishedFrom": search_date_from,
            # "SearchForm.State": "1",
            # "SearchForm.TenderRuleIds": "1",
            # "SearchForm.TenderRuleIds": "2",
            # "SearchForm.TenderRuleIds": "3",
            # "SearchForm.TenderRuleIds": "4",
            # "SearchForm.TenderRuleIds": "5",
            # "SearchForm.MarketPlaceIds": "5",
            # "SearchForm.CurrencyCode": "undefined",
            # "FilterData.PageSize": "2000",
            # "FilterData.PageCount": "1",
            # "FilterData.SortingField": "DatePublished",
            # "FilterData.SortingDirection": "Desc"
        }

        result_list = result_list + \
            get_scrap(url, params)
    
    if len(result_list) > 0:
        print(' '.join(["Запись в БД",platform['platform_name'],'...']))
        sql.create_row_object(platform, result_list)
    
    sql.update_platform_date(platform["id"])
    print(' '.join(["End",platform['platform_name'],'...']))
    return result_list


def get_month(date_list):
    if len(date_list[1]) > 0:
        if date_list[1] == 'января':
            return '01'
        elif date_list[1] == 'февраля':
            return '02'
        elif date_list[1] == 'марта':
            return '03'
        elif date_list[1] == 'апреля':
            return '04'
        elif date_list[1] == 'мая':
            return '05'
        elif date_list[1] == 'июня':
            return '06'
        elif date_list[1] == 'июля':
            return '07'
        elif date_list[1] == 'августа':
            return '08'
        elif date_list[1] == 'сентября':
            return '09'
        elif date_list[1] == 'октября':
            return '10'
        elif date_list[1] == 'ноября':
            return '11'
        elif date_list[1] == 'декабря':
            return '12'
    return None
