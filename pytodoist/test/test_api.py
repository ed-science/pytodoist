#!/usr/bin/env python

"""This module contains unit tests for the pytodoist.api module."""
import json
import unittest
from pytodoist.api import TodoistAPI
from pytodoist.test.util import TestUser

# No magic numbers
_HTTP_OK = 200


class TodoistAPITest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = TodoistAPI()

    def setUp(self):
        self.user = TestUser()
        response = self.api.register(self.user.email, self.user.full_name,
                                     self.user.password)
        if response.status_code != _HTTP_OK:
            # Assume already registered.
            response = self.api.login(self.user.email, self.user.password)
        user_json = response.json()
        self.user.api_token = user_json['api_token']

    def tearDown(self):
        self.api.delete_user(self.user.api_token, self.user.password)

    def test_class_variables(self):
        self.assertEqual(self.api.VERSION, "6")
        self.assertEqual(self.api.URL, "https://api.todoist.com/API/v6/")

    def test_login_success(self):
        response = self.api.login(self.user.email, self.user.password)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertIn('api_token', response.json())

    def test_login_failure(self):
        response = self.api.login(self.user.email, '')
        self.assertNotEqual(response.status_code, _HTTP_OK)
        self.assertIn('error', response.json())

    def test_login_with_google_success(self):
        pass  # TODO

    def test_login_with_google_failure(self):
        response = self.api.login_with_google(self.user.email, '')
        self.assertNotEqual(response.status_code, _HTTP_OK)
        self.assertIn('error', response.json())

    def test_register_success(self):
        self.api.delete_user(self.user.api_token, self.user.password)
        response = self.api.register(self.user.email, self.user.full_name,
                                     self.user.password)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertIn('api_token', response.json())

    def test_register_failure(self):
        response = self.api.register(self.user.email, self.user.full_name,
                                     self.user.password)
        self.assertNotEqual(response.status_code, _HTTP_OK)
        self.assertIn('error', response.json())

    def test_delete_user_success(self):
        response = self.api.delete_user(self.user.api_token,
                                        self.user.password)
        # The Todoist API is returning HTTP 400 but is still deleting
        # the user. Looks like a bug in the API.
        self.assertEqual(response.status_code, 400)
        response = self.api.login(self.user.email, self.user.password)
        self.assertNotEqual(response.status_code, _HTTP_OK)
        self.assertIn('error', response.json())

    def test_delete_user_failure(self):
        self.api.delete_user(self.user.api_token, '')
        response = self.api.login(self.user.email, self.user.password)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertNotIn('error', response.json())

    def test_get_redirect_link(self):
        response = self.api.get_redirect_link(self.user.api_token)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertIn('link', response.json())

    def test_sync_all(self):
        response = self.api.sync(self.user.api_token, self.user.api_seq_no)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertIn('seq_no', response.json())

    def test_query(self):
        queries = ['tomorrow', 'p1']
        response = self.api.query(self.user.api_token, json.dumps(queries))
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertEqual(len(response.json()), len(queries))

    def test_upload_file_success(self):
        file_path = "D:/pictures/0001.jpg"  # Change me
        response = self.api.upload_file(self.user.api_token, file_path)
        self.assertNotEqual(response.status_code, _HTTP_OK)
        self.assertIn('error', response.json())
        error_message = response.json()['error']
        self.assertEqual(error_message, "Premium only feature")

    def test_upload_file_failure(self):
        file_path = "C:/no/such/file"
        with self.assertRaises(IOError):
            self.api.upload_file(self.user.api_token, file_path)

    def test_get_productivity_stats(self):
        response = self.api.get_productivity_stats(self.user.api_token)
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertNotEqual(len(response.json()), 0)

    def test_add_item_success(self):
        response = self.api.add_item(self.user.api_token, 'Task 1')
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertEqual(response.json()['content'], 'Task 1')

    def test_get_all_completed_tasks_empty(self):
        response = self.api.get_all_completed_tasks(self.user.api_token)
        self.assertNotEqual(response.status_code, _HTTP_OK)
        self.assertIn('error', response.json())
        error_message = response.json()['error']
        self.assertEqual(error_message, "Premium only feature")

    def test_update_notification_settings_success(self):
        response = self.api.update_notification_settings(self.user.api_token,
                                                         'user_left_project',
                                                         'email',
                                                         1)  # False
        self.assertEqual(response.status_code, _HTTP_OK)
        self.assertIn('user_left_project', response.json())
        self.assertFalse(response.json()['user_left_project']['notify_email'])


if __name__ == '__main__':
    unittest.main()
