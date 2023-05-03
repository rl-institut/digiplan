# pylint: disable=C0415
import json
import pathlib

import jsonschema

from config.schemas import (
    CHART_SCHEMA,
    KEY_VALUES_SCHEMA,
    LEGEND_SCHEMA,
    POPUP_SCHEMA,
    SOURCES_SCHEMA,
)

# Components Schema Tests

TEST_DIR = pathlib.Path(__file__).parent
TEST_SCHEMAS_DIR = TEST_DIR / "test_data" / "schemas"


def test_if_chart_energy_consumption_example_validates():
    with open(TEST_SCHEMAS_DIR / "chart.energy_consumption.example.json", "rb") as f:
        CHART_ENERGY_CONSUMPTION_EXAMPLE = json.loads(f.read())

    assert jsonschema.validate(CHART_ENERGY_CONSUMPTION_EXAMPLE, CHART_SCHEMA) is None  # noqa: S101


def test_if_chart_population_example_validates():
    with open(TEST_SCHEMAS_DIR / "chart.population.example.json", "rb") as f:
        CHART_POPULATION_EXAMPLE = json.loads(f.read())
    assert jsonschema.validate(CHART_POPULATION_EXAMPLE, CHART_SCHEMA) is None  # noqa: S101


def test_if_key_values_example_validates():
    with open(TEST_SCHEMAS_DIR / "key-values.example.json", "rb") as f:
        KEY_VALUES_EXAMPLE = json.loads(f.read())
    assert jsonschema.validate(KEY_VALUES_EXAMPLE, KEY_VALUES_SCHEMA) is None  # noqa: S101


def test_if_sources_example_validates():
    with open(TEST_SCHEMAS_DIR / "sources.example.json", "rb") as f:
        SOURCES_EXAMPLE = json.loads(f.read())
    assert jsonschema.validate(SOURCES_EXAMPLE, SOURCES_SCHEMA) is None  # noqa: S101


# Schema Tests


def test_if_legend_example_validates():
    with open(TEST_SCHEMAS_DIR / "legend.example.json", "rb") as f:
        LEGEND_EXAMPLE = json.loads(f.read())
    assert jsonschema.validate(LEGEND_EXAMPLE, LEGEND_SCHEMA) is None  # noqa: S101


def test_if_popup_example_validates():
    schema_store = {
        CHART_SCHEMA["$id"]: CHART_SCHEMA,
        KEY_VALUES_SCHEMA["$id"]: KEY_VALUES_SCHEMA,
        POPUP_SCHEMA["$id"]: POPUP_SCHEMA,
        SOURCES_SCHEMA["$id"]: SOURCES_SCHEMA,
    }
    resolver = jsonschema.RefResolver.from_schema(POPUP_SCHEMA, store=schema_store)
    validator = jsonschema.Draft4Validator(POPUP_SCHEMA, resolver=resolver)

    with open(TEST_SCHEMAS_DIR / "popup.example.json", "rb") as f:
        POPUP_EXAMPLE = json.loads(f.read())

    assert validator.validate(POPUP_EXAMPLE) is None  # noqa: S101
