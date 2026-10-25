import math
import unittest
from fusion_app import grip_reference_hexagon as h

class HexagonTests(unittest.TestCase):
    def test_plane_vertices_regular_sides_and_angles(self):
        data=h.hexagon_data();points=data['points'];n=data['normal']
        for i,p in enumerate(points):
            self.assertLess(math.dist(p,h.HINTS_MM[i]),.001)
            self.assertAlmostEqual(sum(a*b for a,b in zip(p,n)),-40.,places=10)
            self.assertAlmostEqual(math.dist(p,points[(i+1)%6]),10,places=10)
            self.assertAlmostEqual(math.dist(p,data['center']),10,places=10)
            u=[points[(i-1)%6][j]-p[j] for j in range(3)]
            v=[points[(i+1)%6][j]-p[j] for j in range(3)]
            self.assertAlmostEqual(sum(a*b for a,b in zip(u,v))/100,-.5,places=10)
        rotated=(0.,-math.sin(math.radians(135)),math.cos(math.radians(135)))
        self.assertAlmostEqual(abs(sum(a*b for a,b in zip(n,rotated))),1,places=12)

if __name__=='__main__':unittest.main()
