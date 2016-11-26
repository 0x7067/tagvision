#!/usr/bin/env python

import os
import time
import requests
from sys import argv
from os.path import join, splitext, dirname

# Variables for API
_url = 'https://api.projectoxford.ai/vision/v1/analyses'
_key = '' # Your API KEY goes here
_maxNumRetries = 10

def processRequest(json, data, headers, params):

    """
    Helper function to process the request to Project Oxford

    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """

    retries = 0
    result = None

    while True:

        response = requests.request('post', _url, json = json, data = data, headers = headers, params = params)

        if response.status_code == 429:

            print("Message: %s" % ( response.json()['error']['message']))

            if retries <= _maxNumRetries:
                time.sleep(1)
                retries += 1
                continue
            else:
                print('Error: failed after retrying!')
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0:
                result = None
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str):
                if 'application/json' in response.headers['content-type'].lower():
                    result = response.json() if response.content else None
                elif 'image' in response.headers['content-type'].lower():
                    result = response.content
        else:
            print("Error code: %d" % (response.status_code))
            print("Message: %s" % (response.json()['message']))
            exit()

        break

    return result

def main():
    script, old = argv
    filename, extension = splitext(old)
    dir_name = dirname(old)
    if dir_name != '':
        dir_name = join(dir_name + '/')

    try:
        with open(old, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print('Error: file not found!')
        exit()
    # Computer Vision parameters
    params = {'visualFeatures' : 'Description'}

    headers = dict()
    headers['Ocp-Apim-Subscription-Key'] = _key
    headers['Content-Type'] = 'application/octet-stream'

    json = None

    result = processRequest(json, data, headers, params)

    new  = str(result['description']['captions'][0]['text'])
    os.rename(old, str(dir_name + new + extension))

if __name__ == '__main__':
    main()
