# eye_demo.py — full version (top indicator with per-eye dots + smoothing)
import argparse, time, math
from collections import deque

import cv2
import numpy as np
import mediapipe as mp

from utils.landmarks import eye_ear, iris_norm_xy
from utils.filters import EMA
from utils.io import log_csv_open, load_calib, now_ms

mp_face_mesh = mp.solutions.face_mesh

# -----------------------------
# Colors
# -----------------------------
COL_OPEN = (0, 200, 0)
COL_CLOSED = (0, 0, 255)
COL_TXT = (255, 255, 255)
COL_HINT = (200, 200, 200)
COL_HINT2 = (180, 180, 180)
COL_GAUGE_FG = (0, 200, 255)
COL_GAUGE_BG = (40, 40, 40)
COL_GAUGE_BD = (200, 200, 200)

COL_L = (0, 0, 255)      # left eye dot = red
COL_R = (255, 0, 0)      # right eye dot = blue
COL_TRAIL = (120, 120, 120)
COL_LM = (0, 255, 255)   # yellow landmark dots

# -----------------------------
# HUD helpers
# -----------------------------
def color_for_state(state: str):
    return COL_OPEN if state == "open" else COL_CLOSED

def put_text(img, text, org, scale=0.8, color=COL_TXT, thick=2):
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)

def draw_bar(img, x, y, w, h, value01, bg=COL_GAUGE_BG, fg=COL_GAUGE_FG, border=COL_GAUGE_BD):
    v = max(0.0, min(1.0, float(value01)))
    cv2.rectangle(img, (x, y), (x + w, y + h), border, 1)
    cv2.rectangle(img, (x + 1, y + 1), (x + w - 1, y + h - 1), bg, -1)
    fill = int((w - 2) * v)
    cv2.rectangle(img, (x + 1, y + 1), (x + 1 + fill, y + h - 1), fg, -1)

def draw_plus_indicator(img, center, size=60, dots=None, trails=None):
    """
    center: (cx, cy)
    dots:   [(dx,dy,color), ...]  where dx,dy are -1..+1 velocity-like values
    trails: [deque([(dx,dy), ...]), ...]
    """
    cx, cy = int(center[0]), int(center[1])
    # green '+' axes
    cv2.line(img, (cx - size, cy), (cx + size, cy), (0, 200, 0), 2)
    cv2.line(img, (cx, cy - size), (cx, cy + size), (0, 200, 0), 2)

    # trails (faint)
    if trails:
        for dq in trails:
            if not dq:
                continue
            n = len(dq)
            for i, (tx, ty) in enumerate(dq):
                x = int(cx + tx * size)
                y = int(cy + ty * size)
                a = 0.35 + 0.65 * (i + 1) / n
                col = (int(COL_TRAIL[0] * a), int(COL_TRAIL[1] * a), int(COL_TRAIL[2] * a))
                cv2.circle(img, (x, y), 3, col, -1)

    # current dots
    if dots:
        for dx, dy, col in dots:
            x = int(cx + dx * size)
            y = int(cy + dy * size)
            cv2.circle(img, (x, y), 6, col, -1)

def clamp_vec(x, y, limit=0.4):
    m = math.hypot(x, y)
    if m > limit and m > 1e-6:
        s = limit / m
        return x * s, y * s
    return x, y

