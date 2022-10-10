import json
import os

from config.settings.base import APPS_DIR

SCHEMA_DIR = APPS_DIR.path("schema")

with open(os.path.join(SCHEMA_DIR, "popup/example/example.popup.population.json"), "rb") as f:
    EXAMPLE_POPUP_POPULATION = json.loads(f.read())

with open(os.path.join(SCHEMA_DIR, "popup/schema.popup.default.json"), "rb") as f:
    SCHEMA_POPUP_DEFAULT = json.loads(f.read())
