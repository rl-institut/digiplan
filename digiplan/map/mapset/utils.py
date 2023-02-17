from digiplan.map.config import config


def get_color(source_layer):
    if source_layer not in config.LAYER_STYLES:
        raise KeyError(f"Could not find layer '{source_layer}' in layer styles (static/config/layer_styles.json)")
    for color_key in ("fill-color", "line-color", "circle-color"):
        try:
            return config.LAYER_STYLES[source_layer]["paint"][color_key]
        except KeyError:
            continue
    return None
