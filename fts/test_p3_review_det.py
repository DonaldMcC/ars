# - Coding UTF8 -
# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first
# this should now answer both a question and an issue


from functional_tests import FunctionalTest, ROOT, USERS
import time
from ddt import ddt, data, unpack
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

@ddt
class AnswerAction (FunctionalTest):

    def setUp(self):
        self.url = ROOT + '/default/user/login'
        get_browser = self.browser.get(self.url)

    fields = ['selection', 'sortorder', 'filters', 'view_scope', 'country', 'subdivision',
              'category', 'startdate', 'enddate', 'coord', 'searchrange']

    # think we add dictionary with keys linked to selectiosn and then do same to ratings
    @data((USERS['USER2'], USERS['PASSWORD2'], 'The world is under-achieving', {'fullname': 'DMcC', 'orgtype': 'Cther'}),
          (USERS['USER3'], USERS['PASSWORD3'], 'Lets get this done', {'fullname': 'DMcC', 'orgtype': 'Cther'}))
    @unpack
    def test_answer_action(self, user, passwd, result, othervals):
        mailstring = user + '@user.com'

        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")
        password.send_keys(passwd)

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)

        self.url = ROOT + '/review/newindex'
        get_browser=self.browser.get(self.url)

        draftclick = self.browser.find_element_by_id("selectionDraft")
        draftclick.click()
        sortordclick = self.browser.find_element_by_id("sortorder2 Importance")
        sortordclick.click()
        #filterclick = self.browser.find_element_by_id("filtersScope")
        #filterclick.click()
        filtercategory = self.browser.find_element_by_id("filtersCategory")
        filtercategory.click()
        #filtersdate = self.browser.find_element_by_id("filtersDate")
        #filtersdate.click()
        #scope2 = self.browser.find_element_by_id("view_scope2 Regional")
        #scope2.click()

        #Select(self.browser.find_element_by_id("viewscope_country")).select_by_visible_text("United Arab Emirates")
        #Select(self.browser.find_element_by_id("viewscope_subdivision")).select_by_visible_text("[Abu Dhabi]")
        #Select(self.browser.find_element_by_id("viewscope_category")).select_by_visible_text("No Poverty")

        #startdate = self.browser.find_element_by_id("viewscope_startdate").click()
        #driver.find_element_by_css_selector("td.selected.day").click()
        #driver.find_element_by_id("viewscope_enddate").click()
        #driver.find_element_by_css_selector("tr.daysrow.rowhilite > td.selected.day").click()
        #driver.find_element_by_xpath("//button[@type='submit']").click()

        submit_button = self.browser.find_element_by_xpath("//button[@type='submit']")
        submit_button.click()
        time.sleep(3)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(result, body.text)

        self.url = ROOT + '/default/user/logout'
        get_browser=self.browser.get(self.url)
