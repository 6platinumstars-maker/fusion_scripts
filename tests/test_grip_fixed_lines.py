import math
import unittest
from fusion_app import grip_fixed_lines as f


class FixedEllipseTests(unittest.TestCase):
    def test_center_and_three_requested_points(self):
        data=f.ellipse_data();a,b,d=data['coefficients']
        self.assertEqual(data['center'],f.CENTER_MM)
        self.assertGreater(data['major'],data['minor'])
        for point in (f.START_MM,f.VIA_MM,f.END_MM):
            x,y=point[0]-f.CENTER_MM[0],point[1]-f.CENTER_MM[1]
            self.assertAlmostEqual(a*x*x+2*b*x*y+d*y*y,1,places=12)
        self.assertAlmostEqual(sum(x*y for x,y in zip(data['u'],data['v'])),0,places=12)

    def test_retained_arc_contains_via_and_exact_endpoints(self):
        data=f.ellipse_data()
        endpoints=[f.point_at(data,data['start']),f.point_at(data,data['start']+data['sweep'])]
        for p in (f.START_MM,f.END_MM):self.assertLess(min(math.dist(p,q) for q in endpoints),1e-10)
        self.assertLess((data['via']-data['start'])%math.tau,data['sweep'])
        self.assertLess(math.dist(f.point_at(data,data['via']),f.VIA_MM),1e-10)
        self.assertGreater(data['sweep'],0)
        self.assertLess(data['sweep'],math.pi)
        for i in range(101):
            self.assertEqual(f.point_at(data,data['start']+data['sweep']*i/100)[2],10.492)

class LowerEllipseTests(unittest.TestCase):
    def test_fxl2_is_identical_xy_and_five_mm_lower(self):
        upper=f.ellipse_data()
        lower=f.ellipse_data(5.492)
        for key in ('major','minor','u','v','start','sweep','via','coefficients'):
            self.assertEqual(upper[key],lower[key])
        for i in range(101):
            t=upper['start']+upper['sweep']*i/100
            a,b=f.point_at(upper,t),f.point_at(lower,t)
            self.assertEqual(a[:2],b[:2])
            self.assertAlmostEqual(a[2]-b[2],5.)
        for t,expected in ((lower['via'],(-79.723,-35.,5.492)),):
            self.assertLess(math.dist(f.point_at(lower,t),expected),1e-10)
        endpoints=[f.point_at(lower,t) for t in (lower['start'],lower['start']+lower['sweep'])]
        for expected in ((-29.854,-35.,5.492),(-76.795,18.768,5.492)):
            self.assertLess(min(math.dist(expected,p) for p in endpoints),1e-10)

if __name__=='__main__':unittest.main()
