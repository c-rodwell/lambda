import json
import boto3
import os
import helpers
import user_lambdas

#_____HANDLERS_____

def add_item(event, context):
	try:
		#user, value = helpers.get_querystring_args(event, {'user':str, 'value':str})
		userId, value = helpers.get_body_args(event, {'userId':str, 'value':str})
		itemNum = user_lambdas.nextItemNum(userId)
		table = itemTableResource()
		resp = table.put_item(Item={"userId": userId, "itemId": itemNum, "value": value})
		return {
			"statusCode": 200,
			"body": "inserted item"
		}
	except Exception as err:
		return helpers.errorMessage(err)

def get_item(event, context):
	try:
		#userId, itemId = helpers.get_body_args(event, {'userId':str, 'itemId':int})
		userId, itemId = helpers.get_querystring_args(event, {'userId':str, 'itemId':int})
		table = itemTableResource()
		resp = table.get_item(Key={"userId": userId, "itemId": itemId})
		if 'Item' not in resp:
			raise FileNotFoundError("item with userId = "+userId+", itemId = "+str(itemId)+" does not exist")
		return{
			"statusCode": 200,
			"body": json.dumps(resp['Item'], cls=helpers.DecimalEncoder)
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