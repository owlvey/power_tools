import unittest

from app.components.RegistrationComponent import RegistrationComponent


class RegistrationComponentTest(unittest.TestCase):

    def test_auto_registration(self):
        component = RegistrationComponent()
        component.auto_register_latency_experience("", "")

    def test_auto_un_registration(self):
        component = RegistrationComponent()
        component.auto_un_register_latency_experienc("", "")
