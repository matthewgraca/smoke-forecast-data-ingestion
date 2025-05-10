from herbie import Herbie, FastHerbie, wgrib2
import xarray as xr
import sys
from typing import Tuple, Dict, Any
import pandas as pd
from functools import reduce
import time
import traceback

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
        data_desc_dict (dict): A dictionary describing the data and model.
    """

    def __init__(
        self,
        date: str = "2025-01-10",
        variable_name: str = "MASSDEN",
        lon_min: float = -119.1,
        lon_max: float = -117.3,
        lat_min: float = 33.28,
        lat_max: float = 34.86,
        extent_name: str = "la_subregion"
    ) -> None:
        """
        Retrieves  HRRR data for a specified geographic region and variable.

        Args:
            date (str): Date of the HRRR forecast in 'YYYY-MM-DD' format.
            variable_name (str): Name of the variable to retrieve.
            lon_min (float): Minimum longitude of the region.
            lon_max (float): Maximum longitude of the region.
            lat_min (float): Minimum latitude of the region.
            lat_max (float): Maximum latitude of the region.
            extent_name (str): A label for the geographical extent.
        """
        extent = (lon_min, lon_max, lat_min, lat_max)

        try:
            FH = FastHerbie(
                pd.date_range(start=date, periods=1, freq="1h"), 
                model='hrrr', 
                fxx=range(0, 24)
            )
        except Exception as e:
            print("Error occurred while pulling from NOAA; try again:")
            print(traceback.format_exec())
            sys.exit(1)

        print(
            reduce(
                lambda acc, x: str().join([acc, f"{repr(x)}\n"]), 
                FH.objects, 
                str()
            )
        )

        self.data_xr = list(map(
            lambda H: self.__get_data(H, variable_name, extent, extent_name),
            FH.objects
        ))

        self.data_dict = list(map(
            lambda d_xr: self.__process(d_xr),
            self.data_xr
        ))

        self.data_desc_dict = self.__get_data_description(
            FH.objects[0], 
            variable_name, 
            extent
        )

    def __get_data_description(self, H, variable_name, extent):
        data_description = {}
        mdens_desc = ( 
            "Fire emitted fine particulate matter (PM2.5, or fire smoke) "
            "concentrations at ~8 meters above the ground." 
        )
        colmd_desc = (
            "Simulated total PM2.5 mass within vertical columns over each "
            "model grid cell. Columns are ~25 kilometers above the ground. "
            "Product displays the effect of fire smoke load that includes "
            "smoke in the boundary layer as well as aloft, illustrating the "
            "integral effect of fire smoke throughout the atmosphere."
        )
        data_description["model_name"] = str(H.DESCRIPTION)
        data_description["product_description"] = str(H.product_description)
        data_description["model_description"] = (
                "GSL's experimental Rapid Refresh - Smoke (RAP-Smoke) and "
                "High-Resolution Rapid Refresh-Smoke (HRRR-Smoke) models "
                "simulate the emissions and transport of smoke from wildfires "
                "and the impact of smoke on the weather. RAP-Smoke and "
                "HRRR-Smoke predict the 3D movement of fire-emitted fine "
                "particulate matter (PM 2.5 or fire smoke)."
        )
        data_description["boundary"] = list(extent)
        match variable_name:
            case "MASSDEN":
                data_description["variable_description"] = mdens_desc 
            case "COLMD":
                data_description["variable_description"] = colmd_desc 
            case _:
                raise ValueError(
                    f"'variable_name' should be either 'COLMD' or 'MASSDEN'; "
                    f"got {variable_name} instead."
            )

        return data_description

    def __subregion_file(
        self,
        H: Herbie,
        extent: Tuple[float, float, float, float],
        extent_name: str,
        variable: str
    ) -> str:
        """
        Uses wgrib2 to subregion the GRIB file.

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
        H: Herbie,
        variable_name: str,
        extent: Tuple[float, float, float, float],
        extent_name: str
    ) -> xr.Dataset:
        """
        Downloads and subregions HRRR data for the specified date, variable,
        and region.

        Args:
            H (Herbie): Herbie object configured for the data download.
            variable_name (str): Variable to download.
            extent (tuple): Tuple of (lon_min, lon_max, lat_min, lat_max).
            extent_name (str): Name of the subregion.

        Returns:
            xarray.Dataset: Dataset opened from the GRIB file.
        """
        print(f"💾 Downloading from {H.grib}...")
        def attempt_download(H, variable_name, retries=3):
            if retries == 0:
                print("Retried too many times, exiting...")
                sys.exit(1)
            try:
                H.download(variable_name)
            except ConnectionResetError as e:
                cooldown = 5
                print("🔴 Error occurred while downloading:", e)
                print("Waiting {cooldown} seconds before retrying...")
                time.sleep(cooldown)
                attempt_download(H, variable_name, retries - 1)
            except Exception as e:
                print("🔴 Unchecked error occurred while downloading:", e)
                print(traceback.format_exec())
                print("Exiting...")
                sys.exit(1)
            return

        attempt_download(H, variable_name)
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

    def full_data_inventory(self):
        """
        Generates a human-readable summary of the processed HRRR data.

        Returns:
            str: Formatted summary string showing dataset structure, key data 
            points, and metadata.
        """
        def dict_to_str(d):
            """
            Creates a pretty string of a dictionary's items
            """
            return reduce(
                # k_v = (key, value)
                lambda acc, k_v: str().join([acc, f"\t{k_v[0]}: {k_v[1]}\n"]),
                d.items(),
                str()
            )

        sample = self.data_dict[0]
        return (
            f"⛈️  Number of forecasts: {len(self.data_xr)}\n"
            f"Examining a the first forecast frame...\n"
            f"🗃️  Dataset inventory: {self.data_xr[0]}\n\n"
            f"🔑 Dictionary keys: {sample.keys()}\n"
            f"🚬 First smoke value: {sample['mdens'][str(0)][0]}\n"
            f"📍 First longitude value: {sample['longitude'][str(0)][0]}\n"
            f"📍 First latitude value: {sample['latitude'][str(0)][0]}\n"
            f"🕰️  Time: {sample['time']['data']}\n"
            f"📜 Metadata:\n"
            f"{dict_to_str(sample['metadata'])}\n"
            f"🔬 Product description:\n"
            f"{dict_to_str(self.data_desc_dict)}"
        )

'''
    def plot(self, H, variable_name):
        ds = H.xarray(variable_name)
'''
