# -*- coding: utf-8 -*-

import sys
import re
import datetime
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from time import sleep
import socket
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, WebDriverException
from urllib3.exceptions import ReadTimeoutError, ProtocolError
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# socket.setdefaulttimeout(300)

isChromeRun = True

desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
headers = {
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4882.400 QQBrowser/9.7.13059.400',
}

for key, value in headers.items():
    desired_capabilities['phantomjs.page.customHeaders.{}'.format(key)] = value


def generate_webdriver_browser():
    print("#############")
    try:
        if isChromeRun == True:
            print("This program is using local Chrome webdrive.")
            print("#############")
            # Chrome webdrive on the local machine with header information
            executable_path = "D:\seleniumWebDrivers\chromedriver.exe"
            options = webdriver.ChromeOptions()
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"
            options.add_argument('user-agent=%s' % user_agent)
            # options.add_argument('--headless')
            browser = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
        else:
            # PhantomJS webdrive on the local machine
            print("This program is using local PhantomJS webdrive.")
            print("#############")
            browser = webdriver.PhantomJS(executable_path=r"D:\seleniumWebDrivers\phantomjs.exe", desired_capabilities=desired_capabilities)
    except WebDriverException:
        # PhantomJS webdrive on the server
        print("This program is using remote server PhantomJS webdrive.")
        print("#############")
        browser = webdriver.PhantomJS(
            executable_path=r"/srv/users/fan.liu/RalphLauren_goods_data/test_tempfile/phantomjs-2.1.1-linux-i686/bin/phantomjs",
            desired_capabilities=desired_capabilities)
    return browser


