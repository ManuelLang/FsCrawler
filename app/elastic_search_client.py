import json
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

client = Elasticsearch("http://localhost:9200/", api_key="")

doc = {
    "author": "kimchy",
    "text": "Elasticsearch: cool. bonsai cool.",
    "timestamp": datetime.now(),
}
resp = client.index(index="test-index", id=1, document=doc)
print(resp["result"])

resp = client.get(index="test-index", id=1)
print(resp["_source"])

client.indices.refresh(index="test-index")

for index_name in ["test-index", "products"]:
    resp = client.search(index=index_name, query={"match_all": {}})
    print("Got {} hits:".format(resp["hits"]["total"]["value"]))
    for hit in resp["hits"]["hits"]:
        item = hit["_source"]
        print(json.dumps(item, indent=4))
        # print("{timestamp} {author} {text}".format(**hit["_source"]))

id: int
objectType: str

s = Search(index="my-index") \
    .filter("term", category="search") \
    .query("match", title="python")   \
    .exclude("match", description="beta")
for hit in s:
    print(hit.title)