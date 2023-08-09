# -*- coding: utf-8 -*-


# standard library imports
import asyncio
import posixpath

# third party imports
import httpx

# library specific imports


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
