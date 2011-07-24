#!/usr/bin/env python
import anyjson, urllib2
from pymongo import Connection
connection = Connection()

db = connection.twitter
followers_db = db.followers

# download initial followers
initial_id = '15057050'

#db.followers.count()

def grab_followers(userid):
    rec = db.followers.find_one({'userid': userid})
    if rec:
        return rec, rec['followers'].split(',')

    print "grabbing", userid

    f = urllib2.urlopen('https://api.twitter.com/1/followers/ids/%s.json' % userid)
    json = anyjson.loads(f.read())

    f_user = urllib2.urlopen('https://api.twitter.com/1/users/lookup.json?user_id=%s' % userid)
    json_user = anyjson.loads(f_user.read())

    rec = followers_db.save({'userid': userid,
                       'screen_name': json_user[0]['screen_name'],
                       'followers': ','.join([str(el) for el in json])
                       })


rec, seed_followers = grab_followers(initial_id)

for userid in seed_followers:
    try:
        grab_followers(userid)
    except:
        pass

