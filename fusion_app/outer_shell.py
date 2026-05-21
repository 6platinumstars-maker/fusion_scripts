import math

import adsk.core
import adsk.fusion

try:
    from . import helpers
    from . import naming
except ImportError:
    import helpers
    import naming


OUTER_SHELL_SCRIPT_REVISION = '2026-05-21-l-button-opening-y32-cut'


OUTER_CIRCLE_CENTER_MM = (-42.0, 5.0)
OUTER_CIRCLE_RADIUS_MM = 33.0
INNER_SHELL_TOP_EDGE_START_MM = (-66.67, 26.918)
INNER_SHELL_TOP_EDGE_END_MM = (-25.0, 30.0)
INNER_SHELL_LOWER_STOP_TOP_Y_MM = -20.0
OUTER_SHELL_CONTACT_FACE_NAME = '外殻内殻接面'
OUTER_SHELL_BOTTOM_OUTER_FACE_POINT_MM = (-5.0, -35.0, -3.0)
OUTER_SHELL_BOTTOM_OUTER_EXTRUDE_DISTANCE_MM = -0.2
OUTER_SHELL_OUTER_PERIMETER_FACE_POINT_MM = (-5.0, -35.0, 0.0)
OUTER_SHELL_OUTER_PERIMETER_EXTRUDE_DISTANCE_MM = 29.0
OUTER_SHELL_REFERENCE_CIRCLE_SKETCH_NAME = '外殻外周円'
OUTER_SHELL_REFERENCE_CIRCLE_CENTER_MM = (-42.0, 5.0, 0.0)
OUTER_SHELL_REFERENCE_CIRCLE_RADIUS_MM = 33.0
OUTER_SHELL_REFERENCE_CIRCLE_FILLET_RADIUS_MM = 6.0
OUTER_SHELL_REFERENCE_CIRCLE_FILLET_REFERENCE_POINTS_MM = (
    (-9.0, 5.0, 0.0),
    (-42.0, -28.0, 0.0),
)
INNER_SHELL_TEMP_MOVE_X_MM = 200.0
OUTER_SHELL_BOTTOM_OUTER_SKETCH_NAME = '外殻底面外側'
OUTER_SHELL_BOTTOM_OUTER_SKETCH_Z_MM = -3.2
OUTER_SHELL_BOTTOM_OUTER_REGION_TARGET_MM = (-60.0, 0.0, 0.0)
OUTER_SHELL_BOTTOM_OUTER_REGION_EXTRUDE_DISTANCE_MM = -2.8
OUTER_SHELL_BOTTOM_OUTER_SLOPE_SKETCH_NAME = '外殻底部外側斜面'
OUTER_SHELL_BOTTOM_OUTER_SLOPE_Y_CUT_SKETCH_NAME = '外殻底部外側斜面 Yカット'
OUTER_SHELL_BOTTOM_OUTER_SLOPE_TRIANGLE_CUT_SKETCH_NAME = '外殻底部外側斜面 三角カット'
OUTER_SHELL_BOTTOM_OUTER_SLOPE_SKETCH_Z_MM = -3.2
OUTER_SHELL_BOTTOM_OUTER_SLOPE_CIRCLE_CENTER_MM = (0.0, 5.0, -3.2)
OUTER_SHELL_BOTTOM_OUTER_SLOPE_CIRCLE_DIAMETER_MM = 55.0
OUTER_SHELL_BOTTOM_OUTER_SLOPE_POINTS_MM = {
    'A': (-25.0, 30.0, -3.2),
    'C': (-3.159, -23.2, -3.2),
    'D': (-29.854, -25.9, -3.2),
    'E': (-29.854, 29.638, -3.2),
    'F_PRIME': (0.0, -22.5, -3.2),
    'G': (0.0, -23.2, -3.2),
    'H': (-19.445, 24.445, -3.2),
}
OUTER_SHELL_BOTTOM_OUTER_SLOPE_PROFILE_TARGET_MM = (-20.0, 10.0, -3.2)
OUTER_SHELL_BOTTOM_OUTER_SLOPE_PROFILE_FALLBACK_TARGETS_MM = (
    (-20.0, 10.0, -3.2),
    (-22.0, 0.0, -3.2),
    (-24.0, -5.0, -3.2),
)
OUTER_SHELL_BOTTOM_OUTER_SLOPE_EXTRUDE_DISTANCE_MM = 2.8
OUTER_SHELL_BOTTOM_OUTER_SLOPE_Y_CUT_POINTS_MM = {
    'I': (0.0, -23.2, -6.0),
    'J': (-3.159, -23.2, -6.0),
    'K': (0.0, -23.2, -5.0),
    'L': (-3.159, -23.2, -5.0),
}
OUTER_SHELL_BOTTOM_OUTER_SLOPE_Y_CUT_PROFILE_TARGET_MM = (-1.5, -23.2, -5.5)
OUTER_SHELL_BOTTOM_OUTER_SLOPE_Y_CUT_DISTANCE_MM = 5.0
OUTER_SHELL_BOTTOM_OUTER_SLOPE_TRIANGLE_POINTS_MM = {
    'J': (-3.159, -23.2, -6.0),
    'L': (-3.159, -23.2, -5.0),
    'M': (-5.0, -23.386, -4.927),
    'O': (-29.854, -25.9, -6.0),
}
OUTER_SHELL_BOTTOM_OUTER_SLOPE_TRIANGLE_CUT_DISTANCE_MM = 70.0
OUTER_SHELL_BOTTOM_OUTER_FILLET_RADIUS_MM = 3.0
OUTER_SHELL_BOTTOM_OUTER_FILLET_Z_MM = -6.0
OUTER_SHELL_BOTTOM_OUTER_FILLET_REFERENCE_POINTS_MM = (
    (-5.0, -23.3, -6.0),
    (-25.0, -19.174, -6.0),
)
INNER_SHELL_LID_SLOPE_FACE_NAME = '内殻蓋部斜面'
OUTER_SHELL_LID_INNER_PLANE_NAME = '外殻蓋部斜面内部'
OUTER_SHELL_LID_INNER_PLANE_Z_OFFSET_MM = 0.2
OUTER_SHELL_LID_INNER_PLANE_EXTRUDE_SKETCH_NAME = '外殻蓋部斜面内部押し出し'
OUTER_SHELL_LID_INNER_PLANE_EXTRUDE_PATH_SKETCH_NAME = '外殻蓋部斜面内部押し出しパス'
OUTER_SHELL_LID_INNER_PLANE_EXTRUDE_DISTANCE_MM = 0.2
OUTER_SHELL_LID_GAP_PLANE_NAME = '外殻蓋部斜面隙間部'
OUTER_SHELL_LID_GAP_PLANE_Z_OFFSET_MM = 0.2
OUTER_SHELL_LID_GAP_SKETCH_NAME = '外殻蓋部斜面隙間部'
OUTER_SHELL_LID_GAP_EXTRUDE_DISTANCE_MM = 3.0
OUTER_SHELL_LID_GAP_EXTENSION_EXTRUDE_DISTANCE_MM = 3.0
OUTER_SHELL_LID_GAP_EXTENSION_FILLET_RADIUS_MM = 3.0
OUTER_SHELL_LID_OUTER_SLOPE_FACE_NAME = '外殻蓋部斜面外側'
OUTER_SHELL_LID_DECORATION_CUT_1_SKETCH_NAME = '蓋部装飾切取り①'
OUTER_SHELL_LID_DECORATION_CUT_1_PLANE_NAME = '蓋部装飾切取り①平面'
OUTER_SHELL_LID_DECORATION_CUT_1_PLANE_X_MM = -41.895
OUTER_SHELL_LID_DECORATION_CUT_1_POINT_O_MM = (-41.895, 5.271, 27.384)
OUTER_SHELL_LID_DECORATION_CUT_1_POINT_P_MM = (-41.895, 6.363, 14.251)
OUTER_SHELL_LID_DECORATION_CUT_1_POINT_A_MM = (-41.895, -29.397, 27.803)
OUTER_SHELL_LID_DECORATION_CUT_1_POINT_B_MM = (-41.895, -23.70, 27.803)
OUTER_SHELL_LID_DECORATION_CUT_1_POINT_C_MM = (-41.895, -23.70, 18.993)
OUTER_SHELL_LID_DECORATION_CUT_1_PROFILE_TARGET_MM = (
    -41.895,
    (-29.397 - 23.70 - 23.70) / 3.0,
    (27.803 + 27.803 + 18.993) / 3.0,
)
OUTER_SHELL_LID_DECORATION_CUT_1_POSITIVE_ANGLE_DEG = 150.0
OUTER_SHELL_LID_DECORATION_CUT_1_NEGATIVE_ANGLE_DEG = 120.0
OUTER_SHELL_LID_DECORATION_CUT_2_REFERENCE_SKETCH_NAME = '蓋部装飾切取り② 基準'
OUTER_SHELL_LID_DECORATION_CUT_2_PLANE_NAME = '蓋部装飾切取り②平面'
OUTER_SHELL_LID_DECORATION_CUT_2_SKETCH_NAME = '蓋部装飾切取り②'
OUTER_SHELL_LID_DECORATION_CUT_2_POINT_D_MM = (-68.493, 20.575, 26.655)
OUTER_SHELL_LID_DECORATION_CUT_2_POINT_E_MM = (-57.635, 23.421, 28.892)
OUTER_SHELL_LID_DECORATION_CUT_2_POINT_F_MM = (-62.792, 22.068, 28.779)
OUTER_SHELL_LID_DECORATION_CUT_2_POINT_G_MM = (-62.227, 19.909, 28.60)
OUTER_SHELL_LID_DECORATION_CUT_2_POINT_H_MM = (-62.53, 21.059, 31.03)
OUTER_SHELL_LID_DECORATION_CUT_2_POINT_I_MM = (-63.354, 24.182, 31.29)
OUTER_SHELL_LID_DECORATION_CUT_2_POINT_J_MM = (-62.736, 21.838, 22.942)
OUTER_SHELL_LID_DECORATION_CUT_2_PLANE_ANGLE_DEG = 90.0
OUTER_SHELL_LID_DECORATION_CUT_2_NEGATIVE_X_DISTANCE_MM = 6.111
OUTER_SHELL_LID_DECORATION_CUT_2_POSITIVE_X_DISTANCE_MM = 5.356
OUTER_SHELL_LID_DECORATION_CUT_2_PROFILE_TARGET_MM = (
    (-62.53 - 63.354 - 62.736) / 3.0,
    (21.059 + 24.182 + 21.838) / 3.0,
    (31.03 + 31.29 + 22.942) / 3.0,
)
OUTER_SHELL_LID_DECORATION_CUT_3_SKETCH_1_NAME = '蓋部装飾切取り③ 断面1'
OUTER_SHELL_LID_DECORATION_CUT_3_SKETCH_2_NAME = '蓋部装飾切取り③ 断面2'
OUTER_SHELL_LID_DECORATION_CUT_3_POINT_A_PRIME_MM = (-68.764, 20.73, 28.668)
OUTER_SHELL_LID_DECORATION_CUT_3_POINT_B_PRIME_MM = (-68.841, 21.023, 25.693)
OUTER_SHELL_LID_DECORATION_CUT_3_POINT_C_PRIME_MM = (-70.262, 21.593, 28.74)
OUTER_SHELL_LID_DECORATION_CUT_3_POINT_H_PRIME_MM = (-69.076, 21.914, 28.767)
OUTER_SHELL_LID_DECORATION_CUT_4_SKETCH_NAME = '蓋部装飾切取り④'
OUTER_SHELL_LID_DECORATION_CUT_4_POINT_K_MM = (-58.50, 26.698, 29.164)
OUTER_SHELL_LID_DECORATION_CUT_4_POINT_L_MM = (-58.50, 26.391, 32.856)
OUTER_SHELL_LID_DECORATION_CUT_4_POINT_M_MM = (-58.047, 25.063, 29.562)
OUTER_SHELL_LID_DECORATION_CUT_4_POINT_N_MM = (-57.505, 23.005, 22.232)
OUTER_SHELL_LID_DECORATION_CUT_4_POINT_Q_MM = (-57.504, 23.005, 29.289)
OUTER_SHELL_LID_DECORATION_CUT_4_REVOLVE_ANGLE_DEG = -120.0
OUTER_SHELL_LID_DECORATION_CUT_4_EXTRUDE_DISTANCE_MM = 1.0
OUTER_SHELL_LID_DECORATION_CUT_4_PROFILE_TARGET_MM = (
    (-58.047 - 57.505 - 57.504) / 3.0,
    (25.063 + 23.005 + 23.005) / 3.0,
    (29.562 + 22.232 + 29.289) / 3.0,
)
OUTER_SHELL_LID_DECORATION_CUT_5_SKETCH_NAME = '蓋部装飾切取り⑤'
OUTER_SHELL_LID_DECORATION_CUT_5_POINT_X_MM = (-57.425, 27.747, 30.067)
OUTER_SHELL_LID_DECORATION_CUT_5_POINT_Y_MM = (-55.067, 30.513, 21.989)
OUTER_SHELL_LID_DECORATION_CUT_5_POINT_Z_MM = (-54.852, 30.297, 30.067)
OUTER_SHELL_LID_DECORATION_CUT_5_POSITIVE_DISTANCE_MM = 20.0
OUTER_SHELL_LID_DECORATION_CUT_5_NEGATIVE_DISTANCE_MM = 1.0
OUTER_SHELL_LID_GAP_CIRCLE_L_RADIUS_MM = 3.4
OUTER_SHELL_LID_GAP_POINT_A_MM = (-90.0, 32.2, 26.621)
OUTER_SHELL_LID_GAP_POINT_B_MM = (-90.0, -35.0, 21.037)
OUTER_SHELL_LID_GAP_POINT_C_MM = (-29.854, -35.0, 21.037)
OUTER_SHELL_LID_GAP_POINT_D_MM = (-29.854, -25.9, 21.793)
OUTER_SHELL_LID_GAP_POINT_E_MM = (-28.579, -22.977, 22.036)
OUTER_SHELL_LID_GAP_POINT_F_MM = (-57.8, 32.2, 26.621)
OUTER_SHELL_LID_GAP_POINT_G_MM = (-63.701, 27.105, 26.198)
OUTER_SHELL_LID_GAP_POINT_H_MM = (-68.784, 20.286, 25.631)
OUTER_SHELL_LID_GAP_POINT_I_MM = (-41.943, 5.298, 24.386)
OUTER_SHELL_LID_YZ_CUT_PLANE_NAME = '外殻蓋部YZ切り取り平面'
OUTER_SHELL_LID_YZ_CUT_PLANE_X_MM = -29.854
OUTER_SHELL_BASE_STRUCTURE_SKETCH_NAME = '外殻基準構造'
OUTER_SHELL_LOWER_STOP_SKETCH_1_NAME = '外殻下部受止 スケッチ1'
OUTER_SHELL_LOWER_STOP_SKETCH_2_NAME = '外殻下部受止 スケッチ2'
OUTER_SHELL_LOWER_STOP_SKETCH_3_NAME = '外殻下部受止 スケッチ3'
OUTER_SHELL_LOWER_STOP_SKETCH_4_NAME = '外殻下部受止 スケッチ4'
OUTER_SHELL_LOWER_STOP_SKETCH_5_NAME = '外殻下部受止 スケッチ5'
OUTER_SHELL_LOWER_STOP_SUPPORT_SKETCH_NAME = '外殻下部受止 押し出し先'
OUTER_SHELL_LOWER_STOP_LOFT_SKETCH_NAME = '外殻下部受止 ロフト2'
OUTER_SHELL_LOWER_STOP_EXTRUDE_DISTANCE_MM = 5.0
OUTER_SHELL_LOWER_STOP_BHIJ_CUT_DISTANCE_MM = 6.0
OUTER_SHELL_LOWER_STOP_BHIJ_CUT_TAPER_ANGLE_DEG = 10.0
OUTER_SHELL_LOWER_STOP_FILLET_RADIUS_MM = 3.0
OUTER_SHELL_LOWER_STOP_ARC_CUT_DISTANCE_MM = 8.2
OUTER_SHELL_LOWER_STOP_ARC_POSITIVE_Z_CUT_DISTANCE_MM = 5.0
OUTER_SHELL_LOWER_STOP_CIRCLE_POSITIVE_Z_CUT_DISTANCE_MM = 30.0
OUTER_SHELL_LOWER_STOP_SKETCH1_POINTS_MM = {
    'A': (-29.854, -35.00, 24.037),
    'B': (-29.854, -25.9, 24.794),
    'C': (-29.854, -35.00, -6.0),
    'D': (-29.854, -25.9, -6.0),
}
OUTER_SHELL_LOWER_STOP_SKETCH2_POINTS_MM = {
    'E': (-29.854, 29.638, -6.0),
    'F': (-28.706, 29.638, -3.2),
    'G': (-29.854, -25.9, -3.2),
}
OUTER_SHELL_LOWER_STOP_SKETCH3_POINTS_MM = {
    'H': (-28.706, -22.709, 25.059),
    'I': (-28.706, -22.709, 22.059),
    'J': (-29.854, -25.9, 21.794),
}
OUTER_SHELL_LOWER_STOP_SKETCH4_POINTS_MM = {
    'K': (-9.703, -24.217, 5.0),
    'L': (-9.703, -19.664, 5.0),
    'M': (-28.967, -22.556, 5.0),
    'N': (-30.161, -25.679, 5.0),
    'O': (-21.0, -10.0, 5.0),
    'P': (-10.0, -20.198, 5.0),
}
OUTER_SHELL_LOWER_STOP_SKETCH5_POINTS_MM = {
    'Q': (0.0, -25.2, 9.2),
    'R': (0.0, -25.2, -5.0),
    'S': (0.0, -23.2, -5.0),
    'T': (0.0, -23.2, 7.2),
    'U': (0.0, -20.0, 7.2),
    'V': (0.0, -20.0, 9.2),
    'W': (0.0, -23.2, 9.2),
}
OUTER_SHELL_END_CUT_SKETCH_NAME = '外殻端修正'
OUTER_SHELL_L_BUTTON_OPENING_SKETCH_NAME = '外殻Lボタン開口部'
OUTER_SHELL_END_CUT_POINT_A_MM = (-51.8, 35.0, 26.654)
OUTER_SHELL_END_CUT_POINT_B_MM = (-51.8, 35.0, 20.654)
OUTER_SHELL_END_CUT_POINT_C_MM = (-51.8, 32.455, 20.654)
OUTER_SHELL_END_CUT_POINT_D_MM = (-51.8, 32.455, 26.442)
OUTER_SHELL_END_CUT_PROFILE_TARGET_MM = (-51.8, 33.7, 23.6)
OUTER_SHELL_END_CUT_MARGIN_MM = 0.8
OUTER_SHELL_END_CUT_DISTANCE_MM = 3.0
OUTER_SHELL_YZ_RECT_CUT_SKETCH_NAME = '外殻YZ矩形切り取り'
OUTER_SHELL_YZ_RECT_CUT_POINT_E_MM = (-51.8, 28.0, 28.0)
OUTER_SHELL_YZ_RECT_CUT_POINT_F_MM = (-51.8, 28.0, -6.0)
OUTER_SHELL_YZ_RECT_CUT_POINT_G_MM = (-51.8, 32.2, -6.0)
OUTER_SHELL_YZ_RECT_CUT_POINT_H_MM = (-51.8, 32.2, 28.0)
OUTER_SHELL_YZ_RECT_CUT_PROFILE_TARGET_MM = (-51.8, 30.1, 11.0)
OUTER_SHELL_YZ_RECT_CUT_DISTANCE_MM = 6.0
OUTER_SHELL_SIDE_EXTENSION_SKETCH_NAME = '外殻側面押し出し'
OUTER_SHELL_SIDE_EXTENSION_POINT_E_MM = (-5.0, -23.2, 21.818)
OUTER_SHELL_SIDE_EXTENSION_POINT_F_MM = (-5.0, -23.3, -6.0)
OUTER_SHELL_SIDE_EXTENSION_POINT_G_MM = (-5.0, -35.0, -6.0)
OUTER_SHELL_SIDE_EXTENSION_POINT_H_MM = (-5.0, -35.0, 20.837)
OUTER_SHELL_SIDE_EXTENSION_PROFILE_TARGET_MM = (-5.0, -5.0, 7.0)
OUTER_SHELL_SIDE_EXTENSION_DISTANCE_MM = 5.0
OUTER_SHELL_FITTING_ADJUSTMENT_SKETCH_NAME = '外殻はめ込み微調整'
OUTER_SHELL_FITTING_ADJUSTMENT_POINT_A_MM = (-9.8, -23.2, -3.2)
OUTER_SHELL_FITTING_ADJUSTMENT_POINT_B_MM = (-9.8, -24.346, -3.2)
OUTER_SHELL_FITTING_ADJUSTMENT_POINT_C_MM = (-9.8, -24.346, 21.723)
OUTER_SHELL_FITTING_ADJUSTMENT_POINT_D_MM = (-9.8, -23.2, 21.818)
OUTER_SHELL_FITTING_ADJUSTMENT_SKETCH_PLANE_X_MM = (
    OUTER_SHELL_FITTING_ADJUSTMENT_POINT_A_MM[0]
    + 0.2
)
OUTER_SHELL_FITTING_ADJUSTMENT_PROFILE_TARGET_MM = (
    OUTER_SHELL_FITTING_ADJUSTMENT_SKETCH_PLANE_X_MM,
    -23.773,
    9.28525,
)
OUTER_SHELL_FITTING_ADJUSTMENT_CUT_DISTANCE_MM = 0.2
OUTER_SHELL_FITTING_CORRECTION_SKETCH_NAME = '外殻はめ込み修正'
OUTER_SHELL_FITTING_CORRECTION_POINTS_MM = {
    'O': (-29.854, 7.499, -3.2),
    'P': (-26.981, -30.932, -3.2),
    'Q': (-44.625, -28.096, -3.2),
    'R': (-27.386, 7.499, -3.2),
}
OUTER_SHELL_FITTING_CORRECTION_PROFILE_TARGET_MM = (
    -32.2115,
    -11.0075,
    -3.2,
)
OUTER_SHELL_FITTING_CORRECTION_CUT_DISTANCE_MM = 25.0
OUTER_SHELL_FITTING_CORRECTION_A_FACE_POINTS_MM = (
    (-26.981, -30.932, 21.80),
    (-26.981, -30.932, -3.2),
    (-27.057, -23.723, 21.80),
)
OUTER_SHELL_FITTING_CORRECTION_A_SECTION_SKETCH_NAME = '外殻はめ込み修正 A断面'
OUTER_SHELL_FITTING_CORRECTION_A_PROFILE_TARGET_MM = (
    -27.006333333333334,
    -28.529,
    13.466666666666667,
)
OUTER_SHELL_FITTING_CORRECTION_B_FACE_POINTS_MM = (
    (-9.703, -21.116, 9.859),
    (-9.703, -24.217, -3.2),
    (-9.703, -24.217, 10.0),
)
OUTER_SHELL_FITTING_CORRECTION_B_SECTION_SKETCH_NAME = '外殻はめ込み修正 B断面'
OUTER_SHELL_FITTING_CORRECTION_B_PROFILE_TARGET_MM = (
    -9.703,
    -23.183333333333334,
    5.553,
)
OUTER_SHELL_L_BUTTON_OPENING_REFERENCE_START_MM = (-55.748, 35.0, 0.0)
OUTER_SHELL_L_BUTTON_OPENING_REFERENCE_END_MM = (-66.477, 27.133, 0.0)
OUTER_SHELL_L_BUTTON_OPENING_LINE_C_MM = (-51.8, 28.218, 0.0)
OUTER_SHELL_L_BUTTON_OPENING_LINE_D_MM = (-66.477, 27.133, 0.0)
OUTER_SHELL_L_BUTTON_OPENING_ENDPOINT_F_MM = (-54.581, 32.455, 0.0)
OUTER_SHELL_L_BUTTON_OPENING_LINE_G_MM = (-51.8, 35.0, 0.0)
OUTER_SHELL_L_BUTTON_OPENING_BASE_CORNER_H_MM = (-51.8, 35.0, 20.654)
OUTER_SHELL_L_BUTTON_OPENING_BASE_CORNER_I_MM = (-59.8, 35.0, 20.654)
OUTER_SHELL_L_BUTTON_OPENING_BASE_CORNER_J_MM = (-59.8, 35.0, -1.346)
OUTER_SHELL_L_BUTTON_OPENING_BASE_CORNER_K_MM = (-51.8, 35.0, -1.364)
OUTER_SHELL_L_BUTTON_OPENING_OFFSET_MM = 2.8
OUTER_SHELL_L_BUTTON_OPENING_PROFILE_TARGET_MM = (-54.8, 33.4, 0.0)
OUTER_SHELL_L_BUTTON_OPENING_BASE_PROFILE_TARGET_MM = (-55.8, 35.0, 9.6)
OUTER_SHELL_L_BUTTON_OPENING_EXTRUDE_DISTANCE_MM = 27.0
OUTER_SHELL_L_BUTTON_OPENING_BASE_CUT_DISTANCE_MM = 20.0
OUTER_SHELL_L_BUTTON_OPENING_BASE_FILLET_AXIS_1_POINT_MM = OUTER_SHELL_L_BUTTON_OPENING_BASE_CORNER_J_MM
OUTER_SHELL_L_BUTTON_OPENING_BASE_FILLET_AXIS_1_RADIUS_MM = 15.0
OUTER_SHELL_L_BUTTON_OPENING_BASE_FILLET_AXIS_2_POINT_MM = OUTER_SHELL_L_BUTTON_OPENING_BASE_CORNER_I_MM
OUTER_SHELL_L_BUTTON_OPENING_BASE_FILLET_AXIS_2_RADIUS_MM = 4.0
OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_SKETCH_NAME = '外殻Lボタン開口部内部仕様'
OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_PLANE_NAME = '外殻Lボタン開口部内部仕様平面'
OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_PLANE_X_MM = -59.8
OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_POINT_A_MM = (-59.8, 27.311, 24.969)
OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_POINT_B_MM = (-59.8, 32.0, 16.654)
OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_POINT_C_MM = (-59.8, 32.0, 11.902)
OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_POINT_D_MM = (-59.8, 27.311, -0.69)
OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_POINT_E_MM = (-59.8, 31.218, 20.473)
OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_POINT_F_MM = (-59.8, 30.747, 4.392)
OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_PROFILE_TARGET_MM = (-59.8, 30.2, 12.0)
OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_SKETCH_NAME = '外殻Lボタン開口部斜面切り取り'
OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_O_MM = (-66.765, 27.112, 26.2)
OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_P_MM = (-48.687, 28.653, -3.2)
OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_Q_MM = (
    OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_O_MM[0],
    OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_O_MM[1],
    OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_P_MM[2],
)
OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_R_MM = (
    OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_P_MM[0],
    OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_P_MM[1],
    OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_O_MM[2],
)
OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_PROFILE_TARGET_MM = (
    (OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_O_MM[0] + OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_P_MM[0]) / 2.0,
    (OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_O_MM[1] + OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_P_MM[1]) / 2.0,
    (OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_O_MM[2] + OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_P_MM[2]) / 2.0,
)
OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_DISTANCE_MM = 0.2
OUTER_SHELL_Y35_FACE_CUT_TARGET_MM = (-55.8, 35.0, 9.6)
OUTER_SHELL_Y35_FACE_CUT_DISTANCE_MM = 2.8
OUTER_SHELL_L_BUTTON_OPENING_FILLET_REFERENCE_POINTS_MM = (
    (-54.581, 32.455, 0.0),
    (-60.8, 29.7, 0.0),
)
OUTER_SHELL_L_BUTTON_OPENING_FILLET_RADIUS_MM = 6.0
OUTER_SHELL_L_BUTTON_OPENING_CUT_DISTANCE_MM = 10.0
OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_SKETCH_NAME = '外殻Lボタン開口部 追加'
OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_PLANE_NAME = '外殻Lボタン開口部 追加平面'
OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_PLANE_Y_MM = 32.20
OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_A_MM = (-57.80, 32.20, 24.966)
OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_B_MM = (-57.80, 32.20, 0.0)
OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_C_MM = (-61.254, 32.20, 19.887)
OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_D_MM = (-61.254, 32.20, 12.80)
OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_PROFILE_TARGET_MM = (-59.8, 32.20, 14.5)
OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_DISTANCE_MM = 15.0
INNER_SHELL_LID_SLOPE_REFERENCE_POINTS_MM = (
    (-63.701, -27.138, 25.8),
    (-62.178, -22.954, 25.452),
    (-32.059, -20.122, 21.873),
)


def mm_to_cm(value_mm):
    return value_mm / 10.0


def create_point_mm(x_mm, y_mm, z_mm=0.0):
    return adsk.core.Point3D.create(
        mm_to_cm(x_mm),
        mm_to_cm(y_mm),
        mm_to_cm(z_mm),
    )


def create_sketch_point(sketch, point_mm):
    return sketch.sketchPoints.add(create_point_mm(*point_mm))


def to_sketch_space(sketch, point_mm):
    return sketch.modelToSketchSpace(create_point_mm(*point_mm))


