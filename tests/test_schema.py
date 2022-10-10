# pylint: disable=C0415


def test_if_schema_popup_default_json_loads_successfully():
    from config.schema import SCHEMA_POPUP_DEFAULT

    assert SCHEMA_POPUP_DEFAULT  # noqa: S101


def test_if_example_json_loads_successfully():
    from config.schema import EXAMPLE_POPUP_POPULATION

    assert EXAMPLE_POPUP_POPULATION  # noqa: S101


def test_example_against_default_schema_which_must_succeed():
    import jsonschema

    from config.schema import EXAMPLE_POPUP_POPULATION  # noqa: I001
    from config.schema import SCHEMA_POPUP_DEFAULT  # noqa: I001

    # noqa: I005
    assert jsonschema.validate(EXAMPLE_POPUP_POPULATION, SCHEMA_POPUP_DEFAULT) is None  # noqa: S101
