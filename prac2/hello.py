import json
import boto3
import os
import helpers

#event structure is {'statuscode': <num>, 'body': <a json in string form> }
#so we loads and dumps the body but not the entire event.

def hello(event, context):
    body = {
        "message": "here is the request you sent",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """

def empty(event, context):
	return {
		"statusCode": 200,
		"body": json.dumps({})
	}

def findargs(event, context):
	try:
		req_body = event['body'] if 'body' in event else None
		queryargs = event['queryStringParameters'] if 'queryStringParameters' in event else None
		resp_body = {
			"body" : req_body,
			"args" : queryargs
		}
		return {
			"statusCode": 200,
			"body": json.dumps(resp_body)
		}
	except Exception as err:
		return {
			"statusCode": 500,
			"body": json.dumps(helpers.errorInfo(err))
		}

#get a number from "num" field in body, double it
#only works if body is json format, not encoded types
def double_body(event, context):
	try:
		if 'body' in event and 'num' in event['body']:
			num = json.loads(event['body'])['num']
			if type(num) in [int, float]:
				statuscode = 200
				body = json.dumps(2*num)
			else:
				statuscode = 400
				body = "num field must be a number"
		else:
			statuscode = 408
			body = "must have num field in request body"
		return {
			"statusCode": statuscode,
			"body": body
		}
	except Exception as err:
		return {
			"statusCode": 500,
			"body": json.dumps(helpers.errorInfo(err))
		}

#get number fro "num" field in query string and double it.
def double_query(event, context):
	try:
		if 'queryStringParameters' in event and 'num' in event['queryStringParameters']:
			num = float(event['queryStringParameters']['num'])
			statuscode = 200
			body = json.dumps(2*num)
		else:
			statuscode = 400
			body = "must have num field in query string"
		return {
			"statusCode": statuscode,
			"body": body
		}
	except ValueError:
		return {
			"statusCode": 400,
			"body": "num field must be a number"
		}
	except Exception as err:
		return {
			"statusCode": 500,
			"body": json.dumps(helpers.errorInfo(err))
		}

#can I put functions here other than handlers?
# def errorInfo(err):
# 	return {
# 		"type": str(type(err)),
# 		"args": str(err.args),
# 		"string": str(err)
# 	}




#insert to a table - should this use environment variables for table name, region, etc?
#created table: table1, us-east-2 , key = "name", type string
#expect fielns in query string: name and value, both string.

#TODO check response , see if insert succeeded

#example success resp: 

		# {'ResponseMetadata': 
		# 	{'RequestId': 'NHJUPAUA28J60R9FSAMGFVT9DNVV4KQNSO5AEMVJF66Q9ASUAAJG',
		# 	'HTTPStatusCode': 200,
		# 	'HTTPHeaders': {
		# 		'server': 'Server',
		# 		'date': 'Sun, 26 Apr 2020 07:58:16 GMT',
		# 		'content-type': 'application/x-amz-json-1.0',
		# 		'content-length': '2',
		# 		'connection': 'keep-alive',
		# 		'x-amzn-requestid': 'NHJUPAUA28J60R9FSAMGFVT9DNVV4KQNSO5AEMVJF66Q9ASUAAJG',
		# 		'x-amz-crc32': '2745614147'},
		# 	'RetryAttempts': 0}}

#inserting a new item, inserting an already existing item (everything same), and replacing (same primary key, different attributes)
	# all succeed with same message, don't give any indication of which of those happened
#bad insert caused exception (clienterror) when I tried insteadd of error message in response.