def offset_point_x_mm(point_mm, offset_x_mm):
    return (
        point_mm[0] + offset_x_mm,
        point_mm[1],
        point_mm[2],
    )


def create_reference_sketch_point(root_comp, point_mm, name=None):
    plane = create_offset_plane_from_xy(root_comp, point_mm[2])
    sketch = root_comp.sketches.add(plane)
    if name:
        sketch.name = name
    return sketch.sketchPoints.add(
        sketch.modelToSketchSpace(create_point_mm(*point_mm))
    )


def create_plane_by_three_points(root_comp, point_a_mm, point_b_mm, point_c_mm, name=None):
    point_a = create_reference_sketch_point(root_comp, point_a_mm)
    point_b = create_reference_sketch_point(root_comp, point_b_mm)
    point_c = create_reference_sketch_point(root_comp, point_c_mm)

    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByThreePoints(point_a, point_b, point_c)
    plane = planes.add(plane_input)
    if name:
        plane.name = name
    return plane


def point3d_to_mm_tuple(point):
    return (
        point.x * 10.0,
        point.y * 10.0,
        point.z * 10.0,
    )


def get_point_distance(point_a, point_b):
    return math.sqrt(
        ((point_a.x - point_b.x) ** 2)
        + ((point_a.y - point_b.y) ** 2)
        + ((point_a.z - point_b.z) ** 2)
    )


def get_body_from_feature(feature):
    body = feature.bodies.item(0)
    if not body:
        raise RuntimeError('外殻ボディを取得できませんでした。')
    return body


def get_face_collection(body):
    return [body.faces.item(index) for index in range(body.faces.count)]


def find_face_by_named_attribute(body, name):
    for face in get_face_collection(body):
        attribute = face.attributes.itemByName(
            naming.ATTRIBUTE_GROUP,
            naming.ATTRIBUTE_NAME_KEY
        )
        if attribute and attribute.value == name:
            return face
    raise RuntimeError('指定された名前の面を取得できませんでした。')


def find_body_face_by_named_attribute(root_comp, name):
    for index in range(root_comp.bRepBodies.count):
        body = root_comp.bRepBodies.item(index)
        try:
            face = find_face_by_named_attribute(body, name)
            return body, face
        except RuntimeError:
            continue
    raise RuntimeError('指定された名前の面を持つボディを取得できませんでした。')


def find_inner_shell_lid_slope_face(body, tolerance=1e-6):
    matching_faces = []
    target_slope = math.tan(math.radians(4.75))
    slope_tolerance = 0.02
    reference_points = [create_point_mm(*point_mm) for point_mm in INNER_SHELL_LID_SLOPE_REFERENCE_POINTS_MM]

    for face in get_face_collection(body):
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        normal = geometry.normal
        if abs(normal.x) > tolerance:
            continue

        if abs(normal.y) <= tolerance or abs(normal.z) <= tolerance:
            continue

        slope = abs(normal.y / normal.z)
        if abs(slope - target_slope) > slope_tolerance:
            continue

        matching_faces.append(face)

    if not matching_faces:
        raise RuntimeError('内殻蓋部斜面を取得できませんでした。')

    def face_score(face):
        box = face.boundingBox
        score = 0.0
        for point in reference_points:
            dx = 0.0
            dy = 0.0
            dz = 0.0
            if point.x < box.minPoint.x:
                dx = box.minPoint.x - point.x
            elif point.x > box.maxPoint.x:
                dx = point.x - box.maxPoint.x
            if point.y < box.minPoint.y:
                dy = box.minPoint.y - point.y
            elif point.y > box.maxPoint.y:
                dy = point.y - box.maxPoint.y
            if point.z < box.minPoint.z:
                dz = box.minPoint.z - point.z
            elif point.z > box.maxPoint.z:
                dz = point.z - box.maxPoint.z
            score += dx + dy + dz
        return score

    return min(matching_faces, key=lambda face: (face_score(face), -face.area))


def find_best_planar_face_near_reference_points(body, reference_points_mm, tolerance=1e-6):
    reference_points = [create_point_mm(*point_mm) for point_mm in reference_points_mm]
    candidate_faces = []

    for face in get_face_collection(body):
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        normal = geometry.normal
        if abs(normal.x) > 0.2:
            continue
        if abs(normal.y) <= tolerance or abs(normal.z) <= tolerance:
            continue

        box = face.boundingBox
        score = 0.0
        for point in reference_points:
            dx = 0.0
            dy = 0.0
            dz = 0.0
            if point.x < box.minPoint.x:
                dx = box.minPoint.x - point.x
            elif point.x > box.maxPoint.x:
                dx = point.x - box.maxPoint.x
            if point.y < box.minPoint.y:
                dy = box.minPoint.y - point.y
            elif point.y > box.maxPoint.y:
                dy = point.y - box.maxPoint.y
            if point.z < box.minPoint.z:
                dz = box.minPoint.z - point.z
            elif point.z > box.maxPoint.z:
                dz = point.z - box.maxPoint.z
            score += dx + dy + dz

            signed_distance = abs(
                normal.x * (point.x - geometry.origin.x)
                + normal.y * (point.y - geometry.origin.y)
                + normal.z * (point.z - geometry.origin.z)
            )
            score += signed_distance

        candidate_faces.append((face, score))

    if not candidate_faces:
        raise RuntimeError('参照点近傍の平面面を取得できませんでした。')

    return min(candidate_faces, key=lambda item: (item[1], -item[0].area))[0]


def get_nearest_distance_to_edge(edge, target_point, sample_count=80):
    evaluator = edge.evaluator
    try:
        success, start_param, end_param = evaluator.getParameterExtents()
    except RuntimeError:
        success = False
        start_param = None
        end_param = None
    if not success:
        start_param = None
        end_param = None

    sampled_points = []
    if start_param is not None and end_param is not None:
        for index in range(sample_count + 1):
            parameter = start_param + ((end_param - start_param) * index / sample_count)
            try:
                success, point = evaluator.getPointAtParameter(parameter)
            except RuntimeError:
                continue
            if success and point:
                sampled_points.append(point)

    if not sampled_points:
        start_vertex = edge.startVertex
        end_vertex = edge.endVertex
        if start_vertex and start_vertex.geometry:
            sampled_points.append(start_vertex.geometry)
        if end_vertex and end_vertex.geometry:
            sampled_points.append(end_vertex.geometry)

    if not sampled_points:
        raise RuntimeError('辺上のサンプル点を取得できませんでした。')

    return min(get_point_distance(point, target_point) for point in sampled_points)


def get_body_bounding_box_center(body):
    box = body.boundingBox
    return adsk.core.Point3D.create(
        (box.minPoint.x + box.maxPoint.x) / 2.0,
        (box.minPoint.y + box.maxPoint.y) / 2.0,
        (box.minPoint.z + box.maxPoint.z) / 2.0,
    )


def get_body_volume(body):
    try:
        physical_properties = body.physicalProperties
    except RuntimeError:
        physical_properties = None

    if physical_properties is not None:
        try:
            return physical_properties.volume
        except RuntimeError:
            pass

    box = body.boundingBox
    return (
        (box.maxPoint.x - box.minPoint.x)
        * (box.maxPoint.y - box.minPoint.y)
        * (box.maxPoint.z - box.minPoint.z)
    )


def get_signed_distance_to_plane(plane_geometry, point):
    origin = plane_geometry.origin
    normal = plane_geometry.normal
    vector = adsk.core.Vector3D.create(
        point.x - origin.x,
        point.y - origin.y,
        point.z - origin.z,
    )
    return normal.dotProduct(vector)


def move_body_by_translation(root_comp, body, x_mm=0.0, y_mm=0.0, z_mm=0.0):
    bodies = adsk.core.ObjectCollection.create()
    bodies.add(body)

    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(
        mm_to_cm(x_mm),
        mm_to_cm(y_mm),
        mm_to_cm(z_mm),
    )

    move_features = root_comp.features.moveFeatures
    move_input = move_features.createInput2(bodies)
    move_input.defineAsFreeMove(transform)
    move_feature = move_features.add(move_input)

    moved_body = move_feature.bodies.item(0)
    if not moved_body:
        raise RuntimeError('移動後のボディを取得できませんでした。')
    return moved_body


def find_face_through_point_on_constant_axis(body, point_mm, axis, tolerance_cm):
    target_point = create_point_mm(*point_mm)

    for face in get_face_collection(body):
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        box = face.boundingBox
        min_value = getattr(box.minPoint, axis)
        max_value = getattr(box.maxPoint, axis)
        if abs(max_value - min_value) > tolerance_cm:
            continue

        if face.isPointOnFace(target_point, tolerance_cm):
            return face

    raise RuntimeError('指定条件に一致する外殻面を取得できませんでした。')


def find_planar_face_through_points(body, point_list_mm, tolerance_cm):
    target_points = [create_point_mm(*point_mm) for point_mm in point_list_mm]
    if len(target_points) < 3:
        raise RuntimeError('平面面の判定には3点以上が必要です。')

    point_a = target_points[0]
    point_b = target_points[1]
    point_c = target_points[2]
    vector_ab = adsk.core.Vector3D.create(
        point_b.x - point_a.x,
        point_b.y - point_a.y,
        point_b.z - point_a.z,
    )
    vector_ac = adsk.core.Vector3D.create(
        point_c.x - point_a.x,
        point_c.y - point_a.y,
        point_c.z - point_a.z,
    )
    reference_normal = vector_ab.crossProduct(vector_ac)
    if reference_normal.length <= 1e-9:
        raise RuntimeError('指定点から基準平面を決定できませんでした。')
    reference_normal.normalize()

    candidate_faces = []

    for face in get_face_collection(body):
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        face_normal = geometry.normal.copy()
        if face_normal.length <= 1e-9:
            continue
        face_normal.normalize()

        alignment = abs(face_normal.dotProduct(reference_normal))
        if alignment < 0.98:
            continue

        box = face.boundingBox
        score = (1.0 - alignment) * 10.0
        for point in target_points:
            signed_distance = abs(
                face_normal.x * (point.x - geometry.origin.x)
                + face_normal.y * (point.y - geometry.origin.y)
                + face_normal.z * (point.z - geometry.origin.z)
            )
            score += signed_distance

            dx = 0.0
            dy = 0.0
            dz = 0.0
            if point.x < box.minPoint.x:
                dx = box.minPoint.x - point.x
            elif point.x > box.maxPoint.x:
                dx = point.x - box.maxPoint.x
            if point.y < box.minPoint.y:
                dy = box.minPoint.y - point.y
            elif point.y > box.maxPoint.y:
                dy = point.y - box.maxPoint.y
            if point.z < box.minPoint.z:
                dz = box.minPoint.z - point.z
            elif point.z > box.maxPoint.z:
                dz = point.z - box.maxPoint.z
            score += dx + dy + dz

        candidate_faces.append((face, score))

    if not candidate_faces:
        raise RuntimeError('指定された3点を通る平面面を取得できませんでした。')

    return min(candidate_faces, key=lambda item: (item[1], -item[0].area))[0]


def find_best_planar_face_for_points(body, point_list_mm, min_alignment=0.9):
    target_points = [create_point_mm(*point_mm) for point_mm in point_list_mm]
    if len(target_points) < 3:
        raise RuntimeError('平面面の判定には3点以上が必要です。')

    point_a = target_points[0]
    point_b = target_points[1]
    point_c = target_points[2]
    vector_ab = adsk.core.Vector3D.create(
        point_b.x - point_a.x,
        point_b.y - point_a.y,
        point_b.z - point_a.z,
    )
    vector_ac = adsk.core.Vector3D.create(
        point_c.x - point_a.x,
        point_c.y - point_a.y,
        point_c.z - point_a.z,
    )
    reference_normal = vector_ab.crossProduct(vector_ac)
    if reference_normal.length <= 1e-9:
        raise RuntimeError('指定点から基準平面を決定できませんでした。')
    reference_normal.normalize()

    candidate_faces = []

    for face in get_face_collection(body):
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        face_normal = geometry.normal.copy()
        if face_normal.length <= 1e-9:
            continue
        face_normal.normalize()

        alignment = abs(face_normal.dotProduct(reference_normal))
        if alignment < min_alignment:
            continue

        box = face.boundingBox
        score = (1.0 - alignment) * 100.0
        for point in target_points:
            signed_distance = abs(
                face_normal.x * (point.x - geometry.origin.x)
                + face_normal.y * (point.y - geometry.origin.y)
                + face_normal.z * (point.z - geometry.origin.z)
            )
            score += signed_distance

            dx = 0.0
            dy = 0.0
            dz = 0.0
            if point.x < box.minPoint.x:
                dx = box.minPoint.x - point.x
            elif point.x > box.maxPoint.x:
                dx = point.x - box.maxPoint.x
            if point.y < box.minPoint.y:
                dy = box.minPoint.y - point.y
            elif point.y > box.maxPoint.y:
                dy = point.y - box.maxPoint.y
            if point.z < box.minPoint.z:
                dz = box.minPoint.z - point.z
            elif point.z > box.maxPoint.z:
                dz = point.z - box.maxPoint.z
            score += dx + dy + dz

        candidate_faces.append((face, score))

    if not candidate_faces:
        raise RuntimeError('指定点近傍の平面面を取得できませんでした。')

    return min(candidate_faces, key=lambda item: (item[1], -item[0].area))[0]


def find_largest_xy_face_at_z_covering_point(body, point_mm, tolerance_cm):
    target_x = mm_to_cm(point_mm[0])
    target_y = mm_to_cm(point_mm[1])
    target_z = mm_to_cm(point_mm[2])
    candidate_faces = []

    for face in get_face_collection(body):
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        normal = geometry.normal
        if abs(normal.x) > tolerance_cm or abs(normal.y) > tolerance_cm or abs(normal.z) <= tolerance_cm:
            continue

        box = face.boundingBox
        if abs(box.minPoint.z - target_z) > tolerance_cm or abs(box.maxPoint.z - target_z) > tolerance_cm:
            continue
        if target_x < box.minPoint.x - tolerance_cm or target_x > box.maxPoint.x + tolerance_cm:
            continue
        if target_y < box.minPoint.y - tolerance_cm or target_y > box.maxPoint.y + tolerance_cm:
            continue

        candidate_faces.append(face)

    if not candidate_faces:
        raise RuntimeError('指定条件に一致する上側 XY 面を取得できませんでした。')

    return max(candidate_faces, key=lambda face: face.area)


def find_largest_xz_face_at_y_covering_point(body, point_mm, tolerance_cm):
    target_x = mm_to_cm(point_mm[0])
    target_y = mm_to_cm(point_mm[1])
    target_z = mm_to_cm(point_mm[2])
    candidate_faces = []

    for face in get_face_collection(body):
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        normal = geometry.normal
        if abs(normal.x) > tolerance_cm or abs(normal.y) <= tolerance_cm or abs(normal.z) > tolerance_cm:
            continue

        box = face.boundingBox
        if abs(box.minPoint.y - target_y) > tolerance_cm or abs(box.maxPoint.y - target_y) > tolerance_cm:
            continue
        if target_x < box.minPoint.x - tolerance_cm or target_x > box.maxPoint.x + tolerance_cm:
            continue
        if target_z < box.minPoint.z - tolerance_cm or target_z > box.maxPoint.z + tolerance_cm:
            continue

        candidate_faces.append(face)

    if not candidate_faces:
        raise RuntimeError('指定条件に一致する Y 一定の XZ 面を取得できませんでした。')

    return max(candidate_faces, key=lambda face: face.area)


def find_largest_yz_face_at_x_covering_point(body, point_mm, tolerance_cm):
    target_x = mm_to_cm(point_mm[0])
    target_y = mm_to_cm(point_mm[1])
    target_z = mm_to_cm(point_mm[2])
    candidate_faces = []

    for face in get_face_collection(body):
        geometry = adsk.core.Plane.cast(face.geometry)
        if not geometry:
            continue

        normal = geometry.normal
        if abs(normal.x) <= tolerance_cm or abs(normal.y) > tolerance_cm or abs(normal.z) > tolerance_cm:
            continue

        box = face.boundingBox
        if abs(box.minPoint.x - target_x) > tolerance_cm or abs(box.maxPoint.x - target_x) > tolerance_cm:
            continue
        if target_y < box.minPoint.y - tolerance_cm or target_y > box.maxPoint.y + tolerance_cm:
            continue
        if target_z < box.minPoint.z - tolerance_cm or target_z > box.maxPoint.z + tolerance_cm:
            continue

        candidate_faces.append(face)

    if not candidate_faces:
        raise RuntimeError('指定条件に一致する X 一定の YZ 面を取得できませんでした。')

    return max(candidate_faces, key=lambda face: face.area)


def is_linear_edge(edge):
    return adsk.core.Line3D.cast(edge.geometry) is not None


def find_linear_edge_parallel_to_y_near_point(body, target_point_mm, tolerance_cm=1e-5):
    target_point = create_point_mm(*target_point_mm)
    candidate_edge = None
    candidate_score = None

    for edge in body.edges:
        line = adsk.core.Line3D.cast(edge.geometry)
        if not line:
            continue

        start_vertex = edge.startVertex
        end_vertex = edge.endVertex
        if not start_vertex or not end_vertex:
            continue

        start_point = start_vertex.geometry
        end_point = end_vertex.geometry
        if not start_point or not end_point:
            continue

        delta_x = end_point.x - start_point.x
        delta_y = end_point.y - start_point.y
        delta_z = end_point.z - start_point.z
        if abs(delta_x) > tolerance_cm or abs(delta_z) > tolerance_cm or abs(delta_y) <= tolerance_cm:
            continue

        box = edge.boundingBox
        if (
            target_point.x < box.minPoint.x - tolerance_cm
            or target_point.x > box.maxPoint.x + tolerance_cm
            or target_point.y < box.minPoint.y - tolerance_cm
            or target_point.y > box.maxPoint.y + tolerance_cm
            or target_point.z < box.minPoint.z - tolerance_cm
            or target_point.z > box.maxPoint.z + tolerance_cm
        ):
            continue

        try:
            score = get_nearest_distance_to_edge(edge, target_point)
        except RuntimeError:
            continue
        if candidate_score is None or score < candidate_score:
            candidate_score = score
            candidate_edge = edge

    if not candidate_edge:
        raise RuntimeError('指定条件に一致する Y 軸平行エッジを取得できませんでした。')

    return candidate_edge


def find_linear_edge_parallel_to_x_near_point(body, target_point_mm, tolerance_cm=1e-5):
    target_point = create_point_mm(*target_point_mm)
    candidate_edge = None
    candidate_score = None
    fallback_edge = None
    fallback_score = None

    for edge in body.edges:
        line = adsk.core.Line3D.cast(edge.geometry)
        if not line:
            continue

        start_vertex = edge.startVertex
        end_vertex = edge.endVertex
        if not start_vertex or not end_vertex:
            continue

        start_point = start_vertex.geometry
        end_point = end_vertex.geometry
        if not start_point or not end_point:
            continue

        delta_x = end_point.x - start_point.x
        delta_y = end_point.y - start_point.y
        delta_z = end_point.z - start_point.z
        if abs(delta_y) > tolerance_cm or abs(delta_z) > tolerance_cm or abs(delta_x) <= tolerance_cm:
            continue

        try:
            score = get_nearest_distance_to_edge(edge, target_point)
        except RuntimeError:
            continue
        if fallback_score is None or score < fallback_score:
            fallback_score = score
            fallback_edge = edge

        box = edge.boundingBox
        if (
            target_point.x < box.minPoint.x - tolerance_cm
            or target_point.x > box.maxPoint.x + tolerance_cm
            or target_point.y < box.minPoint.y - tolerance_cm
            or target_point.y > box.maxPoint.y + tolerance_cm
            or target_point.z < box.minPoint.z - tolerance_cm
            or target_point.z > box.maxPoint.z + tolerance_cm
        ):
            continue

        if candidate_score is None or score < candidate_score:
            candidate_score = score
            candidate_edge = edge

    if not candidate_edge:
        if fallback_edge is not None:
            return fallback_edge
        raise RuntimeError('指定条件に一致する X 軸平行エッジを取得できませんでした。')

    return candidate_edge


def get_face_edge_nearest_point(
    face,
    target_point_mm,
    excluded_tokens=None,
    require_non_linear=False,
    require_linear=False,
):
    target_point = create_point_mm(*target_point_mm)
    nearest_edge = None
    nearest_score = None

    for edge in face.edges:
        if excluded_tokens and edge.entityToken in excluded_tokens:
            continue
        if require_linear and not is_linear_edge(edge):
            continue
        if require_non_linear and is_linear_edge(edge):
            continue

        try:
            score = get_nearest_distance_to_edge(edge, target_point)
        except RuntimeError:
            continue
        if nearest_score is None or score < nearest_score:
            nearest_score = score
            nearest_edge = edge

    if nearest_edge is None:
        raise RuntimeError('指定条件に一致する面エッジを取得できませんでした。')

    return nearest_edge


def project_face_edges_by_token(sketch, face):
    projected_by_token = {}

    for edge in face.edges:
        projected_items = sketch.project(edge)
        projected_by_token[edge.entityToken] = [
            projected_items.item(index)
            for index in range(projected_items.count)
        ]

    return projected_by_token


def find_inner_contact_faces(outer_shell_body, inner_shell_body, tolerance_cm):
    contact_faces = []
    inner_faces = get_face_collection(inner_shell_body)

    for outer_face in get_face_collection(outer_shell_body):
        sample_point = outer_face.pointOnFace
        if not sample_point:
            continue

        for inner_face in inner_faces:
            if inner_face.isPointOnFace(sample_point, tolerance_cm):
                contact_faces.append(outer_face)
                break

    if not contact_faces:
        raise RuntimeError('外殻内殻接面を取得できませんでした。')

    return contact_faces


def offset_contact_faces(root_comp, outer_shell_body, inner_shell_body):
    app = adsk.core.Application.get()
    tolerance_cm = max(app.pointTolerance, 1e-5)
    contact_faces = find_inner_contact_faces(
        outer_shell_body,
        inner_shell_body,
        tolerance_cm,
    )

    offset_faces = root_comp.features.offsetFacesFeatures
    distance = adsk.core.ValueInput.createByReal(mm_to_cm(-0.2))
    offset_input = offset_faces.createInput(contact_faces, distance)
    offset_feature = offset_faces.add(offset_input)

    if offset_feature:
        offset_feature.name = OUTER_SHELL_CONTACT_FACE_NAME
        for face in offset_feature.faces:
            helpers.add_named_attribute(face, OUTER_SHELL_CONTACT_FACE_NAME)

    return offset_feature


def extrude_xy_face_in_negative_z(root_comp, face, distance_mm, tolerance=1e-6):
    geometry = adsk.core.Plane.cast(face.geometry)
    if not geometry:
        raise RuntimeError('押し出し対象面の平面ジオメトリを取得できませんでした。')

    normal = geometry.normal
    if abs(normal.x) > tolerance or abs(normal.y) > tolerance or abs(normal.z) <= tolerance:
        raise RuntimeError('押し出し対象面が Z 方向法線を持っていません。')

    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
    if normal.z > 0.0:
        direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        face,
        adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    distance_value = adsk.core.ValueInput.createByReal(mm_to_cm(distance_mm))
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)


def extrude_xy_face_in_positive_z(root_comp, face, distance_mm, tolerance=1e-6):
    geometry = adsk.core.Plane.cast(face.geometry)
    if not geometry:
        raise RuntimeError('押し出し対象面の平面ジオメトリを取得できませんでした。')

    normal = geometry.normal
    if abs(normal.x) > tolerance or abs(normal.y) > tolerance or abs(normal.z) <= tolerance:
        raise RuntimeError('押し出し対象面が Z 方向法線を持っていません。')

    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
    if normal.z < 0.0:
        direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        face,
        adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    distance_value = adsk.core.ValueInput.createByReal(mm_to_cm(distance_mm))
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)


def get_curve_geometry(sketch_curve):
    geometry = getattr(sketch_curve, 'worldGeometry', None)
    if geometry:
        return geometry
    return getattr(sketch_curve, 'geometry', None)


def get_curve_midpoint(sketch_curve):
    geometry = get_curve_geometry(sketch_curve)
    evaluator = geometry.evaluator
    success, start_param, end_param = evaluator.getParameterExtents()
    if not success:
        raise RuntimeError('断面カーブのパラメータ範囲を取得できませんでした。')

    success, midpoint = evaluator.getPointAtParameter((start_param + end_param) / 2.0)
    if not success:
        raise RuntimeError('断面カーブの中点を取得できませんでした。')

    return midpoint


def get_nearest_point_on_sketch_curves(sketch_curves, target_point, sample_count=80):
    nearest_point = None
    nearest_distance = None

    for sketch_curve in sketch_curves:
        try:
            sample_points = sample_sketch_curve_points_in_sketch_space(
                sketch_curve,
                sample_count=sample_count,
            )
        except RuntimeError:
            continue

        for point in sample_points:
            distance = get_point_distance(point, target_point)
            if nearest_distance is None or distance < nearest_distance:
                nearest_distance = distance
                nearest_point = point

    if nearest_point is None:
        raise RuntimeError('基準曲線上の近傍点を取得できませんでした。')

    return nearest_point


def get_nearest_distance_to_sketch_curve(sketch_curve, target_point, sample_count=80):
    geometry = get_curve_geometry(sketch_curve)
    if not geometry:
        raise RuntimeError('スケッチカーブのジオメトリを取得できませんでした。')

    evaluator = geometry.evaluator
    success, start_param, end_param = evaluator.getParameterExtents()
    if not success:
        raise RuntimeError('スケッチカーブのパラメータ範囲を取得できませんでした。')

    nearest_distance = None
    for index in range(sample_count + 1):
        parameter = start_param + ((end_param - start_param) * index / sample_count)
        success, point = evaluator.getPointAtParameter(parameter)
        if not success:
            continue

        distance = get_point_distance(point, target_point)
        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance

    if nearest_distance is None:
        raise RuntimeError('スケッチカーブ上のサンプル点を取得できませんでした。')

    return nearest_distance


def get_first_sketch_curve(entities, error_message):
    for entity in entities:
        sketch_curve = adsk.fusion.SketchCurve.cast(entity)
        if sketch_curve:
            return sketch_curve
    raise RuntimeError(error_message)


def to_entity_list(entities):
    if entities is None:
        return []

    count = getattr(entities, 'count', None)
    if isinstance(count, int):
        return [entities.item(index) for index in range(count)]

    if callable(count):
        entity_count = count()
        return [entities.item(index) for index in range(entity_count)]

    try:
        return list(entities)
    except TypeError:
        raise RuntimeError('スケッチエンティティ集合を走査できませんでした。')


def get_first_sketch_line(entities, error_message):
    for entity in entities:
        sketch_line = adsk.fusion.SketchLine.cast(entity)
        if sketch_line:
            return sketch_line
    raise RuntimeError(error_message)


def get_curve_endpoint_nearest_point(sketch_curve, target_point):
    start_point = sketch_curve.startSketchPoint.geometry
    end_point = sketch_curve.endSketchPoint.geometry
    start_distance = get_point_distance(start_point, target_point)
    end_distance = get_point_distance(end_point, target_point)
    if start_distance <= end_distance:
        return start_point
    return end_point


def get_curve_endpoint_sketch_point_nearest_point(sketch_curve, target_point):
    start_point = sketch_curve.startSketchPoint.geometry
    end_point = sketch_curve.endSketchPoint.geometry
    start_distance = get_point_distance(start_point, target_point)
    end_distance = get_point_distance(end_point, target_point)
    if start_distance <= end_distance:
        return sketch_curve.startSketchPoint
    return sketch_curve.endSketchPoint


def get_curve_other_endpoint(sketch_curve, target_point):
    start_point = sketch_curve.startSketchPoint.geometry
    end_point = sketch_curve.endSketchPoint.geometry
    start_distance = get_point_distance(start_point, target_point)
    end_distance = get_point_distance(end_point, target_point)
    if start_distance <= end_distance:
        return end_point
    return start_point


def get_midpoint_mm(point_a_mm, point_b_mm):
    return tuple(
        (value_a + value_b) / 2.0
        for value_a, value_b in zip(point_a_mm, point_b_mm)
    )


def get_xy_cross_value(point, line_start_mm, line_end_mm):
    start_x = mm_to_cm(line_start_mm[0])
    start_y = mm_to_cm(line_start_mm[1])
    end_x = mm_to_cm(line_end_mm[0])
    end_y = mm_to_cm(line_end_mm[1])
    return (
        ((end_x - start_x) * (point.y - start_y))
        - ((end_y - start_y) * (point.x - start_x))
    )


def is_point_within_xy_line_segment(point, line_start_mm, line_end_mm, tolerance_cm=1e-5):
    min_x = mm_to_cm(min(line_start_mm[0], line_end_mm[0])) - tolerance_cm
    max_x = mm_to_cm(max(line_start_mm[0], line_end_mm[0])) + tolerance_cm
    min_y = mm_to_cm(min(line_start_mm[1], line_end_mm[1])) - tolerance_cm
    max_y = mm_to_cm(max(line_start_mm[1], line_end_mm[1])) + tolerance_cm
    return min_x <= point.x <= max_x and min_y <= point.y <= max_y


