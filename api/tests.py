from django.test import TestCase
from rest_framework.test import APIClient
from api.models import JCHSData
from rest_framework import status
import pytest

class JCHSDataTest(TestCase):
   pass 

class APIEndpoints(TestCase):
    """ Tests for generic API endpoints """

    def setup(self):
        self.client = APIClient()

    def test_schema_endpoint(self):
        response = self.client.get('/housing-affordability/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_api_endpoint_status(self):
        response = self.client.get('/housing-affordability/api/')
        datasets = ['harvardjchs','homelessness/pit','homelessness/hic','rentalcrisis','policies','programs','permits','taxlots']
        endpoints = { v: f'http://testserver/housing-affordability/api/{v}/' for v in datasets } 
        with self.subTest('status_code'):
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        with self.subTest('content'):
            self.assertEqual(response.json(), endpoints)

    def test_invalid_endpoint(self):
        response = self.client.get('/housing-affordability/api/asdf/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# disable- see issue #52
# class TestJCHSDataEndpoints(TestCase):
#     """ Tests for Harvard JCHS Data endpoints """

#     #fixtures = ['harvardjchs']

#     def setup(self):
#         self.client = APIClient()

#     @pytest.mark.django_db
#     def test_list_endpoint(self):
#         response = self.client.get('/housing-affordability/api/harvardjchs/')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#     #def test_detail_endpoint(self):
#     #    response = self.client.get('/api/harvardjchs/1/')
#     #    self.assertEqual(response.status_code, status.HTTP_200_OK)
