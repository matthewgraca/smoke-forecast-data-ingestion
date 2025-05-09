from herbie import Herbie, paint
from herbie.toolbox import EasyMap, pc
from herbie.crs import get_cf_crs
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import xarray as xr

# Backend kwargs for cfgrib
def set_cfgrib_backend_kwargs():
    backend_kwargs = {}
    backend_kwargs.setdefault("indexpath", "")
    backend_kwargs.setdefault(
        "read_keys",
        [
            "parameterName",
            "parameterUnits",
            "stepRange",
            "uvRelativeToGrid",
            "shapeOfTheEarth",
            "orientationOfTheGridInDegrees",
            "southPoleOnProjectionPlane",
            "LaDInDegrees",
            "LoVInDegrees",
            "Latin1InDegrees",
            "Latin2InDegrees",
        ],
    )
    backend_kwargs.setdefault("errors", "raise")
    return backend_kwargs

backend_kwargs = set_cfgrib_backend_kwargs()

ds = xr.open_dataset("/home/mgraca/data/hrrr/20250110/subset_d9ef9dd4__hrrr.t00z.wrfsfcf00.grib2", decode_timedelta=False, backend_kwargs=backend_kwargs,)

import metpy
variables = [i for i in list(ds) if len(ds[i].dims) > 0]
ds = ds.metpy.parse_cf('longitude')
print(ds)
crs = ds.metpy_crs.item().to_cartopy()
#crs = get_cf_crs(ds)

import numpy as np
def plot(ds, coords=None, coord_sys=crs):
    ug_per_kg = 1000000000
    plt.figure()
    ax = EasyMap("50m", crs=crs, figsize=[10, 8]).BORDERS().STATES().ax
    
    if coords != None:
        ax.set_extent(coords)
    
    p = ax.pcolormesh(
        ds.longitude,
        ds.latitude,
        ds.mdens * ug_per_k,
        transform=pc,
        #transform=ccrs.PlateCarree(),
        **paint.AQIPm25.kwargs2,
    )

    plt.colorbar(
        p,
        ax=ax,
        orientation="horizontal",
        pad=0.01,
        shrink=0.8,
        **paint.AQIPm25.kwargs2,
    )
    
    ax.set_title(
        f"{ds.model.upper()}: {H.product_description}\n"
        f"Valid: {ds.valid_time.dt.strftime('%H:%M UTC %d %b %Y').item()}",
        loc="left",
    )
    ax.set_title(ds.mdens.GRIB_name, loc="right")

    plt.show()
    plt.clf()

plot(ds, coord_sys=crs)
