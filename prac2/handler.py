import json

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
			"body": json.dumps(errorInfo(err))
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
			"body": json.dumps(errorInfo(err))
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
			"body": json.dumps(errorInfo(err))
		}

#can I put functions here other than handlers?
def errorInfo(err):
	return {
		"type": str(type(err)),
		"args": str(err.args),
		"string": str(err)
	}