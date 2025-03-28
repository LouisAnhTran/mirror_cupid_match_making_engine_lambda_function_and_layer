#!/bin/bash

# Set variables
LAYER_NAME="cupid-lambda-dependencies-devtest"
REGION="ap-southeast-1"
PYTHON_VERSION="python3.11"
LAYER_DIR="lambda_layer/python/lib/$PYTHON_VERSION/site-packages"
ZIP_FILE="lambda_layer/layer.zip"
FUNCTION_NAME="cupid_lambda_function_devtest"
ACCOUNT_ID="418272758130"

# Install dependencies
pip install -r requirements.txt -t "$LAYER_DIR"

# Zip the layer
zip -r "$ZIP_FILE" "lambda_layer/python/"

# Publish the layer and get the version
LAYER_VERSION=$(aws lambda publish-layer-version \
    --layer-name "$LAYER_NAME" \
    --zip-file "fileb://$ZIP_FILE" \
    --compatible-runtimes "$PYTHON_VERSION" \
    --region "$REGION" \
    --query 'Version' --output text)

# Attach the new layer version to the Lambda function
aws lambda update-function-configuration \
    --function-name "$FUNCTION_NAME" \
    --layers "arn:aws:lambda:$REGION:$ACCOUNT_ID:layer:$LAYER_NAME:$LAYER_VERSION"