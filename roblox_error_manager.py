import threading
import time
import signal
import sys
import requests
import utils

WARNING_ENABLED = threading.Event()
WARNING_ENABLED.set()  # enable warnings by default
BASE_URL = "http://192.168.1.128:5000"
ALT_NAME = ""

SHUTDOWN = threading.Event()
threads = []

def monitor_json_endpoint(
    url,
    interval=60,
    max_idle_minutes=4,
    timeout=3,
):
    unchanged_minutes = 0
    last_snapshot = None

    print(f"[monitor] started for {url}")

    while not SHUTDOWN.is_set():
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            current_snapshot = response.json()
        except Exception as e:
            print(f"[monitor] fetch error: {e}")
            time.sleep(interval)
            continue

        if last_snapshot is None:
            last_snapshot = current_snapshot

        elif current_snapshot != last_snapshot:
            #print("[monitor] JSON changed..")
            last_snapshot = current_snapshot
            unchanged_minutes = 0

        else:
            unchanged_minutes += 1
            print(f"[monitor] unchanged {unchanged_minutes} min")

        if unchanged_minutes >= max_idle_minutes:
            if WARNING_ENABLED.is_set():
                print("[monitor] JSON unchanged for 5 minutes !")
                utils.reset_roblox(30)
            unchanged_minutes = 0

        # sleep in small chunks so Ctrl+C is responsive
        for _ in range(interval):
            if SHUTDOWN.is_set():
                break
            time.sleep(1)

    print(f"[monitor] stopped for {url}")



def start_json_monitor(alt_name):
    url = f"{BASE_URL}/get/{alt_name}/points"

    t = threading.Thread(
        target=monitor_json_endpoint,
        args=(url,),
        daemon=False
    )
    t.start()
    threads.append(t)


def shutdown_handler(sig, frame):
    print("\n[main] Ctrl+C received, shutting down...")
    SHUTDOWN.set()

    for t in threads:
        t.join()

    print("[main] shutdown complete")
    sys.exit(0)


signal.signal(signal.SIGINT, shutdown_handler)


# ---- main app ----
if __name__ == "__main__":
    start_json_monitor(ALT_NAME)

    # keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown_handler(None, None)

# Anywhere in your code:
# WARNING_ENABLED.clear()  # suppress output
# WARNING_ENABLED.set()    # re-enable output

