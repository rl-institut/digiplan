from itertools import count

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django.db.models import Max, Min
from django.forms import (
    BooleanField,
    Form,
    IntegerField,
    MultipleChoiceField,
    MultiValueField,
    TextInput,
)
from django_select2.forms import Select2MultipleWidget

from . import models
from .config import config
from .widgets import SwitchWidget


class StaticLayerForm(Form):
    switch = BooleanField(
        label=False,
        widget=SwitchWidget(
            attrs={
                "switch_class": "form-check form-switch",
                "switch_input_class": "form-check-input",
            }
        ),
    )
    counter = count()

    def __init__(self, layer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layer = layer
        self.fields["switch"].widget.attrs["id"] = layer.source

        if hasattr(layer.model, "filters"):
            self.has_filters = True
            for filter_ in layer.model.filters:
                if filter_.type == models.LayerFilterType.Range:
                    filter_min = layer.model.vector_tiles.aggregate(Min(filter_.name))[f"{filter_.name}__min"]
                    filter_max = layer.model.vector_tiles.aggregate(Max(filter_.name))[f"{filter_.name}__max"]
                    self.fields[filter_.name] = MultiValueField(
                        label=getattr(layer.model, filter_.name).field.verbose_name,
                        fields=[IntegerField(), IntegerField()],
                        widget=TextInput(
                            attrs={
                                "class": "js-range-slider",
                                "data-type": "double",
                                "data-min": filter_min,
                                "data-max": filter_max,
                                "data-from": filter_min,
                                "data-to": filter_max,
                                "data-grid": True,
                            }
                        ),
                    )
                elif filter_.type == models.LayerFilterType.Dropdown:
                    filter_values = (
                        layer.model.vector_tiles.values_list(filter_.name, flat=True).order_by(filter_.name).distinct()
                    )
                    self.fields[filter_.name] = MultipleChoiceField(
                        choices=[(value, value) for value in filter_values],
                        widget=Select2MultipleWidget(attrs={"id": f"{filter_.name}_{next(self.counter)}"}),
                    )
                else:
                    raise ValueError(f"Unknown filter type '{filter_.type}'")

        self.helper = FormHelper(self)
        self.helper.template = "forms/layer.html"


class TooltipField(Field):
    def __init__(self, *args, tooltip, **kwargs):
        super().__init__(*args, **kwargs)
        self.tooltip = tooltip

    def render(self, *args, **kwargs):
        extra_context = kwargs.pop("extra_context", {})
        extra_context["tooltip"] = self.tooltip
        return super().render(*args, extra_context=extra_context, **kwargs)


class WindAreaForm(Form):
    def __init__(self):
        super().__init__()
        self.helper = FormHelper(self)
        self.helper.layout = Layout()
        for identifier, parameters in config.PARAMETERS.items():
            if parameters["type"] == "slider":
                attrs = {
                    "class": "js-range-slider",
                    "data-min": parameters["min"],
                    "data-max": parameters["max"],
                    "data-from": parameters["start"],
                    "data-grid": True,
                }
                if "to" in parameters:
                    attrs["data-to"] = parameters["to"]
                field = IntegerField(
                    label=parameters["label"],
                    widget=TextInput(attrs=attrs),
                )
                self.helper.layout.append(
                    TooltipField(identifier, tooltip=parameters["tooltip"], template="widgets/slider.html")
                )
            elif parameters["type"] == "switch":
                field = BooleanField(label=parameters["label"])
            else:
                raise ValueError(f"Unknown parameter type '{parameters['type']}'")
            self.fields[identifier] = field