# -----------------------------
# Main
# -----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cam", type=int, default=0)
    ap.add_argument("--alpha", type=float, default=0.5)        # EMA for EAR
    ap.add_argument("--tau_low", type=float, default=0.20)     # close threshold
    ap.add_argument("--tau_high", type=float, default=0.24)    # open threshold
    ap.add_argument("--user", type=str, default="default")     # calibration profile
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--save", action="store_true")             # CSV logging
    ap.add_argument("--show-points", action="store_true")      # yellow eye/iris debug dots
    ap.add_argument("--flip-x", action="store_true", help="mirror/selfie camera: +X is right")
    ap.add_argument("--flip-y", action="store_true", help="flip Y if you want +Y to be up")
    ap.add_argument("--two-cross", action="store_true", help="draw two '+' indicators: left & right")

    # smoothing / taming options
    ap.add_argument("--pos-smooth", type=float, default=0.90, help="gaze coord EMA (0~1, higher = smoother)")
    ap.add_argument("--vel-smooth", type=float, default=0.20, help="velocity EMA (0~1, lower = smoother)")
    ap.add_argument("--deadzone",   type=float, default=0.06, help="ignore small motions under this (norm units)")
    ap.add_argument("--dot-gain",   type=float, default=0.6,  help="scale for indicator dot velocity")
    args = ap.parse_args()

    cap = cv2.VideoCapture(args.cam)
    if args.width:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    if args.height:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    cap.set(cv2.CAP_PROP_FPS, 60)

    # logging
    f = None
    writer = None
    if args.save:
        f, writer = log_csv_open("eye")

    # EAR state
    ema_ear = EMA(args.alpha)
    eye_state = "open"
    blink_t0 = None

    # calibration
    calib = load_calib(args.user)
    biasx = float(calib.get("biasx", 0.0))
    biasy = float(calib.get("biasy", 0.0))
    gainx = float(calib.get("gainx", 1.0))
    gainy = float(calib.get("gainy", 1.0))

    # FPS
    fps_t0 = time.time()
    fps_cnt = 0
    fps = 0.0

    # per-eye filtered coords (EMA)
    nx_l_f = ny_l_f = None
    nx_r_f = ny_r_f = None

    # per-eye velocity/trails
    prev_l = None
    prev_r = None
    vx_l = vy_l = 0.0
    vx_r = vy_r = 0.0
    trail_l = deque(maxlen=6)
    trail_r = deque(maxlen=6)

    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,   # enable iris
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6
    ) as face:

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = face.process(rgb)
            h, w = frame.shape[:2]

            blink_event = 0
            blink_ms = 0

            nx = ny = 0.0           # average (text)
            nx_l = ny_l = 0.0       # left eye raw norm gaze
            nx_r = ny_r = 0.0       # right eye raw norm gaze
            ear_val = float(ema_ear.v or 0.0)

            if res.multi_face_landmarks:
                lms = res.multi_face_landmarks[0].landmark

                # --- EAR ---
                ear_left = eye_ear(lms, w, h, left=True)
                ear_right = eye_ear(lms, w, h, left=False)
                ear = ema_ear.update(0.5 * (ear_left + ear_right))
                ear_val = float(ear if ear is not None else 0.0)

                # hysteresis for blink
                if eye_state == "open" and ear_val < args.tau_low:
                    eye_state = "closed"
                    blink_t0 = now_ms()
                elif eye_state == "closed" and ear_val > args.tau_high:
                    eye_state = "open"
                    if blink_t0 is not None:
                        blink_event = 1
                        blink_ms = now_ms() - blink_t0
                        blink_t0 = None

                # --- per-eye gaze (normalized -1..+1) ---
                nx_l, ny_l = iris_norm_xy(lms, w, h, left=True)
                nx_r, ny_r = iris_norm_xy(lms, w, h, left=False)

                # calibration
                nx_l = (nx_l + biasx) * gainx
                ny_l = (ny_l + biasy) * gainy
                nx_r = (nx_r + biasx) * gainx
                ny_r = (ny_r + biasy) * gainy

                # flips
                if args.flip_x:
                    nx_l, nx_r = -nx_l, -nx_r
                if args.flip_y:
                    ny_l, ny_r = -ny_l, -ny_r

                # ===== ① position smoothing (EMA) =====
                a = float(args.pos_smooth)  # higher -> smoother
                def ema(prev, x): return x if prev is None else a*prev + (1-a)*x
                nx_l_f = ema(nx_l_f, nx_l); ny_l_f = ema(ny_l_f, ny_l)
                nx_r_f = ema(nx_r_f, nx_r); ny_r_f = ema(ny_r_f, ny_r)

                # average for display text
                nx = (nx_l_f + nx_r_f) / 2.0
                ny = (ny_l_f + ny_r_f) / 2.0

                # ===== ② velocity from filtered coords =====
                if prev_l is None:
                    dnx_l = dny_l = 0.0
                else:
                    plx, ply = prev_l
                    dnx_l, dny_l = nx_l_f - plx, ny_l_f - ply
                prev_l = (nx_l_f, ny_l_f)

                if prev_r is None:
                    dnx_r = dny_r = 0.0
                else:
                    prx, pry = prev_r
                    dnx_r, dny_r = nx_r_f - prx, ny_r_f - pry
                prev_r = (nx_r_f, ny_r_f)

                # ===== ③ velocity EMA + deadzone + gain + clamp =====
                b = float(args.vel_smooth)   # lower -> smoother (0.2 default)
                def ema_vel(prev, d): return b*d + (1-b)*prev
                vx_l = ema_vel(vx_l, dnx_l);  vy_l = ema_vel(vy_l, dny_l)
                vx_r = ema_vel(vx_r, dnx_r);  vy_r = ema_vel(vy_r, dny_r)

                dz = float(args.deadzone)
                def apply_deadzone(x, y, dz):
                    if abs(x) < dz: x = 0.0
                    if abs(y) < dz: y = 0.0
                    return x, y
                vx_l, vy_l = apply_deadzone(vx_l, vy_l, dz)
                vx_r, vy_r = apply_deadzone(vx_r, vy_r, dz)

                g = float(args.dot_gain)
                vx_l *= g; vy_l *= g
                vx_r *= g; vy_r *= g

                vx_l, vy_l = clamp_vec(vx_l, vy_l, limit=0.25)
                vx_r, vy_r = clamp_vec(vx_r, vy_r, limit=0.25)

                # trails
                trail_l.append((vx_l, vy_l))
                trail_r.append((vx_r, vy_r))

                # optional: draw a few eye/iris landmarks as yellow dots
                if args.show_points:
                    def _pt_xy(lm): 
                        return int(lm.x * w), int(lm.y * h)
                    for i in [33,133,159,158,153,145, 362,263,386,385,380,374, 468,473]:
                        x, y = _pt_xy(lms[i])
                        cv2.circle(frame, (x, y), 1, COL_LM, -1)

            # ============= HUD =============
            # EAR text
            col = color_for_state(eye_state)
            put_text(frame, f"EAR: {ear_val:.3f} [{eye_state}]", (18, 40), 0.9, col, 2)
            put_text(frame, f"gaze nx,ny=({nx:+.2f},{ny:+.2f})", (18, 75), 0.8, (255, 255, 0), 2)

            # EAR gauge (top-right)
            ear_min, ear_max = 0.10, 0.35
            ear01 = (ear_val - ear_min) / (ear_max - ear_min + 1e-6)
            ear01 = max(0.0, min(1.0, ear01))
            bar_w, bar_h = 240, 18
            draw_bar(frame, frame.shape[1] - bar_w - 20, 20, bar_w, bar_h, ear01)

            # top indicator(s)
            if args.two_cross:
                ind_L = (frame.shape[1] // 2 - 120, 80)
                ind_R = (frame.shape[1] // 2 + 120, 80)
                draw_plus_indicator(frame, ind_L, size=55,
                                    dots=[(vx_l, vy_l, COL_L)],
                                    trails=[trail_l])
                draw_plus_indicator(frame, ind_R, size=55,
                                    dots=[(vx_r, vy_r, COL_R)],
                                    trails=[trail_r])
                put_text(frame, "L", (ind_L[0] - 65, ind_L[1] - 65), 0.9, COL_HINT, 2)
                put_text(frame, "R", (ind_R[0] - 65, ind_R[1] - 65), 0.9, COL_HINT, 2)
            else:
                ind_C = (frame.shape[1] // 2, 80)
                draw_plus_indicator(frame, ind_C, size=55,
                                    dots=[(vx_l, vy_l, COL_L), (vx_r, vy_r, COL_R)],
                                    trails=[trail_l, trail_r])
                put_text(frame, "+X: right  |  +Y: down", (ind_C[0] - 110, ind_C[1] - 65), 0.7, COL_HINT2, 2)

            # blink banner
            if blink_event:
                put_text(frame, f"BLINK {int(blink_ms)}ms", (18, 110), 0.9, (0, 140, 255), 2)

            # FPS
            fps_cnt += 1
            t1 = time.time()
            if t1 - fps_t0 >= 0.5:
                fps = fps_cnt / (t1 - fps_t0)
                fps_t0 = t1
                fps_cnt = 0
            put_text(frame, f"FPS: {fps:.1f}", (18, frame.shape[0] - 20), 0.8, (200, 200, 200), 2)

            # logging
            if writer:
                writer.writerow([
                    now_ms(),
                    f"{ear_val:.4f}",
                    eye_state,
                    f"{nx:.4f}", f"{ny:.4f}",
                    1 if blink_event else 0,
                    int(blink_ms)
                ])

            cv2.imshow("eye-poc", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
                break

    if f:
        f.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
