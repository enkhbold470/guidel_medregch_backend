import os
from flask import Flask, request, jsonify, render_template
import datetime
import time
import pymongo

myclient = pymongo.MongoClient(os.environ.get("MONGODB_URL"))
mydb = myclient["iot_database"]
mycol = mydb["sensor_logs"]


TEMPLATE_DIR = os.path.abspath("templates")
STATIC_DIR = os.path.abspath("static")

# mycol.delete_many({})
# Flask setup
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/update_sensor", methods=["POST"])
def update_sensor():
    if request.is_json:
        data = request.get_json()
        # Process the incoming data as needed
        # For example, you can print it to the console or save it to a database
        today = datetime.datetime.now()
        timezone = time.tzname[0]

        str_today = today.strftime("%Y-%m-%d %H:%M:%S")
        data["timestamp"] = str_today
        data["timezone"] = str(timezone)
        mycol.insert_one(data)
        for x in mycol.find().sort("timestamp", -1).limit(1):
            print(x)
        return jsonify({"data": "received"}), 200
    else:
        return jsonify({"error": "Invalid data format"}), 400


@app.route("/get_sensor_data", methods=["GET"])
def get_sensor_data():
    # Retrieve the most recent sensor data
    recent_data = mycol.find().sort("timestamp", -1).limit(5)
    recent_data_list = list(recent_data)
    # print("recent: ", recent_data_list)
    if recent_data_list:
        recent_data_list[0]["_id"] = str(recent_data_list[0]["_id"])
        return jsonify(recent_data_list[0]), 200
    else:
        return jsonify({"error": "No data found"}), 404


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
