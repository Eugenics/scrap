import time
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

import sql_db as sql


def search(platform: [], word: {}) -> []:
    """
    Returns: List of search result strings

    Parameters:
        platform([]): Platform for search,
        word({}): Search word
    """
    url = platform["platform_url"]
    search_date_from = '01.01.20'  # platform["last_update"]

    search_sub_url = 'https://www.roseltorg.ru/procedures/search_ajax?query_field=' + \
        word['word']+'&customer=&status[]=0&status[]=1&status[]=2&status[]=3&status[]=4&region[]=04&region[]=17&region[]=19&region[]=22&region[]=24&region[]=38&region[]=42&region[]=54&region[]=55&region[]=70&currency=all&start_date_published=' + \
        search_date_from+'&form_id=searchp_form&page=&from=11'
    url = '?'.join([url, search_sub_url])

    result = []

    print(url)
    print(search_date_from)
    print(word)

    print("Start service...")
    service = Service('\\'.join([os.path.dirname(
        os.path.abspath(__file__)), 'chromedriver_win32\\chromedriver']))
    service.start()
    # time.sleep(10)
    driver = webdriver.Remote(service.service_url)
    print("Service started...")
    # time.sleep(5)

    print("Get URL...")
    driver.get(url)
    print("Got URL...")
    time.sleep(10)

    # Get extra properties form elements
    extra_properties_element = driver.find_element_by_class_name(
        'search-form__btn-advanced-search')
    extra_properties_element.click()
    time.sleep(10)

    # Get search elements
    search_element = driver.find_element_by_class_name(
        'search-form__keywordinput')
    date_from_element = driver.find_element_by_id('edit-start-date-published')
    submit_element = driver.find_element_by_class_name(
        'button.search-form__button-submit.js-submit')

    # Fill search elements
    search_element.clear()
    date_from_element.clear()
    time.sleep(5)
    search_element.send_keys(word['word'])
    date_from_element.send_keys(search_date_from)

    # Submit search
    time.sleep(5)
    submit_element.click()
    time.sleep(5)

    # Find results
    print('Findig results...')
    try:
        search_result = driver.find_elements_by_class_name(
            'search-results__info-text')
        print('No results find...')
        driver.quit()
        service.stop()
        print("Service stoped...")
        return result
    except NoSuchElementException as exception:
        print("Results find...")
        print(exception.msg)

    time.sleep(10)

    # Get table element
    #tables = driver.find_elements_by_class_name('es-reestr-tbl.its')
    # if len(tables) > 0:
    # for table in tables:
    # try:
    #table_rows = table.find_elements_by_tag_name('tr')
    #table_row = table_rows[0].text.splitlines()
    #row = {}

    # row["number"] = table_row[].strip()
    # row["type"] = table_row[].strip()
    # row["name"] = table_row[].strip()
    # row["href"] = table_rows[].strip()
    # row["place"] = table_rows[].strip()                     # or set "не указан"
    # row["start_date"] = table_row[].strip()
    # row["end_date"] = table_row[].strip()

    # print(row)
    # result.append(row)
    # except:
    # continue
    print("Stop service...")
    driver.quit()
    service.stop()
    print("Service stoped...")
    time.sleep(5)

    # Insert into db
    if len(result) > 0:
        print(''.join(["Запись в БД", platform["paltform_name"], '...']))
        sql.create_row_object(platform, result)

    sql.update_platform_date(platform["id"])
    return result
