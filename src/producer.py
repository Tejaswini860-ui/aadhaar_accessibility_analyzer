import time
import random
from queue_store import write_to_queue

districts = ["Karimnagar", "Warangal", "Medak", "Nizamabad"]

while True:
    data = {
        "district": random.choice(districts),
        "activity": random.randint(10, 150)
    }

    print("Produced:", data)

    write_to_queue(data)

    time.sleep(3)