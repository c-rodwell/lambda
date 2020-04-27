import json
import boto3
import os
import helpers
import user_lambdas

#_____HANDLERS_____

def add_item(event, context):
	try:
		#user, value = helpers.get_querystring_args(event, {'user':str, 'value':str})
		user, value = helpers.get_body_args(event, {'user':str, 'value':str})
		itemNum = user_lambdas.nextItemNum(user)
		table = itemTableResource()
		resp = table.put_item(Item={"userId": user, "itemId": itemNum, "value": value})
		
		return {
			"statusCode": 200,
			"body": "inserted item"
		}
	except Exception as err:
		return helpers.errorMessage(err)

def edit_item(event, context):
	return

def delete_item(event, context):
	return

#_____INTERNAL_____

def itemTableResource():
	item_table_name = os.environ['ITEM_TABLE']
	region = os.environ['REGION']
	dynamodb = boto3.resource('dynamodb', region_name=region)
	table = dynamodb.Table(item_table_name)
	return table