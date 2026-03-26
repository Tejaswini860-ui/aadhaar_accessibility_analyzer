import json
import os

QUEUE_FILE = "queue.json"

def write_to_queue(data):
    if not os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "w") as f:
            json.dump([], f)

    with open(QUEUE_FILE, "r") as f:
        queue = json.load(f)

    queue.append(data)

    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f)


def read_from_queue():
    if not os.path.exists(QUEUE_FILE):
        return []

    with open(QUEUE_FILE, "r") as f:
        return json.load(f)


def clear_queue():
    with open(QUEUE_FILE, "w") as f:
        json.dump([], f)