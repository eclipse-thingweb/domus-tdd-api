"python import_snapshots.py [filename] [import_route_url]"

import json
import os
import sys
import httpx
import concurrent.futures


client = httpx.Client(timeout=60.0)


def upload_snapshot(filepath):
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
            if r.status_code == 201:
                print(f"ok (id: {r.text})")
            else:
                print("error")
                print(f"ERROR --- {r.text}")
                errors.append(f"{td['id']} - {r.text}")


def upload_snapshots(filespath):
    for root, dirs, files in os.walk(filespath):
        for filename in files:
            # TDs to be extracted from snapshot
            if filename.endswith("json"):
                filepath = os.path.join(root, filename)
                print(
                    "---------------------------------------------------- "
                    + filepath
                    + " ----------------------------------------------------"
                )
                with open(filepath) as fp:
                    ld_content = json.loads(fp.read())
                    context = ld_content["@context"]
                    tds = ld_content["member"]
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        for td in tds:
                            executor.submit(send_request, td, context)
                    # for td in tds:
                    #    send_request(td, context)


def send_request(td, context):
    td["@context"] = context
    print(
        "---------------------------------------------------- "
        + sys.argv[2]
        + "/"
        + td["id"]
        + " ----------------------------------------------------"
    )
    r = client.put(
        sys.argv[2] + "/" + td["id"],
        data=json.dumps(td),
        headers={"Content-Type": "application/json"},
    )
    if r.status_code == 201:
        print(f"ok (id: {r.text})")
    else:
        print("error")
        print(f"ERROR --- {r.text}")
        errors.append(f"{td['id']} - {r.text}")


errors = []

if os.path.isfile(sys.argv[1]):
    upload_snapshot(sys.argv[1])
elif os.path.isdir(sys.argv[1]):
    upload_snapshots(sys.argv[1])
else:
    print(f"{sys.argv[1]} not found")
    print(__doc__)
    sys.exit(1)
if len(errors) > 0:
    print("Errors rapport :")
    for error in errors:
        print(error)