def find_curve_line_intersection_point(
    sketch_curve,
    line_start_mm,
    line_end_mm,
    sample_count=200,
    refinement_steps=30,
):
    geometry = get_curve_geometry(sketch_curve)
    if not geometry:
        raise RuntimeError('交点探索対象のスケッチカーブジオメトリを取得できませんでした。')

    evaluator = geometry.evaluator
    success, start_param, end_param = evaluator.getParameterExtents()
    if not success:
        raise RuntimeError('交点探索対象のスケッチカーブのパラメータ範囲を取得できませんでした。')

    previous_param = None
    previous_point = None
    previous_cross = None
    nearest_point = None
    nearest_score = None

    for index in range(sample_count + 1):
        parameter = start_param + ((end_param - start_param) * index / sample_count)
        success, point = evaluator.getPointAtParameter(parameter)
        if not success:
            continue

        cross_value = get_xy_cross_value(point, line_start_mm, line_end_mm)
        score = abs(cross_value)
        if not is_point_within_xy_line_segment(point, line_start_mm, line_end_mm):
            score += 1.0
        if nearest_score is None or score < nearest_score:
            nearest_score = score
            nearest_point = point

        if abs(cross_value) <= 1e-6 and is_point_within_xy_line_segment(point, line_start_mm, line_end_mm):
            return point

        if (
            previous_point is not None
            and is_point_within_xy_line_segment(point, line_start_mm, line_end_mm)
            and is_point_within_xy_line_segment(previous_point, line_start_mm, line_end_mm)
            and previous_cross is not None
            and (cross_value == 0.0 or previous_cross == 0.0 or (cross_value > 0.0) != (previous_cross > 0.0))
        ):
            lower_param = previous_param
            upper_param = parameter
            lower_cross = previous_cross
            upper_cross = cross_value
            lower_point = previous_point
            upper_point = point

            for _ in range(refinement_steps):
                middle_param = (lower_param + upper_param) / 2.0
                success, middle_point = evaluator.getPointAtParameter(middle_param)
                if not success:
                    break

                middle_cross = get_xy_cross_value(middle_point, line_start_mm, line_end_mm)
                if abs(middle_cross) <= 1e-6 and is_point_within_xy_line_segment(middle_point, line_start_mm, line_end_mm):
                    return middle_point

                if (middle_cross > 0.0) == (lower_cross > 0.0):
                    lower_param = middle_param
                    lower_cross = middle_cross
                    lower_point = middle_point
                else:
                    upper_param = middle_param
                    upper_cross = middle_cross
                    upper_point = middle_point

            return adsk.core.Point3D.create(
                (lower_point.x + upper_point.x) / 2.0,
                (lower_point.y + upper_point.y) / 2.0,
                (lower_point.z + upper_point.z) / 2.0,
            )

        previous_param = parameter
        previous_point = point
        previous_cross = cross_value

    if nearest_point is None:
        raise RuntimeError('オフセット曲線と基準直線の近傍点を取得できませんでした。')

    return nearest_point


def find_non_linear_sketch_curve_near_point(sketch_curves, target_point):
    nearest_curve = None
    nearest_score = None

    for sketch_curve in sketch_curves:
        if adsk.fusion.SketchLine.cast(sketch_curve):
            continue

        try:
            score = get_nearest_distance_to_sketch_curve(sketch_curve, target_point)
        except RuntimeError:
            continue

        if nearest_score is None or score < nearest_score:
            nearest_score = score
            nearest_curve = sketch_curve

    if nearest_curve is None:
        raise RuntimeError('指定条件に一致する非線形スケッチカーブを取得できませんでした。')

    return nearest_curve


def find_face_boundary_point_in_positive_x(face, model_point, tolerance_cm, iterations=40):
    box = face.boundingBox
    low_x = model_point.x
    high_x = box.maxPoint.x

    for _ in range(iterations):
        mid_x = (low_x + high_x) / 2.0
        candidate = adsk.core.Point3D.create(mid_x, model_point.y, model_point.z)
        if face.isPointOnFace(candidate, tolerance_cm):
            low_x = mid_x
        else:
            high_x = mid_x

    return adsk.core.Point3D.create(low_x, model_point.y, model_point.z)


def clone_intersection_curve_as_sketch_geometry(sketch, sketch_curve):
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    circles = sketch.sketchCurves.sketchCircles
    splines = sketch.sketchCurves.sketchFittedSplines

    sketch_line = adsk.fusion.SketchLine.cast(sketch_curve)
    if sketch_line:
        return lines.addByTwoPoints(
            sketch_line.startSketchPoint.geometry,
            sketch_line.endSketchPoint.geometry,
        )

    sketch_arc = adsk.fusion.SketchArc.cast(sketch_curve)
    if sketch_arc:
        return arcs.addByThreePoints(
            sketch_arc.startSketchPoint.geometry,
            get_curve_midpoint(sketch_arc),
            sketch_arc.endSketchPoint.geometry,
        )

    sketch_circle = adsk.fusion.SketchCircle.cast(sketch_curve)
    if sketch_circle:
        geometry = adsk.core.Circle3D.cast(get_curve_geometry(sketch_circle))
        if not geometry:
            raise RuntimeError('断面円のジオメトリを取得できませんでした。')
        return circles.addByCenterRadius(geometry.center, geometry.radius)

    sketch_ellipse = adsk.fusion.SketchEllipse.cast(sketch_curve)
    if sketch_ellipse:
        geometry = adsk.core.Ellipse3D.cast(get_curve_geometry(sketch_ellipse))
        if not geometry:
            raise RuntimeError('断面楕円のジオメトリを取得できませんでした。')
        return sketch.sketchCurves.sketchEllipses.add(
            geometry.center,
            geometry.majorAxis,
            geometry.pointOnEllipse,
        )

    sketch_spline = adsk.fusion.SketchFittedSpline.cast(sketch_curve)
    if sketch_spline:
        geometry = get_curve_geometry(sketch_spline)
        evaluator = geometry.evaluator
        success, start_param, end_param = evaluator.getParameterExtents()
        if not success:
            raise RuntimeError('断面スプラインのパラメータ範囲を取得できませんでした。')

        fit_points = adsk.core.ObjectCollection.create()
        sample_count = 16
        for index in range(sample_count + 1):
            parameter = start_param + ((end_param - start_param) * index / sample_count)
            success, point = evaluator.getPointAtParameter(parameter)
            if not success:
                raise RuntimeError('断面スプラインのサンプル点を取得できませんでした。')
            fit_points.add(point)
        return splines.add(fit_points)

    geometry = get_curve_geometry(sketch_curve)
    if geometry:
        evaluator = geometry.evaluator
        success, start_param, end_param = evaluator.getParameterExtents()
        if success:
            fit_points = adsk.core.ObjectCollection.create()
            sample_count = 24
            for index in range(sample_count + 1):
                parameter = start_param + ((end_param - start_param) * index / sample_count)
                success, point = evaluator.getPointAtParameter(parameter)
                if not success:
                    continue
                fit_points.add(point)
            if fit_points.count >= 2:
                return splines.add(fit_points)

    raise RuntimeError('未対応の断面カーブ種類です。')


def project_inner_shell_section_to_sketch(sketch, inner_shell_body):
    projected_entities = sketch.intersectWithSketchPlane([inner_shell_body])
    projected_curves = []

    for entity in projected_entities:
        sketch_curve = adsk.fusion.SketchCurve.cast(entity)
        if sketch_curve:
            projected_curves.append(sketch_curve)

    for sketch_curve in projected_curves:
        clone_intersection_curve_as_sketch_geometry(sketch, sketch_curve)

    for sketch_curve in projected_curves:
        sketch_curve.deleteMe()


def project_body_section_to_sketch(sketch, body):
    projected_entities = sketch.intersectWithSketchPlane([body])
    projected_curves = []

    for entity in projected_entities:
        sketch_curve = adsk.fusion.SketchCurve.cast(entity)
        if sketch_curve:
            projected_curves.append(sketch_curve)

    for sketch_curve in projected_curves:
        clone_intersection_curve_as_sketch_geometry(sketch, sketch_curve)

    for sketch_curve in projected_curves:
        sketch_curve.deleteMe()


def get_profile_nearest_point(sketch, target_point):
    nearest_profile = None
    nearest_distance = None

    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        centroid = profile.areaProperties().centroid
        distance = math.hypot(
            centroid.x - target_point.x,
            centroid.y - target_point.y,
        )
        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_profile = profile

    if not nearest_profile:
        raise RuntimeError('外殻の押し出しプロファイルを取得できませんでした。')

    return nearest_profile


def is_sketch_point_within_profile_bounding_box(profile, target_point, tolerance_cm=1e-6):
    box = profile.boundingBox
    return (
        (box.minPoint.x - tolerance_cm) <= target_point.x <= (box.maxPoint.x + tolerance_cm)
        and (box.minPoint.y - tolerance_cm) <= target_point.y <= (box.maxPoint.y + tolerance_cm)
    )


def sample_sketch_curve_points_in_sketch_space(sketch_curve, sample_count=40):
    geometry = getattr(sketch_curve, 'geometry', None)
    if not geometry:
        geometry = get_curve_geometry(sketch_curve)
    if not geometry:
        raise RuntimeError('スケッチカーブのジオメトリを取得できませんでした。')

    evaluator = geometry.evaluator
    success, start_param, end_param = evaluator.getParameterExtents()
    if not success:
        raise RuntimeError('スケッチカーブのパラメータ範囲を取得できませんでした。')

    points = []
    for index in range(sample_count + 1):
        parameter = start_param + ((end_param - start_param) * index / sample_count)
        success, point = evaluator.getPointAtParameter(parameter)
        if success:
            points.append(point)

    if len(points) < 2:
        raise RuntimeError('スケッチカーブ上のサンプル点を取得できませんでした。')

    return points


def build_profile_loop_polyline(profile_loop, sample_count=40):
    polyline = []

    for curve_index in range(profile_loop.profileCurves.count):
        profile_curve = profile_loop.profileCurves.item(curve_index)
        sketch_curve = adsk.fusion.SketchCurve.cast(profile_curve.sketchEntity)
        if not sketch_curve:
            continue

        curve_points = sample_sketch_curve_points_in_sketch_space(
            sketch_curve,
            sample_count=sample_count,
        )
        if polyline:
            last_point = polyline[-1]
            forward_distance = get_point_distance(last_point, curve_points[0])
            reverse_distance = get_point_distance(last_point, curve_points[-1])
            if reverse_distance < forward_distance:
                curve_points.reverse()
            polyline.extend(curve_points[1:])
        else:
            polyline.extend(curve_points)

    if len(polyline) < 3:
        raise RuntimeError('プロファイルループのポリライン化に失敗しました。')

    if get_point_distance(polyline[0], polyline[-1]) > 1e-5:
        polyline.append(polyline[0])

    return polyline


def is_point_inside_polyline(target_point, polyline, tolerance_cm=1e-6):
    inside = False
    target_x = target_point.x
    target_y = target_point.y

    for index in range(len(polyline) - 1):
        point_a = polyline[index]
        point_b = polyline[index + 1]

        min_x = min(point_a.x, point_b.x) - tolerance_cm
        max_x = max(point_a.x, point_b.x) + tolerance_cm
        min_y = min(point_a.y, point_b.y) - tolerance_cm
        max_y = max(point_a.y, point_b.y) + tolerance_cm
        cross_value = (
            ((point_b.x - point_a.x) * (target_y - point_a.y))
            - ((point_b.y - point_a.y) * (target_x - point_a.x))
        )
        if abs(cross_value) <= tolerance_cm and min_x <= target_x <= max_x and min_y <= target_y <= max_y:
            return True

        intersects = ((point_a.y > target_y) != (point_b.y > target_y))
        if not intersects:
            continue

        x_at_target_y = point_a.x + (
            ((target_y - point_a.y) * (point_b.x - point_a.x))
            / (point_b.y - point_a.y)
        )
        if x_at_target_y >= target_x - tolerance_cm:
            inside = not inside

    return inside


def does_profile_contain_point(profile, target_point):
    if not is_sketch_point_within_profile_bounding_box(profile, target_point):
        return False

    inside_outer_loop = False

    for loop_index in range(profile.profileLoops.count):
        profile_loop = profile.profileLoops.item(loop_index)
        polyline = build_profile_loop_polyline(profile_loop)
        if not is_point_inside_polyline(target_point, polyline):
            continue
        if profile_loop.isOuter:
            inside_outer_loop = True
        else:
            return False

    return inside_outer_loop


def get_profile_containing_point(sketch, target_point):
    containing_profiles = []

    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        try:
            if does_profile_contain_point(profile, target_point):
                containing_profiles.append(profile)
        except RuntimeError:
            continue

    if not containing_profiles:
        raise RuntimeError('指定点を含むプロファイルを取得できませんでした。')

    if len(containing_profiles) == 1:
        return containing_profiles[0]

    return min(
        containing_profiles,
        key=lambda profile: profile.areaProperties().area,
    )


def get_smallest_profile(sketch):
    smallest_profile = None
    smallest_area = None

    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        area = profile.areaProperties().area
        if smallest_area is None or area < smallest_area:
            smallest_area = area
            smallest_profile = profile

    if not smallest_profile:
        raise RuntimeError('最小プロファイルを取得できませんでした。')

    return smallest_profile


def get_largest_profile(sketch):
    largest_profile = None
    largest_area = None

    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        area = profile.areaProperties().area
        if largest_area is None or area > largest_area:
            largest_area = area
            largest_profile = profile

    if not largest_profile:
        raise RuntimeError('最大プロファイルを取得できませんでした。')

    return largest_profile


def line_y_at_x(point_a_mm, point_b_mm, target_x_mm):
    x1_mm, y1_mm = point_a_mm
    x2_mm, y2_mm = point_b_mm

    if abs(x2_mm - x1_mm) <= 1e-9:
        raise RuntimeError('垂直線では y を一意に求められません。')

    ratio = (target_x_mm - x1_mm) / (x2_mm - x1_mm)
    return y1_mm + ((y2_mm - y1_mm) * ratio)


def line_circle_intersections(point_a_mm, point_b_mm, center_mm, radius_mm):
    ax_mm, ay_mm = point_a_mm
    bx_mm, by_mm = point_b_mm
    cx_mm, cy_mm = center_mm

    dx_mm = bx_mm - ax_mm
    dy_mm = by_mm - ay_mm
    fx_mm = ax_mm - cx_mm
    fy_mm = ay_mm - cy_mm

    a = (dx_mm * dx_mm) + (dy_mm * dy_mm)
    b = 2.0 * ((fx_mm * dx_mm) + (fy_mm * dy_mm))
    c = (fx_mm * fx_mm) + (fy_mm * fy_mm) - (radius_mm * radius_mm)

    discriminant = (b * b) - (4.0 * a * c)
    if discriminant < 0.0:
        raise RuntimeError('円と直線の交点を取得できませんでした。')

    sqrt_discriminant = math.sqrt(discriminant)
    intersections = []
    for sign in (-1.0, 1.0):
        t = (-b + (sign * sqrt_discriminant)) / (2.0 * a)
        intersections.append((
            ax_mm + (dx_mm * t),
            ay_mm + (dy_mm * t),
        ))

    return intersections


def get_sketch_point_mm_components(sketch_point):
    return (
        sketch_point.x * 10.0,
        sketch_point.y * 10.0,
    )


def get_distance_2d_mm(point_a_mm, point_b_mm):
    return math.hypot(
        point_a_mm[0] - point_b_mm[0],
        point_a_mm[1] - point_b_mm[1],
    )


def normalize_vector_2d_mm(vector_x_mm, vector_y_mm):
    length_mm = math.hypot(vector_x_mm, vector_y_mm)
    if length_mm <= 1e-9:
        raise RuntimeError('2D ベクトルを正規化できませんでした。')
    return (
        vector_x_mm / length_mm,
        vector_y_mm / length_mm,
    )


def scale_vector_2d_mm(vector_mm, scale):
    return (
        vector_mm[0] * scale,
        vector_mm[1] * scale,
    )


def add_vector_2d_mm(point_mm, vector_mm):
    return (
        point_mm[0] + vector_mm[0],
        point_mm[1] + vector_mm[1],
    )


def subtract_points_2d_mm(point_a_mm, point_b_mm):
    return (
        point_a_mm[0] - point_b_mm[0],
        point_a_mm[1] - point_b_mm[1],
    )


def dot_product_2d_mm(vector_a_mm, vector_b_mm):
    return (
        vector_a_mm[0] * vector_b_mm[0]
        + vector_a_mm[1] * vector_b_mm[1]
    )


def create_point_in_sketch_space_mm(x_mm, y_mm):
    return adsk.core.Point3D.create(
        mm_to_cm(x_mm),
        mm_to_cm(y_mm),
        0.0,
    )


def get_sketch_space_point_mm(sketch, point_mm):
    point = to_sketch_space(sketch, point_mm)
    return (
        point.x * 10.0,
        point.y * 10.0,
    )


def project_point_to_line_mm(point_mm, line_start_mm, line_end_mm):
    ax_mm, ay_mm = line_start_mm
    bx_mm, by_mm = line_end_mm
    px_mm, py_mm = point_mm
    dx_mm = bx_mm - ax_mm
    dy_mm = by_mm - ay_mm
    denominator = (dx_mm * dx_mm) + (dy_mm * dy_mm)
    if denominator <= 1e-9:
        raise RuntimeError('線分が退化しているため射影点を計算できませんでした。')

    t = (((px_mm - ax_mm) * dx_mm) + ((py_mm - ay_mm) * dy_mm)) / denominator
    return (
        ax_mm + (dx_mm * t),
        ay_mm + (dy_mm * t),
    )


def intersect_lines_2d_mm(line1_start_mm, line1_end_mm, line2_start_mm, line2_end_mm):
    x1, y1 = line1_start_mm
    x2, y2 = line1_end_mm
    x3, y3 = line2_start_mm
    x4, y4 = line2_end_mm

    denominator = ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))
    if abs(denominator) <= 1e-9:
        raise RuntimeError('2直線の交点を取得できませんでした。')

    determinant_1 = (x1 * y2) - (y1 * x2)
    determinant_2 = (x3 * y4) - (y3 * x4)
    intersection_x = (
        (determinant_1 * (x3 - x4)) - ((x1 - x2) * determinant_2)
    ) / denominator
    intersection_y = (
        (determinant_1 * (y3 - y4)) - ((y1 - y2) * determinant_2)
    ) / denominator
    return (intersection_x, intersection_y)


def tangent_points_from_external_point_to_circle_mm(point_mm, center_mm, radius_mm):
    px_mm, py_mm = point_mm
    cx_mm, cy_mm = center_mm
    dx_mm = px_mm - cx_mm
    dy_mm = py_mm - cy_mm
    distance_sq = (dx_mm * dx_mm) + (dy_mm * dy_mm)
    if distance_sq <= (radius_mm * radius_mm):
        raise RuntimeError('外点から円への接点を取得できませんでした。')

    scale = (radius_mm * radius_mm) / distance_sq
    offset = (radius_mm * math.sqrt(distance_sq - (radius_mm * radius_mm))) / distance_sq
    return [
        (
            cx_mm + (scale * dx_mm) - (offset * dy_mm),
            cy_mm + (scale * dy_mm) + (offset * dx_mm),
        ),
        (
            cx_mm + (scale * dx_mm) + (offset * dy_mm),
            cy_mm + (scale * dy_mm) - (offset * dx_mm),
        ),
    ]


def get_tangent_circle_center_between_lines_mm(
    line_vertex_mm,
    line_point_a_mm,
    line_point_b_mm,
    radius_mm,
):
    direction_a = normalize_vector_2d_mm(
        line_point_a_mm[0] - line_vertex_mm[0],
        line_point_a_mm[1] - line_vertex_mm[1],
    )
    direction_b = normalize_vector_2d_mm(
        line_point_b_mm[0] - line_vertex_mm[0],
        line_point_b_mm[1] - line_vertex_mm[1],
    )
    bisector = normalize_vector_2d_mm(
        direction_a[0] + direction_b[0],
        direction_a[1] + direction_b[1],
    )
    angle_cos = max(-1.0, min(1.0, dot_product_2d_mm(direction_a, direction_b)))
    sin_half = math.sqrt(max(0.0, (1.0 - angle_cos) / 2.0))
    if sin_half <= 1e-9:
        raise RuntimeError('接円中心を計算できませんでした。')

    distance_to_center_mm = radius_mm / sin_half
    return add_vector_2d_mm(
        line_vertex_mm,
        scale_vector_2d_mm(bisector, distance_to_center_mm),
    )


def point_on_circle_from_angle_mm(center_mm, radius_mm, angle_rad):
    return (
        center_mm[0] + (radius_mm * math.cos(angle_rad)),
        center_mm[1] + (radius_mm * math.sin(angle_rad)),
    )


def get_tangent_arc_midpoint_at_endpoint_mm(start_point_mm, tangent_point_mm, tangent_line_point_mm):
    tangent_direction_mm = subtract_points_2d_mm(
        tangent_line_point_mm,
        tangent_point_mm,
    )
    tangent_length_mm = math.hypot(
        tangent_direction_mm[0],
        tangent_direction_mm[1],
    )
    if tangent_length_mm <= 1e-9:
        raise RuntimeError('接線方向が退化しているため円弧中点を計算できませんでした。')

    chord_direction_mm = subtract_points_2d_mm(
        tangent_point_mm,
        start_point_mm,
    )
    chord_length_mm = math.hypot(
        chord_direction_mm[0],
        chord_direction_mm[1],
    )
    if chord_length_mm <= 1e-9:
        raise RuntimeError('円弧端点が重複しているため円弧中点を計算できませんでした。')

    chord_midpoint_mm = get_midpoint_mm(start_point_mm, tangent_point_mm)
    center_mm = intersect_lines_2d_mm(
        tangent_point_mm,
        (
            tangent_point_mm[0] - tangent_direction_mm[1],
            tangent_point_mm[1] + tangent_direction_mm[0],
        ),
        chord_midpoint_mm,
        (
            chord_midpoint_mm[0] - chord_direction_mm[1],
            chord_midpoint_mm[1] + chord_direction_mm[0],
        ),
    )
    radius_mm = get_distance_2d_mm(center_mm, start_point_mm)
    start_angle_rad = angle_for_point_on_circle_mm(center_mm, start_point_mm)
    end_angle_rad = angle_for_point_on_circle_mm(center_mm, tangent_point_mm)
    midpoint_angle = midpoint_angle_rad(start_angle_rad, end_angle_rad)
    return point_on_circle_from_angle_mm(center_mm, radius_mm, midpoint_angle)


def angle_for_point_on_circle_mm(center_mm, point_mm):
    return math.atan2(
        point_mm[1] - center_mm[1],
        point_mm[0] - center_mm[0],
    )


def normalize_angle_rad(angle_rad):
    while angle_rad <= -math.pi:
        angle_rad += math.tau
    while angle_rad > math.pi:
        angle_rad -= math.tau
    return angle_rad


def midpoint_angle_rad(start_angle_rad, end_angle_rad, via_angle_rad=None):
    delta = normalize_angle_rad(end_angle_rad - start_angle_rad)
    if via_angle_rad is not None:
        via_delta = normalize_angle_rad(via_angle_rad - start_angle_rad)
        if delta >= 0.0 and not (0.0 <= via_delta <= delta):
            delta -= math.tau
        elif delta < 0.0 and not (delta <= via_delta <= 0.0):
            delta += math.tau
    return start_angle_rad + (delta / 2.0)


def offset_point_from_circle(center_mm, point_mm, offset_mm):
    cx_mm, cy_mm = center_mm
    px_mm, py_mm = point_mm

    vector_x_mm = px_mm - cx_mm
    vector_y_mm = py_mm - cy_mm
    vector_length_mm = math.hypot(vector_x_mm, vector_y_mm)
    if vector_length_mm <= 1e-9:
        raise RuntimeError('円の中心と同一点はオフセットできません。')

    scale = (vector_length_mm + offset_mm) / vector_length_mm
    return (
        cx_mm + (vector_x_mm * scale),
        cy_mm + (vector_y_mm * scale),
    )


def offset_line_on_xz_plane(point_a_mm, point_b_mm, offset_mm):
    ax_mm, _, az_mm = point_a_mm
    bx_mm, _, bz_mm = point_b_mm

    direction_x_mm = bx_mm - ax_mm
    direction_z_mm = bz_mm - az_mm
    direction_length_mm = math.hypot(direction_x_mm, direction_z_mm)
    if direction_length_mm <= 1e-9:
        raise RuntimeError('同一点からはオフセット線を作成できません。')

    normal_x_mm = -direction_z_mm / direction_length_mm
    normal_z_mm = direction_x_mm / direction_length_mm

    return (
        (
            ax_mm + (normal_x_mm * offset_mm),
            point_a_mm[1],
            az_mm + (normal_z_mm * offset_mm),
        ),
        (
            bx_mm + (normal_x_mm * offset_mm),
            point_b_mm[1],
            bz_mm + (normal_z_mm * offset_mm),
        ),
    )


def vertical_line_circle_intersections(center_mm, radius_mm, x_mm):
    cx_mm, cy_mm = center_mm
    offset_x_mm = x_mm - cx_mm
    remaining = (radius_mm * radius_mm) - (offset_x_mm * offset_x_mm)
    if remaining < 0.0:
        raise RuntimeError('円と鉛直線の交点を取得できませんでした。')

    offset_y_mm = math.sqrt(max(remaining, 0.0))
    return [
        (x_mm, cy_mm - offset_y_mm),
        (x_mm, cy_mm + offset_y_mm),
    ]


def build_outer_shell_reference_points(params):
    clearance_mm = params.get('clearance_mm', naming.DEFAULT_OUTER_SHELL_PARAMS['clearance_mm'])

    point_a_mm = (-5.0, -23.0, 0.0)
    point_b_mm = (-5.0, -35.0, 0.0)
    point_c_mm = (-90.0, -35.0, 0.0)
    point_d_mm = (-90.0, 35.0, 0.0)
    point_e_mm = (-51.8, 35.0, 0.0)
    point_f_mm = (-51.8, 29.0, 0.0)

    point_h_y_mm = line_y_at_x(
        INNER_SHELL_TOP_EDGE_START_MM,
        INNER_SHELL_TOP_EDGE_END_MM,
        point_f_mm[0]
    )
    point_h_mm = (point_f_mm[0], point_h_y_mm, 0.0)

    point_i_mm = (point_a_mm[0], INNER_SHELL_LOWER_STOP_TOP_Y_MM, 0.0)
    point_j_mm = point_h_mm

    top_line_intersections = line_circle_intersections(
        INNER_SHELL_TOP_EDGE_START_MM,
        INNER_SHELL_TOP_EDGE_END_MM,
        OUTER_CIRCLE_CENTER_MM,
        OUTER_CIRCLE_RADIUS_MM,
    )
    point_k_mm = max(top_line_intersections, key=lambda point: point[0])
    point_l_mm = offset_point_from_circle(
        OUTER_CIRCLE_CENTER_MM,
        point_k_mm,
        clearance_mm,
    )
    point_m_mm = (
        point_j_mm[0] - 12.0,
        line_y_at_x(
            INNER_SHELL_TOP_EDGE_START_MM,
            INNER_SHELL_TOP_EDGE_END_MM,
            point_j_mm[0] - 12.0
        ) + clearance_mm,
        0.0,
    )
    point_n_mm = (
        -24.0,
        -26.2,
        0.0,
    )

    return {
        'A': point_a_mm,
        'B': point_b_mm,
        'C': point_c_mm,
        'D': point_d_mm,
        'E': point_e_mm,
        'F': point_f_mm,
        'H': point_h_mm,
        'I': point_i_mm,
        'J': point_j_mm,
        'K': (point_k_mm[0], point_k_mm[1], 0.0),
        'L': (point_l_mm[0], point_l_mm[1], 0.0),
        'M': point_m_mm,
        'N': point_n_mm,
    }


def create_outer_shell_sketch(root_comp, inner_shell_body, params):
    sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    sketch.name = OUTER_SHELL_BASE_STRUCTURE_SKETCH_NAME

    points = build_outer_shell_reference_points(params)
    lines = sketch.sketchCurves.sketchLines

    project_inner_shell_section_to_sketch(sketch, inner_shell_body)

    line_segments = [
        ('B', 'I'),
        ('B', 'C'),
        ('C', 'D'),
        ('D', 'E'),
        ('E', 'J'),
    ]

    for start_name, end_name in line_segments:
        lines.addByTwoPoints(
            create_point_mm(*points[start_name]),
            create_point_mm(*points[end_name]),
        )

    for point_name in ('A', 'B', 'C', 'D', 'E', 'F', 'H', 'I', 'J'):
        create_sketch_point(sketch, points[point_name])

    return sketch


