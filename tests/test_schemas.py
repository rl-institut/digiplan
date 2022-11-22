# pylint: disable=C0415


# Components Schema Tests


def test_if_chart_energy_consumption_example_validates():
    import jsonschema

    from config.schemas import CHART_SCHEMA  # noqa: I001
    from config.schemas import CHART_ENERGY_CONSUMPTION_EXAMPLE  # noqa: I001

    assert jsonschema.validate(CHART_ENERGY_CONSUMPTION_EXAMPLE, CHART_SCHEMA) is None  # noqa: S101


def test_if_chart_population_example_validates():
    import jsonschema

    from config.schemas import CHART_SCHEMA  # noqa: I001
    from config.schemas import CHART_POPULATION_EXAMPLE  # noqa: I001

    assert jsonschema.validate(CHART_POPULATION_EXAMPLE, CHART_SCHEMA) is None  # noqa: S101


def test_if_key_values_example_validates():
    import jsonschema

    from config.schemas import KEY_VALUES_SCHEMA  # noqa: I001
    from config.schemas import KEY_VALUES_EXAMPLE  # noqa: I001

    assert jsonschema.validate(KEY_VALUES_EXAMPLE, KEY_VALUES_SCHEMA) is None  # noqa: S101


def test_if_sources_example_validates():
    import jsonschema

    from config.schemas import SOURCES_SCHEMA  # noqa: I001
    from config.schemas import SOURCES_EXAMPLE  # noqa: I001

    assert jsonschema.validate(SOURCES_EXAMPLE, SOURCES_SCHEMA) is None  # noqa: S101


# Schema Tests


def test_if_legend_example_validates():
    import jsonschema

    from config.schemas import LEGEND_SCHEMA  # noqa: I001
    from config.schemas import LEGEND_EXAMPLE  # noqa: I001

    assert jsonschema.validate(LEGEND_EXAMPLE, LEGEND_SCHEMA) is None  # noqa: S101


def test_if_popup_example_validates():
    from jsonschema import Draft4Validator, RefResolver

    from config.schemas import CHART_SCHEMA  # noqa: I001
    from config.schemas import KEY_VALUES_SCHEMA  # noqa: I001
    from config.schemas import POPUP_SCHEMA  # noqa: I001
    from config.schemas import POPUP_EXAMPLE  # noqa: I001
    from config.schemas import SOURCES_SCHEMA  # noqa: I001

    schema_store = {
        CHART_SCHEMA["$id"]: CHART_SCHEMA,
        KEY_VALUES_SCHEMA["$id"]: KEY_VALUES_SCHEMA,
        POPUP_SCHEMA["$id"]: POPUP_SCHEMA,
        SOURCES_SCHEMA["$id"]: SOURCES_SCHEMA,
    }
    resolver = RefResolver.from_schema(POPUP_SCHEMA, store=schema_store)
    validator = Draft4Validator(POPUP_SCHEMA, resolver=resolver)

    assert validator.validate(POPUP_EXAMPLE) is None  # noqa: S101
