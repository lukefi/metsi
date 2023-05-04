import typing
import unittest

from lukefi.metsi.data.formats.ForestBuilder import VMIBuilder, VMI13Builder


class ConverterTestSuite(unittest.TestCase):
    def run_with_test_assertions(self, assertions: typing.List[typing.Tuple], fn: typing.Callable):
        for case in assertions:
            result = fn(*case[0])
            self.assertEqual(case[1], result)

    def assertions_should_raise_TypeError(self, assertions: typing.List[typing.Tuple], fn: typing.Callable):
        for case in assertions:
            self.assertRaises(TypeError, fn, *case[0])


vmi13_data = [
    '1 U 1  99  99 99 9   . 0 20181121 2018 258 3 1 10 10  . 12 10 176 176 893    1    5 4 S 7013044.52 543791.23 7013044.52 543791.23  179.70 1019    . T  1 3   33 220  0   . 0  . 1 0  0  . . 0 1  0  . . 0 0 2 3 0  . 2 3 1 35 2 3 2 0 4  75 0 0 3 1 5  2 .  . .  . 15 4 10 0 15 2 10 8 15 6 26 .  .  .    . 22 187  63 19 . U     . E 1 . . 0 A . . . . 0 . 0 .  . 0 . 7 3 . . 4 1 . 2 2 2   0 . . 0 . .   1  0 0 .   . 0 0 . . .         . 1 7013044.52 543791.23 .    .',
    '3 U 1  99  99 99 9  10 0 20181121 258  11 V  1  250 7 2    .    . 306  863 1  0 0 .   .   .   .   .  . . .  .  .  .  . .  . .  . . . . . .   .   . .  .   .   .   .   . .   . . .   . . .   . . .   . . .   . . .   . . .   . . .   . . . .  . .  . .  . .  . .  . .  . .  . .  .     .     .     .     .     .     .     .     .     .        .        .        .     .       .      .      .      .      .     . .    .',
    '3 U 1  99  99 99 9  10 0 20181121 258  11 V  1  250 7 2    .    . 306  863 1  0 0 .   .   .   .   .  . . .  .  .  .  . .  . .  . . . . . .   .   . .  .   .   .   .   . .   . . .   . . .   . . .   . . .   . . .   . . .   . . .   . . . .  . .  . .  . .  . .  . .  . .  . .  .     .     .     .     .     .     .     .     .     .        .        .        .     .       .      .      .      .      .     . .    .',
    '1 U 1  99  99 99 8   . 0 20181102 2018 258 3 1 10 10  . 11  9 402 402 430    6   20 1 S 7012044.52 543491.23 7012044.52 543491.23  136.10 1084    . T  2 3   54 205  0   . 8 18 1 0  0  . . 0 1  0  . . 0 0 1 3 0  . . 0 0  . 0 . 1 0 1   5 3 2 3 1 3  2 .  . .  .  3 9  2 0  3 2  . .  . .  5 .  .  . 2150  4  35   6  8 . S 10600 E 2 7 0 1 6 0 . . . 2 A 1 A  2 0 . 1 2 . . 0 0 . 2 2 2   0 . . 0 . .   . 25 0 .   . 4 0 . . .         . 1 7030854.37 539811.92 .    .',
    '2 U 1  99  99 99 8   1 0 20181102 258 1  2 3 1350  1400  4  38 E   7  8 F  2 .  0 .  .  . .  . .    .',
    '6 U 1  99  99 99 8   6 0 20181102 258  7  3  0  23 V2  3  53  6  1  4  35  4  .  .   .  .  .  .   .  .  .  .   .  .  .  .   .  .  .  .   .  .  .  .   .  .  .  .   .  .  .  .   .  . .    .',
    ""
]
vmi13_builder: VMIBuilder = VMI13Builder({ 'reference_trees': True}, vmi13_data)
