import json
import os

with open(os.path.join(os.path.dirname(__file__), "example.json"), "rb") as f:
    POPULATION_EXAMPLE = json.loads(f.read())
