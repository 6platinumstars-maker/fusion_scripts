import math
import unittest
from fusion_app.grip_fx4 import sections, HINTS

C=(-41.895,5.3030031238150865,26.984962406065254)
N=(0.,-.08280820751220438,.9965655024977614)
POINTS=((-76.795,8.043842140274874,-6.),
        (-29.854,-24.82609950516279,-6.),
        (-76.795,5.303003123815093,26.984962406065258),
        (-29.844389426562836,-27.33775525755396,24.269508969633157))

class Fx4Tests(unittest.TestCase):
    def test_conics_follow_source_cylinder_and_requested_endpoints(self):
        data=sections(C,N,34.9,POINTS)
        for lower,s in zip((True,False),data):
            self.assertEqual(len(s['knots']),len(s['control'])+3)
            for j in range(0,len(s['control'])-2,2):
                for t in (0,.2,.5,.8,1):
                    basis=((1-t)**2,2*t*(1-t),t*t)
                    weights=[basis[i]*s['weights'][j+i] for i in range(3)]
                    p=tuple(sum(weights[k]*s['control'][j+k][i] for k in range(3))/sum(weights) for i in range(3))
                    delta=[p[i]-C[i] for i in range(3)]
                    axial=sum(delta[i]*N[i] for i in range(3))
                    radius=math.sqrt(sum((delta[i]-axial*N[i])**2 for i in range(3)))
                    self.assertAlmostEqual(radius,34.9,places=10)
                    if lower:self.assertAlmostEqual(p[2],-6,places=10)
                    else:self.assertAlmostEqual(axial,0,places=10)
        ends=[p for s in data for p in (s['control'][0],s['control'][-1])]
        for p,h in zip(ends,HINTS):self.assertLess(math.dist(p,h),.005)

    def test_rejects_changed_source_geometry(self):
        with self.assertRaises(ValueError):sections(C,N,35.0,POINTS)
        wrong=list(POINTS);wrong[-1]=tuple(x+(1 if i==2 else 0) for i,x in enumerate(wrong[-1]))
        with self.assertRaises(ValueError):sections(C,N,34.9,wrong)

if __name__=='__main__':unittest.main()
