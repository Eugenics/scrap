import time
import os

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webelement import WebElement

import sql_db as sql


def search(platform: [], word: {}) -> []:
    """
    Returns: List of search result strings

    Parameters:
        platform([]): Platform for search,
        word({}): Search word
    """
    url = platform["platform_url"]
    search_date_from = platform["last_update"]
    result = []

    print(url)
    print(search_date_from)
    print(word)

    print("Start service...")
    service = Service('\\'.join([os.path.dirname(os.path.abspath(__file__)),'chromedriver_win32\\chromedriver']))
    service.start()
    #time.sleep(10)
    driver = webdriver.Remote(service.service_url)
    print("Service started...")
    #time.sleep(5)

    # driver = Chrome('D:\\Projects\\Python\\scrap\\scripts\\chromedriver_win32\\chromedriver')
    print("Get URL...")
    driver.get('https://www.sberbank-ast.ru/UnitedPurchaseList.aspx')
    print("Got URL...")
    time.sleep(10)    

    # Get extra properties form elements
    extra_properties_element = driver.find_element_by_class_name(
        'element-in-one-row.simple-button.orange-background')
    extra_properties_element.click()
    time.sleep(10)

    # Get form elements
    search_element = driver.find_element_by_id('searchInput')
    date_from_element = driver.find_element_by_id('PublicDateMin')
    submit_element = driver.find_element_by_class_name(
        'mainSearchBar-find')

    # Fill elements
    search_element.clear()
    date_from_element.clear()
    #time.sleep(5)
    search_element.send_keys(word['word'])
    date_from_element.send_keys(' '.join([search_date_from,'00:00']))

    # Submit search
    submit_element.click()
    time.sleep(5)

    
    # Page select
    print("Click pager select button...")
    try:    #NoSuchElementException 
        error = driver.find_elements_by_id('ErrorArea')
        page_select_element = driver.find_element_by_id('headerPagerSelect')
        page_select_element.send_keys('100')
        print("Clicked...")        
        time.sleep(5)            
    except:
        print("Pager select button not found...")
        driver.quit()
        service.stop()
        print("Service stoped...")
        return result

    # Get table element
    tables = driver.find_elements_by_class_name('es-reestr-tbl.its')
    if len(tables) > 0:
        for table in tables:
            try:
                table_rows = table.find_elements_by_tag_name('tr')
                table_row = table_rows[0].text.splitlines()

                """
                    web_elements = []
                    web_elements = table_rows
                    for web_element in web_elements:
                        if web_element.get_attribute('content') == 'node:_source':
                            input_element = web_element.find_element_by_xpath(
                                './/td[2]/div[1]/input[2]')
                            if input_element != None:
                                print(input_element.get_attribute('value'))
                    """

                row = {}

                row["number"] = table_row[4].strip().split()[1].strip()
                row["type"] = table_row[0].strip()
                row["name"] = table_row[8].strip()
                row["href"] = table_rows[0].find_element_by_xpath(
                    './/td[2]/div[1]/input[2]').get_attribute('value').strip()
                row["place"] = "не указан"
                row["start_date"] = table_row[14].split()[0].strip()
                row["end_date"] = table_row[16].split()[0].strip()

                #print(row)

                result.append(row)
            except:
                continue

            """
                //*[@id="resultTbl"]/tbody/tr[1]/td[2]/div[1]/input[2]
                if len(table_rows) > 0:
                    print(len(table_rows))
                    for row in table_rows:
                        print(row.text.splitlines())
                else:
                    print('Nothing')
                """
    print("Stop service...")
    driver.quit()
    service.stop()
    print("Service stoped...")
    time.sleep(5)

    # Insert into db
    if len(result) > 0:
        print("Запись в БД Сбербанк...")
        sql.create_row_object(platform, result)

    sql.update_platform_date(platform["id"])
    return result
