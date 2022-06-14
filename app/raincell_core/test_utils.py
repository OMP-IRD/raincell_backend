
from django.test import TestCase

from .utils import latlon_to_cellid

class LatLonToCellIdTests(TestCase):
    def test_produces_proper_id(self):
        cell_id = latlon_to_cellid(3.875, 11.525)
        self.assertEquals(cell_id, "0938750019152500")


    def test_uses_maxdecimals_value(self):
        "Should round the coord to 1 decimal"
        cell_id = latlon_to_cellid(3.875, 11.525, max_decimals=1)
        self.assertEquals(cell_id, "09391915")


    def test_trims_too_many_decimals(self):
        cell_id = latlon_to_cellid(3.875562, 11.525)
        self.assertEquals(cell_id, "0938755619152500")
