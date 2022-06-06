import unittest
from app import app_io as aio


class TestAppIO(unittest.TestCase):
    def test_sim_cli_arguments(self):
        args = ['input.json', 'control.yaml', 'output.pickle', '-s', 'partial']
        result = aio.sim_cli_arguments(args)
        print(result)
        print(dir(result))
        self.assertEqual(4, len(result.__dict__.keys()))
        self.assertEqual('input.json', result.domain_state_file)
        self.assertEqual('control.yaml', result.control_file)
        self.assertEqual('output.pickle', result.output_file)
        self.assertEqual('partial', result.strategy)
