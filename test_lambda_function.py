import json
from lambda_function import lambda_handler
import asyncio  # Import asyncio to run async functions

test_event = {
    "username": "louis",
    "gender": "Male",
    "gender_preferences": "Female"
}

def main():
    response =  lambda_handler(test_event, None)
    print(response)

main()
