import argparse
import json
import re
from argparse import RawTextHelpFormatter
from typing import Any, Dict, List, Tuple, Union

import matplotlib.pyplot as plt


class NormalizeLabels:
    """A class to generate sub or superscripted text

    The normalized text or label will be used on the plot
    """

    def __init__(self, label: str) -> None:
        self.label = label

    def get(self):
        regex = r"(\w+)_\((\w+)\)(.*)"
        result = re.findall(regex, self.label)
        if not result:
            return self.label
        result = result[0]
        return rf"${result[0]}_{{{result[1]}}}{result[2]}$"


class Plot:
    def __init__(
        self,
        data: Dict[str, float],
        line_properties: Dict[str, str],
        text_properties: Dict[str, str],
        display_values: bool = True,
        display_labels: bool = True,
        offset=5.0,
        distance=2.0,
    ) -> None:
        """Constructor for Plot.

        Args:
            data: A dictionary containing labels as key and 'y' coordinate as value

            display_values: Display values on the plot if True
            display_labels: Display labels on the plot if True
            style: Plot style
            offset: Determines line length starting from beginning 'x' coordinate
            distance: Distance between two lines
        """
        self.display_values = display_values
        self.display_labels = display_labels
        self.line_properties = line_properties
        self.text_properties = text_properties
        self.data = data
        self.offset = offset
        self.begin_at = 0  # The lines will be ploted starting at this 'x' coord.
        self.distance = distance

    def _plot_block(self, coord: Tuple[List[float], List[float]], label: str):
        """Plots a block

        A block contains line, text and value
        """
        label = NormalizeLabels(label).get()
        xcords, ycoords = coord
        text_size = self.text_properties["size"]
        text_color = self.text_properties["color"]
        if self.display_values:
            plt.text(
                xcords[0],
                ycoords[0] + 0.2,
                str(ycoords[0]),
                size=text_size,
                color=text_color,
            )

        plt.plot(
            xcords,
            ycoords,
            color=self.line_properties["color"],
            linewidth=self.line_properties["width"],
        )

        if self.display_labels:
            plt.text(
                xcords[0],
                ycoords[0] - 2,  # - self.line_properties["width"] / 2,
                label,
                size=text_size,
                color=text_color,
            )

    def _plot_dashed_lines(self, starting_points: List[Tuple[float, float]]):
        """Plot dashed lines

        The dashed lines connect end and beginning of consecutive
        main lines.
        """
        color = self.line_properties["color"]
        thicknes = self.line_properties["dashed_width"]
        first = starting_points[0]
        for xcoord, ycoord in starting_points[1:]:
            first_xcoord, first_ycoord = first
            plt.plot(
                [first_xcoord + self.offset, xcoord],
                [first_ycoord, ycoord],
                linestyle="dashed",
                linewidth=thicknes,
                color=color,
            )
            first = (xcoord, ycoord)

    def create(self):
        """Creates the final plot"""
        begin_at = self.begin_at
        starting_points = []
        for label, point in self.data.items():
            xcoords = [begin_at, begin_at + self.offset]
            ycoords = [point, point]
            starting_points.append((begin_at, point))
            self._plot_block((xcoords, ycoords), label)
            begin_at = begin_at + self.offset + self.distance
        self._plot_dashed_lines(starting_points)


def get_available_styles():
    result = "Available stles are:"
    for style in plt.style.available:
        result = f"{result}\n    - {style}"
    return result


parser = argparse.ArgumentParser(
    prog="PotentialEnergySurface",
    description="TODO",
    epilog=get_available_styles(),
    formatter_class=RawTextHelpFormatter,
)

parser.add_argument("filepath", help="Absolute path to a json file which contains data")
parser.add_argument("--no-values", action="store_true", help="Display values if True")
parser.add_argument("--no-labels", action="store_true", help="Display labels if True")
parser.add_argument("--line_width", type=int, default=2, help="width of the main lines")
parser.add_argument(
    "--dashed-line-width", type=int, default=0.5, help="width of the dashed lines"
)
parser.add_argument(
    "--style", type=str, default="bmh", help="Plot style for matplotlib"
)

parser.add_argument(
    "--text_size", type=int, default=10, help="Font size for texts on the plot"
)
parser.add_argument(
    "--distance", type=int, default=2, help="Distance betwee main lines"
)
parser.add_argument("--line-length", type=int, default=5, help="Length of a line")


def read_json(path: str) -> Dict[str, Any]:
    with open(path, "r") as file:
        data = json.load(file)
        return data


def get_line_properties(args, colors, index):
    return {
        "color": colors[index],
        "width": args.line_width,
        "dashed_width": args.dashed_line_width,
    }


def get_text_properties(args, index: int, colors: List[str]):
    return {"color": colors[index], "size": args.text_size}


def seperate_data(data):
    result = []
    length = len(list(data.values())[0])
    dict_ = {}

    for index in range(length):
        for key in data:
            dict_[key] = data[key][index]
        result.append(dict_)
        dict_ = {}
    return result


def init_plt(style, max_, min_, yaxis_annotation: str):

    plt.figure(figsize=(10, 10))
    plt.box(False)
    plt.style.use(style)
    plt.xticks([])
    plt.yticks([])
    plt.plot([-10, -10], [max_ + 2, min_ - 2])
    plt.text(-8, max_ + 2, yaxis_annotation)


def get_min_and_max_vals(data: Dict[str, List[float]]) -> Tuple[float, float]:
    values = [x for y in data.values() for x in y]
    return min(values), max(values)


if __name__ == "__main__":
    args = parser.parse_args()
    data = read_json(args.filepath)
    colors: List[str] = data["colors"]
    data = data["data"]
    min_, max_ = get_min_and_max_vals(data)
    init_plt(args.style, max_, min_, "$\Delta$G [kcal/mol]")
    for index, data in enumerate(seperate_data(data)):

        line_prop = get_line_properties(args, colors, index)
        text_prop = get_text_properties(args, index, colors)
        plot = Plot(
            data=data,  # type: ignore
            display_labels=not args.no_labels,
            display_values=not args.no_values,
            line_properties=line_prop,
            text_properties=text_prop,
            distance=args.distance,
            offset=args.line_length,
        )
        plot.create()
    plt.show()
