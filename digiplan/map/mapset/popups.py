import json
import os
from dataclasses import dataclass
from typing import Optional

from django.conf import settings


@dataclass
class Popup:
    source: str
    layer_id: str
    fields: str
    template_url: Optional[str] = None


def get_popups(layers, prio):
    suffixes = ["", "_distilled"] if settings.USE_DISTILLED_MVTS else [""]
    popups = []
    for layer in layers:
        if not layer.popup_fields:
            continue

        for suffix in suffixes:
            if layer.clustered and suffix == "_distilled":
                # Clustered layers are not distilled
                continue
            layer_id = f"{layer.source}{suffix}"

            popup_fields = {}
            for popup_field in layer.popup_fields:
                label = (
                    getattr(layer.model, popup_field).field.verbose_name
                    if hasattr(layer.model, popup_field)
                    else popup_field
                )
                popup_fields[label] = popup_field
            template_url = (
                f"popups/{layer.source}.html"
                if os.path.exists(settings.APPS_DIR.path("templates", "popups", f"{layer.source}.html"))
                else None
            )
            popups.append(Popup(layer.source, layer_id, json.dumps(popup_fields), template_url=template_url))
    return sorted(popups, key=lambda x: len(prio) if x.source not in prio else prio.index(x.source))
