"python import_all_plugfest.py [dirname|filename] [import_route_url]"
import os
import sys
import httpx


client = httpx.Client(timeout=60.0)


def upload_file(filepath):
    print(f"Uploading {filepath} ... ", end="")
    with open(filepath) as fp:
        data = fp.read()
        r = client.post(
            sys.argv[2], data=data, headers={"Content-Type": "application/json"}
        )

        if r.status_code in [200, 201, 204]:
            print(f"ok (id: {r.text})")
        else:
            print("error")
            print(f"ERROR --- {r.text}")
            errors.append(f"{filepath} - {r.text}")


errors = []
if os.path.isdir(sys.argv[1]):
    for root, dirs, files in os.walk(sys.argv[1]):
        for filename in files:
            if filename.endswith("td.jsonld"):
                filepath = os.path.join(root, filename)
                upload_file(filepath)
elif os.path.isfile(sys.argv[1]):
    upload_file(sys.argv[1])
else:
    print(f"{sys.argv[1]} not found")
    print(__doc__)
    sys.exit(1)
if len(errors) > 0:
    print("Errors rapport :")
    for error in errors:
        print(error)
