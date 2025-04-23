from herbie import Herbie, wgrib2
import xarray as xr

def subregion_file(H, extent, extent_name, product):
    """ Uses wgrib2 to subregion the grib file """
    file = H.get_localFilePath(product)
    idx_file = wgrib2.create_inventory_file(file)
    subset_file = wgrib2.region(file, extent, name=extent_name)
    
    return subset_file

# pull today's forecast using Herbie
test_date = "2025-01-16"
H = Herbie(
    test_date,
    model='hrrr',
    product='sfc',
    fxx=0
)

# define california subregion 
lon_min, lon_max = -124.40, -114.13
lat_min, lat_max= 32.53, 42.00
extent = (lon_min, lon_max, lat_min, lat_max)

# subregion herbie using wgrib2
data_grib = subregion_file(
    H=H, extent=extent, extent_name="california_region", product='MASSDEN'
)
print(f"Path of subset file: {data_grib}")

# convert grib -> xarray
data_xr = xr.open_dataset(
    data_grib, engine='cfgrib', decode_timedelta=False, decode_times=False
)
print(data_xr.info)

# xarray -> dataframe (cleans out metadata)
data_df = data_xr.to_dataframe()
print(data_df)

data_df_essential = data_df.drop(['time', 'step', 'heightAboveGround', 'valid_time'], axis=1)
print(data_df_essential)