def cut_body_with_inner_shell(root_comp, target_body, inner_shell_body):
    tool_body_collection = adsk.core.ObjectCollection.create()
    tool_body_collection.add(inner_shell_body)

    combine_features = root_comp.features.combineFeatures
    combine_input = combine_features.createInput(target_body, tool_body_collection)
    combine_input.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    combine_input.isKeepToolBodies = True
    combine_features.add(combine_input)


def cut_target_body_with_tool_bodies(root_comp, target_body, tool_bodies, keep_tool_bodies=False):
    if target_body is None:
        raise RuntimeError('target_body is required.')

    if not tool_bodies:
        return target_body

    tool_body_collection = adsk.core.ObjectCollection.create()
    for tool_body in tool_bodies:
        if tool_body is not None:
            tool_body_collection.add(tool_body)

    if tool_body_collection.count == 0:
        return target_body

    combine_features = root_comp.features.combineFeatures
    combine_input = combine_features.createInput(target_body, tool_body_collection)
    combine_input.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    combine_input.isKeepToolBodies = keep_tool_bodies
    combine_features.add(combine_input)
    return target_body


def join_tool_bodies_into_target(root_comp, target_body, tool_bodies, keep_tool_bodies=False):
    if target_body is None:
        raise RuntimeError('target_body is required.')

    if not tool_bodies:
        return target_body

    tool_body_collection = adsk.core.ObjectCollection.create()
    for tool_body in tool_bodies:
        if tool_body is not None:
            tool_body_collection.add(tool_body)

    if tool_body_collection.count == 0:
        return target_body

    combine_features = root_comp.features.combineFeatures
    combine_input = combine_features.createInput(target_body, tool_body_collection)
    combine_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    combine_input.isKeepToolBodies = keep_tool_bodies
    combine_features.add(combine_input)
    return target_body


def extrude_outer_shell_profile(root_comp, sketch, inner_shell_body):
    target_point = create_point_mm(-80.0, 0.0, 0.0)
    profile = get_profile_nearest_point(sketch, target_point)

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    distance_value = adsk.core.ValueInput.createByReal(mm_to_cm(3.0))
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        adsk.fusion.ExtentDirections.NegativeExtentDirection,
    )

    feature = extrudes.add(extrude_input)
    body = get_body_from_feature(feature)
    cut_body_with_inner_shell(root_comp, body, inner_shell_body)
    helpers.set_body_identity(body, naming.BODY_OUTER_SHELL)
    offset_contact_faces(root_comp, body, inner_shell_body)
    return body


def add_bottom_outer_face(root_comp, outer_shell_body):
    app = adsk.core.Application.get()
    tolerance_cm = max(app.pointTolerance, 1e-5)
    face = find_face_through_point_on_constant_axis(
        outer_shell_body,
        OUTER_SHELL_BOTTOM_OUTER_FACE_POINT_MM,
        'z',
        tolerance_cm,
    )
    extrude_xy_face_in_negative_z(
        root_comp,
        face,
        OUTER_SHELL_BOTTOM_OUTER_EXTRUDE_DISTANCE_MM,
        tolerance_cm,
    )


def add_outer_perimeter_face(root_comp, outer_shell_body):
    app = adsk.core.Application.get()
    tolerance_cm = max(app.pointTolerance, 1e-5)
    face = find_largest_xy_face_at_z_covering_point(
        outer_shell_body,
        OUTER_SHELL_OUTER_PERIMETER_FACE_POINT_MM,
        tolerance_cm,
    )
    extrude_xy_face_in_positive_z(
        root_comp,
        face,
        OUTER_SHELL_OUTER_PERIMETER_EXTRUDE_DISTANCE_MM,
        tolerance_cm,
    )


def create_bottom_outer_face_sketch(root_comp, outer_shell_body):
    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(
        root_comp.xYConstructionPlane,
        adsk.core.ValueInput.createByReal(mm_to_cm(OUTER_SHELL_BOTTOM_OUTER_SKETCH_Z_MM)),
    )
    sketch_plane = planes.add(plane_input)

    sketch = root_comp.sketches.add(sketch_plane)
    sketch.name = OUTER_SHELL_BOTTOM_OUTER_SKETCH_NAME

    circles = sketch.sketchCurves.sketchCircles
    lines = sketch.sketchCurves.sketchLines

    circle_center_mm = (0.0, 5.0, 0.0)
    circle_point_mm = (-5.0, -23.3, 0.0)
    b_start_mm = (-25.0, 30.0, 0.0)
    b_pass_mm = (-25.0, 14.0, 0.0)
    c_pass_mm = (-51.8, 28.0, 0.0)
    d_start_mm = (-51.8, 35.0, 0.0)
    d_pass_mm = (-51.8, 28.0, 0.0)
    f_point_mm = (-5.0, -35.0, 0.0)
    g_point_mm = (-90.0, -35.0, 0.0)
    h_point_mm = (-90.0, 35.0, 0.0)
    i_point_mm = (-5.0, -34.0, 0.0)
    circle_radius_mm = math.hypot(
        circle_point_mm[0] - circle_center_mm[0],
        circle_point_mm[1] - circle_center_mm[1],
    )
    point_e_xy_mm = min(
        vertical_line_circle_intersections(
            (circle_center_mm[0], circle_center_mm[1]),
            circle_radius_mm,
            b_start_mm[0],
        ),
        key=lambda point: math.hypot(point[0] - b_start_mm[0], point[1] - b_start_mm[1]),
    )
    point_e_mm = (point_e_xy_mm[0], point_e_xy_mm[1], 0.0)
    point_j_xy_mm = min(
        vertical_line_circle_intersections(
            (circle_center_mm[0], circle_center_mm[1]),
            circle_radius_mm,
            i_point_mm[0],
        ),
        key=lambda point: math.hypot(point[0] - i_point_mm[0], point[1] - i_point_mm[1]),
    )
    point_j_mm = (point_j_xy_mm[0], point_j_xy_mm[1], 0.0)

    circles.addByCenterRadius(
        create_point_mm(*circle_center_mm),
        circle_radius_mm / 10.0,
    )
    lines.addByTwoPoints(
        create_point_mm(*b_start_mm),
        create_point_mm(*b_pass_mm),
    )
    lines.addByTwoPoints(
        create_point_mm(*b_start_mm),
        create_point_mm(*c_pass_mm),
    )
    lines.addByTwoPoints(
        create_point_mm(*d_start_mm),
        create_point_mm(*d_pass_mm),
    )
    lines.addByTwoPoints(
        create_point_mm(*f_point_mm),
        create_point_mm(*g_point_mm),
    )
    lines.addByTwoPoints(
        create_point_mm(*g_point_mm),
        create_point_mm(*h_point_mm),
    )
    lines.addByTwoPoints(
        create_point_mm(*h_point_mm),
        create_point_mm(*d_start_mm),
    )
    lines.addByTwoPoints(
        create_point_mm(*f_point_mm),
        create_point_mm(*point_j_mm),
    )

    for point_mm in (
        circle_center_mm,
        circle_point_mm,
        b_start_mm,
        b_pass_mm,
        c_pass_mm,
        d_start_mm,
        d_pass_mm,
        f_point_mm,
        g_point_mm,
        h_point_mm,
        i_point_mm,
        point_e_mm,
        point_j_mm,
    ):
        create_sketch_point(sketch, point_mm)

    return sketch


def create_outer_perimeter_reference_circle_sketch(root_comp):
    sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    sketch.name = OUTER_SHELL_REFERENCE_CIRCLE_SKETCH_NAME
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        create_point_mm(*OUTER_SHELL_REFERENCE_CIRCLE_CENTER_MM),
        mm_to_cm(OUTER_SHELL_REFERENCE_CIRCLE_RADIUS_MM),
    )
    create_sketch_point(sketch, OUTER_SHELL_REFERENCE_CIRCLE_CENTER_MM)
    return sketch


def cut_outer_perimeter_reference_circle(root_comp, sketch, outer_shell_body, inner_shell_body=None):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    current_inner_shell_body = inner_shell_body
    if current_inner_shell_body is None:
        current_inner_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_INNER_SHELL,
        )

    moved_inner_shell_body = None
    if current_inner_shell_body is not None:
        moved_inner_shell_body = move_body_by_translation(
            root_comp,
            current_inner_shell_body,
            x_mm=INNER_SHELL_TEMP_MOVE_X_MM,
        )

    profile = get_profile_nearest_point(
        sketch,
        create_point_mm(*OUTER_SHELL_REFERENCE_CIRCLE_CENTER_MM),
    )

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation
    )

    extrude_input.participantBodies = [current_outer_shell_body]

    distance_value = adsk.core.ValueInput.createByReal(mm_to_cm(40.0))
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    extrudes.add(extrude_input)

    if moved_inner_shell_body is not None:
        move_body_by_translation(
            root_comp,
            moved_inner_shell_body,
            x_mm=-INNER_SHELL_TEMP_MOVE_X_MM,
        )


def add_outer_perimeter_reference_circle_fillet(root_comp, outer_shell_body):
    _ = root_comp
    _ = outer_shell_body
    # 外周円切り抜き後の z=0 mm 円弧エッジ R6.0 フィレットは適用しない。
    return


def extrude_bottom_outer_region(root_comp, sketch):
    profile = get_profile_nearest_point(
        sketch,
        create_point_mm(*OUTER_SHELL_BOTTOM_OUTER_REGION_TARGET_MM),
    )

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(abs(OUTER_SHELL_BOTTOM_OUTER_REGION_EXTRUDE_DISTANCE_MM))
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        adsk.fusion.ExtentDirections.NegativeExtentDirection,
    )
    extrudes.add(extrude_input)


def create_outer_shell_bottom_outer_slope_sketch(root_comp):
    sketch_plane = create_offset_plane_from_xy(
        root_comp,
        OUTER_SHELL_BOTTOM_OUTER_SLOPE_SKETCH_Z_MM,
    )
    sketch = root_comp.sketches.add(sketch_plane)
    sketch.name = OUTER_SHELL_BOTTOM_OUTER_SLOPE_SKETCH_NAME

    points_mm = OUTER_SHELL_BOTTOM_OUTER_SLOPE_POINTS_MM
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs

    local_points_mm = {
        name: (point_mm[0], point_mm[1], 0.0)
        for name, point_mm in points_mm.items()
    }

    circle_center_mm = (
        OUTER_SHELL_BOTTOM_OUTER_SLOPE_CIRCLE_CENTER_MM[0],
        OUTER_SHELL_BOTTOM_OUTER_SLOPE_CIRCLE_CENTER_MM[1],
    )
    radius_mm = OUTER_SHELL_BOTTOM_OUTER_SLOPE_CIRCLE_DIAMETER_MM / 2.0
    point_h_on_circle_xy_mm = offset_point_from_circle(
        circle_center_mm,
        (points_mm['H'][0], points_mm['H'][1]),
        radius_mm - get_distance_2d_mm(circle_center_mm, (points_mm['H'][0], points_mm['H'][1])),
    )
    point_h_on_circle_mm = (
        point_h_on_circle_xy_mm[0],
        point_h_on_circle_xy_mm[1],
        0.0,
    )
    angle_h_rad = angle_for_point_on_circle_mm(circle_center_mm, point_h_on_circle_xy_mm)
    angle_f_prime_rad = angle_for_point_on_circle_mm(
        circle_center_mm,
        (local_points_mm['F_PRIME'][0], local_points_mm['F_PRIME'][1]),
    )
    arc_midpoint_mm = point_on_circle_from_angle_mm(
        circle_center_mm,
        radius_mm,
        midpoint_angle_rad(angle_h_rad, angle_f_prime_rad),
    )
    arc_midpoint_model_mm = (
        arc_midpoint_mm[0],
        arc_midpoint_mm[1],
        0.0,
    )

    lines.addByTwoPoints(
        create_point_in_sketch_space_mm(local_points_mm['A'][0], local_points_mm['A'][1]),
        create_point_in_sketch_space_mm(point_h_on_circle_mm[0], point_h_on_circle_mm[1]),
    )
    arcs.addByThreePoints(
        create_point_in_sketch_space_mm(point_h_on_circle_mm[0], point_h_on_circle_mm[1]),
        create_point_in_sketch_space_mm(arc_midpoint_model_mm[0], arc_midpoint_model_mm[1]),
        create_point_in_sketch_space_mm(local_points_mm['F_PRIME'][0], local_points_mm['F_PRIME'][1]),
    )
    lines.addByTwoPoints(
        create_point_in_sketch_space_mm(local_points_mm['F_PRIME'][0], local_points_mm['F_PRIME'][1]),
        create_point_in_sketch_space_mm(local_points_mm['G'][0], local_points_mm['G'][1]),
    )
    lines.addByTwoPoints(
        create_point_in_sketch_space_mm(local_points_mm['G'][0], local_points_mm['G'][1]),
        create_point_in_sketch_space_mm(local_points_mm['C'][0], local_points_mm['C'][1]),
    )
    lines.addByTwoPoints(
        create_point_in_sketch_space_mm(local_points_mm['C'][0], local_points_mm['C'][1]),
        create_point_in_sketch_space_mm(local_points_mm['D'][0], local_points_mm['D'][1]),
    )
    lines.addByTwoPoints(
        create_point_in_sketch_space_mm(local_points_mm['D'][0], local_points_mm['D'][1]),
        create_point_in_sketch_space_mm(local_points_mm['E'][0], local_points_mm['E'][1]),
    )
    lines.addByTwoPoints(
        create_point_in_sketch_space_mm(local_points_mm['E'][0], local_points_mm['E'][1]),
        create_point_in_sketch_space_mm(local_points_mm['A'][0], local_points_mm['A'][1]),
    )

    for point_mm in (
        local_points_mm['A'],
        point_h_on_circle_mm,
        local_points_mm['F_PRIME'],
        local_points_mm['G'],
        local_points_mm['C'],
        local_points_mm['D'],
        local_points_mm['E'],
        (OUTER_SHELL_BOTTOM_OUTER_SLOPE_CIRCLE_CENTER_MM[0], OUTER_SHELL_BOTTOM_OUTER_SLOPE_CIRCLE_CENTER_MM[1], 0.0),
        arc_midpoint_model_mm,
    ):
        sketch.sketchPoints.add(create_point_in_sketch_space_mm(point_mm[0], point_mm[1]))

    return sketch


def extrude_outer_shell_bottom_outer_slope_region(root_comp, sketch):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    profile = None
    for target_point_mm in OUTER_SHELL_BOTTOM_OUTER_SLOPE_PROFILE_FALLBACK_TARGETS_MM:
        try:
            profile = get_profile_containing_point(
                sketch,
                to_sketch_space(sketch, target_point_mm),
            )
            break
        except RuntimeError:
            continue
    if profile is None:
        profile = get_profile_nearest_point(
            sketch,
            to_sketch_space(sketch, OUTER_SHELL_BOTTOM_OUTER_SLOPE_PROFILE_TARGET_MM),
        )

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    if current_outer_shell_body is not None:
        extrude_input.participantBodies = [current_outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(OUTER_SHELL_BOTTOM_OUTER_SLOPE_EXTRUDE_DISTANCE_MM)
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        adsk.fusion.ExtentDirections.NegativeExtentDirection,
    )
    extrudes.add(extrude_input)


def create_outer_shell_bottom_outer_slope_y_cut_sketch(root_comp):
    sketch_plane = create_offset_plane_from_xz(
        root_comp,
        OUTER_SHELL_BOTTOM_OUTER_SLOPE_Y_CUT_POINTS_MM['I'][1],
        OUTER_SHELL_BOTTOM_OUTER_SLOPE_Y_CUT_SKETCH_NAME,
    )
    sketch = root_comp.sketches.add(sketch_plane)
    sketch.name = OUTER_SHELL_BOTTOM_OUTER_SLOPE_Y_CUT_SKETCH_NAME

    sketch_points = add_model_points_to_sketch(
        sketch,
        OUTER_SHELL_BOTTOM_OUTER_SLOPE_Y_CUT_POINTS_MM,
    )
    add_closed_polyline_to_sketch(sketch, sketch_points, ['I', 'J', 'L', 'K'])
    return sketch


def create_outer_shell_bottom_outer_slope_triangle_cut_sketch(root_comp):
    triangle_points_mm = OUTER_SHELL_BOTTOM_OUTER_SLOPE_TRIANGLE_POINTS_MM
    plane = create_plane_by_three_points(
        root_comp,
        triangle_points_mm['J'],
        triangle_points_mm['L'],
        triangle_points_mm['O'],
        OUTER_SHELL_BOTTOM_OUTER_SLOPE_TRIANGLE_CUT_SKETCH_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_BOTTOM_OUTER_SLOPE_TRIANGLE_CUT_SKETCH_NAME

    plane_geometry = adsk.core.Plane.cast(plane.geometry)
    if not plane_geometry:
        raise RuntimeError('外殻底部外側斜面 三角カット平面のジオメトリを取得できませんでした。')

    projected_points_mm = {}
    for name, point_mm in triangle_points_mm.items():
        point = create_point_mm(*point_mm)
        signed_distance = get_signed_distance_to_plane(plane_geometry, point)
        normal = plane_geometry.normal
        projected_points_mm[name] = (
            point_mm[0] - (normal.x * signed_distance * 10.0),
            point_mm[1] - (normal.y * signed_distance * 10.0),
            point_mm[2] - (normal.z * signed_distance * 10.0),
        )

    sketch_points = add_model_points_to_sketch(
        sketch,
        projected_points_mm,
    )
    add_closed_polyline_to_sketch(sketch, sketch_points, ['J', 'L', 'M', 'O'])
    return sketch


def cut_profile_via_negative_y_sweep(
    root_comp,
    sketch,
    profile,
    outer_shell_body,
    cut_distance_mm,
    inner_shell_body=None,
):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    current_inner_shell_body = inner_shell_body
    if current_inner_shell_body is None:
        current_inner_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_INNER_SHELL,
        )

    moved_inner_shell_body = None
    if current_inner_shell_body is not None:
        moved_inner_shell_body = move_body_by_translation(
            root_comp,
            current_inner_shell_body,
            x_mm=INNER_SHELL_TEMP_MOVE_X_MM,
        )

    try:
        current_outer_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_OUTER_SHELL,
        ) or current_outer_shell_body

        centroid = sketch.sketchToModelSpace(profile.areaProperties().centroid)
        path_plane = create_offset_plane_from_yz(root_comp, centroid.x * 10.0)
        path_sketch = root_comp.sketches.add(path_plane)

        start_point = path_sketch.modelToSketchSpace(centroid)
        end_point = path_sketch.modelToSketchSpace(
            adsk.core.Point3D.create(
                centroid.x,
                centroid.y - mm_to_cm(cut_distance_mm),
                centroid.z,
            )
        )
        path_line = path_sketch.sketchCurves.sketchLines.addByTwoPoints(
            start_point,
            end_point,
        )
        path = root_comp.features.createPath(path_line)

        sweeps = root_comp.features.sweepFeatures
        sweep_input = sweeps.createInput(
            profile,
            path,
            adsk.fusion.FeatureOperations.CutFeatureOperation,
        )
        sweep_input.participantBodies = [current_outer_shell_body]
        sweeps.add(sweep_input)
    finally:
        if moved_inner_shell_body is not None:
            move_body_by_translation(
                root_comp,
                moved_inner_shell_body,
                x_mm=-INNER_SHELL_TEMP_MOVE_X_MM,
            )


def create_body_via_negative_y_sweep(root_comp, sketch, profile, distance_mm):
    centroid = sketch.sketchToModelSpace(profile.areaProperties().centroid)
    path_plane = create_offset_plane_from_yz(root_comp, centroid.x * 10.0)
    path_sketch = root_comp.sketches.add(path_plane)

    start_point = path_sketch.modelToSketchSpace(centroid)
    end_point = path_sketch.modelToSketchSpace(
        adsk.core.Point3D.create(
            centroid.x,
            centroid.y - mm_to_cm(distance_mm),
            centroid.z,
        )
    )
    path_line = path_sketch.sketchCurves.sketchLines.addByTwoPoints(
        start_point,
        end_point,
    )
    path = root_comp.features.createPath(path_line)

    sweeps = root_comp.features.sweepFeatures
    sweep_input = sweeps.createInput(
        profile,
        path,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    )
    feature = sweeps.add(sweep_input)
    return get_body_from_feature(feature)


def create_body_via_positive_y_sweep(root_comp, sketch, profile, distance_mm):
    centroid = sketch.sketchToModelSpace(profile.areaProperties().centroid)
    path_plane = create_offset_plane_from_yz(root_comp, centroid.x * 10.0)
    path_sketch = root_comp.sketches.add(path_plane)

    start_point = path_sketch.modelToSketchSpace(centroid)
    end_point = path_sketch.modelToSketchSpace(
        adsk.core.Point3D.create(
            centroid.x,
            centroid.y + mm_to_cm(distance_mm),
            centroid.z,
        )
    )
    path_line = path_sketch.sketchCurves.sketchLines.addByTwoPoints(
        start_point,
        end_point,
    )
    path = root_comp.features.createPath(path_line)

    sweeps = root_comp.features.sweepFeatures
    sweep_input = sweeps.createInput(
        profile,
        path,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    )
    feature = sweeps.add(sweep_input)
    return get_body_from_feature(feature)


def extrude_outer_shell_bottom_outer_slope(root_comp, outer_shell_body):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    ) or outer_shell_body

    slope_sketch = create_outer_shell_bottom_outer_slope_sketch(root_comp)
    extrude_outer_shell_bottom_outer_slope_region(root_comp, slope_sketch)

    return helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    ) or current_outer_shell_body


def cut_outer_shell_bottom_outer_slope_regions(root_comp, outer_shell_body, inner_shell_body=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    ) or outer_shell_body

    current_inner_shell_body = inner_shell_body
    if current_inner_shell_body is None:
        current_inner_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_INNER_SHELL,
        )

    moved_inner_shell_body = None
    if current_inner_shell_body is not None:
        moved_inner_shell_body = move_body_by_translation(
            root_comp,
            current_inner_shell_body,
            x_mm=INNER_SHELL_TEMP_MOVE_X_MM,
        )

    try:
        current_outer_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_OUTER_SHELL,
        ) or current_outer_shell_body

        y_cut_sketch = create_outer_shell_bottom_outer_slope_y_cut_sketch(root_comp)
        y_cut_profile = get_profile_containing_point(
            y_cut_sketch,
            to_sketch_space(y_cut_sketch, OUTER_SHELL_BOTTOM_OUTER_SLOPE_Y_CUT_PROFILE_TARGET_MM),
        )
        y_cut_body = create_body_via_positive_y_sweep(
            root_comp,
            y_cut_sketch,
            y_cut_profile,
            OUTER_SHELL_BOTTOM_OUTER_SLOPE_Y_CUT_DISTANCE_MM,
        )
        current_outer_shell_body = cut_target_body_with_tool_bodies(
            root_comp,
            current_outer_shell_body,
            [y_cut_body],
        )

        current_outer_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_OUTER_SHELL,
        ) or current_outer_shell_body
        triangle_cut_sketch = create_outer_shell_bottom_outer_slope_triangle_cut_sketch(root_comp)
        triangle_cut_profile = get_largest_profile(triangle_cut_sketch)
        triangle_cut_body = create_body_via_positive_y_sweep(
            root_comp,
            triangle_cut_sketch,
            triangle_cut_profile,
            OUTER_SHELL_BOTTOM_OUTER_SLOPE_TRIANGLE_CUT_DISTANCE_MM,
        )
        current_outer_shell_body = cut_target_body_with_tool_bodies(
            root_comp,
            current_outer_shell_body,
            [triangle_cut_body],
        )
    finally:
        if moved_inner_shell_body is not None:
            move_body_by_translation(
                root_comp,
                moved_inner_shell_body,
                x_mm=-INNER_SHELL_TEMP_MOVE_X_MM,
            )

    return helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    ) or current_outer_shell_body


def find_arc_edge_near_points_on_xy_plane(body, reference_points_mm, z_value_mm, tolerance_cm=1e-5):
    target_points = [create_point_mm(*point_mm) for point_mm in reference_points_mm]
    target_z = mm_to_cm(z_value_mm)
    candidate_edge = None
    candidate_score = None

    for edge in body.edges:
        geometry = edge.geometry
        circle = adsk.core.Circle3D.cast(geometry)
        arc = adsk.core.Arc3D.cast(geometry)

        if circle:
            center = circle.center
            normal = circle.normal
        elif arc:
            center = arc.center
            normal = arc.normal
        else:
            continue

        if abs(center.z - target_z) > tolerance_cm:
            continue
        if abs(normal.x) > tolerance_cm or abs(normal.y) > tolerance_cm:
            continue

        try:
            score = sum(get_nearest_distance_to_edge(edge, point) for point in target_points)
        except RuntimeError:
            continue
        if candidate_score is None or score < candidate_score:
            candidate_score = score
            candidate_edge = edge

    if not candidate_edge:
        raise RuntimeError('指定条件に一致する円弧エッジを取得できませんでした。')

    return candidate_edge


def apply_constant_radius_fillet(root_comp, edge, radius_mm, tangent_chain=True):
    return apply_constant_radius_fillets(
        root_comp,
        [edge],
        radius_mm,
        tangent_chain=tangent_chain,
    )


def apply_constant_radius_fillets(root_comp, edges, radius_mm, tangent_chain=True):
    fillets = root_comp.features.filletFeatures
    fillet_input = fillets.createInput()
    edge_collection = adsk.core.ObjectCollection.create()
    for edge in edges:
        edge_collection.add(edge)

    radius_value = adsk.core.ValueInput.createByReal(mm_to_cm(radius_mm))
    fillet_input.addConstantRadiusEdgeSet(edge_collection, radius_value, tangent_chain)

    return fillets.add(fillet_input)


def find_lid_slope_face(root_comp, inner_shell_body=None):
    if inner_shell_body is None:
        inner_shell_body = helpers.find_body_by_name_or_attribute(root_comp, naming.BODY_INNER_SHELL)
    lid_slope_face = None

    if inner_shell_body is not None:
        try:
            lid_slope_face = find_face_by_named_attribute(
                inner_shell_body,
                INNER_SHELL_LID_SLOPE_FACE_NAME,
            )
        except RuntimeError:
            lid_slope_face = None

        if lid_slope_face is None:
            try:
                lid_slope_face = find_inner_shell_lid_slope_face(inner_shell_body)
            except RuntimeError:
                lid_slope_face = None

        if lid_slope_face is None:
            try:
                lid_slope_face = find_best_planar_face_near_reference_points(
                    inner_shell_body,
                    INNER_SHELL_LID_SLOPE_REFERENCE_POINTS_MM,
                )
            except RuntimeError:
                lid_slope_face = None

    if lid_slope_face is None:
        try:
            _, lid_slope_face = find_body_face_by_named_attribute(
                root_comp,
                INNER_SHELL_LID_SLOPE_FACE_NAME,
            )
        except RuntimeError:
            if inner_shell_body is not None:
                lid_slope_face = find_best_planar_face_near_reference_points(
                    inner_shell_body,
                    INNER_SHELL_LID_SLOPE_REFERENCE_POINTS_MM,
                )
            else:
                raise

    return lid_slope_face


def create_offset_plane_from_lid_slope(
    root_comp,
    plane_name,
    offset_mm,
    inner_shell_body=None,
):
    existing_plane = helpers.find_construction_plane_by_name_or_attribute(
        root_comp,
        plane_name,
    )
    if existing_plane is not None:
        return existing_plane

    lid_slope_face = find_lid_slope_face(root_comp, inner_shell_body)
    if lid_slope_face is None:
        raise RuntimeError('内殻蓋部斜面を取得できませんでした。')

    geometry = adsk.core.Plane.cast(lid_slope_face.geometry)
    if not geometry:
        raise RuntimeError('内殻蓋部斜面の平面ジオメトリを取得できませんでした。')

    normal = geometry.normal
    offset_value_cm = mm_to_cm(offset_mm)
    if normal.z > 0.0:
        offset_value_cm *= -1.0

    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(
        lid_slope_face,
        adsk.core.ValueInput.createByReal(offset_value_cm),
    )
    plane = planes.add(plane_input)
    plane.name = plane_name
    helpers.add_named_attribute(plane, plane_name)
    return plane


def create_lid_inner_split_plane(root_comp, inner_shell_body=None):
    return create_offset_plane_from_lid_slope(
        root_comp,
        OUTER_SHELL_LID_INNER_PLANE_NAME,
        OUTER_SHELL_LID_INNER_PLANE_Z_OFFSET_MM,
        inner_shell_body=inner_shell_body,
    )


