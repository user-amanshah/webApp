#from model import db, Credential, Credentialschema
from views import app
import os, unittest, requests
from flask import json



BASE_URL = 'http://127.0.0.1:5000/v1/user'


class Testapi(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_post(self):

        ###existing user case

        data_var = {
            "first_name": "J1ezdane",
            "last_name": "Dsdeoe",
            "password": "sdd",
            "email_address": "jane.doe@essxample.com"
        }

        response = self.app.post(BASE_URL,
                                 data=json.dumps(data_var),
                                 content_type='application/json')
        self.assertEqual(response.status_code,400)


    def test_post_email(self):

            ####wrong email test case
        data_var = {
            "first_name": "J1ezdane",
            "last_name": "Dsdeoe",
            "password": "sdd",
            "email_address": "wrongemail.com"
        }

        response = self.app.post(BASE_URL,
                                 data=json.dumps(data_var),
                                 content_type='application/json')
        self.assertEqual(response.status_code,400)

    def test_post_success(self):

            ###sucess test case
        data_var = {
            "first_name": "test1",
            "last_name": "test1",
            "password": "sdd12111SSS",
            "email_address": "te1zsqt1343@essxample.com"
        }

        response = self.app.post(BASE_URL,
                                 data=json.dumps(data_var),
                                 content_type='application/json')

        self.assertEqual(response.status_code,500)

        data_response = json.loads(response.get_data())
        self.assertEqual(data_response['first_name'], 'test1')




if __name__ == "__main__":
    unittest.main()
