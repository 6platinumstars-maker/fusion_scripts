import math
import unittest
from fusion_app import grip_reference_x as x
from fusion_app import grip_fixed_arc as f

class ReferenceXTests(unittest.TestCase):
    def test_projected_tangency_on_confirmed_arc_and_reversed_endpoints(self):
        n=(0.,-.08280820751220438,.9965655024977614)
        o=(-59.35288145028793,-1.3669067829940815,26.4307356319431)
        c=(-41.895,5.303,26.985)
        d=x.dot(x.sub(c,o),n)
        base=tuple(c[i]-d*n[i] for i in range(3))
        arc=f.arc_data(base,n,34.9)
        point,q=x.tangent_point(arc['center'],arc['start'],arc['end'],x.SOURCE_HINT_MM)
        reverse,_=x.tangent_point(arc['center'],arc['end'],arc['start'],x.SOURCE_HINT_MM)
        self.assertLess(math.dist(point,reverse),1e-10)
        self.assertLess(math.dist(point,(-52.459,-28.011,26.224)),.001)
        self.assertAlmostEqual(math.dist(point,arc['center']),34.9,places=10)
        self.assertAlmostEqual(x.dot(x.sub(point,arc['center']),n),0,places=10)
        self.assertAlmostEqual(x.dot(x.sub(q,arc['center']),n),0,places=10)
        self.assertAlmostEqual(x.dot(x.sub(point,arc['center']),x.sub(point,q)),0,places=9)
        self.assertGreater(math.dist(q,x.SOURCE_HINT_MM),1.99)
        tangent=x.cross(n,x.sub(point,arc['center']))
        self.assertGreater(math.sqrt(x.dot(x.cross(tangent,x.sub(point,x.SOURCE_HINT_MM)),x.cross(tangent,x.sub(point,x.SOURCE_HINT_MM)))),1)

    def test_no_tangent_or_no_candidate_on_arc_is_rejected(self):
        with self.assertRaises(ValueError):x.tangent_point((0,0,0),(1,0,0),(0,1,0),(0,0,3))
        with self.assertRaises(ValueError):x.tangent_point((0,0,0),(1,0,0),(0,1,0),(-3,0,3))

if __name__=='__main__':unittest.main()