def create_lid_gap_plane(root_comp, inner_shell_body=None):
    lid_inner_plane = create_lid_inner_split_plane(root_comp, inner_shell_body)
    geometry = adsk.core.Plane.cast(lid_inner_plane.geometry)
    if not geometry:
        raise RuntimeError('外殻蓋部斜面内部の平面ジオメトリを取得できませんでした。')

    normal = geometry.normal.copy()
    if normal.length <= 1e-9:
        raise RuntimeError('外殻蓋部斜面内部の法線を取得できませんでした。')
    normal.normalize()

    offset_sketch_points = []
    for index, reference_point_mm in enumerate(INNER_SHELL_LID_SLOPE_REFERENCE_POINTS_MM[:3]):
        reference_point = create_point_mm(*reference_point_mm)
        signed_distance = get_signed_distance_to_plane(geometry, reference_point)
        projected_point = adsk.core.Point3D.create(
            reference_point.x - (normal.x * signed_distance),
            reference_point.y - (normal.y * signed_distance),
            reference_point.z - (normal.z * signed_distance),
        )
        translated_point = adsk.core.Point3D.create(
            projected_point.x,
            projected_point.y,
            projected_point.z + mm_to_cm(OUTER_SHELL_LID_GAP_PLANE_Z_OFFSET_MM),
        )

        point_plane = create_offset_plane_from_xy(
            root_comp,
            translated_point.z * 10.0,
        )
        point_sketch = root_comp.sketches.add(point_plane)
        point_sketch.name = '{} 基準点{}'.format(
            OUTER_SHELL_LID_GAP_PLANE_NAME,
            index + 1,
        )
        offset_sketch_points.append(
            point_sketch.sketchPoints.add(
                point_sketch.modelToSketchSpace(translated_point)
            )
        )

    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByThreePoints(
        offset_sketch_points[0],
        offset_sketch_points[1],
        offset_sketch_points[2],
    )
    plane = planes.add(plane_input)
    plane.name = OUTER_SHELL_LID_GAP_PLANE_NAME
    helpers.add_named_attribute(plane, OUTER_SHELL_LID_GAP_PLANE_NAME)
    return plane


def split_outer_shell_by_lid_inner_plane(root_comp, outer_shell_body, inner_shell_body=None):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    split_plane = create_lid_inner_split_plane(root_comp, inner_shell_body)
    split_plane_geometry = adsk.core.Plane.cast(split_plane.geometry)
    if not split_plane_geometry:
        raise RuntimeError('外殻分割平面のジオメトリを取得できませんでした。')

    split_features = root_comp.features.splitBodyFeatures
    split_input = split_features.createInput(
        current_outer_shell_body,
        split_plane,
        True,
    )
    split_feature = split_features.add(split_input)

    split_bodies = [split_feature.bodies.item(index) for index in range(split_feature.bodies.count)]
    if len(split_bodies) < 2:
        raise RuntimeError('外殻分割後のボディを取得できませんでした。')

    body_distances = [
        (
            body,
            get_signed_distance_to_plane(
                split_plane_geometry,
                get_body_bounding_box_center(body),
            ),
        )
        for body in split_bodies
    ]
    upper_body, upper_distance = max(body_distances, key=lambda item: item[1])
    lower_body, lower_distance = min(body_distances, key=lambda item: item[1])

    if upper_distance <= lower_distance:
        raise RuntimeError('外殻分割後の上下ボディ判定に失敗しました。')

    root_comp.features.removeFeatures.add(upper_body)
    helpers.set_body_identity(lower_body, naming.BODY_OUTER_SHELL)
    return lower_body


def extrude_outer_shell_lid_inner_plane_in_positive_z(
    root_comp,
    outer_shell_body,
    inner_shell_body=None,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    plane = create_lid_inner_split_plane(root_comp, inner_shell_body)
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_LID_INNER_PLANE_EXTRUDE_SKETCH_NAME

    projected_entities = to_entity_list(
        sketch.intersectWithSketchPlane([current_outer_shell_body])
    )
    if not projected_entities:
        raise RuntimeError('外殻蓋部斜面内部で外殻断面を取得できませんでした。')

    profile = get_largest_profile(sketch)
    centroid = sketch.sketchToModelSpace(profile.areaProperties().centroid)
    path_plane = create_offset_plane_from_xz(
        root_comp,
        centroid.y * 10.0,
        OUTER_SHELL_LID_INNER_PLANE_EXTRUDE_PATH_SKETCH_NAME,
    )
    path_sketch = root_comp.sketches.add(path_plane)
    path_sketch.name = OUTER_SHELL_LID_INNER_PLANE_EXTRUDE_PATH_SKETCH_NAME

    start_point = path_sketch.modelToSketchSpace(centroid)
    end_point = path_sketch.modelToSketchSpace(
        adsk.core.Point3D.create(
            centroid.x,
            centroid.y,
            centroid.z + mm_to_cm(OUTER_SHELL_LID_INNER_PLANE_EXTRUDE_DISTANCE_MM),
        )
    )
    path_line = path_sketch.sketchCurves.sketchLines.addByTwoPoints(
        start_point,
        end_point,
    )
    path = root_comp.features.createPath(path_line)

    sweeps = root_comp.features.sweepFeatures
    sweep_input = sweeps.createInput(
        profile,
        path,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    sweep_input.participantBodies = [current_outer_shell_body]
    sweeps.add(sweep_input)
    return current_outer_shell_body


def cut_outer_shell_by_lid_yz_plane(root_comp, outer_shell_body):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    split_plane = create_offset_plane_from_yz(
        root_comp,
        OUTER_SHELL_LID_YZ_CUT_PLANE_X_MM,
        OUTER_SHELL_LID_YZ_CUT_PLANE_NAME,
    )
    helpers.add_named_attribute(split_plane, OUTER_SHELL_LID_YZ_CUT_PLANE_NAME)

    split_features = root_comp.features.splitBodyFeatures
    split_input = split_features.createInput(
        current_outer_shell_body,
        split_plane,
        True,
    )
    split_feature = split_features.add(split_input)

    split_bodies = [
        split_feature.bodies.item(index)
        for index in range(split_feature.bodies.count)
    ]
    if len(split_bodies) < 2:
        raise RuntimeError('YZ 平面分割後の外殻ボディを取得できませんでした。')

    sorted_bodies = sorted(
        split_bodies,
        key=lambda body: get_body_volume(body),
        reverse=True,
    )
    kept_body = sorted_bodies[0]
    removed_bodies = sorted_bodies[1:]

    for body in removed_bodies:
        root_comp.features.removeFeatures.add(body)

    helpers.set_body_identity(kept_body, naming.BODY_OUTER_SHELL)
    return kept_body


def add_bottom_outer_arc_fillet(root_comp, outer_shell_body):
    edge = find_arc_edge_near_points_on_xy_plane(
        outer_shell_body,
        OUTER_SHELL_BOTTOM_OUTER_FILLET_REFERENCE_POINTS_MM,
        OUTER_SHELL_BOTTOM_OUTER_FILLET_Z_MM,
    )
    apply_constant_radius_fillet(
        root_comp,
        edge,
        OUTER_SHELL_BOTTOM_OUTER_FILLET_RADIUS_MM,
    )


def cut_profile_in_negative_y(root_comp, face, profile, outer_shell_body, inner_shell_body=None, cut_distance_mm=None):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    current_inner_shell_body = inner_shell_body
    if current_inner_shell_body is None:
        current_inner_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_INNER_SHELL,
        )

    moved_inner_shell_body = None
    if current_inner_shell_body is not None:
        moved_inner_shell_body = move_body_by_translation(
            root_comp,
            current_inner_shell_body,
            x_mm=INNER_SHELL_TEMP_MOVE_X_MM,
        )

    geometry = adsk.core.Plane.cast(face.geometry)
    if not geometry:
        raise RuntimeError('開口部カット対象面の平面ジオメトリを取得できませんでした。')

    normal = geometry.normal
    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
    if normal.y > 0.0:
        direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    if cut_distance_mm is None:
        cut_distance_mm = OUTER_SHELL_L_BUTTON_OPENING_CUT_DISTANCE_MM
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(cut_distance_mm)
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)

    if moved_inner_shell_body is not None:
        move_body_by_translation(
            root_comp,
            moved_inner_shell_body,
            x_mm=-INNER_SHELL_TEMP_MOVE_X_MM,
        )


def cut_profile_in_negative_y_from_sketch(
    root_comp,
    sketch,
    profile,
    outer_shell_body,
    inner_shell_body=None,
    cut_distance_mm=None,
):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    current_inner_shell_body = inner_shell_body
    if current_inner_shell_body is None:
        current_inner_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_INNER_SHELL,
        )

    moved_inner_shell_body = None
    if current_inner_shell_body is not None:
        moved_inner_shell_body = move_body_by_translation(
            root_comp,
            current_inner_shell_body,
            x_mm=INNER_SHELL_TEMP_MOVE_X_MM,
        )

    plane_geometry = adsk.core.Plane.cast(sketch.referencePlane.geometry)
    if not plane_geometry:
        raise RuntimeError('Y 方向カット対象スケッチ平面のジオメトリを取得できませんでした。')

    normal = plane_geometry.normal
    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
    if normal.y > 0.0:
        direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    if cut_distance_mm is None:
        cut_distance_mm = OUTER_SHELL_L_BUTTON_OPENING_CUT_DISTANCE_MM
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(cut_distance_mm)
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)

    if moved_inner_shell_body is not None:
        move_body_by_translation(
            root_comp,
            moved_inner_shell_body,
            x_mm=-INNER_SHELL_TEMP_MOVE_X_MM,
        )


def cut_xz_face_in_negative_y(root_comp, face, outer_shell_body, distance_mm, inner_shell_body=None, tolerance=1e-6):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    current_inner_shell_body = inner_shell_body
    if current_inner_shell_body is None:
        current_inner_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_INNER_SHELL,
        )

    moved_inner_shell_body = None
    if current_inner_shell_body is not None:
        moved_inner_shell_body = move_body_by_translation(
            root_comp,
            current_inner_shell_body,
            x_mm=INNER_SHELL_TEMP_MOVE_X_MM,
        )

    geometry = adsk.core.Plane.cast(face.geometry)
    if not geometry:
        raise RuntimeError('Y 方向面カット対象面の平面ジオメトリを取得できませんでした。')

    normal = geometry.normal
    if abs(normal.x) > tolerance or abs(normal.y) <= tolerance or abs(normal.z) > tolerance:
        raise RuntimeError('Y 方向面カット対象面が Y 一定の XZ 面ではありません。')

    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
    if normal.y > 0.0:
        direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        face,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(mm_to_cm(distance_mm))
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)

    if moved_inner_shell_body is not None:
        move_body_by_translation(
            root_comp,
            moved_inner_shell_body,
            x_mm=-INNER_SHELL_TEMP_MOVE_X_MM,
        )


def cut_profile_in_negative_x(root_comp, face, profile, outer_shell_body, cut_distance_mm, inner_shell_body=None):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    current_inner_shell_body = inner_shell_body
    if current_inner_shell_body is None:
        current_inner_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_INNER_SHELL,
        )

    moved_inner_shell_body = None
    if current_inner_shell_body is not None:
        moved_inner_shell_body = move_body_by_translation(
            root_comp,
            current_inner_shell_body,
            x_mm=INNER_SHELL_TEMP_MOVE_X_MM,
        )

    geometry = adsk.core.Plane.cast(face.geometry)
    if not geometry:
        raise RuntimeError('端修正カット対象面の平面ジオメトリを取得できませんでした。')

    normal = geometry.normal
    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
    if normal.x > 0.0:
        direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(cut_distance_mm)
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)

    if moved_inner_shell_body is not None:
        move_body_by_translation(
            root_comp,
            moved_inner_shell_body,
            x_mm=-INNER_SHELL_TEMP_MOVE_X_MM,
        )


def cut_profile_in_positive_x(root_comp, face, profile, outer_shell_body, cut_distance_mm):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    geometry = adsk.core.Plane.cast(face.geometry)
    if not geometry:
        raise RuntimeError('X 方向カット対象面の平面ジオメトリを取得できませんでした。')

    normal = geometry.normal
    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
    if normal.x < 0.0:
        direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(cut_distance_mm)
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)


def extrude_profile_in_negative_x(root_comp, face, profile, outer_shell_body, distance_mm):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    geometry = adsk.core.Plane.cast(face.geometry)
    if not geometry:
        raise RuntimeError('X 方向押し出し対象面の平面ジオメトリを取得できませんでした。')

    normal = geometry.normal
    direction = adsk.fusion.ExtentDirections.NegativeExtentDirection
    if normal.x < 0.0:
        direction = adsk.fusion.ExtentDirections.PositiveExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(distance_mm)
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)


def extrude_profile_in_negative_x_from_sketch(root_comp, sketch, profile, outer_shell_body, distance_mm):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    plane_geometry = adsk.core.Plane.cast(sketch.referencePlane.geometry)
    if not plane_geometry:
        raise RuntimeError('X 方向押し出し対象スケッチ平面のジオメトリを取得できませんでした。')

    normal = plane_geometry.normal
    direction = adsk.fusion.ExtentDirections.NegativeExtentDirection
    if normal.x < 0.0:
        direction = adsk.fusion.ExtentDirections.PositiveExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(distance_mm)
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)


def extrude_profile_in_negative_x_from_sketch_new_body(root_comp, sketch, profile, distance_mm):
    plane_geometry = adsk.core.Plane.cast(sketch.referencePlane.geometry)
    if not plane_geometry:
        raise RuntimeError('X 方向押し出し対象スケッチ平面のジオメトリを取得できませんでした。')

    normal = plane_geometry.normal
    direction = adsk.fusion.ExtentDirections.NegativeExtentDirection
    if normal.x < 0.0:
        direction = adsk.fusion.ExtentDirections.PositiveExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
    )
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(distance_mm)
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    feature = extrudes.add(extrude_input)
    return get_body_from_feature(feature)


def extrude_profile_in_positive_x(root_comp, face, profile, outer_shell_body, distance_mm):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    geometry = adsk.core.Plane.cast(face.geometry)
    if not geometry:
        raise RuntimeError('X 方向押し出し対象面の平面ジオメトリを取得できませんでした。')

    normal = geometry.normal
    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
    if normal.x < 0.0:
        direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(distance_mm)
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)


def cut_profile_in_positive_x_from_sketch_with_taper(
    root_comp,
    sketch,
    profile,
    outer_shell_body,
    cut_distance_mm,
    taper_angle_deg,
):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    plane_geometry = adsk.core.Plane.cast(sketch.referencePlane.geometry)
    if not plane_geometry:
        raise RuntimeError('X 方向テーパー切り取り対象スケッチ平面のジオメトリを取得できませんでした。')

    normal = plane_geometry.normal
    direction = adsk.fusion.ExtentDirections.NegativeExtentDirection
    if normal.x < 0.0:
        direction = adsk.fusion.ExtentDirections.PositiveExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(mm_to_cm(cut_distance_mm))
    taper_angle_value = adsk.core.ValueInput.createByString(
        '{} deg'.format(taper_angle_deg)
    )
    extent_definition = adsk.fusion.DistanceExtentDefinition.create(distance_value)

    try:
        extrude_input.setOneSideExtent(
            extent_definition,
            direction,
            taper_angle_value,
        )
    except TypeError:
        extrude_input.setOneSideExtent(
            extent_definition,
            direction,
        )
        if hasattr(extrude_input, 'taperAngle'):
            extrude_input.taperAngle = taper_angle_value
        elif hasattr(extrude_input, 'taperAngleOne'):
            extrude_input.taperAngleOne = taper_angle_value
        else:
            raise RuntimeError('テーパー角度付き押し出し設定を適用できませんでした。')

    extrudes.add(extrude_input)


def cut_profile_in_negative_z(root_comp, sketch, profile, outer_shell_body, cut_distance_mm):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    plane_geometry = adsk.core.Plane.cast(sketch.referencePlane.geometry)
    if not plane_geometry:
        raise RuntimeError('Z 方向カット対象スケッチ平面のジオメトリを取得できませんでした。')

    normal = plane_geometry.normal
    direction = adsk.fusion.ExtentDirections.NegativeExtentDirection
    if normal.z < 0.0:
        direction = adsk.fusion.ExtentDirections.PositiveExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(mm_to_cm(cut_distance_mm))
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)


def cut_profile_in_positive_z(root_comp, sketch, profile, outer_shell_body, cut_distance_mm):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    plane_geometry = adsk.core.Plane.cast(sketch.referencePlane.geometry)
    if not plane_geometry:
        raise RuntimeError('Z 方向カット対象スケッチ平面のジオメトリを取得できませんでした。')

    normal = plane_geometry.normal
    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
    if normal.z < 0.0:
        direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(mm_to_cm(cut_distance_mm))
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)


def create_offset_plane_from_yz(root_comp, offset_x_mm, name=None):
    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(
        root_comp.yZConstructionPlane,
        adsk.core.ValueInput.createByReal(mm_to_cm(offset_x_mm)),
    )
    plane = planes.add(plane_input)
    if name:
        plane.name = name
    return plane


def create_offset_plane_from_xz(root_comp, offset_y_mm, name=None):
    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(
        root_comp.xZConstructionPlane,
        adsk.core.ValueInput.createByReal(mm_to_cm(offset_y_mm)),
    )
    plane = planes.add(plane_input)
    if name:
        plane.name = name
    return plane


def create_offset_plane_from_xy(root_comp, offset_z_mm, name=None):
    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(
        root_comp.xYConstructionPlane,
        adsk.core.ValueInput.createByReal(mm_to_cm(offset_z_mm)),
    )
    plane = planes.add(plane_input)
    if name:
        plane.name = name
    return plane


def create_outer_shell_l_button_opening_sketch(root_comp, outer_shell_body):
    sketch = root_comp.sketches.add(root_comp.xYConstructionPlane)
    sketch.name = OUTER_SHELL_L_BUTTON_OPENING_SKETCH_NAME
    projected_entities = to_entity_list(sketch.intersectWithSketchPlane([outer_shell_body]))
    projected_curves = [
        adsk.fusion.SketchCurve.cast(entity)
        for entity in projected_entities
        if adsk.fusion.SketchCurve.cast(entity)
    ]

    target_point = create_point_mm(
        *get_midpoint_mm(
            OUTER_SHELL_L_BUTTON_OPENING_REFERENCE_START_MM,
            OUTER_SHELL_L_BUTTON_OPENING_REFERENCE_END_MM,
        )
    )
    curve = find_non_linear_sketch_curve_near_point(projected_curves, target_point)
    visible_reference_curve = clone_intersection_curve_as_sketch_geometry(sketch, curve)

    for projected_curve in projected_curves:
        projected_curve.deleteMe()

    point_a_reference = to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_REFERENCE_START_MM)
    point_d_reference = to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_LINE_D_MM)
    curve_point_a = get_curve_endpoint_sketch_point_nearest_point(
        visible_reference_curve,
        point_a_reference,
    )
    curve_point_d = get_curve_endpoint_sketch_point_nearest_point(
        visible_reference_curve,
        point_d_reference,
    )

    lines = sketch.sketchCurves.sketchLines
    point_c = sketch.sketchPoints.add(create_point_mm(*OUTER_SHELL_L_BUTTON_OPENING_LINE_C_MM))
    point_g = sketch.sketchPoints.add(create_point_mm(*OUTER_SHELL_L_BUTTON_OPENING_LINE_G_MM))
    lines.addByTwoPoints(
        point_c,
        curve_point_d,
    )
    lines.addByTwoPoints(
        point_c,
        point_g,
    )
    lines.addByTwoPoints(
        curve_point_a,
        point_g,
    )

    outer_curve_collection = adsk.core.ObjectCollection.create()
    outer_curve_collection.add(visible_reference_curve)

    offset_entities = sketch.offset(
        outer_curve_collection,
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_REFERENCE_START_MM),
        mm_to_cm(-OUTER_SHELL_L_BUTTON_OPENING_OFFSET_MM),
    )
    offset_entities = to_entity_list(offset_entities)
    offset_curve = get_first_sketch_curve(
        [
            entity
            for entity in offset_entities
            if adsk.fusion.SketchCurve.cast(entity)
        ],
        '開口部オフセット曲線の作成に失敗しました。',
    )

    point_e_geometry = find_curve_line_intersection_point(
        offset_curve,
        OUTER_SHELL_L_BUTTON_OPENING_LINE_C_MM,
        OUTER_SHELL_L_BUTTON_OPENING_LINE_D_MM,
    )
    point_e = sketch.sketchPoints.add(point_e_geometry)
    sketch.geometricConstraints.addCoincident(point_e, offset_curve)

    endpoint_f = get_curve_endpoint_nearest_point(
        offset_curve,
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_ENDPOINT_F_MM),
    )
    point_h_geometry = create_point_mm(
        OUTER_SHELL_L_BUTTON_OPENING_LINE_C_MM[0],
        endpoint_f.y * 10.0,
        0.0,
    )
    point_h = sketch.sketchPoints.add(point_h_geometry)

    line_b_to_e = lines.addByTwoPoints(
        curve_point_d,
        point_e,
    )
    line_c_to_h = lines.addByTwoPoints(
        point_c,
        point_h,
    )
    line_f_to_h = lines.addByTwoPoints(
        endpoint_f,
        point_h,
    )

    return {
        'sketch': sketch,
        'face': None,
    }


def create_outer_shell_end_cut_sketch(root_comp, outer_shell_body):
    _ = outer_shell_body
    plane = create_offset_plane_from_yz(
        root_comp,
        OUTER_SHELL_END_CUT_POINT_A_MM[0],
        OUTER_SHELL_END_CUT_SKETCH_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_END_CUT_SKETCH_NAME

    margin_mm = OUTER_SHELL_END_CUT_MARGIN_MM
    y_values = [
        OUTER_SHELL_END_CUT_POINT_A_MM[1],
        OUTER_SHELL_END_CUT_POINT_B_MM[1],
        OUTER_SHELL_END_CUT_POINT_C_MM[1],
        OUTER_SHELL_END_CUT_POINT_D_MM[1],
    ]
    z_values = [
        OUTER_SHELL_END_CUT_POINT_A_MM[2],
        OUTER_SHELL_END_CUT_POINT_B_MM[2],
        OUTER_SHELL_END_CUT_POINT_C_MM[2],
        OUTER_SHELL_END_CUT_POINT_D_MM[2],
    ]
    min_y_mm = min(y_values) - margin_mm
    max_y_mm = max(y_values) + margin_mm
    min_z_mm = min(z_values) - margin_mm
    max_z_mm = max(z_values) + margin_mm

    expanded_point_a_mm = (OUTER_SHELL_END_CUT_POINT_A_MM[0], max_y_mm, max_z_mm)
    expanded_point_b_mm = (OUTER_SHELL_END_CUT_POINT_A_MM[0], max_y_mm, min_z_mm)
    expanded_point_c_mm = (OUTER_SHELL_END_CUT_POINT_A_MM[0], min_y_mm, min_z_mm)
    expanded_point_d_mm = (OUTER_SHELL_END_CUT_POINT_A_MM[0], min_y_mm, max_z_mm)

    lines = sketch.sketchCurves.sketchLines
    point_a = sketch.sketchPoints.add(
        to_sketch_space(sketch, expanded_point_a_mm)
    )
    point_b = sketch.sketchPoints.add(
        to_sketch_space(sketch, expanded_point_b_mm)
    )
    point_c = sketch.sketchPoints.add(
        to_sketch_space(sketch, expanded_point_c_mm)
    )
    point_d = sketch.sketchPoints.add(
        to_sketch_space(sketch, expanded_point_d_mm)
    )

    lines.addByTwoPoints(point_a, point_b)
    lines.addByTwoPoints(point_b, point_c)
    lines.addByTwoPoints(point_c, point_d)
    lines.addByTwoPoints(point_d, point_a)

    return {
        'sketch': sketch,
        'face': plane,
    }


def cut_outer_shell_end_region(
    root_comp,
    outer_shell_body,
    sketch,
    face,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')
    if face is None:
        raise RuntimeError('face is required.')

    profile = get_profile_nearest_point(
        sketch,
        to_sketch_space(sketch, OUTER_SHELL_END_CUT_PROFILE_TARGET_MM),
    )
    cut_profile_in_negative_x(
        root_comp,
        face,
        profile,
        outer_shell_body,
        OUTER_SHELL_END_CUT_DISTANCE_MM,
    )


def create_outer_shell_yz_rect_cut_sketch(root_comp, outer_shell_body):
    _ = outer_shell_body
    plane = create_offset_plane_from_yz(
        root_comp,
        OUTER_SHELL_YZ_RECT_CUT_POINT_E_MM[0],
        OUTER_SHELL_YZ_RECT_CUT_SKETCH_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_YZ_RECT_CUT_SKETCH_NAME

    lines = sketch.sketchCurves.sketchLines
    point_e = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_YZ_RECT_CUT_POINT_E_MM)
    )
    point_f = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_YZ_RECT_CUT_POINT_F_MM)
    )
    point_g = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_YZ_RECT_CUT_POINT_G_MM)
    )
    point_h = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_YZ_RECT_CUT_POINT_H_MM)
    )

    lines.addByTwoPoints(point_e, point_f)
    lines.addByTwoPoints(point_f, point_g)
    lines.addByTwoPoints(point_g, point_h)
    lines.addByTwoPoints(point_h, point_e)

    return {
        'sketch': sketch,
        'face': plane,
    }


def cut_outer_shell_yz_rect_region(
    root_comp,
    outer_shell_body,
    sketch,
    face,
    inner_shell_body=None,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')
    if face is None:
        raise RuntimeError('face is required.')

    profile = get_profile_containing_point(
        sketch,
        to_sketch_space(sketch, OUTER_SHELL_YZ_RECT_CUT_PROFILE_TARGET_MM),
    )
    cut_profile_in_negative_x(
        root_comp,
        face,
        profile,
        outer_shell_body,
        OUTER_SHELL_YZ_RECT_CUT_DISTANCE_MM,
        inner_shell_body=inner_shell_body,
    )


def create_outer_shell_side_extension_sketch(root_comp, outer_shell_body):
    _ = outer_shell_body
    plane = create_offset_plane_from_yz(
        root_comp,
        OUTER_SHELL_SIDE_EXTENSION_POINT_E_MM[0],
        OUTER_SHELL_SIDE_EXTENSION_SKETCH_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_SIDE_EXTENSION_SKETCH_NAME

    lines = sketch.sketchCurves.sketchLines
    point_e = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_SIDE_EXTENSION_POINT_E_MM)
    )
    point_f = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_SIDE_EXTENSION_POINT_F_MM)
    )
    point_g = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_SIDE_EXTENSION_POINT_G_MM)
    )
    point_h = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_SIDE_EXTENSION_POINT_H_MM)
    )

    lines.addByTwoPoints(point_e, point_f)
    lines.addByTwoPoints(point_f, point_g)
    lines.addByTwoPoints(point_g, point_h)
    lines.addByTwoPoints(point_h, point_e)

    return {
        'sketch': sketch,
        'face': plane,
    }


