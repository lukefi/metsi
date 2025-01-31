import unittest
from collections.abc import Callable
from pathlib import Path

from lukefi.metsi.app import file_io
from lukefi.metsi.data.formats.ForestBuilder import VMIBuilder, VMI13Builder, VMI12Builder


class ConverterTestSuite(unittest.TestCase):
    def run_with_test_assertions(self, assertions: list[tuple], fn: Callable):
        for case in assertions:
            result = fn(*case[0])
            self.assertEqual(case[1], result)

    def assertions_should_raise_TypeError(self, assertions: list[tuple], fn: Callable):
        for case in assertions:
            self.assertRaises(TypeError, fn, *case[0])

class ForestBuilderTestBench(unittest.TestCase):

    default_builder_flags = {"measured_trees": True, "strata": True}

    @classmethod
    def vmi12_builder(cls, vmi_builder_flags: dict = default_builder_flags) -> VMI12Builder:
        vmi12_data = [
            'K0999999 99 11    66521333246174    1010   0041721         000059500417      1   0         40020618 B0          0   0 0   0              0  0                   6652133.85 C 102600.11 66521333246174                                                                                          0      0',
            'K0999999 98 11    66521333246174    1010   1141721         140259100417404   6  99  1241271S1280818 101 1 30    0   0 0   0   00  0 10   0  0   111 011004322   6652133.94 J 118950.77 66521333246174 S1 5 1         09K10E10L09M09M19           24189 04506      1298460   0 0   0 0   00 222 1      1',
            'K0999999 98 12 01  1 11             24 190  04606N17 1  84A1 0',
            'K0999999 98 13001 1207217 2  01 15521741  020081711 00                                                              7725 3999  342                                                                                                                                           259959  134571   11515 39185 101864  4303 11769  8489 24696 4196',
            'K0999999 97 11    66521333246174    1010   1117021         060059100170409   2   3  1891251S7260918 101 1 20    0   0 0   0   00  0 00   0  0   0   011004323   6652133.28 T  97955.34 66521333246174 S1 3 3         00M00M00M      00      1800 04050 00705 1000012940A    0 0   0 12  00 222 1      3   9383',
            'K0999999 97 12 01  1 31 1800 5000   04 050  00705F00 1 714B2 0',
            'K0999999 96 21    66521333246174    0100   1041721         000059100417      4  55         S0280818 101 3 4     0   0 0   0    132       0  0        1          6652133.05 T 117155.45 66521333246174    5 1                                                          0A                              3  19 21'
        ]

        vmi12_builder: VMIBuilder = VMI12Builder(vmi_builder_flags, {}, vmi12_data)
        return vmi12_builder

    @classmethod
    def vmi13_builder(cls, vmi_builder_flags: dict = default_builder_flags) -> VMI13Builder:
        vmi13_file_path = Path('tests', 'data', 'resources', 'VMI13_source_mini.dat')
        vmi13_data = file_io.vmi_file_reader(vmi13_file_path)
        vmi13_builder: VMIBuilder = VMI13Builder(vmi_builder_flags, {}, vmi13_data)
        return vmi13_builder

    @classmethod
    def vmi12_built(cls, vmi_builder_flags: dict =default_builder_flags):
        return cls.vmi12_builder(vmi_builder_flags).build()

    @classmethod
    def vmi13_built(cls, vmi_builder_flags: dict = default_builder_flags):
        return cls.vmi13_builder(vmi_builder_flags).build()

# vmi13_data = [
#     '1 U 1  99  99 99 9   . 0 20181121 2018 258 3 1 10 10  . 12 10 176 176 893    1    5 4 S 7013044.52 543791.23 7013044.52 543791.23  179.70 1019    . T  1 3   33 220  0   . 0  . 1 0  0  . . 0 1  0  . . 0 0 2 3 0  . 2 3 1 35 2 3 2 0 4  75 0 0 3 1 5  2 .  . .  . 15 4 10 0 15 2 10 8 15 6 26 .  .  .    . 22 187  63 19 . U     . E 1 . . 0 A . . . . 0 . 0 .  . 0 . 7 3 . . 4 1 . 2 2 2   0 . . 0 . .   1  0 0 .   . 0 0 . . .         . 1 7013044.52 543791.23 .    .',
#     '3 U 1  99  99 99 9  10 0 20181121 258  11 V  1  250 7 2    .    . 306  863 1  0 0 .   .   .   .   .  . . .  .  .  .  . .  . .  . . . . . .   .   . .  .   .   .   .   . .   . . .   . . .   . . .   . . .   . . .   . . .   . . .   . . . .  . .  . .  . .  . .  . .  . .  . .  .     .     .     .     .     .     .     .     .     .        .        .        .     .       .      .      .      .      .     . .    .',
#     '3 U 1  99  99 99 9  10 0 20181121 258  11 V  1  250 7 2    .    . 306  863 1  0 0 .   .   .   .   .  . . .  .  .  .  . .  . .  . . . . . .   .   . .  .   .   .   .   . .   . . .   . . .   . . .   . . .   . . .   . . .   . . .   . . . .  . .  . .  . .  . .  . .  . .  . .  .     .     .     .     .     .     .     .     .     .        .        .        .     .       .      .      .      .      .     . .    .',
#     '1 U 1  99  99 99 8   . 0 20181102 2018 258 3 1 10 10  . 11  9 402 402 430    6   20 1 S 7012044.52 543491.23 7012044.52 543491.23  136.10 1084    . T  2 3   54 205  0   . 8 18 1 0  0  . . 0 1  0  . . 0 0 1 3 0  . . 0 0  . 0 . 1 0 1   5 3 2 3 1 3  2 .  . .  .  3 9  2 0  3 2  . .  . .  5 .  .  . 2150  4  35   6  8 . S 10600 E 2 7 0 1 6 0 . . . 2 A 1 A  2 0 . 1 2 . . 0 0 . 2 2 2   0 . . 0 . .   . 25 0 .   . 4 0 . . .         . 1 7030854.37 539811.92 .    .',
#     '2 U 1  99  99 99 8   1 0 20181102 258 1  2 3 1350  1400  4  38 E   7  8 F  2 .  0 .  .  . .  . .    .',
#     '6 U 1  99  99 99 8   6 0 20181102 258  7  3  0  23 V2  3  53  6  1  4  35  4  .  .   .  .  .  .   .  .  .  .   .  .  .  .   .  .  .  .   .  .  .  .   .  .  .  .   .  .  .  .   .  . .    .',
#     ""
# ]
# vmi13_builder: VMIBuilder = VMI13Builder({ 'measured_trees': True, 'strata': True}, vmi13_data)
