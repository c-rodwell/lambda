import json
import boto3
import os
import helpers

def add_item(event, context):
	try:
		#user, value = helpers.get_querystring_args(event, {'user':str, 'value':str})
		user, value = helpers.get_body_args(event, {'user':str, 'value':str})

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
		return helpers.errorMessage(err)
		# return {
		# 	"statusCode": 500,
		# 	"body": json.dumps(helpers.errorInfo(err))
		# }

def edit_item(event, context):
	return

def delete_item(event, context):
	return