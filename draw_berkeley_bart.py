"""Example visualization for CI / CD exercise.

Example Sketchingpy visualization to use for a CI / CD exercise demonstrating
GitHub actions using https://www.bart.gov/about/reports/ridership data under
CC-BY. Uses March 2024 monthly total trips. This uses the Model View Presenter
architecture.

License: BSD
"""
import sys

import sketchingpy

NUM_ARGS = 2
USAGE_STR = 'USAGE: python draw_berkeley_bart.py input_loc output_loc'

DEFAULT_DATA_LOCATION = 'berkeley_trips.csv'
BG_COLOR = '#EAEAEA'
FG_COLOR = '#333333'
TICK_COLOR = '#FFFFFF'
TITLE = 'Bart trips from Downtown Berkeley to other stations in March 2024.'
WIDTH = 600
HEIGHT = 600
LINE_MIN_LEN = 70
LINE_MAX_LEN = 210


class Station:
    """Data record describing a single station."""

    def __init__(self, name, code, count):
        """Create a new station record.

        Args:
            name: The full name of the station.
            code: The short code name of the station.
            count: The number of trips made in the target month.
        """
        self._name = name
        self._code = code
        self._count = count

    def get_name(self):
        """Get the human-readable name of the station.

        Returns:
            Name of the station like "Downtown Berkeley" as provided by BART.
        """
        return self._name

    def get_code(self):
        """Get the short code name of the station.

        Returns:
            Two character codename for the station like BK.
        """
        return self._code

    def get_count(self):
        """Get the number of trips that went from Berkeley to this station.

        Returns:
            Number of trips to this station in the target month. This is the
            number of "tag outs" for journies which started at Downtown Bereley
            and ended at this station regardless of duration or trains taken.
        """
        return self._count


class DataFacade:
    """Object which simplifies access to ridership data."""

    def __init__(self, sketch):
        """Create a new data facade.

        Args:
            sketch: The sketch through which ridership data will be accessed.
        """
        self._sketch = sketch

    def get_stations(self, loc):
        """Get a list of stations from the underlying data.

        Args:
            loc: The location from which to parse the data.

        Returns:
            List of stations from the underlying dataset sorted by total number
            of trips in ascending order.
        """
        raw_data = self._sketch.get_data_layer().get_csv('berkeley_trips.csv')
        parsed_data = map(lambda x: self._parse_data_point(x), raw_data)
        return sorted(parsed_data, key=lambda x: x.get_count())

    def _parse_data_point(self, target):
        """Parse an input raw CSV row as a Station record.

        Args:
            target: Dictionary representing a single row from the input dataset.

        Returns:
            Station object representing the row after parsing.
        """
        count_str = target['count']
        count_str_clean = count_str.replace(',', '')
        count = int(count_str_clean)
        return Station(target['name'], target['code'], count)


