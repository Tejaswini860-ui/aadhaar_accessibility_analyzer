import time
import joblib
import json
from queue_store import read_from_queue, clear_queue

model = joblib.load("../models/accessibility_model.pkl")

OUTPUT_FILE = "output.json"

while True:
    queue = read_from_queue()

    if queue:
        results = []

        for item in queue:
            activity = item["activity"]

            prediction = model.predict([[activity]])[0]

            results.append({
                "district": item["district"],
                "activity": activity,
                "low_access": int(prediction)
            })

        with open(OUTPUT_FILE, "w") as f:
            json.dump(results, f)

        clear_queue()

        print("Consumed and processed data")

    time.sleep(5)