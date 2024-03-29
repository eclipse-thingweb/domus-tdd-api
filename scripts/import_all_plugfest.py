"""******************************************************************************
 * Copyright (c) 2018 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v. 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0, or the W3C Software Notice and
 * Document License (2015-05-13) which is available at
 * https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document.
 *
 * SPDX-License-Identifier: EPL-2.0 OR W3C-20150513
 ********************************************************************************"""

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
