import json
import os

from config.settings.base import APPS_DIR

SCHEMA_DIR = APPS_DIR.path("schemas")

# ATOMS
with open(os.path.join(SCHEMA_DIR, "atom.chart.schema.json"), "rb") as f:
    ATOM_CHART_SCHEMA = json.loads(f.read())

# ATOM EXAMPLES
with open(os.path.join(SCHEMA_DIR, "atom.chart.example.json"), "rb") as f:
    ATOM_CHART_EXAMPLE = json.loads(f.read())

# SCHEMAS
with open(os.path.join(SCHEMA_DIR, "popup.default.schema.json"), "rb") as f:
    POPUP_DEFAULT_SCHEMA = json.loads(f.read())

# SCHEMA EXAMPLES
with open(os.path.join(SCHEMA_DIR, "popup.default.example.json"), "rb") as f:
    POPUP_DEFAULT_EXAMPLE = json.loads(f.read())
