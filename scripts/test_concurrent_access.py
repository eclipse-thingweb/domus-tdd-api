'''******************************************************************************
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
 ********************************************************************************'''


import asyncio
import posixpath
import httpx


async def request(session, method, url, headers=None, data=None):
    return await session.request(method, url, data=data, headers=headers)


async def send_concurrent_requests(requests):
    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(
            *[
                request(client, method, url, **params)
                for url, method, params in requests
            ]
        )
    for response in responses:
        print(f"{response.url}: {response.status_code} {response.reason_phrase}")
        print(f"... {response.read().decode()}")


if __name__ == "__main__":
    base_url = posixpath.join("http://127.0.0.1:5000", "things")
    with open("tests/data/smart-coffee-machine.td.jsonld") as fp:
        data = fp.read()
    requests = (
        (base_url, "GET", {}),
        (base_url, "POST", {"data": data}),
        (
            posixpath.join(base_url, "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"),
            "GET",
            {},
        ),
    )
    asyncio.run(send_concurrent_requests(requests))
