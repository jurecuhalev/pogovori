#!/usr/bin/env python
#
#   TODO: flag protected users
#         datetime when data was downloaded
# 
import anyjson, urllib2, datetime, time, sys
from pymongo import Connection
connection = Connection()

db = connection.twitter
followers_db = db.followers

# download initial followers
initial_id = '14962721'
base_url = 'https://api.twitter.com/1'

#db.followers.count()

import twitter
from tokens import consumer_key, consumer_secret, ACCESS_TOKEN_LIST
access_token = ACCESS_TOKEN_LIST[0]

api = twitter.Api(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token['oauth_token'], access_token_secret=access_token['oauth_token_secret'])
#print api.VerifyCredentials()

rate_f = api._FetchUrl('https://api.twitter.com/1/account/rate_limit_status.json')
rate_json = anyjson.loads(rate_f)
print rate_json
if rate_json['remaining_hits'] < 5:
    print rate_json
    sys.exit()

def grab_followers(userid):
    rec = db.followers.find_one({'userid': userid})
    if rec and not rec.get('is_protected', False):
        return rec, rec['followers'].split(',')
    elif rec and rec.get('is_protected') == True:
        return rec, None

    print "grabbing", userid

    print 'https://api.twitter.com/1/users/lookup.json?user_id=%s' % userid
    f_user = api._FetchUrl('https://api.twitter.com/1/users/lookup.json?user_id=%s' % userid)
    json_user = anyjson.loads(f_user)
    print json_user

    if type(json_user) == dict and json_user.get('errors') and json_user['errors'][0]['code']:
            rec = followers_db.save({'userid': userid,
                                     'is_protected': True,
                                     'retrieved': datetime.datetime.now()})
            return rec, None
    if json_user[0]['followers_count'] > 10000:
            rec = followers_db.save({'userid': userid,
                                     'is_protected': True,
                                     'retrieved': datetime.datetime.now()})
            return rec, None

    print 'https://api.twitter.com/1/followers/ids/%s.json' % userid
    try:
        f = api._FetchUrl('https://api.twitter.com/1/followers/ids/%s.json' % userid)
    except urllib2.HTTPError:
        # check if we are rate limited
        rate_f = api._FetchUrl('https://api.twitter.com/1/account/rate_limit_status.json')
        rate_json = anyjson.loads(rate_f)
        
        # account info is private and we still have API calls
        if rate_json['remaining_hits'] > 0:
            rec = followers_db.save({'userid': userid,
                                     'is_protected': True,
                                     'retrieved': datetime.datetime.now()})
            return rec, None
        else:
            print rate_json
            print "sleeping for 10 minutes" # % str(rate_json['reset_time_in_seconds'] / 60*60)
            time.sleep(60*10)
            raise

    print f
    json = anyjson.loads(f)


    rec = followers_db.save({'userid': userid,
                       'screen_name': json_user[0]['screen_name'],
                       'followers': ','.join([str(el) for el in json]),
                       'is_protected': False,
                       'retrieved': datetime.datetime.now()
                       })


rec, seed_followers = grab_followers(initial_id)

fail_count = 0
for userid in seed_followers:
    try:
        grab_followers(userid)
    except urllib2.HTTPError:
        print "out of API calls", fail_count
        fail_count += 1
        if fail_count > 150:
            break
