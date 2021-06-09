from crispy_forms.helper import FormHelper
from django.forms import BooleanField, Form, IntegerField, TextInput, MultiValueField
from django.db.models import Min, Max

from .widgets import SwitchWidget


class StaticLayerForm(Form):
    switch = BooleanField(
        label=False, widget=SwitchWidget(switch_class="switch tiny", switch_input_class="switch-input",),
    )

    def __init__(self, layer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layer = layer
        self.fields["switch"].widget.attrs["id"] = f"fill-{layer['source']}"

        if hasattr(layer["model"], "filters"):
            self.has_filters = True
            for filter in layer["model"].filters:
                filter_min = layer["model"].objects.aggregate(Min(filter))[f"{filter}__min"]
                filter_max = layer["model"].objects.aggregate(Max(filter))[f"{filter}__max"]
                self.fields[filter] = MultiValueField(
                    label=getattr(layer["model"], filter).field.verbose_name,
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

        self.helper = FormHelper(self)
        self.helper.template = "forms/layer.html"