def region_top_scraping(rank_category, rank_url):
    print("********** working on", rank_category, "table *********")
    print("**********", rank_url, "**********")

    # customized_strings_index = 0
    # good_subname_strings_index = 0

    topregion_page_loaded = False
    while not topregion_page_loaded:
        try:
            rank_page = generate_webdriver_browser()
            rank_page.maximize_window()
            rank_page.get(rank_url)
            sleep(3)

            category_element = rank_page.find_elements_by_xpath("//div[@class='tab']/div[position()=1]/ul/li")
            category_list = [e.text for e in category_element]
            print(",".join(category_list))
            topregion_page_loaded = True
        except ReadTimeoutError:
            topregion_page_loaded = False
            print("ReadTimeoutError occurs during opening product list page")
            rank_page.close()
            sleep(3)
        except IndexError:
            topregion_page_loaded = False
            print("IndexError happens")
            rank_page.close()
            sleep(3)


    print("Start to Process Category Content...")
    for category_index in range(len(category_element)):
        if category_list[category_index] != input_category:
            print("****** pass %s ******" % category_list[category_index])
        else:
            print("working on %s" % input_category)
            category_element[category_index].click()
            WebDriverWait(rank_page, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, 'tab-title')))
            current_category = category_element[category_index].text
            print("****** Category: %s ******" % current_category)

            subcategory_element = rank_page.find_elements_by_xpath("//div[@class='tab-content tab-bd']/div[position()=%s]/div[@class='tab-hd tab-skin-sub']/ul/li" % (category_index+1))
            subcategory_list = [e.text for e in subcategory_element if e.text]
            print(",".join(subcategory_list))

            for subcategory_index in range(len(subcategory_list)):
                subcategory_element[subcategory_index].click()
                sleep(3)
                current_subcategory = subcategory_element[subcategory_index].text
                print("****** Subcategory: %s ******" % current_subcategory)

                rank_page.find_elements_by_xpath("//div[@class='tab-title']/div[position()=1]/div/div[@class='combo sheng']/div")[0].click()
                WebDriverWait(rank_page, 20).until(EC.visibility_of_element_located((By.ID, 'shengPanel')))

                province_element = rank_page.find_elements_by_xpath("//div[@id='shengPanel']/dl/dd/em/a")
                province_string = [e.text for e in province_element]

                for province_index in range(len(province_string)):
                    rank_page.find_elements_by_xpath("//div[@class='tab-title']/div[position()=1]/div/div[@class='combo sheng']/div")[0].click()
                    WebDriverWait(rank_page, 20).until(EC.visibility_of_element_located((By.ID, 'shengPanel')))
                    rank_page.find_elements_by_xpath("//div[@id='shengPanel']/dl/dd/em/a")[province_index].click()
                    sleep(3)
                    current_province = province_string[province_index]
                    print("****** Province: %s ******" % current_province)

                    if current_province == "全国":
                        current_city = "所有省份"
                        item_list_element = rank_page.find_elements_by_xpath(
                            "//div[@class='tab']/div[@class='tab-content tab-bd']/div[position()=%s]/div[@class='tab-bd']/div[position()=%s]/div[position()=1]/div[@class='item-list-wrap']/ul[@class='item-list']/li/div[@class='item-hd']/a" % (str(input_category_index+1), str(subcategory_index+1)))
                        print("###### number of items in the list: %d ######" % len(item_list_element))
                        list_length = min(len(item_list_element), 10)
                        if list_length == 0:
                            print("This city has no available data\n")
                            current_rank = "DataUnavailable"
                            current_keyword = "DataUnavailable"
                            print("****** rank: %s, keyword: %s ******" % (current_rank, current_keyword))

                            result = ",".join([scrape_date, current_province, current_city, current_category, current_subcategory, current_keyword, current_rank])
                            region_top_table.writelines(result)
                            region_top_table.writelines("\n")
                            region_top_table.flush()
                            sleep(0.3)
                            continue
                        for item_index in range(list_length):
                            current_rank = str(item_index + 1)
                            current_keyword = item_list_element[item_index].get_attribute("title").replace(",","-")
                            print("****** rank: %s, keyword: %s ******" % (current_rank, current_keyword))

                            result = ",".join([scrape_date, current_province, current_city, current_category, current_subcategory,current_keyword, current_rank])
                            region_top_table.writelines(result)
                            region_top_table.writelines("\n")
                            region_top_table.flush()
                            sleep(0.5)
                            print(current_rank, current_keyword, "is completed.")
                        print(current_city, "city is completed.")
                    else:
                        rank_page.find_elements_by_xpath("//div[@class='tab-title']/div[position()=1]/div/div[@class='combo shi']/div")[0].click()
                        WebDriverWait(rank_page, 20).until(EC.visibility_of_element_located((By.ID, 'shiPanel')))

                        city_element = rank_page.find_elements_by_xpath("//div[@id='shiPanel']/dl/dd/em/a")
                        city_string = [e.text for e in city_element]
                        isMetroCity = False
                        if len(city_string) == 2:
                            isMetroCity = True

                        for city_index in range(len(city_string)):
                            rank_page.find_elements_by_xpath("//div[@class='tab-title']/div[position()=1]/div/div[@class='combo shi']/div")[0].click()
                            WebDriverWait(rank_page, 20).until(EC.visibility_of_element_located((By.ID, 'shiPanel')))
                            rank_page.find_elements_by_xpath("//div[@id='shiPanel']/dl/dd/em/a")[city_index].click()
                            sleep(3)
                            current_city = city_string[city_index]
                            print("****** City: %s ******" % current_city)

                            if current_city == "所有城市" and isMetroCity == True:
                                print("This is a metro city")
                                pass
                            else:
                                item_list_element = rank_page.find_elements_by_xpath(
                                    "//div[@class='tab']/div[@class='tab-content tab-bd']/div[position()=%s]/div[@class='tab-bd']/div[position()=%s]/div[position()=1]/div[@class='item-list-wrap']/ul[@class='item-list']/li/div[@class='item-hd']/a" % (str(input_category_index+1),str(subcategory_index+1)))
                                print("###### number of items in the list: %d ######" % len(item_list_element))
                                list_length = min(len(item_list_element), 10)
                                if list_length == 0:
                                    print("This city has no available data\n")
                                    current_rank = "DataUnavailable"
                                    current_keyword = "DataUnavailable"
                                    print("****** rank: %s, keyword: %s ******" % (current_rank, current_keyword))

                                    result = ",".join([scrape_date, current_province, current_city, current_category, current_subcategory, current_keyword, current_rank])
                                    region_top_table.writelines(result)
                                    region_top_table.writelines("\n")
                                    region_top_table.flush()
                                    sleep(0.3)
                                    continue
                                for item_index in range(list_length):
                                    current_rank = str(item_index+1)
                                    current_keyword = item_list_element[item_index].get_attribute("title").replace(",","-")
                                    print("****** rank: %s, keyword: %s ******" % (current_rank, current_keyword))

                                    result = ",".join([scrape_date, current_province, current_city, current_category, current_subcategory, current_keyword, current_rank])
                                    region_top_table.writelines(result)
                                    region_top_table.writelines("\n")
                                    region_top_table.flush()
                                    sleep(0.3)
                                    print(current_rank, current_keyword, "is saved to csv.")
                            sleep(2)
                            print(current_city, "city is completed.\n")
                    sleep(2)
                    print(current_province, "province is completed.\n\n")
                sleep(2)
                print(current_subcategory, "subcategory is completed.\n\n\n")
            sleep(2)
            print(current_category, "category is completed.\n\n\n\n")
    sleep(2)
    print("All top items are completed")
    rank_page.close()



if __name__ == "__main__":
    all_category = ["娱乐", "人物", "小说", "热点", "生活", "热搜"]
    input_category_index = int(sys.argv[1]) - 1
    input_category = all_category[input_category_index]

    start = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    category_list = {
        "top_region": "http://top.baidu.com/region?fr=topregion"
    }

    scrape_date = datetime.datetime.now().strftime('%Y-%m-%d')
    file_date = scrape_date.replace("-","")

    region_top_table = open("BaiduRegionTop_%s.csv" % input_category, "w", encoding="utf-8")
    region_top_table.writelines("date,province,city,category,subcategory,keyword,rank")
    region_top_table.writelines("\n")
    region_top_table.flush()

    for category, category_link in category_list.items():
        region_top_scraping(category, category_link)

    region_top_table.close()

    end = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("\n\n Scraping is Done! %s, %s \n\n" % (start, end))







