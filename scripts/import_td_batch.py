"python import_td_batch.py [dirname|filename] [wot_api_url]"
import json
import os
import sys
import httpx


client = httpx.Client(timeout=60.0)


def upload_tds(tds):
    # create TD Collection
    collection = {
        "@context": "https://w3c.github.io/wot-discovery/context/discovery-context.jsonld",
        "@type": "ThingCollection",
        "members": tds,
    }

    # put on wot api
    resp = client.put(sys.argv[2] + "/import-collection", data=json.dumps(collection))
    print("PUT answer : ", resp, resp.json())


# get all tds from folders
tds_filepaths = []

if os.path.isdir(sys.argv[1]):
    for root, dirs, files in os.walk(sys.argv[1]):
        for filename in files:
            if filename.endswith("td.jsonld"):
                filepath = os.path.join(root, filename)
                tds_filepaths.append(filepath)
elif os.path.isfile(sys.argv[1]):
    tds_filepaths.append(sys.argv[1])
else:
    print(f"{sys.argv[1]} not found")
    print(__doc__)
    sys.exit(1)

tds = []
for filepath in tds_filepaths:
    with open(filepath) as fp:
        tds.append(json.loads(fp.read()))
    if len(tds) >= 200:
        upload_tds(tds)
        tds = []
upload_tds(tds)
