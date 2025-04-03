#!/bin/bash

# Set variables
FUNCTION_NAME="cupid_lambda_function_devtest"
RUNTIME="python3.11"
ROLE_ARN="arn:aws:iam::418272758130:role/LambdaAdminRole"
HANDLER="lambda_function.lambda_handler"
ZIP_FILE="function.zip"
REGION="ap-southeast-1"

# Clean old zip if exists
rm -f "$ZIP_FILE"

# Create function.zip excluding files in .zipignore
zip -r "$ZIP_FILE" . -x@.zipignore

# Create the Lambda function
aws lambda create-function \
    --function-name "$FUNCTION_NAME" \
    --runtime "$RUNTIME" \
    --role "$ROLE_ARN" \
    --handler "$HANDLER" \
    --zip-file "fileb://$ZIP_FILE" \
    --region "$REGION" \
    --architectures x86_64
