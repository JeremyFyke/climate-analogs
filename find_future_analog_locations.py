from geopy import geocoders
import netCDF4 as nc
import numpy as np
from pyproj import Proj
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

plt.switch_backend('agg')

#Get data from multiple climate models
models=["CCSM4","CNRM-CM5","CanESM2","GFDL-CM3","HadGEM2-ES"]

#Set data path and variables to get from file.
sd="NetCDF_data/"
v2="Tave_sm"
v1="PPT_sm"

#Load some spatial stuff
vn=nc.Dataset(sd+"NA_Reference_files_netCDF/ClimateNA_DEM.nc")
easting=vn.variables["easting"][:]
northing=vn.variables["northing"][:]
elev=(vn.variables["Elevation"][:,:])
nx,ny=np.meshgrid(easting,northing)

Projection="+proj=lcc +lat_1=49.0 +lat_2=77.0 +lat_0=0.0 +lon_0=-95.0 +x_0=0.0 +y_0=0.0 +ellps=WGS84 + datum=WGS84 +units=m +no_defs"
p=Proj(Projection)

#Set the location and lat long by hard code (wouldn't it be cool to get lat/lon automagically?
location="Victoria"
lon=-123.3656
lat=48.4284
#Calculate raster indices based on lat/lon (I THINK this is being done correctly)
x,y=p(lon,lat)
xi=abs(easting-x).argmin()
yi=abs(northing-y).argmin()

#loop over models, make masks, and plot with transparency
vn=nc.Dataset(sd+"NA_NORM_8110_Bioclim_netCDF/"+v1+".nc")
v1_hist=vn.variables[v1][:,:]
vn.close()

vn=nc.Dataset(sd+"NA_NORM_8110_Bioclim_netCDF/"+v2+".nc")
v2_hist=vn.variables[v2][:,:]
vn.close()

#is_analog=1 where 
is_analog=np.zeros(np.shape(elev))
#loop over climate models
for n,m in enumerate(models):
  print(i)
  #load climate model data for each of two variables, for each of 2 climate scenarios
  vn=nc.Dataset(sd+m+"_rcp45_2085_Bioclim_netCDF/"+m+"_rcp45_2085_"+v1+".nc")
  v1_fut_rcp45=vn.variables[v1][:,:]
  vn.close()
  vn=nc.Dataset(sd+m+"_rcp85_2085_Bioclim_netCDF/"+m+"_rcp85_2085_"+v1+".nc")
  v1_fut_rcp85=vn.variables[v1][:,:]
  vn.close()

  vn=nc.Dataset(sd+m+"_rcp45_2085_Bioclim_netCDF/"+m+"_rcp45_2085_"+v2+".nc")
  v2_fut_rcp45=vn.variables[v2][:,:]
  vn.close()
  vn=nc.Dataset(sd+m+"_rcp85_2085_Bioclim_netCDF/"+m+"_rcp85_2085_"+v2+".nc")
  v2_fut_rcp85=vn.variables[v2][:,:]
  vn.close()

  #sort threshold values to increase (not decrease)
  thres1=np.sort([v1_fut_rcp45[yi,xi],v1_fut_rcp85[yi,xi]])
  thres2=np.sort([v2_fut_rcp45[yi,xi],v2_fut_rcp85[yi,xi]])

  #threshold two variable ranges
  v1mask = (v1_hist>thres1[0]) & (v1_hist<thres1[1])
  v2mask = (v2_hist>thres2[0]) & (v2_hist<thres2[1])

  #v3mask = (v1_fut_rcp45<v1_hist[yi,xi]) & (v1_fut_rcp85>v1_hist[yi,xi])
  #v4mask =(v2_fut_rcp45<v2_hist[yi,xi]) & (v2_fut_rcp85>v2_hist[yi,xi])
  
  #set mask to transparent, and plot each threshold individually.  The transparencies overlap to show multi-matching locations.  Do some NaN stuff to mask ou oceans
  mask=np.zeros(np.shape(elev))
  mask[:,:]=np.nan
  mask[v1mask]=1
  plt.imshow(mask,alpha=0.3,cmap='RdBu',vmin=0,vmax=1)
  mask=np.zeros(np.shape(elev))
  mask[:,:]=np.nan
  mask[v2mask]=0
  plt.imshow(mask,alpha=0.3,cmap='RdBu',vmin=0,vmax=1)

  del mask
  del v1_fut_rcp45
  del v1_fut_rcp85
  del v2_fut_rcp45
  del v2_fut_rcp85

  is_analog[v1mask]=1
  is_analog[v2mask]=1

#color land  that don't fall within either mask to grey.
mask=np.zeros(np.shape(elev))
mask[:,:]=np.nan
mask[np.where(is_analog==0)]=0.5
mask[elev<0.0]=np.nan
plt.imshow(mask,cmap='binary',vmin=0,vmax=1)

#output results to a PNG file, locally (actually a link to a GCP storage bucket
plt.scatter(xi,yi,s=20,c='red',marker='p')
plt.savefig("climate-na-storage-bucket/"+location+"_climate_analog.png",dpi=300)



