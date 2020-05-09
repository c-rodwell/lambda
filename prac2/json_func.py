import json
import boto3
import os
import decimal

#TODOs:
	#give more bad argument errors: 
		#ClientError on empty string for key - maybe check in get_body_args and get_querystring_args
		#ValueError for string  when it should be int type in get_querystring_args
	#allow optional arguments
	#can body or querystring be turned directly into a dynamodb query without extracting specific args?

#get arguments from query string, throws exception if not found
#args: dictionary of name:type
#exceptions can happen here:
#missing queryStringParameters or parameter -> KeyError with missing arg as the string
#empty string -> botocore.exceptions.ClientError
def get_querystring_args(event, args):
	queryString = event['queryStringParameters']
	output = []
	for name in args:
		arg_type = args[name]
		output.append(arg_type(queryString[name]))
	return output

#optional args - return it if present, or None.
#will still error if argument is not the expected type
def get_querystring_optional_args(event, args):
	queryString = event['queryStringParameters']
	output = []
	for name in args:
		arg_type = args[name]
		if name in queryString
			output.append(arg_type(queryString[name]))
		else:
			output.append(None)
	return output

#get arguments from body, throws exception if not found
#args: dictionary of name:type
#errors:
#missing body or body param -> KeyError
#empty string -> botocore.exceptions.ClientError
#string value type not in quotes -> json.decoder.JSONDecodeError
#wrong type: raise a TypeError
def get_body_args(event, required_args):
	body = json.loads(event['body'])
	output = []
	for name in required_args:
		arg_type = required_args[name]
		value = body[name]
		if type(value) is not arg_type:
			raise TypeError("type error for "+name+": expected type "+str(arg_type)+", found "+str(type(value)))
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
	elif type(err) is json.decoder.JSONDecodeError:
		statusCode = 400
		body = "invalid JSON: "+str(err)
	elif type(err) is FileNotFoundError:
		statusCode = 404
		body = "not found: "+str(err)
	else:
		statusCode = 500
		body = str(type(err))+": "+str(err)
	return {
		"statusCode": statusCode,
		"body": body
	}

#decoder to convert dynamodb decimal type back to int. source: https://www.reddit.com/r/aws/comments/bwvio8/dynamodb_has_been_storing_integers_as/
#use: json.dumps({'someNumber': 123456789}, cls=DecimalEncoder)
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)

def get_username(event):
	client = boto3.client('cognito-idp')
	token = event['headers']['Authorization']
	shorter_token = token[7:] #chop off the "Bearer "
	response = client.get_user(AccessToken = shorter_token)
	return response['Username']