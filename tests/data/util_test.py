from tests.data import test_util
from lukefi.metsi.data.formats.util import parse_int, parse_float, get_or_default


class TestOptionUtil(test_util.ConverterTestSuite):
    def test_parse_int(self):
        assertions = [
            (['123'], 123),
            ([' 2'], 2),
            ([' '], None),
            (['kissa123'], None),
        ]
        self.run_with_test_assertions(assertions, parse_int)

    def test_parse_float(self):
        assertions = [
            (['123'], 123.0),
            (['123.231'], 123.231),
            ([' 2'], 2.0),
            ([' '], None),
            (['kissa123'], None),
        ]
        self.run_with_test_assertions(assertions, parse_float)

    def test_get_or_default(self):
        assertions = [
            ([1], 1),
            ([None, 1], 1),
            ([None], None),
            ([None, None], None)
        ]
        self.run_with_test_assertions(assertions, get_or_default)
