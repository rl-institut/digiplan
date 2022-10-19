import json
import os

from config.settings.base import APPS_DIR

SCHEMAS_DIR = APPS_DIR.path("schemas")
COMPONENTS_DIR = SCHEMAS_DIR.path("components")

with open(os.path.join(SCHEMAS_DIR, "popup.schema.json"), "rb") as f:
    POPUP_SCHEMA = json.loads(f.read())

with open(os.path.join(SCHEMAS_DIR, "popup.example.json"), "rb") as f:
    POPUP_EXAMPLE = json.loads(f.read())

with open(os.path.join(COMPONENTS_DIR, "chart.schema.json"), "rb") as f:
    CHART_SCHEMA = json.loads(f.read())

with open(os.path.join(COMPONENTS_DIR, "chart.example.json"), "rb") as f:
    CHART_EXAMPLE = json.loads(f.read())

with open(os.path.join(COMPONENTS_DIR, "key-values.schema.json"), "rb") as f:
    KEY_VALUES_SCHEMA = json.loads(f.read())

with open(os.path.join(COMPONENTS_DIR, "key-values.example.json"), "rb") as f:
    KEY_VALUES_EXAMPLE = json.loads(f.read())

with open(os.path.join(COMPONENTS_DIR, "sources.schema.json"), "rb") as f:
    SOURCES_SCHEMA = json.loads(f.read())

with open(os.path.join(COMPONENTS_DIR, "sources.example.json"), "rb") as f:
    SOURCES_EXAMPLE = json.loads(f.read())
