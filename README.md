# Setup
You can follow this guide here: https://firebase.google.com/docs/admin/setup#python
1. Download packages. We use `conda`.
``` bash
conda env create -f environment.yml
conda activate firebase-env
```
- Requirements contains the following packages:
    - `herbie-data`, which pulls data from NOAA and helps with preprocessing. https://herbie.readthedocs.io/en/stable/
    - `wgrib2`, NOAA's tool to read, write, and process `.grib` files. https://www.cpc.ncep.noaa.gov/products/wesley/wgrib2/
    - `firebase-admin`, which is the Firebase admin SDK.
2. Generate a private key file for your service account. Follow these steps: https://firebase.google.com/docs/admin/setup#initialize_the_sdk_in_non-google_environments
3. Create a folder called `secrets`, and move the JSON private key file into it
    - Note that it will be named something other than `service-account-file.json`. Replace this name in the script where appropriate.
``` bash
mkdir secrets
mv ~/Downloads/service-account-file.json secrets/
```
4. Set an environment variable to reference this file
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/your/absolute/path/to/secrets/service-account-file.json"
echo $GOOGLE_APPLICATION_CREDENTIALS
```
# Usage
## Running the data ingestion script
1. Start the environment using `source start-env.sh`. This script:
    - Starts the `firebase-env` virtual environment
    - Sets the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the path of your service account file
2. Run the script `python hrrr-smoke-ingest.py`
    - Comes with useful optional args. See: `python hrrr-smoke-ingest.py -h`
## Accessing variables
Suppose `i` and `j` are indices. There are currently five variables you have access to. Please note the dimensions of the variables are (y, x):
- `mdens` -- this is "mass density", i.e. the concentration of smoke 8 meters above ground, in $\frac{kg}{m^3}$.
    - Access: `db['hrrr-smoke-data']['mdens']`
    - Individual values: `db['hrrr-smoke-data']['mdens'][str(i)][j]`
- `longitude`, `latitude` -- simply location
    - Access: `db['hrrr-smoke-data']['longitude']` and `db['hrrr-smoke-data']['latitude']` 
    - Individual values: `db['hrrr-smoke-data']['longitude'][str(i)][j]` and `db['hrrr-smoke-data']['latitude'][str(i)][j]`
- `time` -- the time of the forecast
    - Access: `db['hrrr-smoke-data']['time']['data']`
- `metadata` -- tells you information on how to plot this thing; things like how it uses Lambert Conformal Conical Projection, etc.
    - Access: `db['hrrr-smoke-data']['metadata']`
# Data info
```
<xarray.Dataset> Size: 92kB
Dimensions:            (y: 69, x: 67)
Coordinates:
    time               int64 8B 1736985600
    step               float64 8B 0.0
    heightAboveGround  float64 8B 8.0
    latitude           (y, x) float64 37kB 32.97 32.98 32.99 ... 35.15 35.15
    longitude          (y, x) float64 37kB 241.0 241.0 241.1 ... 242.6 242.6
    valid_time         float64 8B 1.737e+09
Dimensions without coordinates: y, x
Data variables:
    mdens              (y, x) float32 18kB 2e-10 2e-10 2e-10 ... 8e-11 8e-11
Attributes:
    GRIB_edition:            2
    GRIB_centre:             kwbc
    GRIB_centreDescription:  US National Weather Service - NCEP
    GRIB_subCentre:          0
    Conventions:             CF-1.7
    institution:             US National Weather Service - NCEP
    history:                 2025-05-02T15:17 GRIB to CDM+CF via cfgrib-0.9.1... 

🔑 Dictionary keys: dict_keys(['mdens', 'longitude', 'latitude', 'time', 'metadata'])
🚬 First mdens value: 2.000000026702864e-10
📍 First longitude value: 241.010809
📍 First latitude value: 32.97486599999999
🕰️  Time: 1736985600
📜 Metadata:
	GRIB_paramId : 400000
	GRIB_dataType : fc
	GRIB_numberOfPoints : 4623
	GRIB_typeOfLevel : heightAboveGround
	GRIB_stepUnits : 1
	GRIB_stepType : instant
	GRIB_gridType : lambert
	GRIB_uvRelativeToGrid : 1
	GRIB_DxInMetres : 3000.0
	GRIB_DyInMetres : 3000.0
	GRIB_LaDInDegrees : 38.5
	GRIB_Latin1InDegrees : 38.5
	GRIB_Latin2InDegrees : 38.5
	GRIB_LoVInDegrees : 262.5
	GRIB_NV : 0
	GRIB_Nx : 67
	GRIB_Ny : 69
	GRIB_cfName : unknown
	GRIB_cfVarName : mdens
	GRIB_gridDefinitionDescription : Lambert Conformal can be secant or tangent, conical or bipolar
	GRIB_iScansNegatively : 0
	GRIB_jPointsAreConsecutive : 0
	GRIB_jScansPositively : 1
	GRIB_latitudeOfFirstGridPointInDegrees : 32.974866
	GRIB_latitudeOfSouthernPoleInDegrees : 0.0
	GRIB_longitudeOfFirstGridPointInDegrees : 241.010809
	GRIB_longitudeOfSouthernPoleInDegrees : 0.0
	GRIB_missingValue : 3.4028234663852886e+38
	GRIB_name : Mass density
	GRIB_shortName : mdens
	GRIB_units : kg m**-3
	long_name : Mass density
	units : kg m**-3
	standard_name : unknown
```
# Resources
- Setting up a private server and connecting it to your firebase project
    - https://firebase.google.com/docs/admin/setup#python
- Adding documents to the firebase database
    - https://firebase.google.com/docs/firestore/manage-data/add-data#python
- Firebase admin API
    - https://firebase.google.com/docs/reference/admin
- What is HRRR?
    - https://rapidrefresh.noaa.gov/hrrr/

