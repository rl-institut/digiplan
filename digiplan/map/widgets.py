"""Module holds widgets for digiplan."""

from django.forms.widgets import Widget


class SliderWidget(Widget):
    """Widget to render sliders."""

    template_name = "widgets/slider.html"


class SwitchWidget(Widget):
    """Widget to render switches."""

    template_name = "widgets/switch.html"
