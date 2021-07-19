from time import sleep
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

cnic = None

selenium = webdriver.Firefox(
    executable_path=r'C:\Users\Acer\Desktop\geckodriver.exe')


class aaaloginTest(LiveServerTestCase):
    def testform(self):
        # Choose your url to visit
        sleep(2)
        selenium.get('http://127.0.0.1:8000/logout/')
        # find the elements you need to submit form
        cnic = selenium.find_element_by_id('cnic')
        password = selenium.find_element_by_id('password')

        submit = selenium.find_element_by_id('loginSubmit')

        # populate the form with data
        cnic.send_keys('2222233333334')
        password.send_keys('12abcd34')
        # submit form
        sleep(1.5)
        submit.send_keys(Keys.RETURN)


class bbbProfile(LiveServerTestCase):
    def testform(self):
        # Choose your url to visit
        sleep(3)
        selenium.get('http://127.0.0.1:8000/profile')


class cccTimeline(LiveServerTestCase):
    def testform(self):
        # Choose your url to visit
        selenium.get('http://127.0.0.1:8000/profile')
        sleep(2)
        selenium.get('http://127.0.0.1:8000/timeline/')


class dddAllRecords(LiveServerTestCase):

    def testform(self):
        # Choose your url to visit
        sleep(5)
        selenium.get('http://127.0.0.1:8000/viewAllRecords/')


class eeeviewTrustedContact(LiveServerTestCase):

    def testform(self):
        # Choose your url to visit
        sleep(2)
        selenium.get('http://127.0.0.1:8000/viewTrustedContact/')


class fffViewConnections(LiveServerTestCase):

    def testform(self):
        # Choose your url to visit
        sleep(2)
        selenium.get('http://127.0.0.1:8000/viewConnections')
