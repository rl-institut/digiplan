# pylint: disable=C0415


# Components Schema Tests


def test_if_chart_example_validates():
    import jsonschema

    from config.schemas import CHART_SCHEMA  # noqa: I001
    from config.schemas import CHART_EXAMPLE  # noqa: I001

    assert jsonschema.validate(CHART_EXAMPLE, CHART_SCHEMA) is None  # noqa: S101


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


# Popup Schema Test


def test_if_popup_example_validates():
    from jsonschema import Draft202012Validator, RefResolver

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
    validator = Draft202012Validator(POPUP_SCHEMA, resolver=resolver)

    assert validator.validate(POPUP_EXAMPLE) is None  # noqa: S101
