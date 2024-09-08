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

#создаём экземпляр класса ActionChains (класс из библиотеки выше)
actions = ActionChains(driver)

#получаем путь к дом элементу через xpath (для элемента Market data)
market_data_hover = driver.find_element(By.XPATH, '/html/body/header/nav/div[2]/div/div/ul/li[3]/a')

#выполняем действие наводения курсора на элемент
actions.move_to_element(market_data_hover).perform()
time.sleep(2.37)

#получаем путь к элементу Pre-Open Market и кликаем
pre_open_market_click = driver.find_element(By.XPATH, '/html/body/header/nav/div[2]/div/div/ul/li[3]/div/div[1]/div/div[1]/ul/li[1]/a').click()
time.sleep(7.29)

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
time.sleep(9.25)
graph_xpath = driver.find_element(By.XPATH, '//*[@id="tab1_container"]')
#driver.execute_script("arguments[0].scrollIntoView(True);", graph_xpath)
actions.move_to_element(graph_xpath).perform()

#выбираем график NIFTY BANK
driver.find_element(By.XPATH, '//*[@id="tabList_NIFTYBANK"]').click()
time.sleep(1.53)

#нажимаем view all
view_all_xpath = driver.find_element(By.XPATH, '//*[@id="tab4_gainers_loosers"]/div[3]/a')
#driver.execute_script("arguments[0].scrollIntoView(True);", view_all_xpath)
actions.move_to_element(view_all_xpath).click().perform()
time.sleep(7.42)

#выбираем в списке NIFTY ALPHA 50
driver.find_element(By.XPATH, '//*[@id="equitieStockSelect"]').click()
time.sleep(1.91)

nifty_alpha_50_click = driver.find_element(By.XPATH, '//*[@id="equitieStockSelect"]/optgroup[4]/option[7]').click()
time.sleep(1.59)

#Прокручиваем таблицу вниз
nifty_alpha_50_table_xpath = driver.find_element(By.XPATH, '//*[@id="equityStockTable"]')
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);", nifty_alpha_50_table_xpath)
time.sleep(1.50)

driver.quit()
