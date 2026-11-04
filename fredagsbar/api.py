from flask import Flask, jsonify, request

app = Flask(__name__)

# Data ligger i en liste i hukommelsen (forsvinder når API'en genstartes)
events = [
    {"id": 1, "title": "Quizaften", "date": "2026-11-13", "capacity": 3, "participants": ["Anna", "Bo"]},
    {"id": 2, "title": "Brætspilsaften", "date": "2026-11-20", "capacity": 10, "participants": []},
    {"id": 3, "title": "Beerpong-turnering", "date": "2026-11-27", "capacity": 8, "participants": ["Carl"]},
]


def find_event(event_id):
    for event in events:
        if event["id"] == event_id:
            return event
    return None


def error(message, status):
    return jsonify({"error": message}), status


@app.get("/events")
def get_events():
    return jsonify(events), 200


@app.get("/events/<int:event_id>")
def get_event(event_id):
    event = find_event(event_id)
    if event is None:
        return error("Eventet findes ikke", 404)
    return jsonify(event), 200


@app.post("/events")
def create_event():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    date = data.get("date")
    capacity = data.get("capacity")

    if not title or not date or capacity is None:
        return error("title, date og capacity skal udfyldes", 400)
        
    if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 1:
        return error("capacity skal være et positivt heltal", 400)

    new_id = max((e["id"] for e in events), default=0) + 1
    event = {"id": new_id, "title": title, "date": date, "capacity": capacity, "participants": []}
    events.append(event)
    return jsonify(event), 201


@app.delete("/events/<int:event_id>")
def delete_event(event_id):
    event = find_event(event_id)
    if event is None:
        return error("Eventet findes ikke", 404)
    events.remove(event)
    return "", 204


@app.post("/events/<int:event_id>/signups")
def signup(event_id):
    event = find_event(event_id)
    if event is None:
        return error("Eventet findes ikke", 404)

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return error("name skal udfyldes", 400)
    if name in event["participants"]:
        return error(f"{name} er allerede tilmeldt", 409)
    if len(event["participants"]) >= event["capacity"]:
        return error("Eventet er fuldt", 409)

    event["participants"].append(name)
    return jsonify(event), 201


@app.delete("/events/<int:event_id>/signups/<name>")
def cancel_signup(event_id, name):
    event = find_event(event_id)
    if event is None:
        return error("Eventet findes ikke", 404)
    if name not in event["participants"]:
        return error(f"{name} er ikke tilmeldt", 404)

    event["participants"].remove(name)
    return "", 204


if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=5000)
