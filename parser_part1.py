from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
from selenium_stealth import stealth
import csv
from itertools import zip_longest

def get_chromedriver(use_proxy=False, user_agent=None):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("start-maximized")

    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    if use_proxy:
        chrome_options.add_argument('--proxy-server=168.81.65.213:8000')

    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    driver = webdriver.Chrome(options=chrome_options)

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win64",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

    return driver

#ЧАСТЬ 1
  
# Переходим по ссылке
driver = get_chromedriver(use_proxy=True)

driver.get('https://www.nseindia.com')
#driver.get('https://atomurl.net/myip/')
#cur_url = driver.current_url

#получаем путь к дом элементу через xpath (для элемента Market data)
market_data_xpath = "/html/body/header/nav/div[2]/div/div/ul/li[3]/a"
market_data_hover = driver.find_element(By.XPATH, market_data_xpath)

#создаём экземпляр класса ActionChains (класс из библиотеки выше)
actions = ActionChains(driver)

#выполняем действие наводения курсора на элемент
actions.move_to_element(market_data_hover).perform()
time.sleep(2.37)

#получаем путь к элементу Pre-Open Market
pre_open_market_xpath = "/html/body/header/nav/div[2]/div/div/ul/li[3]/div/div[1]/div/div[1]/ul/li[1]/a"
pre_open_market_click = driver.find_element(By.XPATH, pre_open_market_xpath)

#кликаем по элементу Pre-Open Market
actions.move_to_element(pre_open_market_click).click().perform()
time.sleep(8.29)

#Парсим таблицу
rows = driver.find_elements(By.XPATH, '//*[@id="livePreTable"]/tbody/tr')

with open("data_part1.csv", mode="w", encoding='utf-8', newline='') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerow(['Name', 'Price'])
    for row in rows:
        splited_string = row.text.split()
        if splited_string[0]!="Total":
            line = [splited_string[0], splited_string[5]]
            writer.writerow(line)

#Часть 2

#Заново переходим на главную страницу
driver.get('https://www.nseindia.com')

#имитация скроллинга до графика
#html = driver.find_element(By.TAG_NAME, 'html')
#for i in range(10):
#    html.send_keys(Keys.DOWN)
graph_xpath = driver.find_element(By.XPATH, '//*[@id="highcharts-05iem9s-810"]')
driver.execute_script("arguments[0].scrollIntoView(true);", graph_xpath)

#выбираем график NIFTY BANK
nifty_bank_xpath = '//*[@id="tabList_NIFTYBANK"]'
nifty_bank_click = driver.find_element(By.XPATH, nifty_bank_xpath)

actions.move_to_element(nifty_bank_click).click().perform()
time.sleep(2.13)

#нажимаем view all
view_all_xpath = '//*[@id="tab4_gainers_loosers"]/div[3]/a'
view_all_click = driver.find_element(By.XPATH, view_all_xpath)

actions.move_to_element(view_all_click).click().perform()
time.sleep(7.42)

#выбираем в списке NIFTY ALPHA 50
nifty_bank_list_xpath = '//*[@id="equitieStockSelect"]'
nifty_bank_list_click = driver.find_element(By.XPATH, nifty_bank_list_xpath)
time.sleep(1.91)

actions.move_to_element(nifty_bank_list_click).click().perform()

nifty_alpha_50_xpath = '//*[@id="equitieStockSelect"]/optgroup[4]/option[7]'
nifty_alpha_50_click = driver.find_element(By.XPATH, nifty_alpha_50_xpath)

actions.move_to_element(nifty_alpha_50_click).click().perform()
time.sleep(2.09)

#Прокручиваем таблицу вниз
nifty_alpha_50_table_xpath = driver.find_element(By.XPATH, '//*[@id="equityStockTable"]')
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);", nifty_alpha_50_table_xpath)


driver.quit()
