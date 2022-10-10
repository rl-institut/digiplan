# pylint: disable=C0415


def test_if_atom_chart_schema_loads():
    from config.schemas import ATOM_CHART_SCHEMA

    assert ATOM_CHART_SCHEMA  # noqa: S101


def test_if_atom_chart_example_loads():
    from config.schemas import ATOM_CHART_EXAMPLE

    assert ATOM_CHART_EXAMPLE  # noqa: S101


def test_if_atom_chart_example_validates():
    import jsonschema

    from config.schemas import ATOM_CHART_SCHEMA  # noqa: I001
    from config.schemas import ATOM_CHART_EXAMPLE  # noqa: I001

    assert jsonschema.validate(ATOM_CHART_EXAMPLE, ATOM_CHART_SCHEMA) is None  # noqa: S101


def test_if_popup_default_schema_loads():
    from config.schemas import POPUP_DEFAULT_SCHEMA

    assert POPUP_DEFAULT_SCHEMA  # noqa: S101


def test_if_popup_default_example_loads():
    from config.schemas import POPUP_DEFAULT_EXAMPLE

    assert POPUP_DEFAULT_EXAMPLE  # noqa: S101


def test_if_popup_default_example_validates():
    from jsonschema import Draft202012Validator, RefResolver

    from config.schemas import ATOM_CHART_SCHEMA  # noqa: I001
    from config.schemas import POPUP_DEFAULT_SCHEMA  # noqa: I001
    from config.schemas import POPUP_DEFAULT_EXAMPLE  # noqa: I001

    schema_store = {
        ATOM_CHART_SCHEMA["$id"]: ATOM_CHART_SCHEMA,
        POPUP_DEFAULT_SCHEMA["$id"]: POPUP_DEFAULT_SCHEMA,
    }
    resolver = RefResolver.from_schema(ATOM_CHART_SCHEMA, store=schema_store)
    validator = Draft202012Validator(POPUP_DEFAULT_SCHEMA, resolver=resolver)

    assert validator.validate(POPUP_DEFAULT_EXAMPLE) is None  # noqa: S101
