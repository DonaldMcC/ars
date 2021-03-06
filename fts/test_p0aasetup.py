from functional_tests import FunctionalTest, ROOT, USERS
from ddt import ddt, data, unpack
import time
from selenium.webdriver.support.ui import WebDriverWait


# element = WebDriverWait(driver, 10).until(lambda driver : driver.find_element_by_id("createFolderCreateBtn"))
@ddt
class TestRegisterPage (FunctionalTest):
    def setUp(self):     
        self.url = ROOT + '/admin/initialise.html'
        get_browser = self.browser.get(self.url)
        time.sleep(1)

    @data((USERS['USER1'], USERS['PASSWORD1']))
    @unpack
    def test_put_values_in_regester_form(self, user, passwd):
        resultstring = 'admin user can now sign-up'
        body = WebDriverWait(self, 10).until(lambda self: self.browser.find_element_by_tag_name('body'))
        self.assertIn(resultstring, body.text)
