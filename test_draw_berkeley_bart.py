"""Unit tests for the BART Berkeley trips visualization.

License: BSD
"""

import unittest

import sketchingpy

import draw_berkeley_bart


class BerkeleyBartTests(unittest.TestCase):

    def setUp(self):
        self._sketch = sketchingpy.Sketch2D(500, 500)

    def test_parse_data_point(self):
        data_facade = draw_berkeley_bart.DataFacade(self._sketch)
        result = data_facade._parse_data_point({
            'name': 'test',
            'code': 'te',
            'count': '1,234'
        })
        self.assertEqual(result.get_name(), 'test')
        self.assertEqual(result.get_code(), 'te')
        self.assertEqual(result.get_count(), 1234)

    def test_get_line_length_zero(self):
        presenter = draw_berkeley_bart.StationVizPresenter(self._sketch)
        self.assertEqual(presenter._get_line_length(100, 0), draw_berkeley_bart.LINE_MIN_LEN)

    def test_get_line_length_max(self):
        presenter = draw_berkeley_bart.StationVizPresenter(self._sketch)
        self.assertEqual(presenter._get_line_length(100, 100), draw_berkeley_bart.LINE_MAX_LEN)

    def test_get_line_length_half(self):
        presenter = draw_berkeley_bart.StationVizPresenter(self._sketch)
        halfway = (draw_berkeley_bart.LINE_MAX_LEN + draw_berkeley_bart.LINE_MIN_LEN) / 2
        self.assertEqual(presenter._get_line_length(100, 50), halfway)
