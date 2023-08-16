"python import_snapshot.py [filename] [import_route_url]"
import json
import os
import sys
import httpx


client = httpx.Client(timeout=60.0)


def upload_submodels(filepath):
    print(f"Uploading {filepath} ... ", end="")
    with open(filepath) as fp:
        submodels = json.loads(fp.read())
        for submodel in submodels:
            submodel["semanticId"]["type"] = "ExternalReference"
            r = client.post(
                sys.argv[2],
                data=json.dumps(submodel),
                headers={"Content-Type": "application/json"},
            )
            if r.status_code in [200, 201, 204]:
                print(f"ok (id: {r.headers.get('Location', 'no id')})")
            else:
                id = submodel["id"]
                print(f"ERROR ({id}) --- {r.text}")
                errors.append(f"{id} - {r.text}")


errors = []

if os.path.isfile(sys.argv[1]):
    upload_submodels(sys.argv[1])
else:
    print(f"{sys.argv[1]} not found")
    print(__doc__)
    sys.exit(1)
if len(errors) > 0:
    print("Errors: ")
    for error in errors:
        print(error)
