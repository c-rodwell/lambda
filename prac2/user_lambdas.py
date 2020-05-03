import json
import boto3
import os
import helpers

#_____LAMBDAS_____

def create_user(event, context):
	try:
		userId, name = helpers.get_body_args(event, {'userId':str, 'name':str})
		table = userTableResource()
		resp = table.put_item(Item={"userId": userId, "name": name})
		return {
			"statusCode": 201,
			"body": "created user: id = "+userId+", name = "+name
		}
	except Exception as err:
		return helpers.errorMessage(err)

#get one user by id and return their info.
#maybe make an internal getuser helper - logic shared with nextItemNum
def get_user(event, context):
	try:
		[userId] = helpers.get_querystring_args(event, {'userId':str})
		table = userTableResource()
		resp = table.get_item(Key={"userId": userId})
		if 'Item' not in resp:
			raise FileNotFoundError("user "+userId+" does not exist")
		userInfo = resp['Item']
		return{
			"statusCode": 200,
			"body": json.dumps(userInfo)
		}
	except Exception as err:
		return helpers.errorMessage(err)

#edit user- what should be editable?
#userId - not allowed to change since it's the primary key
#name - can change
#numCreatedItems - set through nextItemNum, not editable by user.
def edit_user_attribute(userId, attrName, attrValue):
	raise notImplemented

def delete_user(event, context):
	raise notImplemented

#_____INTERNAL_____

#increment the user's item counter, return the current value
def nextItemNum(userId):
	table = userTableResource()
	getResp = table.get_item(Key={"userId": userId})
	#user doesn't exist - what is appropriate error?
	if 'Item' not in getResp:
		raise FileNotFoundError("user "+userId+" does not exist")
	userInfo = getResp['Item']
	if 'numCreatedItems' in userInfo:
		num = userInfo['numCreatedItems'] + 1
	else:
		num = 1
		
	#set the numCreatedItems for the user to num
	#could make this a separate editUser(attrName, attrValue) function
	editResp = table.update_item(
		Key = {"userId": userId},
		ExpressionAttributeNames={
			"#attrName": "numCreatedItems",
		},
		ExpressionAttributeValues={
			":attrValue": num,
		},
		UpdateExpression="SET #attrName = :attrValue",
	)
	return num

def userTableResource():
	user_table_name = os.environ['USER_TABLE']
	region = os.environ['REGION']
	dynamodb = boto3.resource('dynamodb', region_name=region)
	table = dynamodb.Table(user_table_name)
	return table