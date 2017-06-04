# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class RecordToFix(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://127.0.0.1:8081/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_record_to_fix(self):
        driver = self.driver
        driver.get(self.base_url + "/ars/review/newindex")
        driver.find_element_by_id("selectionDraft").click()
        driver.find_element_by_id("sortorder2 Importance").click()
        driver.find_element_by_id("filtersScope").click()
        driver.find_element_by_id("filtersCategory").click()
        driver.find_element_by_id("filtersDate").click()
        driver.find_element_by_id("view_scope2 Regional").click()
        Select(driver.find_element_by_id("viewscope_country")).select_by_visible_text("United Arab Emirates")
        Select(driver.find_element_by_id("viewscope_subdivision")).select_by_visible_text(u"Abū Ȥaby [Abu Dhabi]")
        Select(driver.find_element_by_id("viewscope_category")).select_by_visible_text("No Poverty")
        driver.find_element_by_id("viewscope_startdate").click()
        driver.find_element_by_css_selector("td.selected.day").click()
        driver.find_element_by_id("viewscope_enddate").click()
        driver.find_element_by_css_selector("tr.daysrow.rowhilite > td.selected.day").click()
        driver.find_element_by_xpath("//button[@type='submit']").click()
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
