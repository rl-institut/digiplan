from crispy_forms.helper import FormHelper
from django.forms import BooleanField, Form, IntegerField, TextInput, MultiValueField

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
                self.fields[filter] = MultiValueField(
                    label=False,
                    fields=[IntegerField(), IntegerField()],
                    widget=TextInput(
                        attrs={
                            "class": "js-range-slider",
                            "data-type": "double",
                            "data-min": 0,
                            "data-max": 1000,
                            "data-from": 200,
                            "data-to": 500,
                            "data-grid": True,
                        }
                    ),
                )

        self.helper = FormHelper(self)
        self.helper.template = "forms/layer.html"
