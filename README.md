# Resources
- Setting up a private server and connecting it to your firebase project
    - https://firebase.google.com/docs/admin/setup#python
- Adding documents to the firebase database
    - https://firebase.google.com/docs/firestore/manage-data/add-data#python
- Firebase admin API
    - https://firebase.google.com/docs/reference/admin
- What is HRRR?
    - https://rapidrefresh.noaa.gov/hrrr/
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
1. Start the environment using `source start-env.sh`. This script:
    - Starts the `firebase-env` virtual environment
    - Sets the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the path of your service account file
2. Run the script `python hrrr-smoke-ingest.py`
    - Comes with useful optional args. See: `python hrrr-smoke-ingest.py -h`
# Data info
```
<xarray.Dataset> Size: 92kB
Dimensions:            (y: 69, x: 67)
Coordinates:
    time               int64 8B ...
    step               float64 8B ...
    heightAboveGround  float64 8B ...
    latitude           (y, x) float64 37kB ...
    longitude          (y, x) float64 37kB ...
    valid_time         float64 8B ...
Dimensions without coordinates: y, x
Data variables:
    mdens              (y, x) float32 18kB ...
Attributes:
    GRIB_edition:            2
    GRIB_centre:             kwbc
    GRIB_centreDescription:  US National Weather Service - NCEP
    GRIB_subCentre:          0
    Conventions:             CF-1.7
    institution:             US National Weather Service - NCEP
    history:                 2025-04-30T19:03 GRIB to CDM+CF via cfgrib-0.9.1...
```
