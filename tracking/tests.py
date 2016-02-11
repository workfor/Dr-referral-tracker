from django.test import TestCase

from tracking.models import Physician


class SimpleTest(TestCase):
    def test_sum(self):
        s = 2 + 2
        self.assertTrue(s, 4)

    # Remove it, if necessary
    def test_export_from_sqlite(self):
        self.assertTrue(Physician.objects.get(physician_name='Dr John'))
