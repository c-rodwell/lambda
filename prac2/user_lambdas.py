import json
import boto3
import os
import json_func

#_____LAMBDAS_____

def create_user(event, context):
	try:
		userId, name = json_func.get_body_args(event, {'userId':str, 'name':str})
		if existingUser(userId):
			return {
				"statusCode": 409,
				"body": "user with: id = "+userId+" already exists"
			}
		table = userTableResource()
		resp = table.put_item(Item={"userId": userId, "name": name})
		return {
			"statusCode": 201,
			"body": "created user: id = "+userId+", name = "+name
		}
	except Exception as err:
		return json_func.errorMessage(err)

#get one user by id and return their info.
#maybe make an internal getuser helper - logic shared with nextItemNum
def get_user(event, context):
	try:
		[userId] = json_func.get_querystring_args(event, {'userId':str})
		userInfo = existingUser(userId)
		if not userInfo:
			raise FileNotFoundError("user "+userId+" does not exist")

		return{
			"statusCode": 200,
			"body": json.dumps(userInfo, cls=json_func.DecimalEncoder)
		}
	except Exception as err:
		return json_func.errorMessage(err)

#edit user- what should be editable?
#userId - not allowed to change since it's the primary key
#name - can change
#numCreatedItems - set through nextItemNum, not editable by user.
def edit_user_attribute(userId, attrName, attrValue):
	raise notImplemented

def delete_user(event, context):
	raise notImplemented

#_____INTERNAL_____

def userTableResource():
	user_table_name = os.environ['USER_TABLE']
	region = os.environ['REGION']
	dynamodb = boto3.resource('dynamodb', region_name=region)
	table = dynamodb.Table(user_table_name)
	return table

#return user info if exists, else None
#use in: get_user, nextItemNum.
#is it inefficient to create userTableResource a bunch of times? could pass as argument
def existingUser(userId):
	table = userTableResource()
	resp = table.get_item(Key={"userId": userId})
	if 'Item' in resp:
		return resp['Item'] 
	return None

#increment the user's item counter, return the current value
def nextItemNum(userId):
	userInfo = existingUser(userId)
	if not userInfo:
		raise FileNotFoundError("user "+userId+" does not exist")

	if 'numCreatedItems' in userInfo:
		num = userInfo['numCreatedItems'] + 1
	else:
		num = 1
		
	#set the numCreatedItems for the user to num
	#could make this a separate editUser(attrName, attrValue) function
	editResp = userTableResource().update_item(
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