from flask import Flask, request, jsonify
from datetime import datetime, timezone
from threading import Lock
from flask import abort
import utils
import requests  # <--- NEW IMPORT REQUIRED


app = Flask(__name__)
lock = Lock()
DWEET_DB_FILE = "dweets_db.json"
POINTS_DB_FILE = "points_db.json"
DEFAULT_PLACE_ID = "12360882630"

@app.route("/dweet/for/<string:thing>", methods=["GET"])
def dweet_for(thing: str):
    content = {}
    for key, value in request.args.items():
        try:
            if "." in value:
                content[key] = float(value)
            else:
                content[key] = int(value)
        except:
            content[key] = value

    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

    new_dweet = {
        "thing": thing,
        "content": content,
        "created": created
    }

    with lock:
        db = utils.read_db(DWEET_DB_FILE)
        db.setdefault(thing, []).append(new_dweet)
        db = utils.clean_database(db)
        utils.write_db(db, DWEET_DB_FILE)

    # ✅ Return dweet.io-compatible JSON
    response = {
        "this": "succeeded",
        "with": [new_dweet]
    }

    return jsonify(response), 200

@app.route("/get/latest/dweet/for/<string:thing>", methods=["GET"])
def get_latest_dweet(thing: str):
    with lock:
        db = utils.read_db(DWEET_DB_FILE)

    if thing not in db or not db[thing]:
        return jsonify({
            "this": "failed",
            "because": "no dweets found for thing",
            "with": []
        }), 404

    latest = db[thing][-1]

    # ✅ dweet.io format: 'with' is a list
    response = {
        "this": "succeeded",
        "with": [latest]
    }

    return jsonify(response), 200

@app.route("/set/<string:alt_name>/points/<int:points>", methods=["GET"])
def manage_points(alt_name: str, points: int):
    with lock:
        db = utils.read_db(POINTS_DB_FILE)
        alts = db.setdefault("alts", {})
        alts.setdefault(alt_name, {})
        alt = alts[alt_name]
        alt.setdefault("points", []).append(points)
        current_points = alt["points"]
        alt.setdefault("failCount", 0)
        if utils.is_failed(current_points):
            alt["failCount"] += 1
        utils.write_db(db, POINTS_DB_FILE)

    # !! CODE BLOCK TEMPORARY FOR MY OLD LAPTOPT !!
    """n = 19 # wanted recursive fail check count (n) = n*2+1
    recursive_fail_count = utils.is_failed(current_points, n)         
    is_broken = recursive_fail_count >= (n-1)/2

    if is_broken:
        utils.reset_roblox()"""
    # DONT USE IN PRODUCTION!
    # !! CODE BLOCK TEMPORARY FOR MY OLD LAPTOPT !!
    fail_count = alt["failCount"]

    response = {
        "alt": alt_name,
        "addedPoint": points,
        "failCount": fail_count,
        #"broken": is_broken,
        "result": "success!"
    }

    return jsonify(response), 200


@app.route("/get/<string:alt_name>/points") 
def show_points(alt_name: str):
    with lock:
        db = utils.read_db(POINTS_DB_FILE)
        alts = db.setdefault("alts", {})
        alts.setdefault(alt_name, {})
        alt = alts[alt_name]
    
    return jsonify(alt), 200


@app.route("/get/serverdata/lowest/<int:limit>")
def get_server_jobid(limit: int):
    # Roblox API validation: limit must be 10, 25, 50, or 100.
    # If the user asks for 5 or 1, we default to 10 to prevent API errors.
    valid_limits = [10, 25, 50, 100]
    if limit not in valid_limits:
        limit = 10

    url = f"https://games.roblox.com/v1/games/{DEFAULT_PLACE_ID}/servers/Public"

    params = {
        "sortOrder": "Asc",  # Ascending = Lowest player count first
        "limit": limit
    }

    try:
        # Roblox sometimes blocks requests without a User-Agent
        headers = {"User-Agent": "RobloxFlaskBackend/1.0"}
        
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status() # Raise error for 4xx/5xx responses
        
        data = response.json()
        server_list = data.get("data", [])

        if not server_list:
            return jsonify({
                "success": False, 
                "message": "No servers found for this game."
            }), 404

        # Because we used sortOrder=Asc, the first item (index 0) 
        # is the server with the lowest player count.
        lowest_server = server_list[0]

        return jsonify({
            "success": True,
            "jobId": lowest_server["id"],
            "playing": lowest_server["playing"],
            "maxPlayers": lowest_server["maxPlayers"],
            "ping": lowest_server["ping"],
            "fps": lowest_server["fps"]
        }), 200

    except Exception as e:
        return jsonify({
            "success": False, 
            "error": str(e)
        }), 500

@app.route("/")
def index():
    return "dweetr.io clone running! Use /dweet/for/my-thing?JobId=abc&Status=ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)