print("hello")

import json
import logging
import asyncpg
import asyncio
import uuid
from twilio.rest import Client
import httpx

from config import (
    DATABASE_URL,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Twilio configuration
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

async def get_connection():
    return await asyncpg.connect(DATABASE_URL)

async def fetch_all_users():
    conn=await get_connection()

    try:
        query=f'''
        select * from users as u
        '''

        result=await conn.fetch(query)

        return result
    except Exception as e:
        print("Failed to retrieve user")
        logger.info(f"Failed to retrieve user ",e.args)
        raise RuntimeError("Server error while fetching users")
    
async def get_user_phonenumber_by_username(username: str):
    conn=await get_connection()

    try:
        query=f'''
        select 
            u.phone_number
        from users as u
        where u.username=$1;
        '''

        result=await conn.fetch(query,username)

        return result
    except Exception as e:
        print("Failed to retrieve user phone number")
        logger.info(f"Failed to retrieve user ",e.args)
        raise RuntimeError("Server error while fetching user phone number")

async def insert_new_pair_to_match_pair_table(
    match_id: str,
    user1: str,
    user2: str
):
    conn=await get_connection()
    
    try:
        query = '''
        INSERT INTO match_pairs (
            match_id, 
            user_1, 
            user_2, 
            user_1_action, 
            user_2_action
        ) 
        VALUES 
            ($1, $2 , $3, NULL, NULL)
        '''

        await conn.execute(query, match_id, user1, user2)
        
        print('Successfuly add pair to match_pairs table')
        logger.info("Successfuly add pair to match_pairs table")
    except Exception as e:
        print("Failed to add pair to match_pairs")
        logging.info("Failed to add pair to match_pairs, error message: ",e.args[0])
        raise RuntimeError("Server error while add pairs")
 
async def update_user_status_after_match(
    match_id: str,
    username: str
):
    conn=await get_connection()
    
    try:
        query = '''
        UPDATE users 
        SET 
            status = 'frozen',
            match_reference_id=$1
        WHERE username = $2;
        '''

        await conn.execute(query, match_id,username)
        
        print(f'Successfuly update status for user {username}')
        logger.info(f'Successfuly update status for user {username}')
    except Exception as e:
        print("Failed to update status for user")
        logging.info("Failed to update status for user ",e.args[0])
        raise RuntimeError("Server error while updating users")
 
async def process_event(event):
    """Helper function to process the event asynchronously"""
    
    users=await fetch_all_users()
    
    print("users: ",users)
    
    # TODO
    # Mathching algorithms come here
    # YOUR CODE
    
    
    # for example after yall do matching, user louis match user emma002
    match_pairs=[('louis','emma002')]
    
    payload={
        "match_pairs": [user1+"-"+user2 for user1,user2 in match_pairs]
    }
    
    # Make the POST request to Backend to send all Match pairs
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://localhost:8001/api/v1/auth/match_pairs", json=payload)
            response.raise_for_status()  # Raise an error if not 2xx
            print("Match posted successfully:", response.json())
        except httpx.HTTPStatusError as exc:
            print(f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
          
    logger.info(f"Received event: {json.dumps(event, indent=4)}")

    return {
        'statusCode': 200,
        'body': json.dumps({"message": "Hello from local Lambda!"})
    }

def lambda_handler(event, context):
    """AWS Lambda entry point (sync wrapper)"""
    return asyncio.run(process_event(event))
