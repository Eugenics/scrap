import json
import requests
import re
import sql_db as sql


from multiprocessing import Queue

from bs4 import BeautifulSoup
from urllib.parse import urlparse


def get_pages(url, params):
    page_count = 0

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
    }

    try:
        html_page = requests.get(url, headers=headers, params=params)
        # print(html_page.url)
        # print(html_page.status_code)

        if html_page.status_code != 200:
            return {"status_code": html_page.status_code, "page_count": 0}

        soup = BeautifulSoup(html_page.content, 'html.parser')
        pages = soup.findAll('li', {'class': 'page'})

        if soup.find_all(attrs={'class', "search-registry-entrys-block"}) != None:
            if pages != None:
                page_count = len(pages)
            else:
                page_count = 1

        return {"status_code": html_page.status_code, "page_count": page_count}
    except:
        print('Error!')
        return {"status_code": "404", "page_count": 0}


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

    pages = soup.findAll('li', {'class': 'page'})
    if pages != None:
        # print(len(pages))
        search_block = soup.find_all(
            attrs={'class', "search-registry-entrys-block"})

        if search_block != None:
            row_scope = soup.findAll(
                attrs={'class', 'row no-gutters registry-entry__form mr-0'})

            # rint(row_scope)

            if len(row_scope) > 0:
                for element in row_scope:
                    row = {}
                    if element.findAll(attrs={'class', 'data-block__value'}) != None:
                        date_elements = element.findAll(
                            attrs={'class', 'data-block__value'})
                        # print(len(date_elements))
                        if len(date_elements) > 0:
                            row["start_date"] = date_elements[0].string.strip()
                            if len(date_elements) == 3:
                                row["end_date"] = date_elements[2].string.strip()
                            else:
                                row["end_date"] = date_elements[1].string.strip()
                        else:
                            row["start_date"] = ""
                            row["end_date"] = ""
                    else:
                        row["start_date"] = ""
                        row["end_date"] = ""
                    if element.find(attrs={'class', 'registry-entry__header-mid__number'}) != None:
                        row["number"] = element.find(
                            attrs={'class', 'registry-entry__header-mid__number'}).a.string.strip()
                    else:
                        row["number"] = ""
                    if element.find(attrs={'class', 'registry-entry__header-top__title text-truncate'}) != None:
                        row["type"] = element.find(
                            attrs={'class', 'registry-entry__header-top__title text-truncate'}).text.replace("\n                               ", " ").strip()
                    else:
                        row["type"] = ""
                    if element.find(attrs={'class', 'registry-entry__body-value'}) != None:
                        row["name"] = element.find(
                            attrs={'class', 'registry-entry__body-value'}).text.strip()
                    else:
                        row["name"] = ""
                    row["place"] = 'СФО'
                    base_url = '{uri.scheme}://{uri.netloc}'.format(
                        uri=urlparse(url))
                    if element.find(attrs={'class', 'registry-entry__header-mid__number'}) != None:
                        _href = element.find(
                            attrs={'class', 'registry-entry__header-mid__number'}).a.get('href')
                        if _href.find("https", 0, 5):
                            row["href"] = "{0}{1}".format(base_url, _href)
                        else:
                            row["href"] = "{0}".format(_href)
                    else:
                        row["href"] = ""

                    result.append(row)

    return result


def search(platform: [], words: []) -> []:
    url = platform["platform_url"]
    search_date_from = platform["last_update"]

    result_list = []

    for word in words:
        params = {
            "searchString": word["word"],
            "morphology": "on",
            "search-filter": "Дате+размещения",
            "pageNumber": "1",
            "sortDirection": "false",
            "recordsPerPage": "_50",
            "showLotsInfoHidden": "false",
            "fz44": "on",
            "fz223": "on",
            "sortBy": "UPDATE_DATE",
            "af": "on",
            "ca": "on",
            "pc": "on",
            "pa": "on",
            "publishDateFrom": search_date_from,
            "currencyIdGeneral": "-1",
            "delKladrIdsWithNested": "on",
            "delKladrIds": "5277384",
            "delKladrIdsCodes": "OKER35"
        }

        page_count = get_pages(url, params)

        # print(page_count)

        if page_count["status_code"] == 200 and page_count["page_count"] > 0:
            # print(word["word"])
            # print(page_count)

            for p in range(page_count["page_count"]):
                # print(p+1)
                params["pageNumber"] = str(p+1).strip()
                result_list = result_list + get_scrap(url, params)

    if len(result_list) > 0:
        print(' '.join(["Запись в БД",platform['platform_name'],'...']))
        sql.create_row_object(platform, result_list)

    sql.update_platform_date(platform["id"])
    print(' '.join(["End",platform['platform_name'],'...']))
    return result_list
