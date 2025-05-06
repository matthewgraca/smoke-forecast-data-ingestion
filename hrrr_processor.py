from herbie import Herbie, wgrib2
import xarray as xr
import sys
from typing import Tuple, Dict, Any


class HRRRProcessor:
    """
    A processor for retrieving and formatting High-Resolution Rapid Refresh
    (HRRR) model data using the Herbie library.

    This class automates the process of downloading HRRR forecast data,
    extracting a subregion using `wgrib2`, and converting the data into a
    dictionary format suitable for Firebase storage.

    Attributes:
        data_xr (xarray.Dataset): The processed dataset in xarray format.
        data_dict (dict): A dictionary representation of the dataset including
            mass density, coordinates, time, and metadata.
    """

    def __init__(
        self,
        date: str = "2025-01-16",
        variable_name: str = "MASSDEN",
        lon_min: float = -124.40,
        lon_max: float = -114.13,
        lat_min: float = 32.53,
        lat_max: float = 42.00,
        extent_name: str = "california_region"
    ) -> None:
        """
        Initializes the HRRRProcessor object, retrieving and processing HRRR
        data for a specified geographic region and variable.

        Args:
            date (str): Date of the HRRR forecast in 'YYYY-MM-DD' format.
            variable_name (str): Name of the variable to retrieve.
            lon_min (float): Minimum longitude of the region of interest.
            lon_max (float): Maximum longitude of the region of interest.
            lat_min (float): Minimum latitude of the region of interest.
            lat_max (float): Maximum latitude of the region of interest.
            extent_name (str): A label for the geographical extent.
        """
        extent = (lon_min, lon_max, lat_min, lat_max)
        data_xr = self.__get_data(date, variable_name, extent, extent_name)
        data_dict = self.__process(data_xr)

        self.data_xr: xr.Dataset = data_xr
        self.data_dict: Dict[str, Any] = data_dict

    def __subregion_file(
        self,
        H: Herbie,
        extent: Tuple[float, float, float, float],
        extent_name: str,
        variable: str
    ) -> str:
        """
        Uses wgrib2 to subregion the GRIB file for a specified variable
        and region.

        Args:
            H (Herbie): Herbie object configured for the data download.
            extent (tuple): Tuple of (lon_min, lon_max, lat_min, lat_max).
            extent_name (str): Name of the subregion.
            variable (str): Variable name to subset.

        Returns:
            str: Path to the subset GRIB file.
        """
        file = H.get_localFilePath(variable)
        idx_file = wgrib2.create_inventory_file(file)
        subset_file = wgrib2.region(file, extent, name=extent_name)
        return subset_file

    def __process(self, data_xr: xr.Dataset) -> Dict[str, Any]:
        """
        Processes the xarray dataset into a dictionary format suitable
        for Firebase.

        Args:
            data_xr (xarray.Dataset): The xarray dataset to process.

        Returns:
            dict: Dictionary with keys 'mdens', 'longitude', 'latitude',
                  'time', and 'metadata'.

        Raises:
            SystemExit: If the expected variables are missing in the dataset.
        """
        xr_dict = data_xr.to_dict()
        try:
            mdens_data = xr_dict["data_vars"]["mdens"]["data"]
            lon_data = xr_dict["coords"]["longitude"]["data"]
            lat_data = xr_dict["coords"]["latitude"]["data"]
            time_data = xr_dict["coords"]["time"]["data"]
            metadata_data = xr_dict["data_vars"]["mdens"]["attrs"]
        except Exception as e:
            print(
                f"🔴 Data returned an unexpected structure. "
                f"Are variables missing? {e}"
            )
            sys.exit(1)

        def enumerate_list(l):
            """ Enumerates a list and produces a dictionary where the key is
                an int converted to a string.
                Example: {'0' : value}
            """
            # cv = (count, value)
            return dict(map(lambda cv: (str(cv[0]), cv[1]), enumerate(l)))

        data = {
            "mdens": enumerate_list(mdens_data),
            "longitude": enumerate_list(lon_data),
            "latitude": enumerate_list(lat_data),
            "time": {"data": time_data},
            "metadata": metadata_data
        }

        return data

    def __get_data(
        self,
        date: str,
        variable_name: str,
        extent: Tuple[float, float, float, float],
        extent_name: str
    ) -> xr.Dataset:
        """
        Downloads and subregions HRRR data for the specified date, variable,
        and region.

        Args:
            date (str): Date for the HRRR data in 'YYYY-MM-DD' format.
            variable_name (str): Variable to download.
            extent (tuple): Tuple of (lon_min, lon_max, lat_min, lat_max).
            extent_name (str): Name of the subregion.

        Returns:
            xarray.Dataset: Dataset opened from the GRIB file.
        """
        H = Herbie(
            date,
            model="hrrr",
            product="sfc",
            fxx=0
        )
        data_grib = self.__subregion_file(
            H=H,
            extent=extent,
            extent_name=extent_name,
            variable=variable_name
        )
        data_xr = xr.open_dataset(
            data_grib,
            engine="cfgrib",
            decode_timedelta=False,
            decode_times=False
        )
        return data_xr

