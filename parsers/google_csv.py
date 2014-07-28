"""Module uses ability to download csv files from google trends
"""
from io import StringIO
import pickle
import random
import time
import urllib
import selenium.common

import selenium.webdriver as webdriver

import contextlib
import os
import lxml.html as LH

__author__ = 'user'


from parsers.parser import Parser
import csv
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GoogleCsvParser(Parser):

    init_dir = "data/gcsv"
    browser = None



    def get_response(self, query):

        if self.browser is None:
            self.browser = self.Render()
        #time.sleep(random.randint(110, 180))
        response = self.browser.get_url("http://www.google.com/trends/explore#q=Madonna%2C%20Adele&cmpt=q")
        #response = pickle.load(open(self.init_dir+'/response', 'rb'))
        loggin_link = self.check_loggin(response)
        if loggin_link:
            self.login(loggin_link)
        return response



    def get_raw_data(self, response):
        #print(response)
        pass

    def check_loggin(self, response):
        link = self.browser.frame.findFirstElement('#gb_70')
        return link.toOuterXml()

    def login(self, loggin_link):
        time.sleep(random.randint(20, 40))
        print('logging...')
        response = self.browser.get_url(loggin_link)


def sleep(min, max):
    time.sleep(random.randint(min, max))


if __name__ == '__main__':
    # gcp = GoogleCsvParser()
    # gcp.parse_fresh("asp.net")
    os.environ["SELENIUM_SERVER_JAR"] = "/home/user/selenium-server-standalone-2.42.1.jar"
    os.environ["PATH"] = os.environ["PATH"] + ":/usr/java/jre1.7.0_65/bin"
    d_capabilities= DesiredCapabilities.OPERA
    d_capabilities["opera.binary"] = "/usr/bin/opera"
    d_capabilities["opera.profile"] = "/home/user/.opera"
    driver = webdriver.Opera(desired_capabilities=d_capabilities)
    driver.get("google.com")

    names = pickle.load(open("../top_names.pkl", 'rb'))
    for idx, name in enumerate(names):
        print(idx, ": ", name)
        link = "http://www.google.com/trends/explore#q={0}&cmpt=q".format(name)
        driver.get(link)
        try:
            loglink = driver.find_element_by_css_selector("#gb_70")
        except selenium.common.exceptions.NoSuchElementException:
            loglink = None
        if loglink is not None:
            print(loglink.text)
            actions = webdriver.ActionChains(driver)
            sleep(5, 15)
            actions.click(loglink)
            actions.perform()

            email_field = driver.find_element_by_css_selector("#Email")
            passw_field = driver.find_element_by_css_selector("#Passwd")
            btn = driver.find_element_by_css_selector("#signIn")

            email_field.send_keys('bspaskov')
            sleep(1, 5)
            passw_field.send_keys('asdfzxcv!')
            sleep(3, 7)

            btn.click()

            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "settings-menu-button"))
                )
            except:
                driver.get("http://www.google.com/trends/explore#cmpt=q")
            sleep(3, 10)
            driver.get(link)
            print("logged")

        btn_menu = driver.find_element_by_css_selector("#settings-menu-button")
        btn_menu.click()
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "exportMI"))
            )
        finally:
            print("  start download")
            download_btn = driver.find_element_by_css_selector('#exportMI')
            download_btn.click()
        print("  find download, sleep")
        sleep(111, 279)






