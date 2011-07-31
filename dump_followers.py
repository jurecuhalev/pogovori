#!/usr/bin/env python
import anyjson
from pymongo import Connection
connection = Connection()

db = connection.twitter
followers_db = db.followers

initial_id = '8019352'

seed = db.followers.find_one({'userid': initial_id})

data = {}
data['nodes'] = {}
data['edges'] = []

# iterate through a list of followers of initial seed
# and add them to dict
for userid in seed['followers'].split(','):
    rec = db.followers.find_one({'userid': userid, 'is_protected':{'$ne' : True}})
    if rec:
        data['nodes'][rec['userid']] = rec['screen_name']

# iterate through a list of followers for initial seed again
for userid in seed['followers'].split(','):
    # if we have a screen_name for this person
    if data['nodes'].get(userid):
        # retrieve rec again
        rec = db.followers.find_one({'userid': userid})

        # we're trying to create a directed graph to show how 
        # each person in the network connects to everyone else
        # so we need to iterate through followers list again
        for follower in rec['followers'].split(','):
            if data['nodes'].get(follower):
                data['edges'].append({'source': userid, 'target': follower})


##### JSON

#print anyjson.dumps(data)

##### GRAPHML

# print u"""<?xml version="1.0" encoding="UTF-8"?>
# <graphml xmlns="http://graphml.graphdrawing.org/xmlns"
# xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
# xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
# http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
# <graph id="G" edgedefault="directed">"""

# for node in data['nodes']:
#     print u"""<node id="n%s"><data key='label'>%s</data></node>""" % (node, data['nodes'][node])

# c = 1

# for edge in data['edges']:
#     print u"""<edge id="e%s" source="n%s" target="n%s"/>""" % (c, edge['source'], edge['target'])
#     c += 1

# print u"""</graph>
# </graphml>"""

##### GEXF

print u"""<gexf xmlns="http://www.gexf.net/1.2draft" xmlns:viz="http://www.gexf.net/1.2draft/viz" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd" version="1.2">
    <graph mode="static" defaultedgetype="directed">
"""

print u"""<nodes>"""
for node in data['nodes']:
    print u"""<node id="%s" label="%s" />""" % (node, data['nodes'][node])
print u"""</nodes>"""

print u"""<edges>"""
c = 1
for edge in data['edges']:
    print u"""<edge id="%s" source="%s" target="%s"/>""" % (c, edge['source'], edge['target'])
    c += 1
print u"""</edges>
    </graph>
</gexf>
"""

