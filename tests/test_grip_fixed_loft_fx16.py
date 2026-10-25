import math
import unittest
from test_grip_twist import load_grip
from fusion_app import grip_fixed_loft_fx16 as loft, grip_reference_ellipse as e, grip_twist as v

class Fx16SectionsTests(unittest.TestCase):
    def test_both_sections_share_g_and_exclude_af1(self):
        env=load_grip();a=env['calculate_finger_a_line']()
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        for data,z in ((e.from_finger(a,direction),10.492),(e.from_a_lower(a,direction),-6.)):
            part=loft.end_to_via_section(data)
            self.assertEqual(part['ends'],(a['points_mm'][0],(-29.854,-35.,z)))
            self.assertGreater(part['sweep'],0)
            self.assertLess(part['sweep'],data['sweep'])
            ends=[e.point_at(data,t) for t in (part['start'],part['start']+part['sweep'])]
            for p in part['ends']:self.assertLess(min(math.dist(p,q) for q in ends),1e-9)
            af_offset=(data['angles'][0]-part['start'])%math.tau
            self.assertGreater(af_offset,part['sweep'])
            for i in range(101):
                t=part['start']+part['sweep']*i/100
                self.assertGreaterEqual(t+1e-10,data['start'])
                self.assertLessEqual(t,data['start']+data['sweep']+1e-10)

    def test_selects_correct_half_when_end_is_stored_first(self):
        data=e.fit_ellipse(((0.,1.,0.),(-1.,0.,0.),(0.,-1.,0.)),
                           {'u':(1.,0.),'major':1.,'minor':1.})
        part=loft.end_to_via_section(data)
        self.assertLess(part['sweep'],data['sweep'])
        for p in part['ends']:
            self.assertLess(min(math.dist(p,e.point_at(data,t)) for t in (part['start'],part['start']+part['sweep'])),1e-9)

if __name__=='__main__':unittest.main()
