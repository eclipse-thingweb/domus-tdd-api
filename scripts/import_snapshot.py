"python import_snapshot.py [filename] [import_route_url]"
import json
import os
import sys
import httpx


client = httpx.Client(timeout=60.0)


def upload_snapshots(filepath):
    print(f"Uploading {filepath} ... ", end="")
    with open(filepath) as fp:
        ld_content = json.loads(fp.read())
        context = ld_content["@context"]
        tds = ld_content["member"]
        for td in tds:
            td["@context"] = context
            r = client.post(
                sys.argv[2],
                data=json.dumps(td),
                headers={"Content-Type": "application/json"},
            )
            if r.status_code in [200, 201, 204]:
                print(f"ok (id: {r.headers.get('Location', 'no id')})")
            else:
                id = td.get("id", "no id")
                print(f"ERROR ({id}) --- {r.text}")
                errors.append(f"{id} - {r.text}")


errors = []

if os.path.isfile(sys.argv[1]):
    upload_snapshots(sys.argv[1])
else:
    print(f"{sys.argv[1]} not found")
    print(__doc__)
    sys.exit(1)
if len(errors) > 0:
    print("Errors rapport :")
    for error in errors:
        print(error)
