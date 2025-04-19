# Resources
- Setting up a private server and connecting it to your firebase project
    - https://firebase.google.com/docs/admin/setup#python
- Adding documents to the firebase database
    - https://firebase.google.com/docs/firestore/manage-data/add-data#python
- Firebase admin API
    - https://firebase.google.com/docs/reference/admin
# Setup
You can follow this guide here: https://firebase.google.com/docs/admin/setup#python
1. Add the Firebase Admin SDK.
```
python -m venv firebase-venv
source firebase-venv/bin/activate
pip install firebase-admin
```
2. Generate a private key file for your service account. Follow these steps: https://firebase.google.com/docs/admin/setup#initialize_the_sdk_in_non-google_environments
3. Create a folder called `secrets`, and move the JSON private key file into it
    - Note that it will be named something other than `service-account-file.json`. Replace this name in the script where appropriate.
```
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
    - Starts the `firebase-venv` virtual environment
    - Sets the environment variable `GOOGLE_APPLICATION_CREDENTIALS` to the path of your service account file
