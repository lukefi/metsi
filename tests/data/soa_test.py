import copy
import unittest
from dataclasses import dataclass
from typing import ClassVar

from lukefi.metsi.data.soa import Soa, Soable


@dataclass
class ExampleType(object):
    i: int = 1
    f: float = 1.0
    s: str = "1"

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


@dataclass
class OverlaidExampleType(Soable):
    i: int = 1
    f: float = 1.0
    s: str = "1"

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()


def create_fixture(cls: type = ExampleType) -> list[ExampleType]:
    return [
        cls(),
        cls(),
        cls()
    ]


class SoaTest(unittest.TestCase):
    def test_soa_initialization_with_no_properties(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture)
        self.assertEqual(3, len(soa.objects))
        self.assertEqual(0, len(soa.props))
        for f in fixture:
            self.assertTrue(soa.has_object(f))
            self.assertFalse(soa.has_object(ExampleType()))
            self.assertEqual(0, len(soa.props))

    def test_soa_initialization_with_some_properties(self):
        fixture = create_fixture()
        property_names = ['f', 'i']
        soa = Soa(object_list=fixture, initial_property_names=property_names)
        self.assertEqual(3, len(soa.objects))
        self.assertEqual(2, len(soa.props))
        for prop in property_names:
            self.assertTrue(soa.has_property(prop))
        for f in fixture:
            self.assertTrue(soa.has_object(f))
            self.assertFalse(soa.has_object(ExampleType()))
            self.assertEqual(2, len(soa.props))
            self.assertListEqual([f.f, f.i], [x[1] for x in soa.get_object_properties(f)])

    def test_object_add_with_no_properties(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture)
        new_object_1 = ExampleType()
        new_object_2 = ExampleType()
        soa.upsert_objects([new_object_1, new_object_2])
        self.assertTrue(soa.has_object(new_object_1))
        self.assertTrue(soa.has_object(new_object_2))
        self.assertEqual(0, len(soa.get_object_properties(new_object_1)))
        self.assertEqual(0, len(soa.get_object_properties(new_object_2)))

    def test_new_object_upsert_with_some_properties(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture, initial_property_names=['i', 'f'])
        new_object_1 = ExampleType(i=4, f=4.0)
        fixture.append(new_object_1)
        new_object_2 = ExampleType(i=5, f=5.0)
        fixture.append(new_object_2)
        soa.upsert_objects([new_object_1, new_object_2])
        self.assertTrue(soa.has_object(new_object_1))
        self.assertTrue(soa.has_object(new_object_2))
        self.assertEqual(2, len(soa.get_object_properties(new_object_1)))
        self.assertEqual(2, len(soa.get_object_properties(new_object_2)))

        # column values
        self.assertListEqual([new_object_1.i, new_object_1.f], [x[1] for x in soa.get_object_properties(new_object_1)])
        self.assertListEqual([new_object_2.i, new_object_2.f], [x[1] for x in soa.get_object_properties(new_object_2)])

        # row values
        self.assertListEqual([x.i for x in fixture], list(soa.get_property_values('i')))
        self.assertListEqual([x.f for x in fixture], list(soa.get_property_values('f')))

    def test_existing_object_upsert_with_some_properties(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture, initial_property_names=['i', 'f'])
        new_value = 10
        fixture[0].i = new_value
        self.assertEqual([1, 1.0], [x[1] for x in soa.get_object_properties(fixture[0])])
        soa.upsert_objects([fixture[0]])
        self.assertEqual([new_value, 1.0], [x[1] for x in soa.get_object_properties(fixture[0])])

    def test_del_objects(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture)
        soa.del_objects([fixture[1]])
        self.assertEqual(2, len(soa.objects))
        self.assertTrue(soa.has_object(fixture[0]))
        self.assertFalse(soa.has_object(fixture[1]))
        self.assertTrue(soa.has_object(fixture[2]))

    def test_get_object_properties(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture, initial_property_names=['i', 'f'])
        result = soa.get_object_properties(fixture[0])
        self.assertListEqual(['i', 'f'], [x[0] for x in result])
        self.assertListEqual([fixture[0].i, fixture[0].f], [x[1] for x in result])

    def test_get_existing_object_property(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture, initial_property_names=['i', 'f'])
        result = soa.get_object_property('i', fixture[0])
        self.assertEqual(1, result)

    def test_get_nonexisting_object_property(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture, initial_property_names=['i', 'f'])
        no_result_prop = soa.get_object_property('h', fixture[0])
        no_result_obj = soa.get_object_property('i', ExampleType())
        self.assertIsNone(no_result_prop)
        self.assertIsNone(no_result_obj)

    def test_get_property_values(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture, initial_property_names=['i', 'f'])
        result = soa.get_property_values('i')
        self.assertListEqual([x.i for x in fixture], list(result))

    def test_set_property_values(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture, initial_property_names=['i', 'f'])
        new_values = [3, 4, 5]
        soa.upsert_property_values('i', new_values)
        # TODO: should we prevent adding values for a property which does not exist in the base class?
        soa.upsert_property_values('g', new_values)

        self.assertListEqual([x.f for x in fixture], list(soa.get_property_values('f')))
        self.assertListEqual(new_values, list(soa.get_property_values('i')))
        self.assertListEqual(new_values, list(soa.get_property_values('g')))

        # should fail upon mismatch of row length
        self.assertRaises(ValueError, soa.upsert_property_values, *['i', [3, 4, 5, 6]])

    def test_set_single_value_for_new_property(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture, initial_property_names=['i'])
        soa.upsert_property_value(fixture[0], 'f', 2.0)

        self.assertTrue(soa.has_property('f'))
        self.assertEqual(2.0, soa.get_object_property('f', fixture[0]))
        self.assertEqual(1.0, soa.get_object_property('f', fixture[1]))

    def test_set_single_value_for_new_object(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture, initial_property_names=['i'])
        new_obj = ExampleType()
        soa.upsert_property_value(new_obj, 'f', 2.0)

        self.assertTrue(soa.has_property('f'))
        self.assertEqual(4, len(soa.objects))
        self.assertEqual(2.0, soa.get_object_property('f', new_obj))
        self.assertEqual(1.0, soa.get_object_property('f', fixture[1]))

    def test_set_single_value_for_existing(self):
        fixture = create_fixture()
        soa = Soa(object_list=fixture, initial_property_names=['i'])
        soa.upsert_property_value(fixture[0], 'i', 2)

        self.assertEqual(2, soa.get_object_property('i', fixture[0]))

    def test_soa_as_overlay(self):
        fixture = create_fixture(OverlaidExampleType)
        OverlaidExampleType.make_soa(object_list=fixture)
        overlay = OverlaidExampleType._overlay

        overlay.upsert_property_values('i', [10, 10, 10])
        self.assertEqual(1, object.__getattribute__(fixture[0], 'i'))
        self.assertEqual(10, fixture[0].i)
        self.assertEqual(1.0, fixture[0].f)
        OverlaidExampleType.forget_soa()

    def test_object_construction_with_overlay(self):
        OverlaidExampleType.make_soa()
        create_fixture(OverlaidExampleType)
        overlay = OverlaidExampleType._overlay
        self.assertListEqual([1, 1, 1], overlay.get_property_values('i'))

    def test_soa_overlay_property_setting(self):
        fixture = create_fixture(OverlaidExampleType)
        OverlaidExampleType.make_soa(object_list=fixture, initial_property_names=['i'])
        overlay = OverlaidExampleType._overlay

        self.assertFalse(overlay.has_property('f'))
        fixture[0].f = 5.0
        self.assertTrue(overlay.has_property('f'))
        self.assertListEqual([5.0, 1.0, 1.0], list(overlay.get_property_values('f')))
        OverlaidExampleType.forget_soa()

    def test_soa_fixate(self):
        fixture = create_fixture(OverlaidExampleType)
        OverlaidExampleType.make_soa(object_list=fixture)
        overlay = OverlaidExampleType._overlay

        overlay.upsert_property_values('i', [10, 10, 10])
        self.assertEqual(1, object.__getattribute__(fixture[0], 'i'))
        overlay.fixate()
        self.assertEqual(10, object.__getattribute__(fixture[0], 'i'))
        self.assertTrue(len(overlay.props) == 0)
        self.assertIsNone(overlay.get_object_property('i', fixture[0]))
        OverlaidExampleType.forget_soa()

    def test_soa_forget(self):
        fixture = create_fixture(OverlaidExampleType)
        OverlaidExampleType.make_soa(object_list=fixture)

        fixture[0].i = 10
        self.assertEqual(10, fixture[0].i)

        OverlaidExampleType.forget_soa()
        self.assertEqual(1, fixture[0].i)

    def test_soa_copy_safety(self):
        fixture = create_fixture(OverlaidExampleType)
        OverlaidExampleType.make_soa(object_list=fixture, initial_property_names=['i'])
        fixture[0].i = 100
        soa = OverlaidExampleType._overlay

        OverlaidExampleType.make_soa(soa)
        copy_soa_1 = OverlaidExampleType._overlay
        fixture[0].i = 200
        self.assertEqual(100, soa.get_object_property('i', fixture[0]))
        self.assertEqual(200, copy_soa_1.get_object_property('i', fixture[0]))
        self.assertEqual(200, fixture[0].i)

        OverlaidExampleType.make_soa(soa)
        copy_soa_2 = OverlaidExampleType._overlay
        fixture[0].i = 300
        self.assertEqual(100, soa.get_object_property('i', fixture[0]))
        self.assertEqual(300, copy_soa_2.get_object_property('i', fixture[0]))
        self.assertEqual(300, fixture[0].i)
        OverlaidExampleType.forget_soa()
        self.assertEqual(1, fixture[0].i)
        soa.fixate()
        self.assertEqual(100, fixture[0].i)
        copy_soa_1.fixate()
        self.assertEqual(200, fixture[0].i)
        copy_soa_2.fixate()
        self.assertEqual(300, fixture[0].i)




