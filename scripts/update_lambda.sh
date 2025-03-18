#!/bin/bash

# Set variables
FUNCTION_NAME="cupid_lambda_function_devtest"
ZIP_FILE="function.zip"

# Update function code
aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --zip-file "fileb://$ZIP_FILE"