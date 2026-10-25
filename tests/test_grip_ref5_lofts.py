import math
import unittest
from test_grip_twist import load_grip
from fusion_app import grip_reference_ellipse as ellipse, grip_ref5_lofts as lofts, grip_twist as v

class Ref5LoftSectionsTests(unittest.TestCase):
    def data(self):
        e=load_grip()
        return ellipse.from_finger(e['calculate_finger_a_line'](),v.sub(e['GRIP_FINGER_A_POINT_P_MM'],e['GRIP_FINGER_D_POINT_P_MM']))

    def test_trim_fx15_to_g_preserves_fx14_and_shared_split(self):
        data=self.data();pieces,split=lofts.sections(data)
        self.assertLess(math.dist(split,lofts.SPLIT_HINT_MM),.001)
        self.assertLess(sum(p['sweep'] for p in pieces.values()),data['sweep'])
        for key,target in (('Fx14',data['points'][2]),('Fx15',data['points'][1])):
            p=pieces[key]
            self.assertGreater(p['sweep'],0)
            self.assertLess(min(math.dist(split,q) for q in p['ends']),1e-10)
            self.assertLess(min(math.dist(target,q) for q in p['ends']),1e-10)
            for i in range(101):
                t=p['start']+p['sweep']*i/100
                self.assertGreaterEqual(t+1e-10,data['start'])
                self.assertLessEqual(t,data['start']+data['sweep']+1e-10)
        self.assertLess(math.dist(pieces['Fx15']['ends'][1],pieces['Fx14']['ends'][0]),1e-10)
        self.assertLess(math.dist(pieces['Fx15']['ends'][0],data['points'][1]),1e-10)
        self.assertGreater(math.dist(pieces['Fx15']['ends'][0],data['points'][0]),1)

    def test_inconsistent_split_or_interval_rejected(self):
        data=self.data();data['center']=v.add(data['center'],(1,0,0))
        with self.assertRaises(ValueError):lofts.sections(data)
        data=self.data();data['start']=.1;data['sweep']=.2
        with self.assertRaises(ValueError):lofts.sections(data)

if __name__=='__main__':unittest.main()
