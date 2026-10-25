import unittest
from fusion_app import grip_solid_xy_lug as m

class AEdgeTests(unittest.TestCase):
    def test_selects_a_edge_in_either_direction_not_other_edges(self):
        low=(-28.982,-28.801,-3.546);high=(-28.982,-28.801,21.480)
        self.assertTrue(m.is_a_edge(low,high))
        self.assertTrue(m.is_a_edge(high,low))
        self.assertFalse(m.is_a_edge((-28.985,-30.801,-3.546),(-28.985,-30.801,21.480)))
        self.assertFalse(m.is_a_edge(low,(-28.982,-28.801,0)))
        self.assertFalse(m.is_a_edge(low,(-31.982,-28.796,-3.546)))
