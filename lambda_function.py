print("hello1")

import json
import logging
import asyncpg
import asyncio
import uuid
import httpx

from config import (
    DATABASE_URL
)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

async def get_connection():
    return await asyncpg.connect(DATABASE_URL)

async def fetch_all_available_users():
    conn = await get_connection()

    try:
        query = '''
        SELECT *
        FROM users AS u 
        WHERE u.status = 'available' and u.is_profile_creation_complete=true and embedding IS NOT null;
        '''

        result = await conn.fetch(query)
        return result

    except Exception as e:
        logger.error("Failed to retrieve available users", exc_info=True)
        raise RuntimeError("Server error while fetching users") from e
    

async def fetch_unmatched_usernames(username: str):
    conn = await get_connection()

    try:
        query = '''
        SELECT u1.username2 as username
        FROM unmatch_pairs AS u1 
        WHERE u1.username1 = $1
        UNION
        SELECT u2.username1 as username
        FROM unmatch_pairs AS u2 
        WHERE u2.username2 = $1;
        '''

        result = await conn.fetch(query, username)
        return result
    except Exception as e:
        logger.error("Failed to retrieve unmatched usernames", exc_info=True)
        raise RuntimeError("Server error while fetching unmatched usernames") from e


async def fetch_most_similar_user(
    embedding_vector: list[float],
    min_age: int,
    max_age: int,
    gender_preference: str,
    included_usernames: list[str]
):
    conn = await get_connection()

    try:
        query = '''
        SELECT *,
               1 - (embedding <#> $1::vector) AS similarity_score
        FROM users
        WHERE embedding IS NOT NULL
          AND DATE_PART('year', AGE(CURRENT_DATE, TO_DATE(birthday, 'YYYY-MM-DD'))) BETWEEN $2 AND $3
          AND gender = $4
          AND username = ANY($5::text[])
        ORDER BY embedding <#> $1::vector
        LIMIT 1;
        '''

        result = await conn.fetchrow(
            query, embedding_vector, min_age, max_age, gender_preference, included_usernames
        )

        if result:
            print(f"Matched user: {result['username']} | Similarity Score: {result['similarity_score']:.4f}")
        return result

    except Exception as e:
        logger.error("Failed to fetch most similar user", exc_info=True)
        raise RuntimeError("Error during similarity search") from e




async def process_event(event):
    """Helper function to process the event asynchronously"""
    
    users_in_available_pool=await fetch_all_available_users()
    
    if not users_in_available_pool:
        return {
        'statusCode': 200,
        'body': json.dumps({"message": "Hello from local Lambda! There is no available user"})
    }
    
    username_users_in_available_pool=[user['username'] for user in users_in_available_pool]
    
    print("available users usernames: ",username_users_in_available_pool)
    
    match_pairs=[]
    
    while username_users_in_available_pool:
        user=username_users_in_available_pool.pop()

        print()
        print("finding match for user: ",user)
        
        record_of_this_user=[entry for entry in users_in_available_pool if entry['username']==user][0]
        
        embedding_of_user=record_of_this_user['embedding']
        
        # print(f"embeding of user {user}: {embedding_of_user}")
        
        preferred_age_range=record_of_this_user['age_range']
        
        print("preferred age range: ",preferred_age_range)
        
        min_age=int(preferred_age_range.split("-")[0])
        
        max_age=int(preferred_age_range.split("-")[1])
        
        preferred_gender=record_of_this_user['gender_preferences']
        
        unmatched_usernames_before=await fetch_unmatched_usernames(username=user)
        
        print("unmatched_usernames_before: ",unmatched_usernames_before)
        
        formatted_unmatched_useranmes_before=[] if not unmatched_usernames_before else [entry['username'] for entry in unmatched_usernames_before]
        
        print('formatted_unmatched_useranmes_before: ',formatted_unmatched_useranmes_before)
            
        included_users_name_for_matching=[user_entry for user_entry in username_users_in_available_pool if user_entry not in formatted_unmatched_useranmes_before]
        
        print('included_users_name_for_matching: ',included_users_name_for_matching)
            
        similar_user_with_score=await fetch_most_similar_user(
            embedding_vector=embedding_of_user,
            min_age=min_age,
            max_age=max_age,
            gender_preference=preferred_gender,
            included_usernames=included_users_name_for_matching
        )
        
        if not similar_user_with_score:
            print(f"can not find any user match with {user}")
            continue
        
        matched_username=similar_user_with_score['username']
        
        
        similarity_score=similar_user_with_score['similarity_score']
        
        print("matched username: ",matched_username)
        
        print("similarity score: ",similarity_score) 
        
        match_pairs.append((user,matched_username))
        
        username_users_in_available_pool.remove(matched_username)
        
        print("available user username: ",username_users_in_available_pool)
        
    print("final match pairs: ",match_pairs)
       
    payload={
        "match_pairs": [user1+"-"+user2 for user1,user2 in match_pairs]
    }
    
    # Make the POST request to Backend to send all Match pairs
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://localhost:8001/api/v1/auth/match_pairs", json=payload)
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
