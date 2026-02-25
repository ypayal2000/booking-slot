from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

booked_slots = {}

def time_conflict(start1, end1 , start2 , end2):
    return max(start1, start2) < min(end1, end2)

def generate_daily_slots():
    slots={}
    start_hour = 10
    end_hour = 18
    for i in range(start_hour, end_hour):
        slot_id = f"slot{i}"
        slots[slot_id] = {
             "start_time": f"{i:02d}:00",
            "end_time": f"{i+1:02d}:00",
            "booked": False,
            "user_id": None
        }
    return slots

daily_slots = generate_daily_slots()

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
    
    if slot_id not in daily_slots:
        return jsonify({'error':'invalid slot id'}), 400
    
    if daily_slots[slot_id]["booked"]:
        return jsonify({'status':'booked', 'message':'slot already booked'}), 409
    
    daily_slots[slot_id]["booked"] = True
    daily_slots[slot_id]["user_id"] = user_id
        
    return jsonify({
        'status':'available',
        'message': f'slot {slot_id} successfully booked',
        'start_time': daily_slots[slot_id]["start_time"],
        'end_time': daily_slots[slot_id]["end_time"]
    }), 201

@app.route('/slots', methods=["GET"])
def get_slots():
    response={}
    for slot_id, details in daily_slots.items():
        response[slot_id]= {
            "start_time": details["start_time"].isoformat(),
            "end_time": details["end_time"].isoformat(),
            "user_id": details["user_id"]
        }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)