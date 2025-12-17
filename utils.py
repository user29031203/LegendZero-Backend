import os
import json
#import roblox_manager
import time
import getpass
from pathlib import Path
import roblox_manager

MAX_DWEETS_PER_THING = 1
REST_TIMEOUT = 60*30
STATE_FILE_NAME = "LegendZero_State.txt"

# ---------- FILE HELPERS ----------

def read_db(DB_FILE):
    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except:
        return {}

def write_db(data, DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# Only for dweets_db.json
def clean_database(db):
    for thing in db:
        if len(db[thing]) > MAX_DWEETS_PER_THING:
            # keep only the last 5
            db[thing] = db[thing][-MAX_DWEETS_PER_THING:]
    return db

# ---------- POINT/LOSE LOGIC ----------
# only for points_db.json + recursive/multi fail_count checker
def is_failed(points, n=2):
    fail_count = 0
    tail = points[-n:]

    for prev, curr in zip(tail, tail[1:]):
        if curr < prev:
            fail_count += 1
    
    return fail_count

# ---------- ROBLOX ETC ----------
def reset_roblox(timeout=REST_TIMEOUT):
    if roblox_manager.is_roblox_running():
        roblox_manager.kill_roblox()
    username = getpass.getuser()
    file_path = f"C:\\Users\\{username}\\AppData\\Local\\Xeno\\workspace\\{STATE_FILE_NAME}"
    if Path(file_path).exists():
        os.remove(file_path)
    time.sleep(timeout)
    roblox_manager.launch_roblox()
    