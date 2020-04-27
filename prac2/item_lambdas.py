import json
import boto3
import os
import helpers


#TODO separate method to extract arguments:
#use it like: user, value = get_args(event, ['user', 'value'])

# def add_item(event, context):
# 	try:
# 		#get name and value params
# 		if 'queryStringParameters' not in event:
# 			return {
# 				"statusCode": 400,
# 				"body": "missing parameters - must have name and value in query string"
# 			}
# 		params = event['queryStringParameters']
# 		if 'user' not in params or 'value' not in params:
# 			return {
# 				"statusCode": 400,
# 				"body": "missing name or value parameter"
# 			}
# 		user = params['user']
# 		value = params['value']

# 		#figure out what itemnum to add the value as.
		
# 		#instert into table
# 		item_table_name = os.environ['ITEM_TABLE']
# 		region = os.environ['REGION']
# 		dynamodb = boto3.resource('dynamodb', region_name=region)
# 		table = dynamodb.Table(item_table_name) #TODO get table name as a constant or environment variable

# 		# with table.batch_writer() as batch: #TODO maybe theres a better way for single write.
# 		#     batch.put_item(Item={"name": name, "value": value})
# 		resp = table.put_item(Item={"userId": user, "value": value})

# 		return {
# 			"statusCode": 200,
# 			"body": "inserted item"
# 		}
# 	except Exception as err:
# 		return {
# 			"statusCode": 500,
# 			"body": json.dumps(helpers.errorInfo(err))
# 		}

def add_item(event, context):
	try:
		user, value = helpers.get_querystring_args(event, {'user':str, 'value':str})
		#user, value = helpers.get_body_args(event, {'user':str, 'value':str})

		#TODO figure out what itemnum to add the value as.
		itemNum = 1
		item_table_name = os.environ['ITEM_TABLE']
		region = os.environ['REGION']
		dynamodb = boto3.resource('dynamodb', region_name=region)
		table = dynamodb.Table(item_table_name)
		resp = table.put_item(Item={"userId": user, "itemId": itemNum, "value": value})
		return {
			"statusCode": 200,
			"body": "inserted item"
		}
	except Exception as err:
		return {
			"statusCode": 500,
			"body": json.dumps(helpers.errorInfo(err))
		}

def edit_item(event, context):
	return

def delete_item(event, context):
	return