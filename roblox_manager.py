import psutil
import time
import os

# Standard Roblox Web Client Process Name
# Note: If you use the Microsoft Store version, it might be "Windows10Universal.exe"
PROCESS_NAME = "RobloxPlayerBeta.exe"

def is_roblox_running():
    """
    Checks if Roblox is currently running in the background.
    Returns: Boolean
    """
    for proc in psutil.process_iter(['name']):
        try:
            # Check if process name matches (case insensitive)
            if proc.info['name'] and proc.info['name'].lower() == PROCESS_NAME.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def kill_roblox():
    """
    Forcefully kills all running instances of Roblox.
    Returns: True if processes were killed, False if none were found.
    """
    killed_any = False
    print(f"[Manager] Attempting to kill {PROCESS_NAME}...")

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Check if name matches
            if proc.info['name'] and proc.info['name'].lower() == PROCESS_NAME.lower():
                pid = proc.info['pid']
                
                # Kill the process
                proc.kill()
                
                # Wait for it to actually die (prevents zombies)
                try:
                    proc.wait(timeout=3)
                except psutil.TimeoutExpired:
                    print(f"[Manager] Warning: Process {pid} is stubborn.")

                print(f"[Manager] 💀 Killed Roblox Process (PID: {pid})")
                killed_any = True
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            # Process might have closed itself while we were looking at it
            pass

    if not killed_any:
        print("[Manager] Roblox was not running.")
    
    return killed_any

def launch_roblox(place_id="10449761463", job_id=None):
    """
    Launches Roblox directly using the DeepLink protocol.
    """
    print(f"[Manager] 🚀 Launching Roblox for Place: {place_id}...")
    
    # Base Protocol URL
    launch_url = f"roblox://experiences/start?placeId={place_id}"
    
    # Append Job ID if provided
    if job_id:
        launch_url += f"&gameInstanceId={job_id}"
    
    try:
        # METHOD 1: The Best Way (Windows Only)
        # This mimics 'Run' dialog or double-clicking.
        os.startfile(launch_url)
        
        print("[Manager] Launch command sent successfully.")
        
    except AttributeError:
        # Fallback for non-Windows systems (Linux/Mac) if you ever move this script
        import webbrowser
        webbrowser.open(launch_url)
        
    except Exception as e:
        print(f"[Manager] ❌ Failed to launch: {e}")
