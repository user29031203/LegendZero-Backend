from flask import Flask, request, jsonify
from datetime import datetime, timezone
from threading import Lock
from flask import abort
import utils

app = Flask(__name__)
lock = Lock()
DWEET_DB_FILE = "dweets_db.json"
POINTS_DB_FILE = "points_db.json"

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
def managePoints(alt_name: str, points: int):
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
def showPoints(alt_name: str):
    with lock:
        db = utils.read_db(POINTS_DB_FILE)
        alts = db.setdefault("alts", {})
        alts.setdefault(alt_name, {})
        alt = alts[alt_name]
    
    return jsonify(alt), 200

@app.route("/")
def index():
    return "dweetr.io clone running! Use /dweet/for/my-thing?JobId=abc&Status=ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)