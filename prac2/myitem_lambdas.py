import json
import boto3
import os
import json_func
import user_lambdas
from boto3.dynamodb.conditions import Key

#myitems - do all the item lambdas but get user id from auth instead of a prarameter

#_____LAMBDAS_____

#add item to a user
#if user doesn't exist, nextItemNum will error - check that more explicitly in here?
def add_item(event, context):
	try:
		userId = json_func.get_username(event)
		[value] = json_func.get_body_args(event, {'value':str})
		itemNum = user_lambdas.nextItemNum(userId)
		table = itemTableResource()
		resp = table.put_item(Item={"userId": userId, "itemId": itemNum, "value": value})
		return {
			"statusCode": 201,
			"body": "added item"
		}
	except Exception as err:
		return json_func.errorMessage(err)

#get user's items which match a query
#caution - make sure it can't get other user's items, even with strange queries.
def get_matching_items(event, context):
	try:
		userId = json_func.get_username(event)
		keyExpression = Key('userId').eq(userId)
		
		#apply optional filers on itemId
		#operator, compareto = json_func.get_querystring_optional_args(event, {'operator': str, 'compareto': int})#, 'val2': int})
		
		operator = None
		if 'queryStringParameters' in event:
			queryString = event['queryStringParameters']
			operator = queryString['operator']
			compareto = int(queryString['compareto'])

		sortKeyOperators = {
			"eq": boto3.dynamodb.conditions.Key.eq,
			"lt": boto3.dynamodb.conditions.Key.lt,
			"lte": boto3.dynamodb.conditions.Key.lte,
			"gt": boto3.dynamodb.conditions.Key.gt,
			"gte": boto3.dynamodb.conditions.Key.gte
			#begins with - only applies to strings
			#"between": boto3.dynamodb.conditions.key.between	#need an extra argument for this.
		}
		if operator:
			func = sortKeyOperators[operator]
			keyExpression = keyExpression & func(Key('itemId'), compareto)

		#TODO: apply FilterExpression to filter results by non-key attributes.

		#do the query, return results
		resp = itemTableResource().query(KeyConditionExpression=keyExpression)
		return{
			"statusCode": 200,
			"body": json.dumps(resp, cls=json_func.DecimalEncoder)
		}
	except Exception as err:
		return json_func.errorMessage(err)

#change one attribute of the item, including custom attributes. currently value has to be string.
#do we want to allow something this general?
def edit_item_field(event, context):
	try:
		userId = json_func.get_username(event)
		itemId, attrName, attrValue = json_func.get_body_args(event, {'itemId':int, 'attrName':str, 'attrValue':str})
		if not existingItem(userId, itemId):
			return{
				"statusCode": 404,
				"body": "item with itemId = "+str(itemId)+" does not exist."
			}
		editResp = itemTableResource().update_item(
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
		return json_func.errorMessage(err)

#delete one item by userId and itemId
#version with client.delete_item : client doesn't specify region, deletes from table in the region matching the lambda
#should this use resource delete_item instead?
def delete_item(event, context):
	try:
		userId = json_func.get_username(event)
		[itemId] = json_func.get_body_args(event, {'itemId':int})
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
				"body": "item with itemId = "+str(itemId)+" does not exist."
			}
	except Exception as err:
		return json_func.errorMessage(err)

#_____INTERNAL_____

def itemTableResource():
	item_table_name = os.environ['ITEM_TABLE']
	region = os.environ['REGION']
	dynamodb = boto3.resource('dynamodb', region_name=region)
	table = dynamodb.Table(item_table_name)
	return table

def existingItem(userId, itemId):
	table = itemTableResource()
	resp = table.get_item(Key={"userId": userId, "itemId": itemId})
	if 'Item' in resp:
		return resp['Item'] 
	return None