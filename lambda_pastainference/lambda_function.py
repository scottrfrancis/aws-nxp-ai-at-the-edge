import os
import io
import boto3
import json
import csv

import base64
from base64 import b64encode

# grab environment variables
ENDPOINT_NAME = 'object-detection-2019-08-22-20-44-51-420'
runtime= boto3.client('runtime.sagemaker')

def lambda_handler(event, context):

    #*** Get image data ***
    image_read = base64.b64decode(event["picture"])
    b = bytearray(image_read)


    #*** Call the inference function ***
    response = runtime.invoke_endpoint(EndpointName=ENDPOINT_NAME,
                                           ContentType='image/jpeg',
                                           Body=image_read)

    #detections = json.loads(results)
    result = json.loads(response['Body'].read().decode())

    return result
