"""Module to implement hooks for django-oemof."""


def parameter_setup(parameters: dict) -> dict:
    """
    First draft of a parameter setup hook for django-oemof.

    Parameters
    ----------
    parameters: dict
        Parameters set by user in digiplan ES settings form

    Returns
    -------
    dict
        Updated parameters as input for ES building in django-oemof
    """

    demand = parameters.pop("electricity")
    parameters["demand0"] = {"amount": demand["demand"]}
    return parameters
