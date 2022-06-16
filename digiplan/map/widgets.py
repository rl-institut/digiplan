from django.forms.widgets import Widget
from django.utils.safestring import mark_safe


class SliderWidget(Widget):
    template_name = "widgets/slider.html"

    def __init__(
        self,
        label,
        items=None,
        icon=None,
        start=None,
        end=None,
        step=None,
        initial=None,
        item_classes=None,
        tooltip=None,
        **attrs,
    ):
        attrs = {} if attrs is None else attrs.copy()
        attrs["label"] = label
        if items:
            item_classes = item_classes or [None] * len(items)
            attrs["items"] = list(zip(items, item_classes))
        attrs["icon"] = icon
        start = start or 0
        attrs["start"] = start
        if not items and not end:
            raise ValueError("You must either set end or items")
        attrs["end"] = end or len(items) - 1
        attrs["step"] = step or 1
        attrs["initial_start"] = initial or start
        attrs["tooltip"] = tooltip
        super(SliderWidget, self).__init__(attrs)


class DisplayWidget(SliderWidget):
    template_name = "widgets/display.html"


class SliderInputWidget(Widget):
    template_name = "widgets/slider_with_input.html"

    def __init__(self, start, end, step=None, initial=None, **attrs):
        attrs = {} if attrs is None else attrs.copy()
        attrs["start"] = start
        attrs["end"] = end
        attrs["step"] = step or 1
        attrs["initial_start"] = initial or start
        super(SliderInputWidget, self).__init__(attrs)


class SwitchWidget(Widget):
    template_name = "widgets/switch.html"

    def __init__(self, **attrs):
        super(SwitchWidget, self).__init__(attrs)


class JsonWidget:
    def __init__(self, json):
        self.json = json

    def __convert_to_html(self, data, level=0):
        html = ""
        if isinstance(data, dict):
            html += (
                f'<div style="margin-left: {level*2}rem;'
                f"margin-bottom: 0.75rem;"
                f"padding-left: 0.5rem;"
                f'border-left: 1px dotted #002E4F;">'
                if level > 0
                else "<div>"
            )
            for key, value in data.items():
                html += f"<b>{key}:</b> {self.__convert_to_html(value, level+1)}"
            html += "</div>"
        elif isinstance(data, list):
            html += f'<div style="margin-left: {level*2}rem;">'
            for item in data:
                html += f"{self.__convert_to_html(item, level+1)}"
            html += "</div>"
        else:
            html += f"{data}<br>"
        return html

    def render(self):
        header = ""
        if self.json["title"] != "":
            header += f'<p class="lead">{self.json["title"]}</p>'
        if self.json["description"] != "":
            header += f'<p>{self.json["description"]}</p>'
        return mark_safe(header + self.__convert_to_html(data=self.json))  # noqa: S703,S308
