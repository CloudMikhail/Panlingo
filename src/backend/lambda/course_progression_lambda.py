import json
import time
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
user_progress_table = dynamodb.Table('panlingo-user-progress')
course_content_table = dynamodb.Table('panlingo-course-content')

def lambda_handler(event, context):
    user_id = event['user_id']
    course_id = event['course_id']
    lesson_id = event['lesson_id']
    
    update_user_progress(user_id, course_id, lesson_id)
    
    next_lesson = get_next_lesson(course_id, lesson_id)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Progress updated successfully',
            'next_lesson': next_lesson
        })
    }

def update_user_progress(user_id, course_id, lesson_id):
    user_progress_table.update_item(
        Key={'user_id': user_id, 'course_id': course_id},
        UpdateExpression="set current_lesson_id = :l, last_updated = :t",
        ExpressionAttributeValues={
            ':l': lesson_id,
            ':t': int(time.time())
        }
    )

def get_next_lesson(course_id, current_lesson_id):
    response = course_content_table.query(
        KeyConditionExpression=Key('course_id').eq(course_id) & Key('lesson_id').gt(current_lesson_id),
        Limit=1
    )
    
    if response['Items']:
        return response['Items'][0]
    else:
        return None