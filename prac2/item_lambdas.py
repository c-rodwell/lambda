import json
import boto3
import os
import helpers
import user_lambdas
from boto3.dynamodb.conditions import Key

#_____LAMBDAS_____

def add_item(event, context):
	try:
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

#get all items for the user
#TODO - allow filters
#return count and metadata, or just the items list?
def get_user_items(event, context):
	try:
		[userId] = helpers.get_querystring_args(event, {'userId':str})
		table = itemTableResource()
		resp = table.query(KeyConditionExpression=Key('userId').eq(userId))
		return{
			"statusCode": 200,
			"body": json.dumps(resp, cls=helpers.DecimalEncoder)
		}
	except Exception as err:
		return helpers.errorMessage(err)

#change one attribute of the item, including custom attributes. currently value has to be string.
#do we want to allow something this general?
def edit_item_field(event, context):
	try:
		userId, itemId, attrName, attrValue = helpers.get_body_args(event, {'userId':str, 'itemId':int, 'attrName':str, 'attrValue':str})
		table = itemTableResource()
		editResp = table.update_item(
			Key = {"userId": userId, "itemId": itemId},
			ExpressionAttributeNames={
				"#attrName": attrName,
			},
			ExpressionAttributeValues={
				":attrValue": attrValue,
			},
			UpdateExpression="SET #attrName = :attrValue",
		)

		#TODO check the edit response for success, or return the response
		return{
			"statusCode": 200,
			"body": "set attribute '"+attrName+"' to "+repr(attrValue)
		}
	except Exception as err:
		return helpers.errorMessage(err)

#delete one item by userId and itemId
#version with client.delete_item : client doesn't specify region, deletes from table in the region matching the lambda
#should this use resource delete_item instead?
def delete_item(event, context):
	try:
		userId, itemId = helpers.get_body_args(event, {'userId':str, 'itemId':int})
		item_table_name = os.environ['ITEM_TABLE']
		client = boto3.client('dynamodb')
		resp = client.delete_item(
			TableName=item_table_name,
			Key={
				'userId':{
					'S': userId,
				},
				'itemId':{
					'N': str(itemId) 	#should it be entered as string type?
				}

			},
			ReturnValues='ALL_OLD')
		if "Attributes" in resp: #deleted something
			return{
				"statusCode": 200,
				"body": "deleted item: "+json.dumps(resp['Attributes'])
			}
		else:
			return{
				"statusCode": 404,
				"body": "item with userId = "+userId+", itemId = "+str(itemId)+" does not exist."
			}
	except Exception as err:
		return helpers.errorMessage(err)

#_____INTERNAL_____

def itemTableResource():
	item_table_name = os.environ['ITEM_TABLE']
	region = os.environ['REGION']
	dynamodb = boto3.resource('dynamodb', region_name=region)
	table = dynamodb.Table(item_table_name)
	return table