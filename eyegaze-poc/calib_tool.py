import time, cv2, numpy as np, mediapipe as mp
from utils.landmarks import iris_norm_xy
from utils.io import save_calib

mp_face_mesh = mp.solutions.face_mesh

def capture_avg(face, cap, seconds=1.0, text="look here"):
    t0 = time.time(); vals=[]
    while time.time()-t0 < seconds:
        ok, frame = cap.read()
        if not ok: continue
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = face.process(rgb)
        h,w = frame.shape[:2]
        if res.multi_face_landmarks:
            lms = res.multi_face_landmarks[0].landmark
            nx_l, ny_l = iris_norm_xy(lms,w,h,True)
            nx_r, ny_r = iris_norm_xy(lms,w,h,False)
            vals.append(((nx_l+nx_r)/2.0, (ny_l+ny_r)/2.0))
        cv2.putText(frame, f"Calibration: {text}", (18,40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,255), 2)
        cv2.imshow("calib", frame); cv2.waitKey(1)
    if not vals: return 0.0, 0.0
    return float(np.mean([v[0] for v in vals])), float(np.mean([v[1] for v in vals]))

def main():
    cap = cv2.VideoCapture(0)
    with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True) as face:
        steps = [("center",1.0),("left",1.0),("right",1.0),("up",1.0),("down",1.0)]
        samples = {}
        for name, sec in steps:
            time.sleep(0.4)
            x,y = capture_avg(face, cap, seconds=sec, text=name)
            samples[name]=(x,y)
        # 간단한 오프셋/스케일 추정 (center 기준 바이어스, 좌우/상하 범위로 게인)
        biasx = -samples["center"][0]
        biasy = -samples["center"][1]
        span_x = (samples["right"][0]+biasx) - (samples["left"][0]+biasx)
        span_y = (samples["down"][1]+biasy) - (samples["up"][1]+biasy)
        gainx = 2.0 / (span_x if abs(span_x)>1e-3 else 1.0)
        gainy = 2.0 / (span_y if abs(span_y)>1e-3 else 1.0)

        save_calib("default", {"biasx":biasx, "biasy":biasy, "gainx":gainx, "gainy":gainy})
        print("Saved calib:", {"biasx":biasx, "biasy":biasy, "gainx":gainx, "gainy":gainy})
    cap.release(); cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
