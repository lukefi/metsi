import datetime
import xml.etree.ElementTree as ET

from types import SimpleNamespace
from lukefi.metsi.data.formats import smk_util
from tests.data import test_util


def generate_test_data(stand_data_element='', point_element='', polygon_element='', tree_stand_element='', operations_element='') -> ET.Element:
    """ Generates test data for smk xml test suites

        The returned xml element corresponds to a single xml stand
     """
    source_data = """
        <ForestPropertyData xsi:schemaLocation="http://standardit.tapio.fi/schemas/forestData ForestData.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:gml="http://www.opengis.net/gml" xmlns:gdt="http://standardit.tapio.fi/schemas/forestData/common/geometricDataTypes" xmlns:co="http://standardit.tapio.fi/schemas/forestData/common" xmlns:sf="http://standardit.tapio.fi/schemas/forestData/specialFeature" xmlns:op="http://standardit.tapio.fi/schemas/forestData/operation" xmlns:dts="http://standardit.tapio.fi/schemas/forestData/deadTreeStrata" xmlns:tss="http://standardit.tapio.fi/schemas/forestData/treeStandSummary" xmlns:tst="http://standardit.tapio.fi/schemas/forestData/treeStratum" xmlns:ts="http://standardit.tapio.fi/schemas/forestData/treeStand" xmlns:st="http://standardit.tapio.fi/schemas/forestData/Stand" xmlns="http://standardit.tapio.fi/schemas/forestData">
            <st:Stands>
                <st:Stand id="111">
                    <st:StandBasicData>
                        {stand_data_element}
                        <gdt:PolygonGeometry>
                            {point_element}
                            {polygon_element}
                        </gdt:PolygonGeometry>
                    </st:StandBasicData>
                    <ts:TreeStandData>
                        {tree_stand_element}
                    </ts:TreeStandData>
                    <op:Operations>
                        {operations_element}
                    </op:Operations>
                </st:Stand>
            </st:Stands>
        </ForestPropertyData>
    """.format(stand_data_element=stand_data_element, point_element=point_element,
        polygon_element=polygon_element, tree_stand_element=tree_stand_element,
        operations_element=operations_element)
    root = ET.fromstring(source_data)
    return root[0][0]

