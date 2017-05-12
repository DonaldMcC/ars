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

    @data((USERS['USER2'], USERS['PASSWORD2'], 'The world is under-achieving'), (USERS['USER3'], USERS['PASSWORD3'], 'Lets get this done'))
    @unpack
    def test_answer_action(self, user, passwd, result):
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

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(result, body.text)

        self.url = ROOT + '/default/user/logout'
        get_browser=self.browser.get(self.url)
