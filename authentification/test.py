import json
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framewrok import status
from rest_framewrok.authtoken.models import Token
from rest_framewrok.test import APITestCase

from authentification.serializers import CreateHrSerializer


# class RegisterTestcase(APITestCase):
#     def test_register(self):
#         data = {'username': "ibosh", "first_name": "Ibrohim", "last_name": "Istamov", "password": "1"}
#         response = self.client.post("/create-hr/", data)
#         self.asser