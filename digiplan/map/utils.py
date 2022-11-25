import json
import pathlib
from typing import Optional, Union

import colorbrewer

MAX_COLORBREWER_STEPS = 9


class Choropleth:
    def __init__(self, choropleth_styles_file: Union[str, pathlib.Path]):
        with open(choropleth_styles_file, mode="r", encoding="utf-8") as cs_file:
            self.choropleths = json.load(cs_file)

    def get_all_styles(self):
        return {name: self.get_fill_color(name) for name in self.choropleths}

    def get_fill_color(self, name: str, values: Optional[list] = None):
        """
        Returns fill_color in choropleth style for setPaintProperty of maplibre

        Parameters
        ----------
        name: str
            Name of choropleth
        values: Optional
            Values must be given either dynamically as parameter or must be present as static values in choropleths

        Returns
        -------
        dict:
            Dictionary which can be used as fill_color in maplibre layer

        Raises
        ------
        KeyError
            if either `num_colors` or `values` key is missing in chorpleth style
        IndexError
            if values exceed colorbrewer steps
        """
        choropleth_config = self.choropleths[name]
        if values:
            if "num_colors" not in choropleth_config:
                raise KeyError("`num_colors` has to be se in choropleth style for dynamic choropleth composition.")
            min_value = min(values)
            max_value = max(values)
            num = choropleth_config["num_colors"]
            step = (max_value - min_value) / (num - 1)
            steps = [min_value + i * step for i in range(num - 1)] + [max_value]
        else:
            if "values" not in choropleth_config:
                raise KeyError("`values` have to be set in style file in order to composite choropleth colors.")
            steps = choropleth_config["values"]
        if choropleth_config["color_palette"] not in colorbrewer.sequential["multihue"]:
            raise KeyError(f"Invalid color palette for choropleth {name=}.")
        if len(steps) > MAX_COLORBREWER_STEPS:
            raise IndexError(f"Too many choropleth values given for {name=}.")
        colors = colorbrewer.sequential["multihue"][choropleth_config["color_palette"]][len(steps)]
        fill_color = [
            "interpolate",
            ["linear"],
            ["feature-state", name],
        ]
        for value, color in zip(steps, colors):
            fill_color.append(value)
            rgb_color = f"rgb({color[0]}, {color[1]}, {color[2]})"
            fill_color.append(rgb_color)
        return fill_color