def extrude_outer_shell_side_extension_region(
    root_comp,
    outer_shell_body,
    sketch,
    face,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')
    if face is None:
        raise RuntimeError('face is required.')

    profile = get_profile_nearest_point(
        sketch,
        to_sketch_space(sketch, OUTER_SHELL_SIDE_EXTENSION_PROFILE_TARGET_MM),
    )
    extrude_profile_in_positive_x(
        root_comp,
        face,
        profile,
        outer_shell_body,
        OUTER_SHELL_SIDE_EXTENSION_DISTANCE_MM,
    )


def create_outer_shell_fitting_adjustment_sketch(root_comp, outer_shell_body):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    plane = create_offset_plane_from_yz(
        root_comp,
        OUTER_SHELL_FITTING_ADJUSTMENT_SKETCH_PLANE_X_MM,
        OUTER_SHELL_FITTING_ADJUSTMENT_SKETCH_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_FITTING_ADJUSTMENT_SKETCH_NAME

    lines = sketch.sketchCurves.sketchLines
    point_a = sketch.sketchPoints.add(
        to_sketch_space(
            sketch,
            (
                OUTER_SHELL_FITTING_ADJUSTMENT_SKETCH_PLANE_X_MM,
                OUTER_SHELL_FITTING_ADJUSTMENT_POINT_A_MM[1],
                OUTER_SHELL_FITTING_ADJUSTMENT_POINT_A_MM[2],
            ),
        )
    )
    point_b = sketch.sketchPoints.add(
        to_sketch_space(
            sketch,
            (
                OUTER_SHELL_FITTING_ADJUSTMENT_SKETCH_PLANE_X_MM,
                OUTER_SHELL_FITTING_ADJUSTMENT_POINT_B_MM[1],
                OUTER_SHELL_FITTING_ADJUSTMENT_POINT_B_MM[2],
            ),
        )
    )
    point_c = sketch.sketchPoints.add(
        to_sketch_space(
            sketch,
            (
                OUTER_SHELL_FITTING_ADJUSTMENT_SKETCH_PLANE_X_MM,
                OUTER_SHELL_FITTING_ADJUSTMENT_POINT_C_MM[1],
                OUTER_SHELL_FITTING_ADJUSTMENT_POINT_C_MM[2],
            ),
        )
    )
    point_d = sketch.sketchPoints.add(
        to_sketch_space(
            sketch,
            (
                OUTER_SHELL_FITTING_ADJUSTMENT_SKETCH_PLANE_X_MM,
                OUTER_SHELL_FITTING_ADJUSTMENT_POINT_D_MM[1],
                OUTER_SHELL_FITTING_ADJUSTMENT_POINT_D_MM[2],
            ),
        )
    )

    lines.addByTwoPoints(point_a, point_b)
    lines.addByTwoPoints(point_b, point_c)
    lines.addByTwoPoints(point_c, point_d)
    lines.addByTwoPoints(point_d, point_a)

    return {
        'sketch': sketch,
        'face': plane,
    }


def cut_outer_shell_fitting_adjustment_region(
    root_comp,
    outer_shell_body,
    sketch,
    face,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')
    if face is None:
        raise RuntimeError('face is required.')

    profile = get_profile_containing_point(
        sketch,
        to_sketch_space(sketch, OUTER_SHELL_FITTING_ADJUSTMENT_PROFILE_TARGET_MM),
    )
    cut_profile_in_negative_x(
        root_comp,
        face,
        profile,
        outer_shell_body,
        OUTER_SHELL_FITTING_ADJUSTMENT_CUT_DISTANCE_MM,
    )


def create_outer_shell_fitting_correction_sketch(root_comp):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')

    plane = create_offset_plane_from_xy(
        root_comp,
        OUTER_SHELL_FITTING_CORRECTION_POINTS_MM['O'][2],
        OUTER_SHELL_FITTING_CORRECTION_SKETCH_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_FITTING_CORRECTION_SKETCH_NAME
    sketch_points = add_model_points_to_sketch(
        sketch,
        OUTER_SHELL_FITTING_CORRECTION_POINTS_MM,
    )

    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    lines.addByTwoPoints(sketch_points['O'], sketch_points['R'])
    lines.addByTwoPoints(sketch_points['R'], sketch_points['P'])
    lines.addByTwoPoints(sketch_points['Q'], sketch_points['O'])

    center_o_xy_mm = (
        OUTER_SHELL_FITTING_CORRECTION_POINTS_MM['O'][0],
        OUTER_SHELL_FITTING_CORRECTION_POINTS_MM['O'][1],
    )
    point_p_xy_mm = (
        OUTER_SHELL_FITTING_CORRECTION_POINTS_MM['P'][0],
        OUTER_SHELL_FITTING_CORRECTION_POINTS_MM['P'][1],
    )
    point_q_xy_mm = (
        OUTER_SHELL_FITTING_CORRECTION_POINTS_MM['Q'][0],
        OUTER_SHELL_FITTING_CORRECTION_POINTS_MM['Q'][1],
    )
    radius_pq_mm = get_distance_2d_mm(center_o_xy_mm, point_p_xy_mm)
    angle_p_rad = angle_for_point_on_circle_mm(center_o_xy_mm, point_p_xy_mm)
    angle_q_rad = angle_for_point_on_circle_mm(center_o_xy_mm, point_q_xy_mm)
    arc_midpoint_xy_mm = point_on_circle_from_angle_mm(
        center_o_xy_mm,
        radius_pq_mm,
        midpoint_angle_rad(
            angle_p_rad,
            angle_q_rad,
            via_angle_rad=(-math.pi / 2.0),
        ),
    )
    arcs.addByThreePoints(
        sketch_points['P'].geometry,
        create_point_in_sketch_space_mm(*arc_midpoint_xy_mm),
        sketch_points['Q'].geometry,
    )
    return sketch


def loft_cut_between_faces(root_comp, face_a, face_b, outer_shell_body):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if face_a is None or face_b is None:
        raise RuntimeError('ロフト切り取り対象面が不足しています。')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    lofts = root_comp.features.loftFeatures
    loft_input = lofts.createInput(adsk.fusion.FeatureOperations.CutFeatureOperation)
    loft_input.isSolid = True
    loft_input.loftSections.add(face_a)
    loft_input.loftSections.add(face_b)
    if hasattr(loft_input, 'participantBodies'):
        loft_input.participantBodies = [outer_shell_body]
    lofts.add(loft_input)


def remove_split_outer_shell_fragments(root_comp):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')

    candidate_bodies = []
    inner_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_INNER_SHELL,
    )

    for index in range(root_comp.bRepBodies.count):
        body = root_comp.bRepBodies.item(index)
        if inner_shell_body is not None and body == inner_shell_body:
            continue
        candidate_bodies.append(body)

    if not candidate_bodies:
        raise RuntimeError('外殻候補ボディを取得できませんでした。')

    kept_body = max(candidate_bodies, key=lambda body: get_body_volume(body))
    for body in candidate_bodies:
        if body == kept_body:
            continue
        root_comp.features.removeFeatures.add(body)

    helpers.set_body_identity(kept_body, naming.BODY_OUTER_SHELL)
    return kept_body


def add_outer_shell_fitting_correction(root_comp, outer_shell_body, inner_shell_body=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    current_inner_shell_body = inner_shell_body
    if current_inner_shell_body is None:
        current_inner_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_INNER_SHELL,
        )

    moved_inner_shell_body = None
    if current_inner_shell_body is not None:
        moved_inner_shell_body = move_body_by_translation(
            root_comp,
            current_inner_shell_body,
            x_mm=INNER_SHELL_TEMP_MOVE_X_MM,
        )

    try:
        correction_sketch = create_outer_shell_fitting_correction_sketch(root_comp)
        correction_profile = get_largest_profile(
            correction_sketch,
        )
        cut_profile_in_positive_z(
            root_comp,
            correction_sketch,
            correction_profile,
            current_outer_shell_body,
            OUTER_SHELL_FITTING_CORRECTION_CUT_DISTANCE_MM,
        )

        current_outer_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_OUTER_SHELL,
        ) or current_outer_shell_body

        face_tolerance_cm = mm_to_cm(0.5)
        face_a = find_planar_face_through_points(
            current_outer_shell_body,
            OUTER_SHELL_FITTING_CORRECTION_A_FACE_POINTS_MM,
            face_tolerance_cm,
        )
        face_b = find_planar_face_through_points(
            current_outer_shell_body,
            OUTER_SHELL_FITTING_CORRECTION_B_FACE_POINTS_MM,
            face_tolerance_cm,
        )
        loft_cut_between_faces(
            root_comp,
            face_a,
            face_b,
            current_outer_shell_body,
        )
        current_outer_shell_body = remove_split_outer_shell_fragments(root_comp)
    finally:
        if moved_inner_shell_body is not None:
            move_body_by_translation(
                root_comp,
                moved_inner_shell_body,
                x_mm=-INNER_SHELL_TEMP_MOVE_X_MM,
            )

    return current_outer_shell_body


def create_outer_shell_l_button_opening_base_structure_sketch(root_comp, outer_shell_body):
    face = find_largest_xz_face_at_y_covering_point(
        outer_shell_body,
        OUTER_SHELL_L_BUTTON_OPENING_BASE_PROFILE_TARGET_MM,
        tolerance_cm=mm_to_cm(0.2),
    )
    sketch = root_comp.sketches.add(face)
    sketch.name = OUTER_SHELL_L_BUTTON_OPENING_SKETCH_NAME

    lines = sketch.sketchCurves.sketchLines
    point_h = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_BASE_CORNER_H_MM)
    )
    point_i = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_BASE_CORNER_I_MM)
    )
    point_j = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_BASE_CORNER_J_MM)
    )
    point_k = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_BASE_CORNER_K_MM)
    )

    lines.addByTwoPoints(point_h, point_i)
    lines.addByTwoPoints(point_i, point_j)
    lines.addByTwoPoints(point_j, point_k)
    lines.addByTwoPoints(point_k, point_h)

    return {
        'sketch': sketch,
        'face': face,
    }


def cut_outer_shell_l_button_opening_base_structure_region(
    root_comp,
    outer_shell_body,
    inner_shell_body,
    sketch,
    face,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')
    if face is None:
        raise RuntimeError('face is required.')

    profile = get_profile_nearest_point(
        sketch,
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_BASE_PROFILE_TARGET_MM),
    )
    cut_profile_in_negative_y(
        root_comp,
        face,
        profile,
        outer_shell_body,
        inner_shell_body=inner_shell_body,
        cut_distance_mm=OUTER_SHELL_L_BUTTON_OPENING_BASE_CUT_DISTANCE_MM,
    )


def create_outer_shell_l_button_opening_slope_cut_sketch(root_comp, outer_shell_body):
    face = find_planar_face_through_points(
        outer_shell_body,
        (
            OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_O_MM,
            OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_Q_MM,
            OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_P_MM,
        ),
        tolerance_cm=mm_to_cm(1.0),
    )
    sketch = root_comp.sketches.add(face)
    sketch.name = OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_SKETCH_NAME

    lines = sketch.sketchCurves.sketchLines
    point_o = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_O_MM)
    )
    point_q = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_Q_MM)
    )
    point_p = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_P_MM)
    )
    point_r = sketch.sketchPoints.add(
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_POINT_R_MM)
    )

    lines.addByTwoPoints(point_o, point_r)
    lines.addByTwoPoints(point_r, point_p)
    lines.addByTwoPoints(point_p, point_q)
    lines.addByTwoPoints(point_q, point_o)

    return {
        'sketch': sketch,
        'face': face,
    }


def create_outer_shell_l_button_opening_inner_spec_sketch(root_comp, outer_shell_body):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    plane = create_offset_plane_from_yz(
        root_comp,
        OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_PLANE_X_MM,
        name=OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_PLANE_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_SKETCH_NAME
    projected_entities = to_entity_list(sketch.intersectWithSketchPlane([outer_shell_body]))
    for projected_entity in projected_entities:
        sketch_curve = adsk.fusion.SketchCurve.cast(projected_entity)
        if sketch_curve:
            sketch_curve.isConstruction = True

    sketch_points = {}
    for name, point_mm in (
        ('A', OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_POINT_A_MM),
        ('B', OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_POINT_B_MM),
        ('C', OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_POINT_C_MM),
        ('D', OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_POINT_D_MM),
        ('E', OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_POINT_E_MM),
        ('F', OUTER_SHELL_L_BUTTON_OPENING_INNER_SPEC_POINT_F_MM),
    ):
        sketch_points[name] = sketch.sketchPoints.add(
            to_sketch_space(sketch, point_mm)
        )

    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    axis_line = lines.addByTwoPoints(sketch_points['A'], sketch_points['D'])
    lines.addByTwoPoints(sketch_points['B'], sketch_points['C'])
    arcs.addByThreePoints(
        sketch_points['A'].geometry,
        sketch_points['E'].geometry,
        sketch_points['B'].geometry,
    )
    arcs.addByThreePoints(
        sketch_points['C'].geometry,
        sketch_points['F'].geometry,
        sketch_points['D'].geometry,
    )

    return {
        'sketch': sketch,
        'plane': plane,
        'axis_line': axis_line,
    }


def create_outer_shell_l_button_opening_y32_cut_sketch(root_comp, outer_shell_body):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    plane = create_offset_plane_from_xz(
        root_comp,
        OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_PLANE_Y_MM,
        name=OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_PLANE_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_SKETCH_NAME

    projected_entities = to_entity_list(sketch.intersectWithSketchPlane([outer_shell_body]))
    for projected_entity in projected_entities:
        sketch_curve = adsk.fusion.SketchCurve.cast(projected_entity)
        if sketch_curve:
            sketch_curve.isConstruction = True

    sketch_points = {}
    for name, point_mm in (
        ('A', OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_A_MM),
        ('B', OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_B_MM),
        ('C', OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_C_MM),
        ('D', OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_D_MM),
    ):
        sketch_points[name] = sketch.sketchPoints.add(
            to_sketch_space(sketch, point_mm)
        )

    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    lines.addByTwoPoints(sketch_points['A'], sketch_points['B'])
    line_dc = lines.addByTwoPoints(sketch_points['D'], sketch_points['C'])

    point_a_xz_mm = (
        OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_A_MM[0],
        OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_A_MM[2],
    )
    point_b_xz_mm = (
        OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_B_MM[0],
        OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_B_MM[2],
    )
    point_c_xz_mm = (
        OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_C_MM[0],
        OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_C_MM[2],
    )
    point_d_xz_mm = (
        OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_D_MM[0],
        OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_POINT_D_MM[2],
    )

    arc_ca_midpoint_mm = get_tangent_arc_midpoint_at_endpoint_mm(
        point_a_xz_mm,
        point_c_xz_mm,
        point_d_xz_mm,
    )
    arc_bd_midpoint_mm = get_tangent_arc_midpoint_at_endpoint_mm(
        point_b_xz_mm,
        point_d_xz_mm,
        point_c_xz_mm,
    )
    arc_ca_midpoint_model_mm = (
        arc_ca_midpoint_mm[0],
        OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_PLANE_Y_MM,
        arc_ca_midpoint_mm[1],
    )
    arc_bd_midpoint_model_mm = (
        arc_bd_midpoint_mm[0],
        OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_PLANE_Y_MM,
        arc_bd_midpoint_mm[1],
    )

    arc_ca = arcs.addByThreePoints(
        sketch_points['C'].geometry,
        to_sketch_space(sketch, arc_ca_midpoint_model_mm),
        sketch_points['A'].geometry,
    )
    arc_bd = arcs.addByThreePoints(
        sketch_points['B'].geometry,
        to_sketch_space(sketch, arc_bd_midpoint_model_mm),
        sketch_points['D'].geometry,
    )
    sketch.geometricConstraints.addTangent(line_dc, arc_ca)
    sketch.geometricConstraints.addTangent(line_dc, arc_bd)

    return {
        'sketch': sketch,
        'plane': plane,
    }


def cut_outer_shell_l_button_opening_inner_spec_region(
    root_comp,
    outer_shell_body,
    sketch,
    axis_line,
    inner_shell_body=None,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')
    if axis_line is None:
        raise RuntimeError('axis_line is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    current_inner_shell_body = inner_shell_body
    if current_inner_shell_body is None:
        current_inner_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_INNER_SHELL,
        )

    moved_inner_shell_body = None
    if current_inner_shell_body is not None:
        moved_inner_shell_body = move_body_by_translation(
            root_comp,
            current_inner_shell_body,
            x_mm=INNER_SHELL_TEMP_MOVE_X_MM,
        )

    profile = get_largest_profile(sketch)

    revolves = root_comp.features.revolveFeatures
    revolve_input = revolves.createInput(
        profile,
        axis_line,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    revolve_input.participantBodies = [current_outer_shell_body]
    angle_value = adsk.core.ValueInput.createByString('360 deg')
    revolve_input.setAngleExtent(False, angle_value)
    revolves.add(revolve_input)

    if moved_inner_shell_body is not None:
        move_body_by_translation(
            root_comp,
            moved_inner_shell_body,
            x_mm=-INNER_SHELL_TEMP_MOVE_X_MM,
        )


def cut_outer_shell_l_button_opening_y32_region(
    root_comp,
    outer_shell_body,
    sketch,
    inner_shell_body=None,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')

    profile = get_profile_nearest_point(
        sketch,
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_PROFILE_TARGET_MM),
    )
    cut_profile_in_negative_y_from_sketch(
        root_comp,
        sketch,
        profile,
        outer_shell_body,
        inner_shell_body=inner_shell_body,
        cut_distance_mm=OUTER_SHELL_L_BUTTON_OPENING_Y32_CUT_DISTANCE_MM,
    )


def create_outer_shell_lid_decoration_cut_1_sketch(root_comp, outer_shell_body):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    plane = create_offset_plane_from_yz(
        root_comp,
        OUTER_SHELL_LID_DECORATION_CUT_1_PLANE_X_MM,
        name=OUTER_SHELL_LID_DECORATION_CUT_1_PLANE_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_LID_DECORATION_CUT_1_SKETCH_NAME
    projected_entities = to_entity_list(sketch.intersectWithSketchPlane([outer_shell_body]))
    for projected_entity in projected_entities:
        sketch_curve = adsk.fusion.SketchCurve.cast(projected_entity)
        if sketch_curve:
            sketch_curve.isConstruction = True

    sketch_points = {}
    for name, point_mm in (
        ('O', OUTER_SHELL_LID_DECORATION_CUT_1_POINT_O_MM),
        ('P', OUTER_SHELL_LID_DECORATION_CUT_1_POINT_P_MM),
        ('A', OUTER_SHELL_LID_DECORATION_CUT_1_POINT_A_MM),
        ('B', OUTER_SHELL_LID_DECORATION_CUT_1_POINT_B_MM),
        ('C', OUTER_SHELL_LID_DECORATION_CUT_1_POINT_C_MM),
    ):
        sketch_points[name] = sketch.sketchPoints.add(
            to_sketch_space(sketch, point_mm)
        )

    lines = sketch.sketchCurves.sketchLines
    lines.addByTwoPoints(sketch_points['A'], sketch_points['B'])
    lines.addByTwoPoints(sketch_points['B'], sketch_points['C'])
    lines.addByTwoPoints(sketch_points['C'], sketch_points['A'])
    axis_line = lines.addByTwoPoints(sketch_points['O'], sketch_points['P'])
    axis_line.isConstruction = True

    return {
        'sketch': sketch,
        'plane': plane,
        'axis_line': axis_line,
    }


def cut_outer_shell_lid_decoration_cut_1_region(
    root_comp,
    outer_shell_body,
    sketch,
    axis_line,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')
    if axis_line is None:
        raise RuntimeError('axis_line is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    profile = get_profile_nearest_point(
        sketch,
        to_sketch_space(sketch, OUTER_SHELL_LID_DECORATION_CUT_1_PROFILE_TARGET_MM),
    )

    revolves = root_comp.features.revolveFeatures
    revolve_input = revolves.createInput(
        profile,
        axis_line,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    revolve_input.participantBodies = [current_outer_shell_body]
    revolve_input.setTwoSideAngleExtent(
        adsk.core.ValueInput.createByString(
            '{} deg'.format(OUTER_SHELL_LID_DECORATION_CUT_1_POSITIVE_ANGLE_DEG)
        ),
        adsk.core.ValueInput.createByString(
            '{} deg'.format(OUTER_SHELL_LID_DECORATION_CUT_1_NEGATIVE_ANGLE_DEG)
        ),
    )
    revolves.add(revolve_input)

    updated_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if updated_outer_shell_body is None:
        updated_outer_shell_body = current_outer_shell_body
    return updated_outer_shell_body


def create_plane_by_angle(root_comp, linear_entity, angle_deg, planar_entity, name=None):
    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByAngle(
        linear_entity,
        adsk.core.ValueInput.createByString('{} deg'.format(angle_deg)),
        planar_entity,
    )
    plane = planes.add(plane_input)
    if name:
        plane.name = name
    return plane


def find_construction_plane_by_name(root_comp, name):
    planes = root_comp.constructionPlanes
    for index in range(planes.count):
        plane = planes.item(index)
        if plane and plane.name == name:
            return plane
    raise RuntimeError('指定された名前の構築平面を取得できませんでした。')


def get_all_sketch_curves(sketch):
    curves = []
    collections = (
        sketch.sketchCurves.sketchLines,
        sketch.sketchCurves.sketchArcs,
        sketch.sketchCurves.sketchCircles,
        sketch.sketchCurves.sketchEllipses,
        sketch.sketchCurves.sketchFittedSplines,
    )
    for collection in collections:
        for index in range(collection.count):
            curves.append(collection.item(index))
    return curves


def create_fitted_spline_segment_between_points(
    sketch,
    source_curve,
    target_point_a,
    target_point_b,
    sample_count=120,
):
    sample_points = sample_sketch_curve_points_in_sketch_space(
        source_curve,
        sample_count=sample_count,
    )
    if len(sample_points) < 2:
        raise RuntimeError('断面カーブのサンプル点が不足しています。')

    index_a = min(
        range(len(sample_points)),
        key=lambda index: get_point_distance(sample_points[index], target_point_a),
    )
    index_b = min(
        range(len(sample_points)),
        key=lambda index: get_point_distance(sample_points[index], target_point_b),
    )
    if index_a == index_b:
        if index_b < len(sample_points) - 1:
            index_b += 1
        elif index_a > 0:
            index_a -= 1
        else:
            raise RuntimeError('断面カーブから NQ 区間を切り出せませんでした。')

    start_index = min(index_a, index_b)
    end_index = max(index_a, index_b)
    segment_points = sample_points[start_index:end_index + 1]
    if len(segment_points) < 2:
        raise RuntimeError('断面カーブから有効な NQ 区間を取得できませんでした。')

    fit_points = adsk.core.ObjectCollection.create()
    fit_points.add(target_point_a)
    for point in segment_points[1:-1]:
        fit_points.add(point)
    fit_points.add(target_point_b)
    return sketch.sketchCurves.sketchFittedSplines.add(fit_points)


def get_sampled_segment_points_between_points(
    source_curve,
    target_point_a,
    target_point_b,
    sample_count=120,
):
    sample_points = sample_sketch_curve_points_in_sketch_space(
        source_curve,
        sample_count=sample_count,
    )
    if len(sample_points) < 2:
        raise RuntimeError('断面カーブのサンプル点が不足しています。')

    index_a = min(
        range(len(sample_points)),
        key=lambda index: get_point_distance(sample_points[index], target_point_a),
    )
    index_b = min(
        range(len(sample_points)),
        key=lambda index: get_point_distance(sample_points[index], target_point_b),
    )
    if index_a == index_b:
        if index_b < len(sample_points) - 1:
            index_b += 1
        elif index_a > 0:
            index_a -= 1
        else:
            raise RuntimeError('断面カーブから NQ 区間を切り出せませんでした。')

    start_index = min(index_a, index_b)
    end_index = max(index_a, index_b)
    segment_points = sample_points[start_index:end_index + 1]
    if len(segment_points) < 2:
        raise RuntimeError('断面カーブから有効な NQ 区間を取得できませんでした。')

    return [target_point_a, *segment_points[1:-1], target_point_b]


def create_outer_shell_lid_decoration_cut_2_sketch(root_comp, outer_shell_body):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    outer_slope_face = find_face_by_named_attribute(
        current_outer_shell_body,
        OUTER_SHELL_LID_OUTER_SLOPE_FACE_NAME,
    )
    reference_sketch = root_comp.sketches.add(outer_slope_face)
    reference_sketch.name = OUTER_SHELL_LID_DECORATION_CUT_2_REFERENCE_SKETCH_NAME

    reference_points = {}
    for name, point_mm in (
        ('D', OUTER_SHELL_LID_DECORATION_CUT_2_POINT_D_MM),
        ('E', OUTER_SHELL_LID_DECORATION_CUT_2_POINT_E_MM),
        ('F', OUTER_SHELL_LID_DECORATION_CUT_2_POINT_F_MM),
        ('G', OUTER_SHELL_LID_DECORATION_CUT_2_POINT_G_MM),
    ):
        reference_points[name] = reference_sketch.sketchPoints.add(
            to_sketch_space(reference_sketch, point_mm)
        )

    reference_lines = reference_sketch.sketchCurves.sketchLines
    reference_lines.addByTwoPoints(reference_points['D'], reference_points['E']).isConstruction = True
    axis_line = reference_lines.addByTwoPoints(reference_points['F'], reference_points['G'])
    axis_line.isConstruction = True

    plane = create_plane_by_angle(
        root_comp,
        axis_line,
        OUTER_SHELL_LID_DECORATION_CUT_2_PLANE_ANGLE_DEG,
        outer_slope_face,
        name=OUTER_SHELL_LID_DECORATION_CUT_2_PLANE_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_LID_DECORATION_CUT_2_SKETCH_NAME

    sketch_points = {}
    for name, point_mm in (
        ('H', OUTER_SHELL_LID_DECORATION_CUT_2_POINT_H_MM),
        ('I', OUTER_SHELL_LID_DECORATION_CUT_2_POINT_I_MM),
        ('J', OUTER_SHELL_LID_DECORATION_CUT_2_POINT_J_MM),
    ):
        sketch_points[name] = sketch.sketchPoints.add(
            to_sketch_space(sketch, point_mm)
        )

    lines = sketch.sketchCurves.sketchLines
    lines.addByTwoPoints(sketch_points['H'], sketch_points['I'])
    lines.addByTwoPoints(sketch_points['I'], sketch_points['J'])
    lines.addByTwoPoints(sketch_points['J'], sketch_points['H'])

    return {
        'reference_sketch': reference_sketch,
        'plane': plane,
        'sketch': sketch,
    }


def cut_outer_shell_lid_decoration_cut_2_region(
    root_comp,
    outer_shell_body,
    sketch,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    profile = get_profile_nearest_point(
        sketch,
        to_sketch_space(sketch, OUTER_SHELL_LID_DECORATION_CUT_2_PROFILE_TARGET_MM),
    )
    plane_geometry = adsk.core.Plane.cast(sketch.referencePlane.geometry)
    if not plane_geometry:
        raise RuntimeError('蓋部装飾切取り②スケッチ平面のジオメトリを取得できませんでした。')

    negative_x_direction = adsk.fusion.ExtentDirections.NegativeExtentDirection
    positive_x_direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
    if plane_geometry.normal.x < 0.0:
        negative_x_direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
        positive_x_direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByReal(
                mm_to_cm(OUTER_SHELL_LID_DECORATION_CUT_2_NEGATIVE_X_DISTANCE_MM)
            )
        ),
        negative_x_direction,
    )
    extrudes.add(extrude_input)

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    ) or current_outer_shell_body
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByReal(
                mm_to_cm(OUTER_SHELL_LID_DECORATION_CUT_2_POSITIVE_X_DISTANCE_MM)
            )
        ),
        positive_x_direction,
    )
    extrudes.add(extrude_input)

    updated_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if updated_outer_shell_body is None:
        updated_outer_shell_body = current_outer_shell_body
    return updated_outer_shell_body


def create_outer_shell_lid_decoration_cut_3_faces(root_comp, outer_shell_body):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    face_tolerance_cm = mm_to_cm(0.6)
    face_1_points = (
        OUTER_SHELL_LID_DECORATION_CUT_3_POINT_A_PRIME_MM,
        OUTER_SHELL_LID_DECORATION_CUT_3_POINT_B_PRIME_MM,
        OUTER_SHELL_LID_DECORATION_CUT_3_POINT_C_PRIME_MM,
    )
    face_2_points = (
        OUTER_SHELL_LID_DECORATION_CUT_3_POINT_A_PRIME_MM,
        OUTER_SHELL_LID_DECORATION_CUT_3_POINT_B_PRIME_MM,
        OUTER_SHELL_LID_DECORATION_CUT_3_POINT_H_PRIME_MM,
    )

    try:
        face_1 = find_planar_face_through_points(
            current_outer_shell_body,
            face_1_points,
            face_tolerance_cm,
        )
    except RuntimeError:
        face_1 = find_best_planar_face_for_points(
            current_outer_shell_body,
            face_1_points,
            min_alignment=0.9,
        )

    try:
        face_2 = find_planar_face_through_points(
            current_outer_shell_body,
            face_2_points,
            face_tolerance_cm,
        )
    except RuntimeError:
        face_2 = find_best_planar_face_for_points(
            current_outer_shell_body,
            face_2_points,
            min_alignment=0.9,
        )

    return {
        'face_1': face_1,
        'face_2': face_2,
    }


def loft_cut_between_profiles(root_comp, profile_a, profile_b, outer_shell_body):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if profile_a is None or profile_b is None:
        raise RuntimeError('ロフト切り取り対象プロファイルが不足しています。')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    lofts = root_comp.features.loftFeatures
    loft_input = lofts.createInput(adsk.fusion.FeatureOperations.CutFeatureOperation)
    loft_input.isSolid = True
    loft_input.loftSections.add(profile_a)
    loft_input.loftSections.add(profile_b)
    if hasattr(loft_input, 'participantBodies'):
        loft_input.participantBodies = [outer_shell_body]
    lofts.add(loft_input)


def cut_outer_shell_lid_decoration_cut_3_region(
    root_comp,
    outer_shell_body,
    face_1,
    face_2,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if face_1 is None or face_2 is None:
        raise RuntimeError('faces are required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    loft_cut_between_faces(
        root_comp,
        face_1,
        face_2,
        current_outer_shell_body,
    )
    updated_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if updated_outer_shell_body is None:
        updated_outer_shell_body = current_outer_shell_body
    return updated_outer_shell_body


def create_outer_shell_lid_decoration_cut_4_sketch(root_comp, outer_shell_body):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    plane = find_construction_plane_by_name(
        root_comp,
        OUTER_SHELL_LID_DECORATION_CUT_2_PLANE_NAME,
    )

    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_LID_DECORATION_CUT_4_SKETCH_NAME

    sketch_points = {}
    for name, point_mm in (
        ('K', OUTER_SHELL_LID_DECORATION_CUT_4_POINT_K_MM),
        ('L', OUTER_SHELL_LID_DECORATION_CUT_4_POINT_L_MM),
        ('M', OUTER_SHELL_LID_DECORATION_CUT_4_POINT_M_MM),
        ('N', OUTER_SHELL_LID_DECORATION_CUT_4_POINT_N_MM),
        ('Q', OUTER_SHELL_LID_DECORATION_CUT_4_POINT_Q_MM),
    ):
        sketch_points[name] = sketch.sketchPoints.add(
            to_sketch_space(sketch, point_mm)
        )

    lines = sketch.sketchCurves.sketchLines
    lines.addByTwoPoints(sketch_points['M'], sketch_points['N'])
    lines.addByTwoPoints(sketch_points['N'], sketch_points['Q'])
    lines.addByTwoPoints(sketch_points['Q'], sketch_points['M'])
    axis_line = lines.addByTwoPoints(sketch_points['K'], sketch_points['L'])
    axis_line.isConstruction = True

    return {
        'plane': plane,
        'sketch': sketch,
        'axis_line': axis_line,
    }


def cut_outer_shell_lid_decoration_cut_4_region(
    root_comp,
    outer_shell_body,
    sketch,
    axis_line,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')
    if axis_line is None:
        raise RuntimeError('axis_line is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    profile = get_profile_nearest_point(
        sketch,
        to_sketch_space(sketch, OUTER_SHELL_LID_DECORATION_CUT_4_PROFILE_TARGET_MM),
    )
    revolves = root_comp.features.revolveFeatures
    revolve_input = revolves.createInput(
        profile,
        axis_line,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    revolve_input.participantBodies = [current_outer_shell_body]
    revolve_input.setAngleExtent(
        False,
        adsk.core.ValueInput.createByString(
            '{} deg'.format(OUTER_SHELL_LID_DECORATION_CUT_4_REVOLVE_ANGLE_DEG)
        ),
    )
    revolves.add(revolve_input)

    updated_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if updated_outer_shell_body is None:
        updated_outer_shell_body = current_outer_shell_body

    extrudes = root_comp.features.extrudeFeatures
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(OUTER_SHELL_LID_DECORATION_CUT_4_EXTRUDE_DISTANCE_MM)
    )

    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [updated_outer_shell_body]
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        adsk.fusion.ExtentDirections.NegativeExtentDirection,
    )
    extrudes.add(extrude_input)

    updated_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    ) or updated_outer_shell_body
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [updated_outer_shell_body]
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    extrudes.add(extrude_input)

    return helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    ) or updated_outer_shell_body


def create_outer_shell_lid_decoration_cut_5_sketch(root_comp, outer_shell_body):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    profile_plane = create_plane_by_three_points(
        root_comp,
        OUTER_SHELL_LID_DECORATION_CUT_5_POINT_X_MM,
        OUTER_SHELL_LID_DECORATION_CUT_5_POINT_Y_MM,
        OUTER_SHELL_LID_DECORATION_CUT_5_POINT_Z_MM,
        OUTER_SHELL_LID_DECORATION_CUT_5_SKETCH_NAME,
    )
    sketch = root_comp.sketches.add(profile_plane)
    sketch.name = OUTER_SHELL_LID_DECORATION_CUT_5_SKETCH_NAME
    sketch_points = add_model_points_to_sketch(
        sketch,
        {
            'X': OUTER_SHELL_LID_DECORATION_CUT_5_POINT_X_MM,
            'Y': OUTER_SHELL_LID_DECORATION_CUT_5_POINT_Y_MM,
            'Z': OUTER_SHELL_LID_DECORATION_CUT_5_POINT_Z_MM,
        },
    )
    add_closed_polyline_to_sketch(sketch, sketch_points, ['X', 'Y', 'Z'])

    return {
        'sketch': sketch,
        'plane': profile_plane,
    }


def cut_outer_shell_lid_decoration_cut_5_region(
    root_comp,
    outer_shell_body,
    sketch,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    profile = get_largest_profile(sketch)
    plane_geometry = adsk.core.Plane.cast(sketch.referencePlane.geometry)
    if not plane_geometry:
        raise RuntimeError('蓋部装飾切取り⑤スケッチ平面のジオメトリを取得できませんでした。')

    direction = adsk.fusion.ExtentDirections.PositiveExtentDirection
    if plane_geometry.normal.x > 0.0:
        direction = adsk.fusion.ExtentDirections.NegativeExtentDirection

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByReal(
                mm_to_cm(OUTER_SHELL_LID_DECORATION_CUT_5_POSITIVE_DISTANCE_MM)
            )
        ),
        direction,
    )
    extrudes.add(extrude_input)

    updated_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    ) or current_outer_shell_body

    opposite_direction = adsk.fusion.ExtentDirections.NegativeExtentDirection
    if direction == adsk.fusion.ExtentDirections.NegativeExtentDirection:
        opposite_direction = adsk.fusion.ExtentDirections.PositiveExtentDirection

    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [updated_outer_shell_body]
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByReal(
                mm_to_cm(OUTER_SHELL_LID_DECORATION_CUT_5_NEGATIVE_DISTANCE_MM)
            )
        ),
        opposite_direction,
    )
    extrudes.add(extrude_input)

    return helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    ) or updated_outer_shell_body


