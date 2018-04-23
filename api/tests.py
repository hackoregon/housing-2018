from django.test import TestCase, Client
from api.models import JCHSData
from rest_framework.test import APIClient
from rest_framework import status

class JCHSDataTest(TestCase):
   pass 

class APIEndpoints(TestCase):
    """ Tests for generic API endpoints """

    def setup(self):
        self.client = Client()

    def test_schema_endpoint(self):
        response = self.client.get('/housing/schema/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_endpoint_status(self):
        response = self.client.get('/housing/api/')
        datasets = ['harvardjchs']
        endpoints = { v: f'http://testserver/housing/api/{v}/' for v in datasets } 
        with self.subTest('status_code'):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        with self.subTest('content'):
            self.assertEqual(response.json(), endpoints)

    def test_invalid_endpoint(self):
        response = self.client.get('/housing/api/asdf/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TestJCHSDataEndpoints(TestCase):
    """ Tests for Harvard JCHS Data endpoints """

    fixtures = ['harvardjchs']

    def setup(self):
        self.client = Client()

    def test_list_endpoint(self):
        response = self.client.get('/housing/api/harvardjchs/')
        with self.subTest('status_code'):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        with self.subTest('content'):
            self.assertEqual(response.json()['count'], 8)

    def test_detail_endpoint(self):
        response = self.client.get('/housing/api/harvardjchs/1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
