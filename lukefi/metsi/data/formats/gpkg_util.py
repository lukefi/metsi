from typing import Any, TypedDict
import sqlite3
import pandas as pd
import geopandas
from shapely.geometry.polygon import Polygon
import numpy as np


def _read_stand_geometry(path: str) -> geopandas.GeoDataFrame:
    '''
    NOTE: Stand geometry is read with geopandas. This could be done purely with SQLite using spatialite library
    but as installation of spatialite would assume manual it was desided to be done with geopandas. Problems with
    using geopandas to read geometry information is that it is 100-times slower than pure SQL request.
    In other words the reading the geometry from source could be optimized,
    but now (24.8.2023) a very little need for this was seen.
    '''
    return geopandas.read_file(path, layer="stand")


def _read_from_gpkg(query, conn) -> pd.DataFrame:
    """ Extecutes sql query for connection to SQLite db """
    return pd.read_sql_query(query, conn)


def _replace_nan(df: pd.DataFrame, value: Any = None) -> pd.DataFrame:
    """ Replaces NaN values in pandas dataframe """
    return df.replace(np.nan, value)


class Centroid(TypedDict):
    centroid: tuple[float, float]
    crs: str


def _extract_centroid(geometry: Polygon) -> Centroid:
    """ Extracts centroid information from polygon coordinates """
    cid = geometry.centroid
    latitude = round(float(cid.y), 2)
    longitude = round(float(cid.x), 2)
    return {"centroid": (longitude, latitude), "crs": cid.crs.srs.upper()}


def _attach_location(df: pd.DataFrame, gdf: geopandas.GeoDataFrame) -> pd.DataFrame:
    """ Inserts into df the centroid information from gdf """
    centroids = []
    for sid in df['standid']:
        stand_geometry = gdf[gdf['standid'] == sid]
        cid = _extract_centroid(stand_geometry['geometry'])
        centroids.append(cid)
    df.insert(0, 'centroid', centroids)
    return df


def read_geopackage(path: str, type_value: int = 1) -> tuple[pd.DataFrame, pd.DataFrame]:
    """ Reads stands and strata from Forest Centre (FC) gpkg format.
    path: string path to SQLite .gpkg format
    type_value: FC strata origin type value 1(=invented), 2(=calculated) or 3(=forecasted).
    :returns: Stand and stratum tuple of pandas Dataframe.
    """
    RESTRICTION_TYPE_CUTTINGS = 1
    stands_query = f'''
        SELECT DISTINCT s.standid,
            s.maingroup,
            s.subgroup,
            s.fertilityclass,
            s.soiltype,
            s.drainagestate,
            s.developmentclass,
            s.area,
            s.areadecrease,
            sd.date,
            r.restrictiontype,
            r.restrictioncode
        FROM stand as s
        JOIN treestand AS sd ON s.standid=sd.standid AND sd.type={type_value}
        LEFT JOIN restriction AS r ON s.standid=r.standid AND r.restrictiontype={RESTRICTION_TYPE_CUTTINGS}
    '''
    strata_query = f'''
        SELECT s.standid,
            ts.treestratumid,
            ts.stratumnumber,
            ts.treespecies,
            ts.storey,
            ts.age,
            ts.basalarea,
            ts.stemcount,
            ts.meandiameter,
            ts.meanheight
        FROM treestratum as ts
        JOIN treestand AS sd ON ts.treestandid=sd.treestandid AND sd.type={type_value}
        JOIN stand AS s ON sd.standid=s.standid
    '''
    conn = sqlite3.connect(path)
    stands = _read_from_gpkg(stands_query, conn)
    strata = _read_from_gpkg(strata_query, conn)
    conn.close()
    stand_geometries = _read_stand_geometry(path)
    stands = _attach_location(stands, stand_geometries)
    stands = _replace_nan(stands)
    strata = _replace_nan(strata)
    return (stands, strata)
