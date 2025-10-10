import csv, json, time, os
from datetime import datetime

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def log_csv_open(run_name="run"):
    ensure_dir("out/logs")
    fn = f"out/logs/{run_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    f = open(fn, "w", newline="", encoding="utf-8")
    w = csv.writer(f)
    w.writerow(["ts_ms","ear","state","nx","ny","blink_event","blink_ms"])
    return f, w

def save_calib(user="default", data=None):
    ensure_dir("out/calib")
    with open(f"out/calib/{user}.json","w",encoding="utf-8") as fp:
        json.dump(data or {}, fp, ensure_ascii=False, indent=2)

def load_calib(user="default"):
    try:
        with open(f"out/calib/{user}.json","r",encoding="utf-8") as fp:
            return json.load(fp)
    except FileNotFoundError:
        return {}

def now_ms():
    return int(time.time()*1000)
