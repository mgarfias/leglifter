#!/usr/bin/env python

from pymongo import MongoClient
import base64
import httplib
import httplib2
import urllib
import urllib2
import yaml
import json
import sys
from datetime import date
import re


mongo_host = '127.0.0.1'
api_host = '127.0.0.1'
#dog_db = "dogtest"
api_port = 5000
#mongo_port = 27017
#token = base64.b64encode('superpass:')
#auth = "Basic %s" % token
#print "Auth: %s" % auth
#headers = {"Content-type": "application/json", "Authorization": auth}
# need to insert initial admin user first - set it up generic, then we will create real users using the API.
# lets connect
#client = MongoClient(mongo_host,mongo_port)
#db = client[dog_db]

def lookup_collection(endpoint):
    url = 'http://%s:%d/%s' % (api_host,api_port,endpoint)
    req = urllib2.Request(url)
    req.add_header('Content-Type','application/json')
    #req.add_header('Authorization', 'Basic %s' % token)
    try:
        response = urllib2.urlopen(req)
        data = json.load(response)
    except:
        return False
    return data

def lookup_object(endpoint,query,data):
    url = 'http://localhost:5000/api/%s' % (endpoint, urllib.quote(query.encode('utf-8')), urllib.quote(data.encode('utf-8')))
    #print "Endpiont: %s, Query: %s, Data: %s" % ( endpoint, query, data )
    req = urllib2.Request(url)
    req.add_header('Content-Type','application/json')
    req.add_header('Authorization', 'Basic %s' % token)
    try:
        response = urllib2.urlopen(req)
        ret = json.load(response)

    except urllib2.HTTPError, err:
        print "Error locating %s" % data
        ret = False
    except ValueError:
        return False
    return ret

def lookup_object_id(endpoint,query,data):
    url = 'http://localhost:5000/%s?where={"%s":"%s"}' % (endpoint, urllib.quote(query.encode('utf-8')), urllib.quote(data.encode('utf-8')))
    #print "Endpiont: %s, Query: %s, Data: %s" % ( endpoint, query, data )
    req = urllib2.Request(url)
    req.add_header('Content-Type','application/json')
    req.add_header('Authorization', 'Basic %s' % token)
    try:
        response = urllib2.urlopen(req)
        data = json.load(response)
        if data['_items']:
            ret = data['_items'][0]['_id']
        else:
            ret = False;
    except urllib2.HTTPError, err:
        print "Error locating %s" % data
        ret = False
    except ValueError:
        return False
    return ret

def load_data(endpoint,data):
    #print "Loading data for: %s - Data: %s" % (endpoint,data)
    url = 'http://localhost:5000/api/%s' % endpoint
    req = urllib2.Request(url)
    req.add_header('Content-Type','application/json')
    #req.add_header('Authorization', 'Basic %s' % token)
    json_data = json.dumps(data)
    #print "JSONified data: %s" % json_data
    try:
        response = urllib2.urlopen(req,json_data)
    except urllib2.HTTPError as e:
        if e.code >= 400:
            print "Error inserting to %s endpoint.  Data: %s error_code: %s" % (endpoint, json_data, e.code)
def patch_data(endpoint,data,id,etag):

    url = 'http://localhost:5000/%s/%s' % (endpoint, id)
    #req = urllib2.Request(url)
    #req.get_method = lambda: 'PATCH'
    #req.add_header('Content-Type','application/json')
    #req.add_header('Authorization', 'Basic %s' % token)
    json_data = json.dumps(data)
    #print "Patching data for endpoint: \"%s\" Data: %s" % (endpoint,json_data)
    headers = {'If-Match': etag, 'Content-Type':'application/json','Authorization':'Basic %s' % token}
    http = httplib2.Http()
    #print "JSONified data: %s" % json_data
    try:
        response, content = http.request(url, "PATCH", json_data,headers=headers)
        if response.status >= 400:
            print content
    except httplib2.ServerNotFoundError:
        print "some stupid error"


def httpdate(dt):
    """Return a string representation of a date according to RFC 1123
    (HTTP/1.1).

    The supplied date must be in UTC.

    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
        dt.year, 0, 0, 0)

#accounts = db.accounts

inital_admin = {
  'username': 'initadmin',
  'password': 'cheezeball',
  'roles': [ 'admin', 'superuser'],
  'token': 'superpass'
}


#admin_account = Accounts(username='initadmin', password='cheezeball', roles = 'superuser', token='superpass:')
#session.add(admin_account)
#session.commit()
accounts = db.accounts
initadmin_id = accounts.insert(inital_admin)
dogsdb = db.dogs

# collect our data
# accounts
stream = open("initial_data/accounts.yaml","r")
accounts = yaml.load(stream)
for account in accounts:
    load_data('accounts',account)

# bodies
stream = open("initial_data/bodies.yaml","r")
bodies = yaml.load(stream)
for body in bodies:
    load_data('bodies', body)

# clearances
stream = open("initial_data/health.yaml","r")
healths = yaml.load(stream)
for health in healths:
    #print "WTF: %s" % clearance['test']
    health['body'] = lookup_object_id('bodies','abrv',clearance['body'])
