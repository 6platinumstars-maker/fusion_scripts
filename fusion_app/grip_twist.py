"""Two-plane finger closure, independent of the Fusion runtime. Units: mm."""
import math


def add(a, b): return tuple(x+y for x, y in zip(a, b))
def sub(a, b): return tuple(x-y for x, y in zip(a, b))
def mul(a, s): return tuple(x*s for x in a)
def dot(a, b): return sum(x*y for x, y in zip(a, b))
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a): return math.sqrt(dot(a, a))
def unit(a):
    if norm(a) < 1e-12: raise ValueError('指の回転軸を定義できません。')
    return mul(a, 1/norm(a))
def rotate(v, axis, angle):
    c, s = math.cos(angle), math.sin(angle)
    return add(add(mul(v, c), mul(cross(axis, v), s)), mul(axis, dot(axis, v)*(1-c)))
def angle(a, b): return math.degrees(math.acos(max(-1., min(1., dot(unit(a), unit(b))))))


def solve(data, twist_deg, b_plane_normal, reference_normal, joint_index=2):
    """Preserve lengths and other bends; solve bend at the twist joint, then pose.

    Pose minimizes summed squared joint displacement about fixed GP.
    Choose twist handedness by the next joint's distance to BJ prime after closure.
    """
    if joint_index not in (1, 2, 3):
        raise ValueError('ねじり関節はG1、G2またはG3を指定してください。')
    k = joint_index
    if not math.isfinite(twist_deg) or not 0 <= twist_deg < 180:
        raise ValueError('ねじり角は0以上180度未満で指定してください。')
    if k == 1:
        return solve_g1(data, twist_deg, b_plane_normal, reference_normal)
    if twist_deg == 0: return dict(data, twist_deg=0., twist_joint_index=k)
    old = data['points_mm']; g, p = old[0], old[-1]
    q = [sub(x, g) for x in old]
    target = norm(q[-1]); gp = unit(q[-1])
    u = unit(sub(q[k], q[k-1]))
    bend_axis = unit(cross(u, sub(q[k+1], q[k])))
    original_bend = math.radians(180-data['angles_deg'][k])
    bn = unit(b_plane_normal)
    candidates = []
    for sign in (-1, 1):
        twist = math.radians(sign*twist_deg)
        def shape(bend):
            return q[:k+1] + [add(q[k], rotate(rotate(sub(x, q[k]), bend_axis,
                          bend-original_bend), u, twist)) for x in q[k+1:]]
        def error(bend): return norm(shape(bend)[-1])-target
        roots = []
        low = 1e-8; f_low = error(low)
        for step in range(1, 721):
            high = 1e-8 + (math.pi-2e-8)*step/720
            f_high = error(high)
            if f_low*f_high <= 0:
                lo, hi, flo = low, high, f_low
                for _ in range(60):
                    mid = (lo+hi)/2; fm = error(mid)
                    if flo*fm <= 0: hi = mid
                    else: lo, flo = mid, fm
                roots.append((lo+hi)/2)
            low, f_low = high, f_high
        for bend in roots:
            pts = shape(bend)
            end = unit(pts[-1]); axis = cross(end, gp)
            if norm(axis) > 1e-12:
                axis = unit(axis); turn = math.atan2(norm(cross(end, gp)), dot(end, gp))
                pts = [rotate(x, axis, turn) for x in pts]
            elif dot(end, gp) < 0:
                pts = [rotate(x, unit(cross(end, u)), math.pi) for x in pts]
            # Closed-form best rotation around GP for all four interior joints.
            c = sum(dot(x, y)-dot(x, gp)*dot(y, gp) for x, y in zip(pts[1:5], q[1:5]))
            s = sum(dot(cross(gp, x), y) for x, y in zip(pts[1:5], q[1:5]))
            pts = [rotate(x, gp, math.atan2(s, c)) for x in pts]
            distance = abs(dot(pts[k+1], bn))
            movement = sum(norm(sub(x, y))**2 for x, y in zip(pts, q))
            candidates.append((distance, movement, bend, sign, pts))
    approaching = [c for c in candidates if c[0] < abs(dot(q[k+1], bn))-1e-8]
    if not approaching:
        raise ValueError('指定ねじり角では、到達点P固定かつBの関節平面BJ′へ近づく解がありません。')
    # Closest bend branch first; handedness is selected toward BJ prime.
    chosen = min(approaching, key=lambda c: (abs(c[2]-original_bend), c[1]))
    distance, movement, bend, sign, pts = chosen
    result = [add(g, x) for x in pts]
    if norm(sub(result[-1], p)) > 1e-7: raise ValueError('到達点Pへの接続誤差が大きすぎます。')
    result[0], result[-1] = g, p
    angles = [math.degrees(math.asin(min(1., abs(dot(unit(sub(result[1], g)), unit(reference_normal))))))]
    angles += [angle(sub(result[i-1], result[i]), sub(result[i+1], result[i])) for i in range(1,5)]
    return dict(data, points_mm=result, angles_deg=tuple(angles), twist_deg=twist_deg,
                signed_twist_deg=sign*twist_deg, twist_joint_index=k,
                direction_point_index=k+1, baseline_angles_deg=data['angles_deg'],
                direction_point_b_plane_distance_before_mm=abs(dot(q[k+1], bn)),
                direction_point_b_plane_distance_after_mm=distance)


