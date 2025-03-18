#!/bin/bash

# Set variables
FUNCTION_NAME="cupid_lambda_function_devtest"
REGION="ap-southeast-1"
TIMEOUT=900  # 900 seconds = 15 minutes

# Update function timeout
aws lambda update-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --timeout "$TIMEOUT" \
    --region "$REGION"