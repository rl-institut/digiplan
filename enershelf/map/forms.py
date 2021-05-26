from crispy_forms.helper import FormHelper
from django.forms import BooleanField, Form, IntegerField

from .widgets import SliderWidget, SwitchWidget


class StaticLayerForm(Form):
    switch = BooleanField(
        label=False,
        widget=SwitchWidget(
            switch_class="switch tiny", switch_input_class="switch-input",
        ),
    )

    def __init__(self, layer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layer = layer
        self.fields["switch"].widget.attrs["id"] = f"fill-{layer['source']}"

        if hasattr(layer["model"], "setup"):
            self.has_setup = True
            setup_model = layer["model"]._meta.get_field("setup").related_model
            for setup in setup_model._meta.fields:
                if setup.name == "id":
                    continue
                self.fields[setup.name] = IntegerField(
                    label=False,
                    widget=SliderWidget(
                        label=setup.verbose_name,
                        icon=setup.icon,
                        items=[choice[0] for choice in setup.choices],
                        id=setup.name,
                        item_id=f"{setup.name}_items",
                        filter_class="slider-item",
                        header_class="slider-item__heading",
                        item_class="slider-item__numbers",
                    ),
                )

        self.helper = FormHelper(self)
        self.helper.template = "forms/layer.html"
