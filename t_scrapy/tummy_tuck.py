from py2neo import Graph, Node, Relationship
import json

f = open('tt2.json', 'r')
jj = json.loads(f.read())
f.close()


graph = Graph('http://neo4j:tummy@localhost:7474/db/data')

for post in jj:
    poster = graph.merge_one("User", "id", post['poster'])
    neoPost = graph.merge_one("Post", "id", post['id'])
    posted = graph.create_unique(Relationship(poster, "POSTED", neoPost))
    print "(%s)-[:POSTED]->(%s)" % (post['poster'], post['id'])

    if post.get('reblogged_from'):
        reblogger = graph.merge_one("User", "id", post['reblogged_from'])
        reblogged_post = graph.merge_one("Post", "id", post['reblog_post_id'])
        graph.create_unique(Relationship(reblogger, "POSTED", reblogged_post))
        graph.create_unique(Relationship(neoPost, "REBLOG_OF", reblogged_post))
        print "(%s)-[:POSTED]->(%s)" % (post['reblogged_from'], post['reblog_post_id'])

    if post.get('original_poster'):
        original_poster = graph.merge_one("User", "id", post['original_poster'])
        original_post = graph.merge_one("Post", "id", post['original_post_id'])
        graph.create_unique(Relationship(original_poster, "POSTED", original_post))
        graph.create_unique(Relationship(neoPost, "ORIGINATES_FROM", original_post))
        print "(%s)-[:POSTED]->(%s)" % (post['original_poster'], post['original_post_id'])
