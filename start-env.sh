#!/bin/bash

# to execute, you type `source script_name`
# source runs the commands in the current shell
# ./ runs the command in a new shell, then exits
# ~ the more you know ~

conda activate firebase-env 
export GOOGLE_APPLICATION_CREDENTIALS="/home/mgraca/Workspace/smoke-app/smoke-forecast-data-ingestion/secrets/smoke-forecast-visualizer-firebase-adminsdk-fbsvc-414e1a7cc5.json"
