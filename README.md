## Main components:

- Lambda function is defined under [Lambda function](https://github.com/LouisAnhTran/mirror_cupid_match_making_engine_lambda_function_and_layer/blob/main/lambda_function.py)
- Lambda layer is defined under [Lambda layer](https://github.com/LouisAnhTran/mirror_cupid_match_making_engine_lambda_function_and_layer/tree/main/lambda_layer)
- All Shell Scriptings are defined under [Shell Scriptings](https://github.com/LouisAnhTran/mirror_cupid_match_making_engine_lambda_function_and_layer/tree/main/scripts)
  

## Run and Deploy Lambda function
  
  - Activate python virtual environment
    ```
    source myenv/bin/activate    
    ```
    
  - Run lambda function locally
    ```
    python test_lambda_function.py  
    ```
    
  - Deploy lambda function and lambda layer to AWS Lambda
    ```
    ./scripts/update_lambda.sh    
    ```

    ```
    ./scripts/update_deploy_layer.sh    
    ```

    