def cut_outer_shell_l_button_opening_slope_region(
    root_comp,
    outer_shell_body,
    sketch,
    face,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')
    if face is None:
        raise RuntimeError('face is required.')

    profile = get_profile_nearest_point(
        sketch,
        to_sketch_space(sketch, OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_PROFILE_TARGET_MM),
    )

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(OUTER_SHELL_L_BUTTON_OPENING_SLOPE_CUT_DISTANCE_MM)
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        adsk.fusion.ExtentDirections.NegativeExtentDirection,
    )
    extrudes.add(extrude_input)

    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    extrude_input.participantBodies = [outer_shell_body]
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    extrudes.add(extrude_input)


def cut_outer_shell_y35_face_region(root_comp, outer_shell_body, inner_shell_body=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    app = adsk.core.Application.get()
    tolerance_cm = max(app.pointTolerance, 1e-5)
    face = find_largest_xz_face_at_y_covering_point(
        outer_shell_body,
        OUTER_SHELL_Y35_FACE_CUT_TARGET_MM,
        tolerance_cm,
    )
    cut_xz_face_in_negative_y(
        root_comp,
        face,
        outer_shell_body,
        OUTER_SHELL_Y35_FACE_CUT_DISTANCE_MM,
        inner_shell_body=inner_shell_body,
        tolerance=tolerance_cm,
    )


def add_outer_shell_l_button_opening_base_structure_fillets(root_comp, outer_shell_body):
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    axis_1_edge = find_linear_edge_parallel_to_y_near_point(
        current_outer_shell_body,
        OUTER_SHELL_L_BUTTON_OPENING_BASE_FILLET_AXIS_1_POINT_MM,
    )
    apply_constant_radius_fillet(
        root_comp,
        axis_1_edge,
        OUTER_SHELL_L_BUTTON_OPENING_BASE_FILLET_AXIS_1_RADIUS_MM,
        tangent_chain=False,
    )

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    axis_2_edge = find_linear_edge_parallel_to_y_near_point(
        current_outer_shell_body,
        OUTER_SHELL_L_BUTTON_OPENING_BASE_FILLET_AXIS_2_POINT_MM,
    )
    apply_constant_radius_fillet(
        root_comp,
        axis_2_edge,
        OUTER_SHELL_L_BUTTON_OPENING_BASE_FILLET_AXIS_2_RADIUS_MM,
        tangent_chain=False,
    )


def extrude_outer_shell_l_button_opening_region(root_comp, outer_shell_body, sketch):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')

    profile = get_largest_profile(sketch)

    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    extrude_input.participantBodies = [outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(OUTER_SHELL_L_BUTTON_OPENING_EXTRUDE_DISTANCE_MM)
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        adsk.fusion.ExtentDirections.PositiveExtentDirection,
    )
    extrudes.add(extrude_input)


def create_outer_shell_lid_gap_sketch(root_comp, outer_shell_body, inner_shell_body=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    lid_inner_plane = create_lid_inner_split_plane(root_comp, inner_shell_body)
    lid_inner_reference_sketch = root_comp.sketches.add(lid_inner_plane)
 
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    sketch_face = find_best_planar_face_near_reference_points(
        current_outer_shell_body,
        (
            OUTER_SHELL_LID_GAP_POINT_A_MM,
            OUTER_SHELL_LID_GAP_POINT_F_MM,
            OUTER_SHELL_LID_GAP_POINT_H_MM,
        ),
    )
    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(
        sketch_face,
        adsk.core.ValueInput.createByReal(0.0),
    )
    sketch_plane = planes.add(plane_input)
    sketch_plane.name = '{} 平面'.format(OUTER_SHELL_LID_GAP_SKETCH_NAME)
    sketch = root_comp.sketches.add(sketch_plane)
    sketch.name = OUTER_SHELL_LID_GAP_SKETCH_NAME

    projected_entities = to_entity_list(sketch.intersectWithSketchPlane([outer_shell_body]))
    for projected_entity in projected_entities:
        sketch_curve = adsk.fusion.SketchCurve.cast(projected_entity)
        if sketch_curve:
            sketch_curve.isConstruction = True

    points_3d_mm = {
        'A': OUTER_SHELL_LID_GAP_POINT_A_MM,
        'B': OUTER_SHELL_LID_GAP_POINT_B_MM,
        'C': OUTER_SHELL_LID_GAP_POINT_C_MM,
        'D': OUTER_SHELL_LID_GAP_POINT_D_MM,
        'E': OUTER_SHELL_LID_GAP_POINT_E_MM,
        'F': OUTER_SHELL_LID_GAP_POINT_F_MM,
        'G': OUTER_SHELL_LID_GAP_POINT_G_MM,
        'H': OUTER_SHELL_LID_GAP_POINT_H_MM,
        'I': OUTER_SHELL_LID_GAP_POINT_I_MM,
    }
    points_mm = {
        name: (
            lid_inner_reference_sketch.modelToSketchSpace(create_point_mm(*point_mm)).x * 10.0,
            lid_inner_reference_sketch.modelToSketchSpace(create_point_mm(*point_mm)).y * 10.0,
        )
        for name, point_mm in points_3d_mm.items()
    }
    lid_inner_reference_sketch.deleteMe()

    circle_k_radius_mm = (
        get_distance_2d_mm(points_mm['I'], points_mm['E'])
        + get_distance_2d_mm(points_mm['I'], points_mm['H'])
    ) / 2.0
    points_mm['E'] = offset_point_from_circle(
        points_mm['I'],
        points_mm['E'],
        circle_k_radius_mm - get_distance_2d_mm(points_mm['I'], points_mm['E']),
    )
    points_mm['H'] = offset_point_from_circle(
        points_mm['I'],
        points_mm['H'],
        circle_k_radius_mm - get_distance_2d_mm(points_mm['I'], points_mm['H']),
    )
    circle_l_center_mm = get_tangent_circle_center_between_lines_mm(
        points_mm['I'],
        points_mm['F'],
        points_mm['G'],
        OUTER_SHELL_LID_GAP_CIRCLE_L_RADIUS_MM,
    )
    point_m_mm = project_point_to_line_mm(
        circle_l_center_mm,
        points_mm['I'],
        points_mm['F'],
    )
    tangent_points_n_mm = tangent_points_from_external_point_to_circle_mm(
        points_mm['H'],
        circle_l_center_mm,
        OUTER_SHELL_LID_GAP_CIRCLE_L_RADIUS_MM,
    )
    point_n_mm = min(
        tangent_points_n_mm,
        key=lambda point_mm: get_distance_2d_mm(point_mm, points_mm['I']),
    )

    sketch_points = {}
    for name, point_mm in points_mm.items():
        sketch_points[name] = sketch.sketchPoints.add(
            create_point_in_sketch_space_mm(*point_mm)
        )
    sketch_points['M'] = sketch.sketchPoints.add(
        create_point_in_sketch_space_mm(*point_m_mm)
    )
    sketch_points['N'] = sketch.sketchPoints.add(
        create_point_in_sketch_space_mm(*point_n_mm)
    )
    points_mm['M'] = point_m_mm
    points_mm['N'] = point_n_mm

    lines = sketch.sketchCurves.sketchLines
    circles = sketch.sketchCurves.sketchCircles
    arcs = sketch.sketchCurves.sketchArcs

    for start_name, end_name in (
        ('A', 'B'),
        ('B', 'C'),
        ('C', 'D'),
        ('D', 'E'),
        ('A', 'F'),
        ('F', 'M'),
        ('H', 'N'),
    ):
        if get_distance_2d_mm(points_mm[start_name], points_mm[end_name]) <= 1e-6:
            continue
        lines.addByTwoPoints(
            sketch_points[start_name],
            sketch_points[end_name],
        )

    line_if = lines.addByTwoPoints(sketch_points['I'], sketch_points['F'])
    line_if.isConstruction = True
    line_ig = lines.addByTwoPoints(sketch_points['I'], sketch_points['G'])
    line_ig.isConstruction = True

    circle_k = circles.addByCenterRadius(
        sketch_points['I'].geometry,
        mm_to_cm(circle_k_radius_mm),
    )
    circle_k.isConstruction = True
    circle_l = circles.addByCenterRadius(
        create_point_in_sketch_space_mm(*circle_l_center_mm),
        mm_to_cm(OUTER_SHELL_LID_GAP_CIRCLE_L_RADIUS_MM),
    )
    circle_l.isConstruction = True

    angle_e_rad = angle_for_point_on_circle_mm(points_mm['I'], points_mm['E'])
    angle_h_rad = angle_for_point_on_circle_mm(points_mm['I'], points_mm['H'])
    mid_angle_k_rad = midpoint_angle_rad(
        angle_e_rad,
        angle_h_rad,
    )
    arc_k_midpoint_mm = point_on_circle_from_angle_mm(
        points_mm['I'],
        circle_k_radius_mm,
        mid_angle_k_rad,
    )
    arcs.addByThreePoints(
        sketch_points['E'].geometry,
        create_point_in_sketch_space_mm(*arc_k_midpoint_mm),
        sketch_points['H'].geometry,
    )

    angle_m_rad = angle_for_point_on_circle_mm(circle_l_center_mm, point_m_mm)
    angle_n_rad = angle_for_point_on_circle_mm(circle_l_center_mm, point_n_mm)
    angle_i_rad = angle_for_point_on_circle_mm(circle_l_center_mm, points_mm['I'])
    mid_angle_l_rad = midpoint_angle_rad(
        angle_m_rad,
        angle_n_rad,
        via_angle_rad=angle_i_rad,
    )
    arc_l_midpoint_mm = point_on_circle_from_angle_mm(
        circle_l_center_mm,
        OUTER_SHELL_LID_GAP_CIRCLE_L_RADIUS_MM,
        mid_angle_l_rad,
    )
    arcs.addByThreePoints(
        sketch_points['M'].geometry,
        create_point_in_sketch_space_mm(*arc_l_midpoint_mm),
        sketch_points['N'].geometry,
    )
    primary_profile_target_mm = (
        (points_mm['A'][0] + points_mm['F'][0]) / 2.0,
        points_mm['A'][1] - 10.0,
    )

    return {
        'plane': sketch_plane,
        'sketch': sketch,
        'primary_profile_target_point': create_point_in_sketch_space_mm(*primary_profile_target_mm),
    }


def extrude_outer_shell_lid_gap_region(root_comp, outer_shell_body, sketch, plane, profile_target_point):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')
    if plane is None:
        raise RuntimeError('plane is required.')
    if profile_target_point is None:
        raise RuntimeError('profile_target_point is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    plane_geometry = adsk.core.Plane.cast(plane.geometry)
    if not plane_geometry:
        raise RuntimeError('外殻蓋部斜面隙間部平面のジオメトリを取得できませんでした。')

    profile = get_profile_containing_point(sketch, profile_target_point)
    centroid = sketch.sketchToModelSpace(profile.areaProperties().centroid)
    path_plane = create_offset_plane_from_xz(
        root_comp,
        centroid.y * 10.0,
        '{} パス'.format(OUTER_SHELL_LID_GAP_SKETCH_NAME),
    )
    path_sketch = root_comp.sketches.add(path_plane)
    path_sketch.name = '{} パス'.format(OUTER_SHELL_LID_GAP_SKETCH_NAME)

    start_point = path_sketch.modelToSketchSpace(centroid)
    end_point = path_sketch.modelToSketchSpace(
        adsk.core.Point3D.create(
            centroid.x,
            centroid.y,
            centroid.z + mm_to_cm(OUTER_SHELL_LID_GAP_EXTRUDE_DISTANCE_MM),
        )
    )
    path_line = path_sketch.sketchCurves.sketchLines.addByTwoPoints(
        start_point,
        end_point,
    )
    path = root_comp.features.createPath(path_line)

    sweeps = root_comp.features.sweepFeatures
    sweep_input = sweeps.createInput(
        profile,
        path,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    sweep_input.participantBodies = [current_outer_shell_body]
    feature = sweeps.add(sweep_input)

    translated_reference_points_mm = [
        (point_mm[0], point_mm[1], point_mm[2] + OUTER_SHELL_LID_GAP_EXTRUDE_DISTANCE_MM)
        for point_mm in (
            OUTER_SHELL_LID_GAP_POINT_A_MM,
            OUTER_SHELL_LID_GAP_POINT_F_MM,
            OUTER_SHELL_LID_GAP_POINT_H_MM,
        )
    ]

    updated_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if updated_outer_shell_body is None:
        updated_outer_shell_body = current_outer_shell_body

    top_face = find_best_planar_face_near_reference_points(
        updated_outer_shell_body,
        translated_reference_points_mm,
    )
    helpers.add_named_attribute(top_face, OUTER_SHELL_LID_OUTER_SLOPE_FACE_NAME)
    return updated_outer_shell_body


def calculate_outer_shell_lid_gap_extension_profile_geometry_mm(root_comp, inner_shell_body=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')

    lid_inner_plane = create_lid_inner_split_plane(root_comp, inner_shell_body)
    lid_inner_reference_sketch = root_comp.sketches.add(lid_inner_plane)

    points_3d_mm = {
        'F': OUTER_SHELL_LID_GAP_POINT_F_MM,
        'G': OUTER_SHELL_LID_GAP_POINT_G_MM,
        'H': OUTER_SHELL_LID_GAP_POINT_H_MM,
        'I': OUTER_SHELL_LID_GAP_POINT_I_MM,
    }
    points_mm = {
        name: (
            lid_inner_reference_sketch.modelToSketchSpace(create_point_mm(*point_mm)).x * 10.0,
            lid_inner_reference_sketch.modelToSketchSpace(create_point_mm(*point_mm)).y * 10.0,
        )
        for name, point_mm in points_3d_mm.items()
    }
    lid_inner_reference_sketch.deleteMe()

    circle_k_radius_mm = (
        get_distance_2d_mm(points_mm['I'], points_mm['F'])
        + get_distance_2d_mm(points_mm['I'], points_mm['G'])
    ) / 2.0
    points_mm['F'] = offset_point_from_circle(
        points_mm['I'],
        points_mm['F'],
        circle_k_radius_mm - get_distance_2d_mm(points_mm['I'], points_mm['F']),
    )
    points_mm['G'] = offset_point_from_circle(
        points_mm['I'],
        points_mm['G'],
        circle_k_radius_mm - get_distance_2d_mm(points_mm['I'], points_mm['G']),
    )
    circle_l_center_mm = get_tangent_circle_center_between_lines_mm(
        points_mm['I'],
        points_mm['F'],
        points_mm['G'],
        OUTER_SHELL_LID_GAP_CIRCLE_L_RADIUS_MM,
    )
    point_m_mm = project_point_to_line_mm(
        circle_l_center_mm,
        points_mm['I'],
        points_mm['F'],
    )
    tangent_points_n_mm = tangent_points_from_external_point_to_circle_mm(
        points_mm['H'],
        circle_l_center_mm,
        OUTER_SHELL_LID_GAP_CIRCLE_L_RADIUS_MM,
    )
    point_n_mm = min(
        tangent_points_n_mm,
        key=lambda point_mm: get_distance_2d_mm(point_mm, points_mm['I']),
    )
    point_p_mm = intersect_lines_2d_mm(
        points_mm['H'],
        point_n_mm,
        points_mm['G'],
        points_mm['I'],
    )

    angle_m_rad = angle_for_point_on_circle_mm(circle_l_center_mm, point_m_mm)
    angle_n_rad = angle_for_point_on_circle_mm(circle_l_center_mm, point_n_mm)
    angle_i_rad = angle_for_point_on_circle_mm(circle_l_center_mm, points_mm['I'])
    mid_angle_l_rad = midpoint_angle_rad(
        angle_m_rad,
        angle_n_rad,
        via_angle_rad=angle_i_rad,
    )
    arc_l_midpoint_mm = point_on_circle_from_angle_mm(
        circle_l_center_mm,
        OUTER_SHELL_LID_GAP_CIRCLE_L_RADIUS_MM,
        mid_angle_l_rad,
    )

    angle_f_rad = angle_for_point_on_circle_mm(points_mm['I'], points_mm['F'])
    angle_g_rad = angle_for_point_on_circle_mm(points_mm['I'], points_mm['G'])
    mid_angle_fg_rad = midpoint_angle_rad(
        angle_f_rad,
        angle_g_rad,
    )
    arc_fg_midpoint_mm = point_on_circle_from_angle_mm(
        points_mm['I'],
        circle_k_radius_mm,
        mid_angle_fg_rad,
    )

    extension_profile_target_mm = (
        (points_mm['G'][0] + point_p_mm[0] + point_n_mm[0] + point_m_mm[0] + points_mm['F'][0]) / 5.0,
        (points_mm['G'][1] + point_p_mm[1] + point_n_mm[1] + point_m_mm[1] + points_mm['F'][1]) / 5.0,
    )

    return {
        'points_mm': points_mm,
        'point_m_mm': point_m_mm,
        'point_n_mm': point_n_mm,
        'point_p_mm': point_p_mm,
        'arc_nm_midpoint_mm': arc_l_midpoint_mm,
        'arc_fg_midpoint_mm': arc_fg_midpoint_mm,
        'extension_profile_target_mm': extension_profile_target_mm,
    }


def create_outer_shell_lid_gap_extension_sketch(root_comp, outer_shell_body, inner_shell_body=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    lid_inner_plane = create_lid_inner_split_plane(root_comp, inner_shell_body)
    lid_inner_reference_sketch = root_comp.sketches.add(lid_inner_plane)

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    sketch_face = find_best_planar_face_near_reference_points(
        current_outer_shell_body,
        (
            OUTER_SHELL_LID_GAP_POINT_A_MM,
            OUTER_SHELL_LID_GAP_POINT_F_MM,
            OUTER_SHELL_LID_GAP_POINT_H_MM,
        ),
    )
    planes = root_comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(
        sketch_face,
        adsk.core.ValueInput.createByReal(0.0),
    )
    sketch_plane = planes.add(plane_input)
    sketch_plane.name = '{} 追加平面'.format(OUTER_SHELL_LID_GAP_SKETCH_NAME)
    sketch = root_comp.sketches.add(sketch_plane)
    sketch.name = '{} 追加'.format(OUTER_SHELL_LID_GAP_SKETCH_NAME)

    points_3d_mm = {
        'F': OUTER_SHELL_LID_GAP_POINT_F_MM,
        'G': OUTER_SHELL_LID_GAP_POINT_G_MM,
        'H': OUTER_SHELL_LID_GAP_POINT_H_MM,
        'I': OUTER_SHELL_LID_GAP_POINT_I_MM,
    }
    points_mm = {
        name: (
            lid_inner_reference_sketch.modelToSketchSpace(create_point_mm(*point_mm)).x * 10.0,
            lid_inner_reference_sketch.modelToSketchSpace(create_point_mm(*point_mm)).y * 10.0,
        )
        for name, point_mm in points_3d_mm.items()
    }
    lid_inner_reference_sketch.deleteMe()

    circle_k_radius_mm = (
        get_distance_2d_mm(points_mm['I'], points_mm['F'])
        + get_distance_2d_mm(points_mm['I'], points_mm['G'])
    ) / 2.0
    points_mm['F'] = offset_point_from_circle(
        points_mm['I'],
        points_mm['F'],
        circle_k_radius_mm - get_distance_2d_mm(points_mm['I'], points_mm['F']),
    )
    points_mm['G'] = offset_point_from_circle(
        points_mm['I'],
        points_mm['G'],
        circle_k_radius_mm - get_distance_2d_mm(points_mm['I'], points_mm['G']),
    )
    circle_l_center_mm = get_tangent_circle_center_between_lines_mm(
        points_mm['I'],
        points_mm['F'],
        points_mm['G'],
        OUTER_SHELL_LID_GAP_CIRCLE_L_RADIUS_MM,
    )
    point_m_mm = project_point_to_line_mm(
        circle_l_center_mm,
        points_mm['I'],
        points_mm['F'],
    )
    tangent_points_n_mm = tangent_points_from_external_point_to_circle_mm(
        points_mm['H'],
        circle_l_center_mm,
        OUTER_SHELL_LID_GAP_CIRCLE_L_RADIUS_MM,
    )
    point_n_mm = min(
        tangent_points_n_mm,
        key=lambda point_mm: get_distance_2d_mm(point_mm, points_mm['I']),
    )
    point_p_mm = intersect_lines_2d_mm(
        points_mm['H'],
        point_n_mm,
        points_mm['G'],
        points_mm['I'],
    )

    sketch_points = {}
    for name, point_mm in points_mm.items():
        sketch_points[name] = sketch.sketchPoints.add(
            create_point_in_sketch_space_mm(*point_mm)
        )
    sketch_points['M'] = sketch.sketchPoints.add(
        create_point_in_sketch_space_mm(*point_m_mm)
    )
    sketch_points['N'] = sketch.sketchPoints.add(
        create_point_in_sketch_space_mm(*point_n_mm)
    )
    sketch_points['P'] = sketch.sketchPoints.add(
        create_point_in_sketch_space_mm(*point_p_mm)
    )

    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs

    lines.addByTwoPoints(sketch_points['G'], sketch_points['P'])
    lines.addByTwoPoints(sketch_points['P'], sketch_points['N'])
    lines.addByTwoPoints(sketch_points['M'], sketch_points['F'])

    angle_m_rad = angle_for_point_on_circle_mm(circle_l_center_mm, point_m_mm)
    angle_n_rad = angle_for_point_on_circle_mm(circle_l_center_mm, point_n_mm)
    angle_i_rad = angle_for_point_on_circle_mm(circle_l_center_mm, points_mm['I'])
    mid_angle_l_rad = midpoint_angle_rad(
        angle_m_rad,
        angle_n_rad,
        via_angle_rad=angle_i_rad,
    )
    arc_l_midpoint_mm = point_on_circle_from_angle_mm(
        circle_l_center_mm,
        OUTER_SHELL_LID_GAP_CIRCLE_L_RADIUS_MM,
        mid_angle_l_rad,
    )
    arcs.addByThreePoints(
        sketch_points['N'].geometry,
        create_point_in_sketch_space_mm(*arc_l_midpoint_mm),
        sketch_points['M'].geometry,
    )

    angle_f_rad = angle_for_point_on_circle_mm(points_mm['I'], points_mm['F'])
    angle_g_rad = angle_for_point_on_circle_mm(points_mm['I'], points_mm['G'])
    mid_angle_fg_rad = midpoint_angle_rad(
        angle_f_rad,
        angle_g_rad,
    )
    arc_fg_midpoint_mm = point_on_circle_from_angle_mm(
        points_mm['I'],
        circle_k_radius_mm,
        mid_angle_fg_rad,
    )
    arcs.addByThreePoints(
        sketch_points['F'].geometry,
        create_point_in_sketch_space_mm(*arc_fg_midpoint_mm),
        sketch_points['G'].geometry,
    )

    extension_profile_target_mm = (
        (points_mm['G'][0] + point_p_mm[0] + point_n_mm[0] + point_m_mm[0] + points_mm['F'][0]) / 5.0,
        (points_mm['G'][1] + point_p_mm[1] + point_n_mm[1] + point_m_mm[1] + points_mm['F'][1]) / 5.0,
    )

    return {
        'plane': sketch_plane,
        'sketch': sketch,
        'extension_profile_target_point': create_point_in_sketch_space_mm(*extension_profile_target_mm),
    }


def add_outer_shell_lid_gap_extension_fillet(
    root_comp,
    outer_shell_body,
    sketch,
    plane,
    inner_shell_body=None,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')
    if plane is None:
        raise RuntimeError('plane is required.')

    plane_geometry = adsk.core.Plane.cast(plane.geometry)
    if not plane_geometry:
        raise RuntimeError('外殻蓋部斜面隙間部平面のジオメトリを取得できませんでした。')

    normal = plane_geometry.normal.copy()
    if normal.length <= 1e-9:
        raise RuntimeError('外殻蓋部斜面隙間部平面の法線を取得できませんでした。')
    normal.normalize()

    geometry_mm = calculate_outer_shell_lid_gap_extension_profile_geometry_mm(
        root_comp,
        inner_shell_body=inner_shell_body,
    )
    reference_points_2d = {
        'arc_nm': geometry_mm['arc_nm_midpoint_mm'],
        'line_pn': (
            (geometry_mm['point_p_mm'][0] + geometry_mm['point_n_mm'][0]) / 2.0,
            (geometry_mm['point_p_mm'][1] + geometry_mm['point_n_mm'][1]) / 2.0,
        ),
        'line_mf': (
            (geometry_mm['point_m_mm'][0] + geometry_mm['points_mm']['F'][0]) / 2.0,
            (geometry_mm['point_m_mm'][1] + geometry_mm['points_mm']['F'][1]) / 2.0,
        ),
        'face_f': geometry_mm['points_mm']['F'],
        'face_g': geometry_mm['points_mm']['G'],
        'face_center': geometry_mm['extension_profile_target_mm'],
    }
    translated_points_mm = {}
    offset_distance_cm = mm_to_cm(OUTER_SHELL_LID_GAP_EXTENSION_EXTRUDE_DISTANCE_MM)

    for key, point_2d_mm in reference_points_2d.items():
        model_point = sketch.sketchToModelSpace(
            create_point_in_sketch_space_mm(*point_2d_mm)
        )
        translated_point = adsk.core.Point3D.create(
            model_point.x - (normal.x * offset_distance_cm),
            model_point.y - (normal.y * offset_distance_cm),
            model_point.z - (normal.z * offset_distance_cm),
        )
        translated_points_mm[key] = point3d_to_mm_tuple(translated_point)

    target_face = find_best_planar_face_near_reference_points(
        outer_shell_body,
        (
            translated_points_mm['face_f'],
            translated_points_mm['face_g'],
            translated_points_mm['face_center'],
        ),
    )

    selected_tokens = set()
    arc_edge = get_face_edge_nearest_point(
        target_face,
        translated_points_mm['arc_nm'],
        excluded_tokens=selected_tokens,
        require_non_linear=True,
    )
    selected_tokens.add(arc_edge.entityToken)

    line_pn_edge = get_face_edge_nearest_point(
        target_face,
        translated_points_mm['line_pn'],
        excluded_tokens=selected_tokens,
        require_linear=True,
    )
    selected_tokens.add(line_pn_edge.entityToken)

    line_mf_edge = get_face_edge_nearest_point(
        target_face,
        translated_points_mm['line_mf'],
        excluded_tokens=selected_tokens,
        require_linear=True,
    )

    apply_constant_radius_fillets(
        root_comp,
        [arc_edge, line_pn_edge, line_mf_edge],
        OUTER_SHELL_LID_GAP_EXTENSION_FILLET_RADIUS_MM,
        tangent_chain=False,
    )


def extrude_outer_shell_lid_gap_extension_region(
    root_comp,
    outer_shell_body,
    sketch,
    plane,
    profile_target_point,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')
    if sketch is None:
        raise RuntimeError('sketch is required.')
    if plane is None:
        raise RuntimeError('plane is required.')
    if profile_target_point is None:
        raise RuntimeError('profile_target_point is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    profile = get_profile_nearest_point(sketch, profile_target_point)
    plane_geometry = adsk.core.Plane.cast(plane.geometry)
    if not plane_geometry:
        raise RuntimeError('外殻蓋部斜面隙間部平面のジオメトリを取得できませんでした。')

    direction = adsk.fusion.ExtentDirections.NegativeExtentDirection
    extrudes = root_comp.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile,
        adsk.fusion.FeatureOperations.JoinFeatureOperation,
    )
    extrude_input.participantBodies = [current_outer_shell_body]
    distance_value = adsk.core.ValueInput.createByReal(
        mm_to_cm(OUTER_SHELL_LID_GAP_EXTENSION_EXTRUDE_DISTANCE_MM)
    )
    extrude_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(distance_value),
        direction,
    )
    extrudes.add(extrude_input)

    updated_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if updated_outer_shell_body is None:
        updated_outer_shell_body = current_outer_shell_body
    add_outer_shell_lid_gap_extension_fillet(
        root_comp,
        updated_outer_shell_body,
        sketch,
        plane,
    )
    return updated_outer_shell_body


def add_model_points_to_sketch(sketch, point_map_mm):
    sketch_points = {}
    for name, point_mm in point_map_mm.items():
        sketch_points[name] = sketch.sketchPoints.add(
            to_sketch_space(sketch, point_mm)
        )
    return sketch_points


def add_closed_polyline_to_sketch(sketch, sketch_points, point_names):
    lines = sketch.sketchCurves.sketchLines
    for start_name, end_name in zip(point_names, point_names[1:] + point_names[:1]):
        lines.addByTwoPoints(
            sketch_points[start_name],
            sketch_points[end_name],
        )


def create_outer_shell_lower_stop_sketch_1(root_comp):
    plane = create_offset_plane_from_yz(
        root_comp,
        OUTER_SHELL_LID_YZ_CUT_PLANE_X_MM,
        OUTER_SHELL_LOWER_STOP_SKETCH_1_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_LOWER_STOP_SKETCH_1_NAME
    sketch_points = add_model_points_to_sketch(
        sketch,
        OUTER_SHELL_LOWER_STOP_SKETCH1_POINTS_MM,
    )
    add_closed_polyline_to_sketch(sketch, sketch_points, ['A', 'B', 'D', 'C'])
    return sketch


def create_outer_shell_lower_stop_sketch_2(root_comp):
    plane = create_plane_by_three_points(
        root_comp,
        OUTER_SHELL_LOWER_STOP_SKETCH2_POINTS_MM['E'],
        OUTER_SHELL_LOWER_STOP_SKETCH2_POINTS_MM['F'],
        OUTER_SHELL_LOWER_STOP_SKETCH2_POINTS_MM['G'],
        OUTER_SHELL_LOWER_STOP_SKETCH_2_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_LOWER_STOP_SKETCH_2_NAME
    add_model_points_to_sketch(
        sketch,
        OUTER_SHELL_LOWER_STOP_SKETCH2_POINTS_MM,
    )
    return sketch


def create_outer_shell_lower_stop_sketch_3(root_comp):
    point_map_mm = dict(OUTER_SHELL_LOWER_STOP_SKETCH1_POINTS_MM)
    point_map_mm.update(OUTER_SHELL_LOWER_STOP_SKETCH3_POINTS_MM)
    plane = create_plane_by_three_points(
        root_comp,
        point_map_mm['B'],
        point_map_mm['H'],
        point_map_mm['I'],
        OUTER_SHELL_LOWER_STOP_SKETCH_3_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_LOWER_STOP_SKETCH_3_NAME
    sketch_points = add_model_points_to_sketch(
        sketch,
        {
            'B': point_map_mm['B'],
            'H': point_map_mm['H'],
            'I': point_map_mm['I'],
            'J': point_map_mm['J'],
        },
    )
    add_closed_polyline_to_sketch(sketch, sketch_points, ['B', 'H', 'I', 'J'])
    return sketch


def create_outer_shell_lower_stop_sketch_4(root_comp):
    plane = create_offset_plane_from_xy(
        root_comp,
        OUTER_SHELL_LOWER_STOP_SKETCH4_POINTS_MM['K'][2],
        OUTER_SHELL_LOWER_STOP_SKETCH_4_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_LOWER_STOP_SKETCH_4_NAME

    points_2d_mm = {
        name: (point_mm[0], point_mm[1])
        for name, point_mm in OUTER_SHELL_LOWER_STOP_SKETCH4_POINTS_MM.items()
    }
    sketch_points = {
        name: sketch.sketchPoints.add(create_point_in_sketch_space_mm(*point_mm))
        for name, point_mm in points_2d_mm.items()
    }

    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    lines.addByTwoPoints(sketch_points['K'], sketch_points['L'])
    lines.addByTwoPoints(sketch_points['M'], sketch_points['N'])

    center_o_mm = points_2d_mm['O']
    radius_ol_mm = get_distance_2d_mm(center_o_mm, points_2d_mm['L'])
    angle_l_rad = angle_for_point_on_circle_mm(center_o_mm, points_2d_mm['L'])
    angle_m_rad = angle_for_point_on_circle_mm(center_o_mm, points_2d_mm['M'])
    midpoint_lm_rad = midpoint_angle_rad(angle_l_rad, angle_m_rad)
    arc_lm_midpoint_mm = point_on_circle_from_angle_mm(
        center_o_mm,
        radius_ol_mm,
        midpoint_lm_rad,
    )
    arcs.addByThreePoints(
        sketch_points['L'].geometry,
        create_point_in_sketch_space_mm(*arc_lm_midpoint_mm),
        sketch_points['M'].geometry,
    )

    radius_ok_mm = get_distance_2d_mm(center_o_mm, points_2d_mm['K'])
    angle_n_rad = angle_for_point_on_circle_mm(center_o_mm, points_2d_mm['N'])
    angle_k_rad = angle_for_point_on_circle_mm(center_o_mm, points_2d_mm['K'])
    midpoint_nk_rad = midpoint_angle_rad(angle_n_rad, angle_k_rad)
    arc_nk_midpoint_mm = point_on_circle_from_angle_mm(
        center_o_mm,
        radius_ok_mm,
        midpoint_nk_rad,
    )
    arcs.addByThreePoints(
        sketch_points['N'].geometry,
        create_point_in_sketch_space_mm(*arc_nk_midpoint_mm),
        sketch_points['K'].geometry,
    )

    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        create_point_in_sketch_space_mm(*center_o_mm),
        mm_to_cm(get_distance_2d_mm(center_o_mm, points_2d_mm['P'])),
    )
    return sketch


def create_outer_shell_lower_stop_arc_cut_support_sketch(root_comp):
    plane = create_offset_plane_from_xy(
        root_comp,
        OUTER_SHELL_LOWER_STOP_SKETCH4_POINTS_MM['K'][2],
    )
    sketch = root_comp.sketches.add(plane)
    points_2d_mm = {
        name: (point_mm[0], point_mm[1])
        for name, point_mm in OUTER_SHELL_LOWER_STOP_SKETCH4_POINTS_MM.items()
        if name in ('K', 'L', 'M', 'N', 'O')
    }
    sketch_points = {
        name: sketch.sketchPoints.add(create_point_in_sketch_space_mm(*point_mm))
        for name, point_mm in points_2d_mm.items()
    }
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    lines.addByTwoPoints(sketch_points['K'], sketch_points['L'])
    lines.addByTwoPoints(sketch_points['M'], sketch_points['N'])

    center_o_mm = points_2d_mm['O']
    radius_ol_mm = get_distance_2d_mm(center_o_mm, points_2d_mm['L'])
    angle_l_rad = angle_for_point_on_circle_mm(center_o_mm, points_2d_mm['L'])
    angle_m_rad = angle_for_point_on_circle_mm(center_o_mm, points_2d_mm['M'])
    midpoint_lm_rad = midpoint_angle_rad(angle_l_rad, angle_m_rad)
    arc_lm_midpoint_mm = point_on_circle_from_angle_mm(
        center_o_mm,
        radius_ol_mm,
        midpoint_lm_rad,
    )
    arcs.addByThreePoints(
        sketch_points['L'].geometry,
        create_point_in_sketch_space_mm(*arc_lm_midpoint_mm),
        sketch_points['M'].geometry,
    )

    radius_ok_mm = get_distance_2d_mm(center_o_mm, points_2d_mm['K'])
    angle_n_rad = angle_for_point_on_circle_mm(center_o_mm, points_2d_mm['N'])
    angle_k_rad = angle_for_point_on_circle_mm(center_o_mm, points_2d_mm['K'])
    midpoint_nk_rad = midpoint_angle_rad(angle_n_rad, angle_k_rad)
    arc_nk_midpoint_mm = point_on_circle_from_angle_mm(
        center_o_mm,
        radius_ok_mm,
        midpoint_nk_rad,
    )
    arcs.addByThreePoints(
        sketch_points['N'].geometry,
        create_point_in_sketch_space_mm(*arc_nk_midpoint_mm),
        sketch_points['K'].geometry,
    )
    return sketch


def create_outer_shell_lower_stop_circle_cut_support_sketch(root_comp):
    plane = create_offset_plane_from_xy(
        root_comp,
        OUTER_SHELL_LOWER_STOP_SKETCH4_POINTS_MM['K'][2],
    )
    sketch = root_comp.sketches.add(plane)
    center_o_mm = (
        OUTER_SHELL_LOWER_STOP_SKETCH4_POINTS_MM['O'][0],
        OUTER_SHELL_LOWER_STOP_SKETCH4_POINTS_MM['O'][1],
    )
    point_p_mm = (
        OUTER_SHELL_LOWER_STOP_SKETCH4_POINTS_MM['P'][0],
        OUTER_SHELL_LOWER_STOP_SKETCH4_POINTS_MM['P'][1],
    )
    sketch.sketchCurves.sketchCircles.addByCenterRadius(
        create_point_in_sketch_space_mm(*center_o_mm),
        mm_to_cm(get_distance_2d_mm(center_o_mm, point_p_mm)),
    )
    return sketch


def create_outer_shell_lower_stop_sketch_5(root_comp):
    sketch = root_comp.sketches.add(root_comp.yZConstructionPlane)
    sketch.name = OUTER_SHELL_LOWER_STOP_SKETCH_5_NAME
    sketch_points = add_model_points_to_sketch(
        sketch,
        OUTER_SHELL_LOWER_STOP_SKETCH5_POINTS_MM,
    )
    add_closed_polyline_to_sketch(sketch, sketch_points, ['Q', 'R', 'S', 'T', 'U', 'V', 'W'])
    return sketch


def create_outer_shell_lower_stop_support_sketch(root_comp, lower_stop_body):
    if lower_stop_body is None:
        raise RuntimeError('lower_stop_body is required.')

    plane = create_offset_plane_from_yz(
        root_comp,
        -OUTER_SHELL_LOWER_STOP_EXTRUDE_DISTANCE_MM,
        OUTER_SHELL_LOWER_STOP_SUPPORT_SKETCH_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_LOWER_STOP_SUPPORT_SKETCH_NAME
    projected_entities = to_entity_list(
        sketch.intersectWithSketchPlane([lower_stop_body])
    )
    if not projected_entities:
        raise RuntimeError('外殻下部受止のフィレット後断面を取得できませんでした。')

    for projected_entity in projected_entities:
        sketch_curve = adsk.fusion.SketchCurve.cast(projected_entity)
        if sketch_curve:
            sketch_curve.isConstruction = False
    return sketch


def create_outer_shell_lower_stop_loft_sketch(root_comp):
    point_map_mm = dict(OUTER_SHELL_LOWER_STOP_SKETCH1_POINTS_MM)
    point_map_mm.update(OUTER_SHELL_LOWER_STOP_SKETCH3_POINTS_MM)
    point_map_mm.update({
        'Up': offset_point_x_mm(OUTER_SHELL_LOWER_STOP_SKETCH5_POINTS_MM['U'], -OUTER_SHELL_LOWER_STOP_EXTRUDE_DISTANCE_MM),
        'Vp': offset_point_x_mm(OUTER_SHELL_LOWER_STOP_SKETCH5_POINTS_MM['V'], -OUTER_SHELL_LOWER_STOP_EXTRUDE_DISTANCE_MM),
    })
    plane = create_plane_by_three_points(
        root_comp,
        point_map_mm['B'],
        point_map_mm['J'],
        point_map_mm['Up'],
        OUTER_SHELL_LOWER_STOP_LOFT_SKETCH_NAME,
    )
    sketch = root_comp.sketches.add(plane)
    sketch.name = OUTER_SHELL_LOWER_STOP_LOFT_SKETCH_NAME
    sketch_points = add_model_points_to_sketch(
        sketch,
        {
            'B': point_map_mm['B'],
            'J': point_map_mm['J'],
            'Up': point_map_mm['Up'],
            'Vp': point_map_mm['Vp'],
        },
    )
    add_closed_polyline_to_sketch(sketch, sketch_points, ['B', 'J', 'Up', 'Vp'])
    return sketch


def loft_profiles(root_comp, profile_a, profile_b):
    lofts = root_comp.features.loftFeatures
    loft_input = lofts.createInput(adsk.fusion.FeatureOperations.JoinFeatureOperation)
    loft_input.isSolid = True
    loft_input.loftSections.add(profile_a)
    loft_input.loftSections.add(profile_b)
    lofts.add(loft_input)


def loft_profiles_new_body(root_comp, profile_a, profile_b):
    lofts = root_comp.features.loftFeatures
    loft_input = lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    loft_input.isSolid = True
    loft_input.loftSections.add(profile_a)
    loft_input.loftSections.add(profile_b)
    feature = lofts.add(loft_input)
    return get_body_from_feature(feature)


def add_outer_shell_lower_stop_structure(root_comp, outer_shell_body, inner_shell_body=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_body is None:
        raise RuntimeError('outer_shell_body is required.')

    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    )
    if current_outer_shell_body is None:
        current_outer_shell_body = outer_shell_body

    sketch_1 = create_outer_shell_lower_stop_sketch_1(root_comp)
    create_outer_shell_lower_stop_sketch_2(root_comp)
    sketch_3 = create_outer_shell_lower_stop_sketch_3(root_comp)
    create_outer_shell_lower_stop_sketch_4(root_comp)
    arc_cut_sketch = create_outer_shell_lower_stop_arc_cut_support_sketch(root_comp)
    circle_cut_sketch = create_outer_shell_lower_stop_circle_cut_support_sketch(root_comp)
    sketch_5 = create_outer_shell_lower_stop_sketch_5(root_comp)
    loft_sketch = create_outer_shell_lower_stop_loft_sketch(root_comp)

    lower_stop_body = extrude_profile_in_negative_x_from_sketch_new_body(
        root_comp,
        sketch_5,
        get_largest_profile(sketch_5),
        OUTER_SHELL_LOWER_STOP_EXTRUDE_DISTANCE_MM,
    )

    for point_name in ('Q', 'R'):
        extruded_point_mm = offset_point_x_mm(
            OUTER_SHELL_LOWER_STOP_SKETCH5_POINTS_MM[point_name],
            -OUTER_SHELL_LOWER_STOP_EXTRUDE_DISTANCE_MM,
        )
        target_point_mm = get_midpoint_mm(
            OUTER_SHELL_LOWER_STOP_SKETCH5_POINTS_MM[point_name],
            extruded_point_mm,
        )
        edge = find_linear_edge_parallel_to_x_near_point(
            lower_stop_body,
            target_point_mm,
        )
        apply_constant_radius_fillet(
            root_comp,
            edge,
            OUTER_SHELL_LOWER_STOP_FILLET_RADIUS_MM,
            tangent_chain=False,
        )

    support_sketch = create_outer_shell_lower_stop_support_sketch(
        root_comp,
        lower_stop_body,
    )

    current_inner_shell_body = inner_shell_body
    if current_inner_shell_body is None:
        current_inner_shell_body = helpers.find_body_by_name_or_attribute(
            root_comp,
            naming.BODY_INNER_SHELL,
        )

    moved_inner_shell_body = None
    if current_inner_shell_body is not None:
        moved_inner_shell_body = move_body_by_translation(
            root_comp,
            current_inner_shell_body,
            x_mm=INNER_SHELL_TEMP_MOVE_X_MM,
        )

    try:
        lower_stop_loft_body_1 = loft_profiles_new_body(
            root_comp,
            get_largest_profile(support_sketch),
            get_largest_profile(sketch_1),
        )
        lower_stop_loft_body_2 = loft_profiles_new_body(
            root_comp,
            get_largest_profile(sketch_3),
            get_largest_profile(loft_sketch),
        )
        current_outer_shell_body = join_tool_bodies_into_target(
            root_comp,
            current_outer_shell_body,
            [lower_stop_body, lower_stop_loft_body_1, lower_stop_loft_body_2],
        )

        arc_profile = get_largest_profile(arc_cut_sketch)
        cut_profile_in_positive_z(
            root_comp,
            arc_cut_sketch,
            arc_profile,
            current_outer_shell_body,
            OUTER_SHELL_LOWER_STOP_ARC_POSITIVE_Z_CUT_DISTANCE_MM,
        )
        cut_profile_in_negative_z(
            root_comp,
            arc_cut_sketch,
            arc_profile,
            current_outer_shell_body,
            OUTER_SHELL_LOWER_STOP_ARC_CUT_DISTANCE_MM,
        )

        circle_profile = get_largest_profile(circle_cut_sketch)
        cut_profile_in_positive_z(
            root_comp,
            circle_cut_sketch,
            circle_profile,
            current_outer_shell_body,
            OUTER_SHELL_LOWER_STOP_CIRCLE_POSITIVE_Z_CUT_DISTANCE_MM,
        )
        cut_profile_in_negative_z(
            root_comp,
            circle_cut_sketch,
            circle_profile,
            current_outer_shell_body,
            OUTER_SHELL_LOWER_STOP_ARC_CUT_DISTANCE_MM,
        )
    finally:
        if moved_inner_shell_body is not None:
            move_body_by_translation(
                root_comp,
                moved_inner_shell_body,
                x_mm=-INNER_SHELL_TEMP_MOVE_X_MM,
            )

    return helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    ) or current_outer_shell_body


def add_outer_shell_l_button_opening_offset_fillet(root_comp, outer_shell_body):
    _ = root_comp
    _ = outer_shell_body
    # 外殻Lボタン開口部の 6 mm フィレットは適用しない。
    return


def build_outer_shell_base_structure(root_comp, inner_shell_body, params=None):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if inner_shell_body is None:
        raise RuntimeError('inner_shell_body is required to build the outer shell base structure.')

    if params is None:
        params = dict(naming.DEFAULT_OUTER_SHELL_PARAMS)

    sketch = create_outer_shell_sketch(root_comp, inner_shell_body, params)
    outer_shell_body = extrude_outer_shell_profile(root_comp, sketch, inner_shell_body)
    add_outer_perimeter_face(root_comp, outer_shell_body)
    add_bottom_outer_face(root_comp, outer_shell_body)
    reference_circle_sketch = create_outer_perimeter_reference_circle_sketch(root_comp)
    bottom_outer_sketch = create_bottom_outer_face_sketch(root_comp, outer_shell_body)
    extrude_bottom_outer_region(root_comp, bottom_outer_sketch)
    outer_shell_body = split_outer_shell_by_lid_inner_plane(root_comp, outer_shell_body, inner_shell_body)
    outer_shell_body = extrude_outer_shell_lid_inner_plane_in_positive_z(
        root_comp,
        outer_shell_body,
        inner_shell_body,
    )
    cut_outer_perimeter_reference_circle(root_comp, reference_circle_sketch, outer_shell_body, inner_shell_body)
    outer_shell_body = cut_outer_shell_by_lid_yz_plane(root_comp, outer_shell_body)
    return outer_shell_body


def add_structures_to_outer_shell_base_structure(
    root_comp,
    outer_shell_base_structure_body,
    inner_shell_body,
    params=None,
):
    if root_comp is None:
        raise RuntimeError('root_comp is required.')
    if outer_shell_base_structure_body is None:
        raise RuntimeError('outer_shell_base_structure_body is required.')

    _ = params
    current_outer_shell_body = outer_shell_base_structure_body
    opening_data = create_outer_shell_l_button_opening_sketch(
        root_comp,
        current_outer_shell_body,
    )
    extrude_outer_shell_l_button_opening_region(
        root_comp,
        current_outer_shell_body,
        opening_data['sketch'],
    )
    end_cut_data = create_outer_shell_end_cut_sketch(
        root_comp,
        current_outer_shell_body,
    )
    cut_outer_shell_end_region(
        root_comp,
        current_outer_shell_body,
        end_cut_data['sketch'],
        end_cut_data['face'],
    )
    side_extension_data = create_outer_shell_side_extension_sketch(
        root_comp,
        current_outer_shell_body,
    )
    extrude_outer_shell_side_extension_region(
        root_comp,
        current_outer_shell_body,
        side_extension_data['sketch'],
        side_extension_data['face'],
    )
    fitting_adjustment_data = create_outer_shell_fitting_adjustment_sketch(
        root_comp,
        current_outer_shell_body,
    )
    cut_outer_shell_fitting_adjustment_region(
        root_comp,
        current_outer_shell_body,
        fitting_adjustment_data['sketch'],
        fitting_adjustment_data['face'],
    )
    add_outer_shell_l_button_opening_offset_fillet(
        root_comp,
        current_outer_shell_body,
    )
    current_outer_shell_body = split_outer_shell_by_lid_inner_plane(
        root_comp,
        current_outer_shell_body,
        inner_shell_body,
    )
    lid_gap_data = create_outer_shell_lid_gap_sketch(
        root_comp,
        current_outer_shell_body,
        inner_shell_body=inner_shell_body,
    )
    lid_gap_extension_data = create_outer_shell_lid_gap_extension_sketch(
        root_comp,
        current_outer_shell_body,
        inner_shell_body=inner_shell_body,
    )
    opening_base_data = create_outer_shell_l_button_opening_base_structure_sketch(
        root_comp,
        current_outer_shell_body,
    )
    cut_outer_shell_l_button_opening_base_structure_region(
        root_comp,
        current_outer_shell_body,
        inner_shell_body,
        opening_base_data['sketch'],
        opening_base_data['face'],
    )
    add_outer_shell_l_button_opening_base_structure_fillets(
        root_comp,
        current_outer_shell_body,
    )
    slope_cut_data = create_outer_shell_l_button_opening_slope_cut_sketch(
        root_comp,
        current_outer_shell_body,
    )
    cut_outer_shell_l_button_opening_slope_region(
        root_comp,
        current_outer_shell_body,
        slope_cut_data['sketch'],
        slope_cut_data['face'],
    )
    inner_spec_data = create_outer_shell_l_button_opening_inner_spec_sketch(
        root_comp,
        current_outer_shell_body,
    )
    cut_outer_shell_l_button_opening_inner_spec_region(
        root_comp,
        current_outer_shell_body,
        inner_spec_data['sketch'],
        inner_spec_data['axis_line'],
        inner_shell_body=inner_shell_body,
    )
    y32_cut_data = create_outer_shell_l_button_opening_y32_cut_sketch(
        root_comp,
        current_outer_shell_body,
    )
    cut_outer_shell_l_button_opening_y32_region(
        root_comp,
        current_outer_shell_body,
        y32_cut_data['sketch'],
        inner_shell_body=inner_shell_body,
    )
    current_outer_shell_body = helpers.find_body_by_name_or_attribute(
        root_comp,
        naming.BODY_OUTER_SHELL,
    ) or current_outer_shell_body
    current_outer_shell_body = extrude_outer_shell_lid_gap_region(
        root_comp,
        current_outer_shell_body,
        lid_gap_data['sketch'],
        lid_gap_data['plane'],
        lid_gap_data['primary_profile_target_point'],
    )
    current_outer_shell_body = extrude_outer_shell_lid_gap_extension_region(
        root_comp,
        current_outer_shell_body,
        lid_gap_extension_data['sketch'],
        lid_gap_extension_data['plane'],
        lid_gap_extension_data['extension_profile_target_point'],
    )
    current_outer_shell_body = add_outer_shell_lower_stop_structure(
        root_comp,
        current_outer_shell_body,
        inner_shell_body=inner_shell_body,
    )
    lid_decoration_cut_1_data = create_outer_shell_lid_decoration_cut_1_sketch(
        root_comp,
        current_outer_shell_body,
    )
    current_outer_shell_body = cut_outer_shell_lid_decoration_cut_1_region(
        root_comp,
        current_outer_shell_body,
        lid_decoration_cut_1_data['sketch'],
        lid_decoration_cut_1_data['axis_line'],
    )
    lid_decoration_cut_2_data = create_outer_shell_lid_decoration_cut_2_sketch(
        root_comp,
        current_outer_shell_body,
    )
    current_outer_shell_body = cut_outer_shell_lid_decoration_cut_2_region(
        root_comp,
        current_outer_shell_body,
        lid_decoration_cut_2_data['sketch'],
    )
    lid_decoration_cut_3_data = create_outer_shell_lid_decoration_cut_3_faces(
        root_comp,
        current_outer_shell_body,
    )
    current_outer_shell_body = cut_outer_shell_lid_decoration_cut_3_region(
        root_comp,
        current_outer_shell_body,
        lid_decoration_cut_3_data['face_1'],
        lid_decoration_cut_3_data['face_2'],
    )
    lid_decoration_cut_4_data = create_outer_shell_lid_decoration_cut_4_sketch(
        root_comp,
        current_outer_shell_body,
    )
    current_outer_shell_body = cut_outer_shell_lid_decoration_cut_4_region(
        root_comp,
        current_outer_shell_body,
        lid_decoration_cut_4_data['sketch'],
        lid_decoration_cut_4_data['axis_line'],
    )
    lid_decoration_cut_5_data = create_outer_shell_lid_decoration_cut_5_sketch(
        root_comp,
        current_outer_shell_body,
    )
    current_outer_shell_body = cut_outer_shell_lid_decoration_cut_5_region(
        root_comp,
        current_outer_shell_body,
        lid_decoration_cut_5_data['sketch'],
    )
    current_outer_shell_body = add_outer_shell_fitting_correction(
        root_comp,
        current_outer_shell_body,
        inner_shell_body=inner_shell_body,
    )
    current_outer_shell_body = extrude_outer_shell_bottom_outer_slope(
        root_comp,
        current_outer_shell_body,
    )
    current_outer_shell_body = cut_outer_shell_bottom_outer_slope_regions(
        root_comp,
        current_outer_shell_body,
        inner_shell_body=inner_shell_body,
    )
    return current_outer_shell_body


def build_outer_shell(root_comp, inner_shell_body, params=None):
    outer_shell_base_structure_body = build_outer_shell_base_structure(
        root_comp,
        inner_shell_body,
        params,
    )
    return add_structures_to_outer_shell_base_structure(
        root_comp,
        outer_shell_base_structure_body,
        inner_shell_body,
        params,
    )
