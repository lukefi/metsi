import unittest

from app import app_io as aio

class TestAppIO(unittest.TestCase):
    def test_app_io(self):
        args = ['input.json', 'control.yaml']
        result = aio.parse_cli_arguments(args)
        print(result)
        print(dir(result))
        self.assertEquals(2, len(result.__dict__.keys()))
        self.assertEquals('input.json', result.domain_state_file)
        self.assertEquals('control.yaml', result.control_file)
