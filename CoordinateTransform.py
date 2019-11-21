# -*- encoding: utf-8 -*-
import numpy
from osgeo import osr


def geo2imgxy(geotrans, px, py):
    '''
    根据GDAL的六 参数模型将给定的投影或地理坐标转为影像图上坐标（行列号）
    :param dataset: GDAL地理数据
    :param px: 投影或地理坐标x
    :param py: 投影或地理坐标y
    :return: 影坐标或地理坐标(px, py)对应的影像图上行列号(row, col)
    '''
    a = numpy.array([[geotrans[1], geotrans[2]], [geotrans[4], geotrans[5]]])
    b = numpy.array([px - geotrans[0], py - geotrans[3]])
    row,col=numpy.linalg.solve(a, b)  # 使用numpy的linalg.solve进行二元一次方程的求解
    return(int(row),int(col))


def imgxy2geo(geotrans, row, col):
    '''
    根据GDAL的六参数模型将影像图上坐标（行列号）转为投影坐标或地理坐标（根据具体数据的坐标系统转换）
    :param dataset: GDAL地理数据
    :param row: 像素的行号
    :param col: 像素的列号
    :return: 行列号(row, col)对应的投影坐标或地理坐标(px, py)

    Fetches the coefficients for transforming between pixel / line (P, L) raster space, and projection coordinates (Xp, Yp) space.
    Xp = padfTransform[0] + P * padfTransform[1] + L * padfTransform[2];
    Yp = padfTransform[3] + P * padfTransform[4] + L * padfTransform[5];
    //如果图像不含地理坐标信息，默认返回值是：(0,1,0,0,0,1)
    //In a north up image,
    //左上角点坐标(padfGeoTransform[0],padfGeoTransform[3])；
    //padfGeoTransform[1]是像元宽度(影像在宽度上的分辨率)；
    //adfGeoTransform[5]是像元高度(影像在高度上的分辨率)；
    //如果影像是指北的,padfGeoTransform[2]和padfGeoTransform[4]这两个参数的值为0。
    '''
    px = geotrans[0] + col * geotrans[1] + row * geotrans[2]
    py = geotrans[3] + col * geotrans[4] + row * geotrans[5]
    return px, py


def getSRSPair(dataset):
    '''
    获得给定数据的投影参考系和地理参考系
    :param dataset: GDAL地理数据
    :return: 投影参考系和地理参考系
    '''
    prosrs = osr.SpatialReference()
    prosrs.ImportFromWkt(dataset.GetProjection())
    geosrs = prosrs.CloneGeogCS()
    return prosrs, geosrs

def geo2lonlat(dataset, x, y):
    '''
    将投影坐标转为经纬度坐标（具体的投影坐标系由给定数据确定）
    :param dataset: GDAL地理数据
    :param x: 投影坐标x
    :param y: 投影坐标y
    :return: 投影坐标(x, y)对应的经纬度坐标(lon, lat)
    '''
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(prosrs, geosrs)
    coords = ct.TransformPoint(x, y)
    return coords[:2]

def lonlat2geo(dataset, lon, lat):
    '''
    将经纬度坐标转为投影坐标（具体的投影坐标系由给定数据确定）
    :param dataset: GDAL地理数据
    :param lon: 地理坐标lon经度
    :param lat: 地理坐标lat纬度
    :return: 经纬度坐标(lon, lat)对应的投影坐标
    '''
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(geosrs, prosrs)
    coords = ct.TransformPoint(lon, lat)
    return coords[:2]
