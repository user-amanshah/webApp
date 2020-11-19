#from model import db, Credential, Credentialschema
from views import app
import os, unittest, requests
from flask import json



BASE_URL = 'http://127.0.0.1:8080/v1/user'


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
        self.assertEqual(response.status_code,200)


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

   


if __name__ == "__main__":
    unittest.main()
