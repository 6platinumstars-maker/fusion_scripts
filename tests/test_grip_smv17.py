import unittest
from test_grip_twist import load_grip
from fusion_app import grip_smv17 as f, grip_width as w, grip_twist as v, grip_reference_hexagon as h, grip_reference_ellipse as e, grip_hexagon_curved_surfaces as curved

class SmV17Tests(unittest.TestCase):
    def test_actual_df2_and_shared_ref9_arc(self):
        env=load_grip();d=env['calculate_finger_d_line']();c=env['calculate_finger_c_line']()
        direction=v.sub(env['GRIP_FINGER_A_POINT_P_MM'],env['GRIP_FINGER_D_POINT_P_MM'])
        points=f.corners(d,direction)
        width=next(face for face in w.output_faces('D',d,direction) if face['index']==2)
        df2=dict(zip(width['names'],width['corners']))['F2']
        self.assertEqual(points,[h.hexagon_data()['points'][1],df2,d['points_mm'][1]])
        piece=curved.section(e.from_cd_hexagon(c,d)['Ref9'])
        f.validate_arc_ends(points,piece['ends'])
        f.validate_arc_ends(points,piece['ends'][::-1])
        with self.assertRaises(ValueError):
            f.validate_arc_ends(points,curved.section(e.from_cd_hexagon(c,d)['Ref11'])['ends'])
        updated=f.corners(env['calculate_finger_d_line'](twist_deg=20),direction)
        self.assertEqual(points[0],updated[0])
        self.assertGreater(v.norm(v.sub(points[1],updated[1])),.01)

if __name__=='__main__':unittest.main()