def solve_g1(data, twist_deg, b_plane_normal, reference_normal):
    """Keep bends; twist about GG1, then minimally align the endpoint with GP.

    No extra GP roll: that would cancel a G1 twist. Transport the original
    front-plane normal through the same root rotation to define the L0 width.
    """
    old=data['points_mm'];g,p=old[0],old[-1]
    q=[sub(x,g) for x in old];u=unit(q[1]);gp=unit(q[-1])
    front=unit(cross(q[1],sub(q[2],q[1])))
    bn=unit(b_plane_normal)
    before=abs(dot(q[2],bn))
    candidates=[]
    for sign in (-1,1):
        theta=math.radians(sign*twist_deg)
        pts=q[:2]+[add(q[1],rotate(sub(x,q[1]),u,theta)) for x in q[2:]]
        end=unit(pts[-1]);axis=cross(end,gp);n=front
        if norm(axis)>1e-12:
            turn=math.atan2(norm(axis),dot(end,gp));axis=unit(axis)
            pts=[rotate(x,axis,turn) for x in pts]
            n=rotate(front,axis,turn)
        elif dot(end,gp)<0:
            axis=unit(cross(end,front))
            pts=[rotate(x,axis,math.pi) for x in pts];n=rotate(front,axis,math.pi)
        distance=abs(dot(pts[2],bn))
        movement=sum(norm(sub(a,b))**2 for a,b in zip(pts,q))
        if twist_deg==0 or distance<before-1e-8:
            candidates.append((movement,distance,sign,pts,n))
    if not candidates:
        raise ValueError('G1ねじりでP固定かつBの関節面へ近づく解がありません。')
    _,distance,sign,pts,front_normal=min(candidates,key=lambda c:(c[0],c[1]))
    result=[add(g,x) for x in pts]
    if norm(sub(result[-1],p))>1e-7:raise ValueError('G1ねじりの到達点誤差が大きすぎます。')
    result[0],result[-1]=g,p
    angles=[math.degrees(math.asin(min(1.,abs(dot(unit(sub(result[1],g)),unit(reference_normal))))))]
    angles += [angle(sub(result[i-1],result[i]),sub(result[i+1],result[i])) for i in range(1,5)]
    if twist_deg==0:result=list(old);angles=data['angles_deg']
    return dict(data,points_mm=result,angles_deg=tuple(angles),twist_deg=twist_deg,
                signed_twist_deg=sign*twist_deg,twist_joint_index=1,
                front_plane_normal=front_normal,direction_point_index=2,
                baseline_angles_deg=data['angles_deg'],
                direction_point_b_plane_distance_before_mm=before,
                direction_point_b_plane_distance_after_mm=distance)
