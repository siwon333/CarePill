import numpy as np

# MediaPipe FaceMesh indices (left/right)
LEFT_EYE_IDX = [33,133,159,158,153,145]   # p1,p4,p2,p3,p5,p6
RIGHT_EYE_IDX = [362,263,386,385,380,374]

# Corners for normalization
LEFT_HORIZONTAL = (33,133)
RIGHT_HORIZONTAL = (362,263)

IRIS_CENTER = (468, 473)  # left, right

def _pt(lms, i, w, h):
    lm = lms[i]
    return np.array([lm.x*w, lm.y*h], dtype=np.float32)

def eye_ear(lms, w, h, left=True):
    idx = LEFT_EYE_IDX if left else RIGHT_EYE_IDX
    p1,p4,p2,p3,p5,p6 = [_pt(lms, i, w, h) for i in idx]
    num = np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)
    den = 2.0*np.linalg.norm(p1 - p4) + 1e-6
    return float(num / den)

def np_l2(a,b): return np.linalg.norm(a-b)

def iris_norm_xy(lms, w, h, left=True):
    # normalize iris center into eye-local coords (-1..1)
    iris_idx = IRIS_CENTER[0] if left else IRIS_CENTER[1]
    c = _pt(lms, iris_idx, w, h)
    a = _pt(lms, LEFT_HORIZONTAL[0] if left else RIGHT_HORIZONTAL[0], w, h)
    b = _pt(lms, LEFT_HORIZONTAL[1] if left else RIGHT_HORIZONTAL[1], w, h)
    # x: along the eye width
    nx = 2 * (c[0] - a[0]) / (np_l2(b, a) + 1e-6) - 1.0
    # y: eyelid band normalization
    if left:
        upper = (_pt(lms,159,w,h)+_pt(lms,158,w,h))/2
        lower = (_pt(lms,153,w,h)+_pt(lms,145,w,h))/2
    else:
        upper = (_pt(lms,386,w,h)+_pt(lms,385,w,h))/2
        lower = (_pt(lms,380,w,h)+_pt(lms,374,w,h))/2
    ny = 2 * (c[1] - upper[1]) / ( (lower[1]-upper[1]) + 1e-6 ) - 1.0
    return float(nx), float(ny)
