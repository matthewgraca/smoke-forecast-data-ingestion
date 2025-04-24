from herbie import Herbie, wgrib2
import xarray as xr

class HRRRProcessor:
    def __init__(
        self,
        date="2025-01-16", 
        variable_name='MASSDEN',
        lon_min=-124.40,
        lon_max=-114.13,
        lat_min=32.53,
        lat_max=42.00,
        extent_name='california_region'
    ):
        # processing pipeline
        extent = (lon_min, lon_max, lat_min, lat_max)
        data_xr = self.__get_data(date, variable_name, extent, extent_name)
        data_dict = self.__process(data_xr)

        # attributes
        self.data = data_xr
        self.firebase_data = data_dict

    def __subregion_file(self, H, extent, extent_name, variable):
        """ Uses wgrib2 to subregion the grib file """
        file = H.get_localFilePath(variable)
        idx_file = wgrib2.create_inventory_file(file)
        subset_file = wgrib2.region(file, extent, name=extent_name)
        
        return subset_file

    def __process(self, data_xr):
        """ Trims the xarray of its metadata and converts it to a dictionary """
        # trim xarray
        vars_to_drop = ['step', 'heightAboveGround', 'valid_time']
        data_xr_subset = data_xr.drop_attrs().drop_vars(vars_to_drop)

        return data_xr.to_dict()

    def __get_data(self, date, variable_name, extent, extent_name):
        """ Downloads HRRR data, subregions it, returning an xarray """
        # herbie
        H = Herbie(
            date,
            model='hrrr',
            product='sfc',
            fxx=0
        )
        # subregion
        data_grib = self.__subregion_file(
            H=H, extent=extent, extent_name=extent_name, variable=variable_name
        )
        # grib -> xarray
        data_xr = xr.open_dataset(
            data_grib, engine='cfgrib', decode_timedelta=False, decode_times=False
        )

        return data_xr
