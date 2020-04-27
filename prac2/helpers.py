import json
import boto3
import os



#get arguments from query string, throws exception if not found
#args: dictionary of name:type
#queryStringParameters is already json object - don't need to loads
#values in queryString are all strings - cast to the required type

#could catch specific exceptions and re-throw with more info
#missing queryStringParameters or parameter -> KeyError with missing arg as the string
#empty string -> botocore.exceptions.ClientError

def get_querystring_args(event, required_args):
	queryString = event['queryStringParameters']
	output = []
	for name in required_args:
		arg_type = required_args[name]
		output.append(arg_type(queryString[name]))
	return output

#get arguments from body, throws exception if not found
#args: dictionary of name:type
#body is string form of json, so use loads
#because we loads, values in body already are that type, so assert instead of casting.

#errors:
#missing body or body param -> KeyError
#string value type not in quotes -> json.decoder.JSONDecodeError
#fail assert -> AssertionError

def get_body_args(event, required_args):
	body = json.loads(event['body'])
	output = []
	for name in required_args:
		arg_type = required_args[name]
		value = body[name]
		if type(value) is not arg_type:
			raise TypeError("argument "+name+": expected type "+str(arg_type)+", found "+str(type(value)))
		output.append(value)
	return output

#error message to return - give right error code and explain it
#should be 400 for bad inputs and 500 for unexpected error
def errorMessage(err):
	if type(err) is KeyError:
		statusCode = 400
		body = "missing parameter: "+str(err)
	elif type(err) is TypeError:
		statusCode = 400
		body = str(err)
	else:
		statusCode = 500
		body = str(type(err))+": "+str(err)
	return {
		"statusCode": statusCode
		"body": body
	}

def errorInfo(err):
	return {
		"type": str(type(err)),
		"args": str(err.args),
		"string": str(err)
	}

#increment the user's item counter, return the current value
def nextItemNum(userId):
	#if user doens't have an item count, make it zero
	#add one to item count
	#return the increased value
	return
