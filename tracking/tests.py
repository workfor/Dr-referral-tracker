from django.test import TestCase


class SimpleTest(TestCase):
    def test_sum(self):
        s = 2 + 2
        self.assertTrue(s, 4)
