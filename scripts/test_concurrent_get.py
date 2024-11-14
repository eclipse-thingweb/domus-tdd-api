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

import concurrent.futures
import requests

# Set up some global variables
urls = [
    # 	'http://127.0.0.1:5050/things?format=array&offset=0&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=1&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=2&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=3&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=4&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=5&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=6&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=7&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=8&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=9&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=10&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=11&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=12&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=13&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=14&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=15&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=16&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=17&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=18&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=19&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=20&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=21&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=22&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=23&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=24&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=25&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=26&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=27&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=28&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=29&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=30&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=31&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=32&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=33&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=34&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=35&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=36&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=37&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=38&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=39&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=40&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=41&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=42&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=43&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=44&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=45&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=46&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=47&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=48&limit=1',
    # 	'http://127.0.0.1:5050/things?format=array&offset=49&limit=1',
    "http://127.0.0.1:5050/things?format=array&offset=50&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=51&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=52&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=53&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=54&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=55&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=56&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=57&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=58&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=59&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=60&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=61&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=62&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=63&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=64&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=65&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=66&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=67&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=68&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=69&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=70&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=71&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=72&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=73&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=74&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=75&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=76&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=77&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=78&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=79&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=80&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=81&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=82&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=83&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=84&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=85&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=86&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=87&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=88&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=89&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=90&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=91&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=92&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=93&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=94&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=95&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=96&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=97&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=98&limit=1",
    "http://127.0.0.1:5050/things?format=array&offset=99&limit=1",
]
results = []


# Define a function that will be called by the executor to send the request
def send_request(url):
    response = requests.get(url)
    results.append(response.text)


# Use the concurrent.futures.ThreadPoolExecutor to send the requests in parallel
with concurrent.futures.ThreadPoolExecutor() as executor:
    for url in urls:
        executor.submit(send_request, url)

# Print the results of the requests
# for result in results:
#    print(result)
