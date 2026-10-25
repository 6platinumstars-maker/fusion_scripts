import unittest
from fusion_app import grip_fx6_cut as f

class Fx6CutTests(unittest.TestCase):
    def test_five_corners_preserve_exact_reference_points(self):
        d=(-44.13609722665777,-23.14693037219348,-6.)
        c=(-59.23834345932146,2.64776868767,-6.)
        points,area=f.cut_corners(d,c)
        self.assertEqual(points,[*f.FIXED_START,d,c,f.FIXED_END])
        self.assertGreater(area,1000)
        self.assertLess(area,2280)
        for bad_d,bad_c in [(d,(c[0],c[1],0)),(d,d),((float('nan'),0,-6),c)]:
            with self.assertRaises(ValueError):f.cut_corners(bad_d,bad_c)

if __name__=='__main__':unittest.main()