class TestSmkXMLConversion(test_util.ConverterTestSuite):

    def test_parse_stand_basic_data(self):
        assertion = SimpleNamespace(
            id='111',
            CompleteState='1',
            StandBasicDataDate='2015-02-17', # year
            Area='1.73', # area & areaweight
            MainGroup='1', # land_use
            SubGroup='1', # soil
            FertilityClass='3', # site
            DrainageState='1', # drain_class
            CuttingRestriction='0', # mana_cate
        )
        test_element = """
            <st:CompleteState>1</st:CompleteState>
            <st:StandBasicDataDate>2015-02-17</st:StandBasicDataDate>
            <st:Area>1.73</st:Area>
            <st:SubGroup>1</st:SubGroup>
            <st:FertilityClass>3</st:FertilityClass>
            <st:DrainageState>1</st:DrainageState>
            <st:MainGroup>1</st:MainGroup>
            <st:CuttingRestriction>0</st:CuttingRestriction>
        """
        reference_stand = generate_test_data(stand_data_element=test_element)
        sns = smk_util.parse_stand_basic_data(reference_stand)
        self.assertEqual(assertion, sns)

    def test_parse_stand_identifier_via_stand_number_extension(self):
        test_element = """
            <st:StandNumber>123</st:StandNumber>
            <st:StandNumberExtension>124</st:StandNumberExtension>
        """
        reference_stand = generate_test_data(stand_data_element=test_element)
        sns = smk_util.parse_stand_basic_data(reference_stand)
        self.assertEqual("123.124", sns.id)

    def test_parse_stand_identifier_via_stand_number(self):
        test_element = """
            <st:StandNumber>123</st:StandNumber>
        """
        reference_stand = generate_test_data(stand_data_element=test_element)
        sns = smk_util.parse_stand_basic_data(reference_stand)
        self.assertEqual("123", sns.id)

    def test_parse_stand_identifier_with_fallback_id(self):
        test_element = ''
        reference_stand = generate_test_data(stand_data_element=test_element)
        sns = smk_util.parse_stand_basic_data(reference_stand)
        self.assertEqual("111", sns.id)

    def test_parse_stand_operation_data(self):
        ...


    def test_parse_stand_stratum_data(self):
        assertion = SimpleNamespace(
            id='233',
            StratumNumber='1',
            TreeSpecies='1',
            Storey='5',
            Age='60',
            BasalArea='12.1',
            StemCount='120',
            MeanDiameter='22.0',
            MeanHeight='20.5',
            Volume='93.2',
            DataSource='2'
        )

        test_element = """
            <ts:TreeStandDataDate type="1" date="2012-02-13">
                <tst:TreeStrata>
                    <tst:TreeStratum id="233">
                    <tst:StratumNumber>1</tst:StratumNumber>
                    <tst:TreeSpecies>1</tst:TreeSpecies>
                    <tst:Storey>5</tst:Storey>
                    <tst:Age>60</tst:Age>
                    <tst:BasalArea>12.1</tst:BasalArea>
                    <tst:StemCount>120</tst:StemCount>
                    <tst:MeanDiameter>22.0</tst:MeanDiameter>
                    <tst:MeanHeight>20.5</tst:MeanHeight>
                    <tst:Volume>93.2</tst:Volume>
                    <co:DataSource>2</co:DataSource>
                    </tst:TreeStratum>
                </tst:TreeStrata>
            </ts:TreeStandDataDate>
        """
        reference_stand = generate_test_data(tree_stand_element=test_element)
        estratum = reference_stand.find('ts:TreeStandData/ts:TreeStandDataDate/tst:TreeStrata/tst:TreeStratum', smk_util.NS)
        sns = smk_util.parse_stratum_data(estratum)
        self.assertEqual(assertion, sns)


    def test_parse_year(self):
        assertions = [
            (['2010-01-01'], 2010),
            (['kissa123'], None),
            ([''], None),
            (['a'], None),
            (['ab'], None),
            (['abc'], None),
            (['abcd'], None),
        ]
        self.run_with_test_assertions(assertions, smk_util.parse_year)


    def test_parse_land_use_category(self):
        assertions = [
            (['1'], 1),
            (['2'], 2),
            (['3'], 3),
            (['999'], None),
            (['kissa123'], None)
        ]
        self.run_with_test_assertions(assertions, smk_util.parse_land_use_category)


    def test_parse_drainage_category(self):
        assertions = [
            (['1'], 0),
            (['2'], 0),
            (['3'], 1),
            (['6'], 2),
            (['7'], 3),
            (['8'], 4),
            (['9'], 5),
            (['999'], 999),
            (['kissa123'], None)
        ]
        self.run_with_test_assertions(assertions, smk_util.parse_drainage_category)


    def test_parse_forest_management_category(self):
        assertions = [
            (['1'], 2.1),
            (['2'], 2.2),
            (['3'], 2.2),
            (['4'], 2.3),
            (['6'], 2.4),
            (['7'], 2.4),
            (['5'], 2.5),
            (['8'], 2.6),
            (['9'], 7),
            (['999'], 1),
            (['kissa123'], 1),
            ([None], None)
        ]
        self.run_with_test_assertions(assertions, smk_util.parse_forest_management_category)


    def test_point_series(self):
        assertions = [
            ('123456.123,7654321.123', 1),
            ('123456.123,7654321.123 111111.1111,22222222.2222', 2)
        ]
        for i in assertions:
            result = smk_util.point_series(i[0])
            self.assertEqual(123456.123, result[0][0])
            self.assertEqual(2, len(result[0]))
            self.assertEqual(i[1], len(result))


    def test_parse_centroid(self):
        point_element = """
            <gml:pointProperty>
                <gml:Point srsName="EPSG:3067">
                    <gml:coordinates>506093.8555,6775744.2412</gml:coordinates>
                </gml:Point>
            </gml:pointProperty>
        """
        polygon_element = """
            <gml:polygonProperty>
                <gml:Polygon srsName="EPSG:3067">
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:coordinates>506076.0073,6775799.3646 506058.1140,6775800.1567 506026.8213,6775805.5843 506026.5725,6775789.2247 506026.9702,6775778.6663 506016.8331,6775762.4472 505992.5045,6775723.9258 505980.3399,6775726.9669 505973.2438,6775716.8298 505969.6961,6775702.6382 505963.6461,6775689.2848 505966.6449,6775685.2865 505971.6427,6775690.2848 505988.6360,6775702.2798 506002.6298,6775706.2787 506019.6230,6775703.2798 506035.6169,6775694.2831 506049.6112,6775686.2865 506059.6073,6775680.2893 506067.6039,6775675.2910 506076.6006,6775676.2910 506082.5978,6775679.2899 506088.5955,6775685.2871 506095.5927,6775691.2848 506104.5888,6775690.2854 506108.3657,6775691.5135 506112.7174,6775697.4972 506120.3331,6775703.4815 506127.4051,6775705.1135 506131.2129,6775702.9371 506151.5697,6775713.2764 506160.5663,6775717.2747 506175.5601,6775716.2753 506184.5562,6775716.2753 506196.5517,6775718.2747 506202.5489,6775733.2685 506204.5478,6775745.2635 506206.5472,6775760.2573 506192.4101,6775775.3730 506190.2343,6775787.8848 506186.4264,6775794.9567 506173.3708,6775795.5006 506159.7713,6775796.0444 506149.6888,6775798.8011 506130.1242,6775798.9011 506109.9966,6775793.4612 506101.2933,6775791.2854 506090.5938,6775796.2427 506089.4736,6775798.8051 506076.0073,6775799.3646</gml:coordinates>
                        </gml:LinearRing>
                    </gml:exterior>
                </gml:Polygon>
            </gml:polygonProperty>
        """
        reference_stand = generate_test_data(point_element=point_element, polygon_element=polygon_element)

        test_config = [
            ('point',
             './gml:coordinates',
             './st:StandBasicData/gdt:PolygonGeometry/gml:pointProperty/gml:Point',
             (506093.8555, 6775744.2412, 'EPSG:3067')
            ),
            ('polygon',
             './gml:exterior/gml:LinearRing/gml:coordinates',
             './st:StandBasicData/gdt:PolygonGeometry/gml:polygonProperty/gml:Polygon',
             (506093.8625353831, 6775744.33567775, 'EPSG:3067')
            )
        ]
        assertions = []
        for config in test_config:
            sns = SimpleNamespace(geometry_type=None, egeometry=None, coord_xpath=None)
            sns.geometry_type = config[0]
            sns.coord_xpath = config[1]
            sns.egeometry = reference_stand.find(config[2], smk_util.NS)
            assertions.append( ([sns], config[3]) )
        self.run_with_test_assertions(assertions, smk_util.parse_centroid)


    def test_parse_coordinates_from_point(self):
        point_element = """
            <gml:pointProperty>
                <gml:Point srsName="EPSG:3067">
                    <gml:coordinates>506093.8555,6775744.2412</gml:coordinates>
                </gml:Point>
            </gml:pointProperty>
        """
        reference_stand = generate_test_data(point_element=point_element)
        result = smk_util.parse_coordinates(reference_stand)
        self.assertEqual((6775744.2412, 506093.8555, 'EPSG:3067'), result)


    def test_parse_coordinates_from_polygon(self):
        polygon_element = """
            <gml:polygonProperty>
                <gml:Polygon srsName="EPSG:3067">
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:coordinates>506076.0073,6775799.3646 506058.1140,6775800.1567 506026.8213,6775805.5843 506026.5725,6775789.2247 506026.9702,6775778.6663 506016.8331,6775762.4472 505992.5045,6775723.9258 505980.3399,6775726.9669 505973.2438,6775716.8298 505969.6961,6775702.6382 505963.6461,6775689.2848 505966.6449,6775685.2865 505971.6427,6775690.2848 505988.6360,6775702.2798 506002.6298,6775706.2787 506019.6230,6775703.2798 506035.6169,6775694.2831 506049.6112,6775686.2865 506059.6073,6775680.2893 506067.6039,6775675.2910 506076.6006,6775676.2910 506082.5978,6775679.2899 506088.5955,6775685.2871 506095.5927,6775691.2848 506104.5888,6775690.2854 506108.3657,6775691.5135 506112.7174,6775697.4972 506120.3331,6775703.4815 506127.4051,6775705.1135 506131.2129,6775702.9371 506151.5697,6775713.2764 506160.5663,6775717.2747 506175.5601,6775716.2753 506184.5562,6775716.2753 506196.5517,6775718.2747 506202.5489,6775733.2685 506204.5478,6775745.2635 506206.5472,6775760.2573 506192.4101,6775775.3730 506190.2343,6775787.8848 506186.4264,6775794.9567 506173.3708,6775795.5006 506159.7713,6775796.0444 506149.6888,6775798.8011 506130.1242,6775798.9011 506109.9966,6775793.4612 506101.2933,6775791.2854 506090.5938,6775796.2427 506089.4736,6775798.8051 506076.0073,6775799.3646</gml:coordinates>
                        </gml:LinearRing>
                    </gml:exterior>
                </gml:Polygon>
            </gml:polygonProperty>
        """
        reference_stand = generate_test_data(polygon_element=polygon_element)
        result = smk_util.parse_coordinates(reference_stand)
        self.assertEqual((6775744.33567775, 506093.8625353831, 'EPSG:3067'), result)


    def test_parse_coordinates_none(self):
        reference_stand = generate_test_data()
        result = smk_util.parse_coordinates(reference_stand)
        self.assertEqual((None, None, None), result)


    def test_parse_date(self):
        self.assertEqual(datetime.date(2000, 1, 1), smk_util.parse_date('2000-01-01'))
        self.assertRaises(TypeError, smk_util.parse_date, '2000')
        self.assertRaises(TypeError, smk_util.parse_date, '2000-01')
        self.assertRaises(ValueError, smk_util.parse_date, 'asd-01-01')
        self.assertRaises(ValueError, smk_util.parse_date, 'kissa123')


    def test_parse_past_operations(self):
        operations_element = """
            <op:Operation id="10314067" mainType="1">
                <op:OperationType>3</op:OperationType>
                    <op:CompletionData>
                        <op:CompletionDate>2017-02-07</op:CompletionDate>
                    </op:CompletionData>
                <co:DataSource>2</co:DataSource>
                <op:Cutting/>
            </op:Operation>
            <op:Operation id="57490034" mainType="1">
                <op:OperationType>4</op:OperationType>
                    <op:CompletionData>
                        <op:CompletionDate>1992-02-01</op:CompletionDate>
                    </op:CompletionData>
                <co:DataSource>2</co:DataSource>
                <op:Cutting/>
            </op:Operation>
        """
        reference_stand = generate_test_data(operations_element=operations_element)
        eoperations = reference_stand.findall('./op:Operations/op:Operation', smk_util.NS)
        fixture = {
            10314067: (3, 2017),
            57490034: (4, 1992)
        }
        result = smk_util.parse_past_operations(eoperations)
        self.assertEqual(fixture, result)


    def test_parse_future_operations(self):
        operations_element = """
            <op:Operation id="443" mainType="2">
                <op:OperationType>410</op:OperationType>
                <op:ProposalData>
                        <op:ProposalType>0</op:ProposalType>
                        <op:ProposalYear>2015</op:ProposalYear>
                </op:ProposalData>
                <op:Silviculture/>
            </op:Operation>
            <op:Operation id="444" mainType="2">
                <op:OperationType>520</op:OperationType>
                <op:ProposalData>
                    <op:ProposalType>0</op:ProposalType>
                    <op:ProposalYear>2020</op:ProposalYear>
                </op:ProposalData>
                <op:Silviculture/>
            </op:Operation>
        """
        reference_stand = generate_test_data(operations_element=operations_element)
        eoperations = reference_stand.findall('./op:Operations/op:Operation', smk_util.NS)
        fixture = {
            443: (410, 2015),
            444: (520, 2020)
        }
        result = smk_util.parse_future_operations(eoperations)
        self.assertEqual(fixture, result)


    def test_parse_stand_operations(self):
        operations_element = """
            <op:Operation id="544" mainType="1">
                <op:OperationType>3</op:OperationType>
                <op:CompletionData>
                    <op:CompletionDate>2020-03-01</op:CompletionDate>
                </op:CompletionData>
                <co:DataSource>2</co:DataSource>
                <op:Cutting/>
            </op:Operation>
            <op:Operation id="555" mainType="2">
                <op:OperationType>410</op:OperationType>
                <op:ProposalData>
                        <op:ProposalType>0</op:ProposalType>
                        <op:ProposalYear>2022</op:ProposalYear>
                </op:ProposalData>
                <op:Silviculture/>
            </op:Operation>
        """
        reference_stand = generate_test_data(operations_element=operations_element)
        result = smk_util.parse_stand_operations(reference_stand)
        self.assertEqual(2, len(result))
        oper1 = result.get(544)
        self.assertEqual(oper1[0], 3)
        self.assertEqual(oper1[1], 2020)
        oper2 = result.get(555)
        self.assertEqual(oper2[0], 410)
        self.assertEqual(oper2[1], 2022)


    def test_parse_stand_operations_only_past(self):
        operations_element = """
            <op:Operation id="1234" mainType="1">
                <op:OperationType>3</op:OperationType>
                <op:CompletionData>
                    <op:CompletionDate>2026-04-01</op:CompletionDate>
                </op:CompletionData>
                <co:DataSource>2</co:DataSource>
                <op:Cutting/>
            </op:Operation>
            <op:Operation id="1235" mainType="2">
                <op:OperationType>410</op:OperationType>
                <op:ProposalData>
                        <op:ProposalType>0</op:ProposalType>
                        <op:ProposalYear>2050</op:ProposalYear>
                </op:ProposalData>
                <op:Silviculture/>
            </op:Operation>
        """
        reference_stand = generate_test_data(operations_element=operations_element)
        result = smk_util.parse_stand_operations(reference_stand, target_operations='past')
        self.assertEqual(1, len(result))
        oper = result.get(1234)
        self.assertEqual(oper[0], 3)
        self.assertEqual(oper[1], 2026)


    def test_parse_stand_operations_only_future(self):
        operations_element = """
            <op:Operation id="128" mainType="1">
                <op:OperationType>3</op:OperationType>
                <op:CompletionData>
                    <op:CompletionDate>2021-04-01</op:CompletionDate>
                </op:CompletionData>
                <co:DataSource>2</co:DataSource>
                <op:Cutting/>
            </op:Operation>
            <op:Operation id="123" mainType="2">
                <op:OperationType>410</op:OperationType>
                <op:ProposalData>
                        <op:ProposalType>0</op:ProposalType>
                        <op:ProposalYear>2041</op:ProposalYear>
                </op:ProposalData>
                <op:Silviculture/>
            </op:Operation>
        """
        reference_stand = generate_test_data(operations_element=operations_element)
        result = smk_util.parse_stand_operations(reference_stand, target_operations='future')
        self.assertEqual(1, len(result))
        oper = result.get(123)
        self.assertEqual(oper[0], 410)
        self.assertEqual(oper[1], 2041)
