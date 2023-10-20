import sqlite3
import pandas as pd
import numpy as np
from geopandas import GeoDataFrame
from shapely import Polygon
from lukefi.metsi.data.formats import gpkg_util
from tests.data import test_util


class TestGeoPackageConversion(test_util.ConverterTestSuite):

    GPKG_DB_PATH="tests/data/resources/SMK_source.gpkg"

    def test_read_geopackage(self):
        args = dict(path=self.GPKG_DB_PATH, type_value=1)
        (stands,
         strata) = gpkg_util.read_geopackage(**args)
        # test stands
        self.assertEqual(len(stands), 9)
        self.assertEqual(int(stands.iloc[0].standid), 41652739)
        self.assertEqual(int(stands.iloc[1].standid), 41652748)
        self.assertEqual(int(stands.iloc[2].standid), 41784529)
        self.assertEqual(int(stands.iloc[2].maingroup), 1)
        self.assertEqual(float(stands.iloc[2].area), 0.213)
        self.assertEqual(float(stands.iloc[2].restrictiontype), 1.0)
        self.assertEqual(float(stands.iloc[2].restrictioncode), 9.0)
        # test strata
        self.assertEqual(len(strata), 24)
        self.assertEqual(int(strata.iloc[0].standid), 41652739)
        self.assertEqual(int(strata.iloc[1].standid), 41652739)
        self.assertEqual(int(strata.iloc[2].standid), 41652739)
        self.assertEqual(int(strata.iloc[3].standid), 41652748)
        self.assertEqual(int(strata.iloc[3].treespecies), 2)
        self.assertEqual(float(strata.iloc[3].basalarea), 19.59)

    def test_attach_location(self):
        gpkg_util._attach_location()

    def test_read_stand_geometry(self):
        gdf = gpkg_util._read_stand_geometry(self.GPKG_DB_PATH)
        self.assertEqual(len(gdf), 9)
        self.assertEqual(int(gdf.iloc[0].standid), 41652739)
        self.assertEqual(int(gdf.iloc[1].standid), 41652748)
        self.assertEqual(int(gdf.iloc[2].standid), 42205670)
        self.assertEqual(type(gdf.iloc[2].geometry), Polygon)
        self.assertEqual(gdf.iloc[2].geometry.centroid.x, 324268.10274978995)
        self.assertEqual(gdf.iloc[2].geometry.centroid.y, 7059047.568198285)
        self.assertEqual(gdf.iloc[2].geometry.area, 9606.429926999523)

    def test_read_from_gpkg(self):
        query = """ SELECT * FROM stand WHERE id=685 """
        conn = sqlite3.connect(self.GPKG_DB_PATH)
        args = dict(query=query, conn=conn)
        df = gpkg_util._read_from_gpkg(**args)
        self.assertEqual(int(df.standid), 41784529)

    def test_extract_nan(self):
        df = pd.DataFrame(dict(a=[pd.NA, np.nan], b=[1, 2]))
        result = gpkg_util._replace_nan(df)
        self.assertEqual(result.a[0], None)
        self.assertEqual(result.a[1], None)

    def test_extract_centroid(self):
        p = Polygon([(1,10), (3, 30), (1, 20)])
        gdf = GeoDataFrame(dict(geometry=[p])).set_crs('EPSG:3067')
        result = gpkg_util._extract_centroid(gdf['geometry'])
        self.assertEqual(result.get('centroid'), (1.67, 20.0))
        self.assertEqual(result.get('crs'), 'EPSG:3067')

    def test_attach_location(self):
        p = Polygon([(1,10), (3, 30), (1, 20)])
        gdf = GeoDataFrame(
            dict(
                geometry=[p],
                standid=[123]
            )
        ).set_crs('EPSG:3067')
        df = pd.DataFrame(
            dict(standid=[123])
        )
        result = gpkg_util._attach_location(df, gdf)
        self.assertEqual(type(result), pd.DataFrame)
        self.assertEqual(result.iloc[0].centroid.get('centroid'), (1.67, 20.0))
        self.assertEqual(result.iloc[0].centroid.get('crs'), 'EPSG:3067')