"python check_framing.py [filename] [proxyapi_describe_url]"
import os
import sys
import httpx
import json

from jsoncomparison import Compare

TD_PATH = sys.argv[1]
DESCRIBE_ROUTE = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:5000/describe"


def check_snapshot_framing(filepath, describe_route):
    print(f"Checking {filepath} ... ")
    with open(filepath) as fp:
        ld_content = json.loads(fp.read())
        context = ld_content["@context"]
        tds = ld_content["member"]
        for td in tds:
            td["@context"] = context
            describe_and_diff_jsonld(td, describe_route)


def check_framing(filepath, describe_route):
    print(f"Checking {filepath} ... ")
    with open(filepath) as fp:
        td = json.loads(fp.read())
        describe_and_diff_jsonld(td, describe_route)


def describe_and_diff_jsonld(source, describe_route):
    td_id = source["id"]
    resp = httpx.get(describe_route, params={"uri": td_id})
    target = resp.json()
    print(f"FETCHED TD ----- {td_id}")
    print(f"IS THE SAME : {source == target}")

    diff = Compare().check(source, target)
    print(json.dumps(diff, indent=2))


if DESCRIBE_ROUTE is None:
    print("proxyapi_url describe route must be defined")
    print(__doc__)
    sys.exit(1)


if os.path.isfile(TD_PATH):
    if os.path.basename(TD_PATH).startswith("snapshot"):
        check_snapshot_framing(TD_PATH, DESCRIBE_ROUTE)
    else:
        check_framing(TD_PATH, DESCRIBE_ROUTE)
else:
    print(f"{TD_PATH} not found")
    print(__doc__)
    sys.exit(1)
