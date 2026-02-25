from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

booked_slots = {}

def time_conflict(start1, end1 , start2 , end2):
    return max(start1, start2) < min(end1, end2)

@app.route('/book', methods=['POST'])
def book_slot():
    data = request.json

    slot_id = data.get("slot_id")
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    user_id = data.get("user_id")

    if not all([[slot_id, start_time, end_time, user_id]]):
        return jsonify({'error':'missing required fields'}), 400
    
    try:
        start_time = datetime.fromisoformat(start_time)
        end_time = datetime.fromisoformat(end_time)
    except ValueError:
        return jsonify({'error':'Invalid datetime format use ISO format'}), 400
    
    if start_time >= end_time:
        return jsonify({'error':'start time must be before end time'}), 400
    
    if slot_id in booked_slots:
        return jsonify({'status':'booked', 'message':'slot already booked'}), 409
    
    for existing_slot in booked_slots.values():
        if time_conflict(start_time, end_time, existing_slot["start_time"], existing_slot["end_time"]):
            return jsonify({'status':'booked', 'messsage':'time conflict with another booking'}), 409
        
    booked_slots[slot_id] = {
        "start_time": start_time,
        "end_time": end_time,
        "user_id": user_id
    }

    return jsonify({'status':'available', 'message':'slot sucessfully booked'}), 201

@app.route('/slots', methods=["GET"])
def get_slots():
    response={}
    for slot_id, details in booked_slots.items():
        response[slot_id]= {
            "start_time": details["start_time"].isoformat(),
            "end_time": details["end_time"].isoformat(),
            "user_id": details["user_id"]
        }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)