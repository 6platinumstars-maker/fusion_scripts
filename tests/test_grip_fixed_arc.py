import math
import unittest
from fusion_app import grip_fixed_arc as f

class FixedArcTests(unittest.TestCase):
    def test_offset_radius_angle_and_direction(self):
        n=(0.,-.08280820751220438,.9965655024977614)
        center=tuple(f.CENTER_HINT[i]-2*n[i] for i in range(3))
        data=f.arc_data(center,n,34.9)
        self.assertEqual(data,f.arc_data(center,tuple(-v for v in n),34.9))
        self.assertLess(math.dist(data['center'],f.CENTER_HINT),1e-10)
        vectors=[]
        for key in ('start','end'):
            p=data[key]
            self.assertAlmostEqual(math.dist(p,data['center']),34.9,places=10)
            self.assertAlmostEqual(f.dot(tuple(p[i]-center[i] for i in range(3)),n),2,places=10)
            vectors.append(tuple(p[i]-data['center'][i] for i in range(3)))
        angle=math.degrees(math.acos(f.dot(*vectors)/34.9**2))
        self.assertAlmostEqual(angle,113.23323558676071,places=9)
        self.assertAlmostEqual(angle,math.degrees(data["sweep"]),places=9)
        self.assertLess(math.dist(data["end"],(-35.234374737827935, -29.002857431824047, 26.141113513589218)),1e-10)
        self.assertLess(math.dist(data['start'],f.START_HINT),.005)
        self.assertGreater(math.dist(data['end'],f.END_HINT),.60)
        self.assertLess(math.dist(data['end'],f.END_HINT),.62)

if __name__=='__main__':unittest.main()
