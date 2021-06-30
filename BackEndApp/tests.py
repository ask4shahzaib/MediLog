from time import sleep
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

selenium = webdriver.Firefox(
    executable_path=r'C:\Users\Acer\Desktop\geckodriver.exe')
cnic = None


class aaasignupTest(LiveServerTestCase):

    def testform(self):
        # Choose your url to visit
        selenium.get('http://127.0.0.1:8000/register/')
        # find the elements you need to submit form
        sleep(2)
        cnic = selenium.find_element_by_id('cnic')
        password = selenium.find_element_by_id('password')
        fname = selenium.find_element_by_id('fname')
        lname = selenium.find_element_by_id('lname')
        phone = selenium.find_element_by_id('phone')
        email = selenium.find_element_by_id('email')
        dob = selenium.find_element_by_id('dob')
        address = selenium.find_element_by_id('address')
        prescription = selenium.find_element_by_id('prescription')

        submit = selenium.find_element_by_id('signupSubmit')

        # populate the form with data
        cnic.send_keys('3333344444445')
        password.send_keys('12abcd34')
        fname.send_keys('Bilal')
        lname.send_keys('Tahir')
        phone.send_keys('090078601')
        email.send_keys('bilalTahir@gmail.com')
        dob.send_keys('1998-04-15')
        address.send_keys('852-B Faisal Town Lahore')
        prescription.send_keys(
            r'C:\Users\Acer\MediLog\static\images\profile.jpg')

        # submit form
        sleep(2)
        submit.send_keys(Keys.RETURN)


class bbbloginTest(LiveServerTestCase):

    def testform(self):
        # Choose your url to visit
        sleep(2)
        selenium.get('http://127.0.0.1:8000/login/')
        # find the elements you need to submit form
        cnic = selenium.find_element_by_id('cnic')
        password = selenium.find_element_by_id('password')

        submit = selenium.find_element_by_id('loginSubmit')

        # populate the form with data
        cnic.send_keys('hospital1')
        password.send_keys('12abcd34')
        # submit form
        sleep(1.5)
        submit.send_keys(Keys.RETURN)


class cccaddPrescriptionTest(LiveServerTestCase):

    def testform(self):
        # Choose your url to visit
        sleep(2)
        selenium.get('http://127.0.0.1:8000/addPrescription/')
        # find the elements you need to submit form
        patient = selenium.find_element_by_id('patient')
        doctor = selenium.find_element_by_id('doctor')
        label = selenium.find_element_by_id('label')
        description = selenium.find_element_by_id('description')
        date = selenium.find_element_by_id('date')
        prescription = selenium.find_element_by_id('prescription')

        submit = selenium.find_element_by_id('addPrescriptionSubmit')

        # populate the form with data
        patient.send_keys('1111122222223')
        doctor.send_keys('doctor1')
        label.send_keys('Flu')
        description.send_keys('Runny Nose')
        date.send_keys('2021-06-16')
        prescription.send_keys(
            r'C:\Users\Acer\MediLog\static\images\prescriptions\flu.jpg')

        # submit form
        submit.send_keys(Keys.RETURN)


class dddlogoutTest(LiveServerTestCase):

    def testform(self):
        # Choose your url to visit
        sleep(5)
        selenium.get('http://127.0.0.1:8000/logout/')


class eeeloginTest(LiveServerTestCase):

    def testform(self):
        # Choose your url to visit
        sleep(2)
        selenium.get('http://127.0.0.1:8000/login/')
        # find the elements you need to submit form
        cnic = selenium.find_element_by_id('cnic')
        password = selenium.find_element_by_id('password')

        submit = selenium.find_element_by_id('loginSubmit')

        # populate the form with data
        cnic.send_keys('doctor1')
        password.send_keys('12abcd34')
        # submit form
        sleep(1.5)
        submit.send_keys(Keys.RETURN)


class fffViewPrescriptionTest(LiveServerTestCase):

    def testform(self):
        # Choose your url to visit
        sleep(2)
        selenium.get('http://127.0.0.1:8000/viewAllRecords/')
        cnic = selenium.find_element_by_id('cnic')

        submit = selenium.find_element_by_id('ViewRecordSubmit')

        # populate the form with data
        cnic.send_keys('1111122222223')
        # submit form
        sleep(1.5)
        submit.send_keys(Keys.RETURN)


class gggViewPrescriptionTest(LiveServerTestCase):

    def testform(self):
        # Choose your url to visit
        sleep(2)
        selenium.get('http://127.0.0.1:8000/timeline/')
        submit = selenium.find_element_by_id('allRecords')
        sleep(1.5)
        submit.send_keys(Keys.RETURN)


class hhhViewProfileTest(LiveServerTestCase):

    def testform(self):
        # Choose your url to visit
        sleep(2)
        selenium.get('http://127.0.0.1:8000/profile/')