class StationVizPresenter:
    """Presenter which runs the visualization."""

    def __init__(self, sketch):
        """Create a presenter to run a bart visualization.

        Args:
            sketch: The sketch to run.
        """
        self._sketch = sketch

    def draw(self, records):
        """Draw the visualization.

        Args:
            records: The stations to draw.
        """
        self._sketch.clear(BG_COLOR)

        max_value = max(map(lambda x: x.get_count(), records))

        self._draw_title()
        self._draw_axis(max_value)
        self._draw_data(max_value, records)

    def _draw_title(self):
        """Draw the title at the bottom of the visual."""
        self._sketch.clear_stroke()
        self._sketch.set_fill(FG_COLOR)
        self._sketch.set_text_font('PublicSans-Regular.otf', 14)
        self._sketch.set_text_align('center', 'center')
        self._sketch.draw_text(WIDTH / 2, HEIGHT - 20, TITLE)

    def _draw_axis(self, max_value):
        """Draw the axis and other non-data chart elements.

        Args:
            max_value: The maximum number of trips to a single station expected.
        """
        # We will change the coordinate system such that 300, 300 is 0, 0 and
        # push saves the original coordinate system state.
        self._sketch.push_transform()

        # Move to the center of the visualization
        self._sketch.translate(WIDTH / 2, HEIGHT / 2)

        # Setup some drawing preferences
        self._sketch.set_text_align('center', 'center')
        self._sketch.set_ellipse_mode('radius')

        # Draw the Bereley text at the center
        self._sketch.clear_stroke()
        self._sketch.set_fill(FG_COLOR)
        self._sketch.set_text_font('PublicSans-Regular.otf', 20)
        self._sketch.draw_text(0, 0, 'Berkeley')

        # Draw ticks
        self._sketch.set_text_font('PublicSans-Regular.otf', 10)
        for value in range(0, max_value + 5000, 5000):
            x = self._get_line_length(max_value, value)

            # Draw a light reference line as a circle
            self._sketch.clear_fill()
            self._sketch.set_stroke(TICK_COLOR)
            self._sketch.draw_ellipse(0, 0, x, x)

            # Draw number of trips as text
            self._sketch.clear_stroke()
            self._sketch.set_fill(FG_COLOR)
            self._sketch.draw_text(x, 0, f'{value:,}')

        # Put the coordinate system back (restore the coordinate system state
        # we saved earlier with push_transform). This undoes the translate.
        self._sketch.pop_transform()

    def _draw_data(self, max_value, records):
        # We will change the coordinate system such that 300, 300 is 0, 0 and
        # rotate. Push saves the original coordinate system state.
        self._sketch.push_transform()

        # Move to the center of the visualization
        self._sketch.translate(WIDTH / 2, HEIGHT / 2)

        # Set some drawing preferences
        self._sketch.set_angle_mode('degrees')

        # Determine how much we have to space out stations
        num_lanes = len(records) + 1

        # Draw each station
        for record in records:
            # Figure out how far from the center this station will be drawn.
            length = self._get_line_length(max_value, record.get_count())

            # Rotate a little for each station
            self._sketch.rotate(360 / num_lanes)

            # Draw a line from the center according to (length proportional to)
            # the number of trips to that station from Downtown Berkeley.
            self._sketch.clear_fill()
            self._sketch.set_stroke(FG_COLOR)
            self._sketch.draw_line(70, 0, length, 0)

            # Draw the name of the station.
            self._sketch.clear_stroke()
            self._sketch.set_fill(FG_COLOR)
            self._sketch.set_text_font('PublicSans-Regular.otf', 10)
            self._sketch.set_text_align('left', 'center')
            self._sketch.draw_text(length + 2, 0, record.get_name())

        # Put the coordinate system back (restore the coordinate system state
        # we saved earlier with push_transform). This undoes the translate and
        # rotate.
        self._sketch.pop_transform()

    def _get_line_length(self, max_value, count):
        return (LINE_MAX_LEN - LINE_MIN_LEN) / max_value * count + LINE_MIN_LEN


def main():
    """Main function either running in browser, desktop, or command line."""
    if len(sys.argv) == 1:
        data_loc = DEFAULT_DATA_LOCATION
        output_loc = None
        interactive = True
    elif len(sys.argv) == NUM_ARGS + 1:
        data_loc = sys.argv[1]
        output_loc = sys.argv[2]
        interactive = False
    else:
        print(USAGE_STR)
        sys.exit(1)

    # Create a sketch and initalize the data facade (model) and presenter.
    if interactive:
        sketch = sketchingpy.Sketch2DApp(WIDTH, HEIGHT)
    else:
        sketch = sketchingpy.Sketch2DStatic(WIDTH, HEIGHT)

    data_facade = DataFacade(sketch)
    presenter = StationVizPresenter(sketch)

    # Get the data
    data = data_facade.get_stations(data_loc)

    # If running interactive, show the visualization. Otherwise write to disk
    # at location specified.
    if interactive:
        sketch.on_step(lambda x: presenter.draw(data))
        sketch.show()
    else:
        presenter.draw(data)
        sketch.save_image(output_loc)


if __name__ == '__main__':
    main()
