import unittest
from app import app_io as aio


class TestAppIO(unittest.TestCase):
    def test_app_io(self):
        args = ['input.json', 'control.yaml']
        result = aio.parse_cli_arguments(args)
        print(result)
        print(dir(result))
        self.assertEqual(2, len(result.__dict__.keys()))
        self.assertEqual('input.json', result.domain_state_file)
        self.assertEqual('control.yaml', result.control_file)
