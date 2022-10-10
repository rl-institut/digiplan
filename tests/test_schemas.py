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
    import jsonschema

    from config.schemas import POPUP_DEFAULT_SCHEMA  # noqa: I001
    from config.schemas import POPUP_DEFAULT_EXAMPLE  # noqa: I001

    assert jsonschema.validate(POPUP_DEFAULT_EXAMPLE, POPUP_DEFAULT_SCHEMA) is None  # noqa: S101
