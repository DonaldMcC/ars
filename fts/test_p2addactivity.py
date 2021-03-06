# These tests are all based on the tutorial at http://killer-web-development.com/
# if registration is successful this may work but lets
# try and get user logged in first


from functional_tests import FunctionalTest, ROOT, USERS
from ddt import ddt, data, unpack
import time
from selenium.webdriver.support.ui import WebDriverWait


@ddt
class AddBasicAction (FunctionalTest):

    def setUp(self):
        self.url = ROOT + '/default/user/login'        
        get_browser = self.browser.get(self.url)

        mailstring = USERS['USER3']+'@user.com'
        email = self.browser.find_element_by_name("email")

        email = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name("email"))
        email.send_keys(mailstring)

        password = self.browser.find_element_by_name("password")    
        password.send_keys(USERS['PASSWORD3'])

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()
        time.sleep(1)

    @data(('/submit/index', 'Lets get this done', {'fullname': 'DMcC', 'orgtype': 'Cther', 'organisation': 'DMcC Ltd',
                                                    'town': 'bla'}),
          ('/submit/index', 'The world is under-achieving',
           {'fullname': 'DMcC', 'orgtype': 'Cther', 'organisation': 'DMcC Ltd',
            'country': 'United States', 'subdivision': 'Unspecified', 'town': 'bla', 'category': 'Energy'}),
          ('/submit/index', 'Thailand Unspecified Subdivision Category Energy',
           {'fullname': 'DMcC', 'orgtype': 'Cther', 'organisation': 'DMcC Ltd',
            'country': 'Thailand', 'subdivision': 'Unspecified', 'town': 'bla', 'category': 'Energy'}),
          ('/submit/index', 'United Kingdom subdivision Staffordshire',
           {'fullname': 'King James VI', 'orgtype': 'Government', 'organisation': 'DMcC Ltd',
            'country': 'United Kingdom', 'subdivision': 'Staffordshire', 'town': 'bla', 'category': 'Energy'}),
          ('/submit/index', 'Ransomware is infecting computers',
           {'fullname': 'Not Yet Known', 'orgtype': 'Cther', 'organisation': 'Unknown',
            'country': 'Unspecified', 'subdivision': 'Unspecified', 'town': 'Not Known', 'category': 'Industry'}))
    @unpack
    def test_question(self, urltxt, itemtext, othervals):
        self.url = ROOT + urltxt
        get_browser = self.browser.get(self.url)
        time.sleep(1)  # still getting blank category for some reason but not if loaded manually
        questiontext = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name('activity'))
        questiontext.send_keys(itemtext)
        questiontext = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name('details'))
        questiontext.send_keys(itemtext)

        for key in sorted(othervals):  # sorting to ensure country before subdivision
            keycode = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_name(key))
            keycode.send_keys(othervals[key])
            if key == 'country':
                time.sleep(1)

        submit_button = self.browser.find_element_by_css_selector("#submit_record__row input")
        submit_button.click()

        welcome_message = self.browser.find_element_by_css_selector(".w2p_flash")
        self.assertIn('Details Submitted', welcome_message.text)
