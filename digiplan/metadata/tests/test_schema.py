# pylint: disable=C0415


def test_if_schema_json_loads_successfully():
    from digiplan.metadata.schema.population.schema import POPULATION_SCHEMA

    assert POPULATION_SCHEMA


def test_if_example_json_loads_successfully():
    from digiplan.metadata.schema.population.example import POPULATION_EXAMPLE

    assert POPULATION_EXAMPLE


def test_example_against_schema_which_should_succeed():
    import jsonschema
    from digiplan.metadata.schema.population.example import POPULATION_EXAMPLE
    from digiplan.metadata.schema.population.schema import POPULATION_SCHEMA

    assert jsonschema.validate(POPULATION_EXAMPLE, POPULATION_SCHEMA) is None
