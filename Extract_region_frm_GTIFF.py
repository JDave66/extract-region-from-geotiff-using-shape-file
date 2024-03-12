# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 19:07:24 2024

@author: Husky
"""

import rasterio
from rasterio.mask import mask
from rasterio.warp import transform_geom
from rasterio.crs import CRS
import fiona
import glob
import os 


location = 'Penn State'
sp = 'PSU'
typ = 'LST' #LST
level = 'L2'
shape_path = f"E:/Sentinel3Work/New_Data/SURFRAD/{sp}.shp"
# Read all features from the shapefile
with fiona.open(shape_path, 'r') as shapefile:
    shapes = [feature['geometry'] for feature in shapefile]

folder_path = glob.glob(f'E:/Sentinel3Work/New_Data/{location}/{typ}/*')

for Jpath in folder_path:
    
    geotiff_file1 = glob.glob(f'{Jpath}/*{level}.tif')
    geotiff_file = geotiff_file1[0]
    # Open the raster file
    with rasterio.open(geotiff_file) as src:
        # Read the CRS of the raster
        raster_crs = src.crs
        
        # Reproject the input shapes to match the CRS of the raster
        reprojected_shapes = [transform_geom(
            CRS.from_epsg(4326),  # Assuming input shapes have EPSG:4326 CRS, change it accordingly
            raster_crs,
            shape
        ) for shape in shapes]
        
        # Mask the raster with the reprojected shapes
        out_image, out_transform = mask(src, reprojected_shapes, crop=True)
        out_meta = src.meta
    
        # Update metadata for the output GeoTIFF
        out_meta.update({
            "driver": 'GTiff',
            'height': out_image.shape[1],
            'width': out_image.shape[2],
            'transform': out_transform
        })
        
        bla = f'{Jpath}/{sp}'
        os.makedirs(bla, exist_ok=True)
        # Write the masked image to a new GeoTIFF file
        bla1= geotiff_file
        bla2= bla1[-15:]
        with rasterio.open(f'{Jpath}/{sp}/{bla2}', 'w', **out_meta) as dst:
            dst.write(out_image)
