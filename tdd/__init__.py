import sys
import time
from flask import Flask, request, Response, stream_with_context
import json
import json_merge_patch
import httpx
import toml

from tdd.errors import (
    AppException,
    JSONDecodeError,
    JSONSchemaError,
    IDNotFound,
    WrongMimeType,
)
from tdd.td import (
    get_all_tds,
    get_paginated_tds,
    get_total_number,
    put_td_rdf_in_sparql,
    put_td_json_in_sparql,
    validate_td,
    validate_td_json_schema,
    get_td_description,
)
from tdd.common import (
    delete_id,
)
from tdd.sparql import query, sparql_query
from tdd.utils import (
    POSSIBLE_MIMETYPES,
    create_link_params,
    negociate_mime_type,
    get_collection_etag,
    update_collection_etag,
)
from tdd.config import CONFIG


LIMIT_SPARQLENDPOINT_TEST = 10


def wait_for_sparqlendpoint():
    test_num = 0
    while test_num < LIMIT_SPARQLENDPOINT_TEST:
        try:
            resp = query("SELECT * WHERE {?a ?b ?c} LIMIT 1")
            if resp.status_code == 200:
                return True
        except httpx.NetworkError:
            pass
        print(
            f"{LIMIT_SPARQLENDPOINT_TEST - test_num} - Waiting for the SPARQL endpoint"
            f" ({CONFIG['SPARQLENDPOINT_URL']})"
        )
        time.sleep(1)
        test_num += 1
    print("The SPARQL endpoint seems unavailable. TDD API cannot be used")
    sys.exit(1)


def create_app():
    app = Flask(__name__)
    app.config.from_file("../config.toml", load=toml.load)
    wait_for_sparqlendpoint()
    register_error_handler(app)
    register_routes(app)
    return app


def register_error_handler(app):
    @app.errorhandler(AppException)
    def error_response(e):
        lang = request.lang
        return Response(
            json.dumps(e.to_dict(lang)),
            content_type="application/problem+json",
            status=e.status_code,
        )


def register_routes(app):
    @app.before_request
    def before_request():
        lang = request.accept_languages.best_match(["en", "fr", "de"])
        request.lang = lang

    # TODO code below should run as "daemon" and not here since it is time-costly
    # def clear_expired_tds_request():
    #    clear_expired_td()

    @app.after_request
    def add_cors_headers(response):
        response.headers.add("Access-Control-Allow-Origin", "localhost")
        response.headers.add("Access-Control-Allow-Headers", "Authorization")
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE"
        )
        return response

    def get_check_schema_from_url_params(request):
        check_schema_param = request.args.get("check-schema")
        check_schema = CONFIG["CHECK_SCHEMA"]
        if check_schema_param in ["false", "False", "0"]:
            check_schema = False
        return check_schema

    @app.route("/", methods=["GET"])
    def directory_description():
        with open("tdd/data/tdd-description.json", "r") as f:
            tdd_description = json.loads(f.read())
            tdd_description["base"] = CONFIG["TD_REPO_URL"]
            return Response(
                json.dumps(tdd_description), content_type="application/td+json"
            )

    # ********** WoT Routes **********
    @app.route("/things/<id>", methods=["PUT"])
    def create_td(id):
        mimetype = request.content_type
        check_schema = get_check_schema_from_url_params(request)
        if mimetype == "application/json":
            mimetype = "application/td+json"
        if mimetype == "application/td+json":
            json_ld_content = request.get_data()
            td_content = validate_td(json_ld_content, id=id, check_schema=check_schema)
            updated, uri = put_td_json_in_sparql(td_content)
        elif mimetype in POSSIBLE_MIMETYPES:
            td_content = request.get_data()
            updated, uri = put_td_rdf_in_sparql(
                td_content, mimetype, check_schema=check_schema, uri=id
            )
        else:
            raise WrongMimeType(mimetype)
        update_collection_etag()
        return Response(status=201 if not updated else 204, headers={"Location": uri})

    @app.route("/things/<id>", methods=["PATCH"])
    def update_td(id):
        check_schema = get_check_schema_from_url_params(request)
        json_patch = request.get_data()
        try:
            json_patch = json.loads(json_patch)
        except json.decoder.JSONDecodeError as exc:
            raise JSONDecodeError(exc)
        td = get_td_description(id)
        if td is None:
            raise IDNotFound()
        td_updated = json_merge_patch.merge(td, json_patch)
        if check_schema:
            validated, errors = validate_td_json_schema(td_updated)
            if not validated:
                raise JSONSchemaError(errors, td_id=id)
        put_td_json_in_sparql(td_updated)
        update_collection_etag()
        return Response(status=204)

    @app.route("/things", methods=["POST"])
    def create_anonymous_td():
        mimetype = request.content_type
        check_schema = get_check_schema_from_url_params(request)
        if mimetype == "application/json":
            mimetype = "application/td+json"
        if mimetype == "application/td+json":
            json_ld_content = request.get_data()
            td_content = validate_td(json_ld_content, check_schema=check_schema)
            updated, uri = put_td_json_in_sparql(td_content, delete_if_exists=False)
        elif mimetype in POSSIBLE_MIMETYPES:
            td_content = request.get_data()
            updated, uri = put_td_rdf_in_sparql(
                td_content, mimetype, delete_if_exists=False, check_schema=check_schema
            )
        else:  # wrong mimetype
            raise WrongMimeType(mimetype)
        update_collection_etag()
        return Response(status=201 if not updated else 204, headers={"Location": uri})

    @app.route("/things/<id>", methods=["DELETE"])
    def delete_route_td(id):
        response = delete_id(id)
        if response.status_code in [200, 204]:
            update_collection_etag()
        return response

    @app.route("/things", methods=["GET"])
    def describe_tds():
        format = request.args.get("format", "array")

        sort_by = request.args.get("sort_by")
        sort_order = request.args.get("sort_order")

        number_total = get_total_number()

        sort_params = {}
        if sort_order:
            sort_params["sort_order"] = sort_order
        if sort_by:
            sort_params["sort_by"] = sort_by

        if format == "array":
            offset = request.args.get("offset", 0)
            limit = request.args.get("limit")
            if limit is not None:  # if a limit is given, the result is not chunked
                limit = int(limit)
                offset = int(offset)
                tds = get_paginated_tds(limit, offset, sort_by, sort_order)
                next_offset = offset + limit
                response = Response(json.dumps(tds), content_type="application/ld+json")
                link = f'</things>; rel="canonical"; etag="{get_collection_etag()}"'

                if next_offset < number_total:
                    next_link_params = {
                        "offset": next_offset,
                        "limit": limit,
                        **sort_params,
                    }
                    link += (
                        f',</things?{create_link_params(next_link_params)}>; rel="next"'
                    )

                response.headers["Link"] = link
                return response

            def generate():
                all_tds = get_all_tds(sort_by, sort_order)
                # all_tds = get_paginated_tds(number_total, 0)
                first_td = next(all_tds, None)
                if first_td is None:
                    yield "[]"
                    return
                yield f"[{json.dumps(first_td)}"
                for td in all_tds:
                    yield f",\n {json.dumps(td)}"
                yield "]"

            response = Response(
                stream_with_context(generate()), content_type="application/ld+json"
            )
            response.headers[
                "Link"
            ] = f'</things>; rel="canonical"; etag="{get_collection_etag()}"'
            return response

        elif format == "collection":
            params = {
                "offset": int(request.args.get("offset", 0)),
                "limit": int(request.args.get("limit", CONFIG["LIMIT_BATCH_TDS"])),
                **sort_params,
            }

            all_tds = get_paginated_tds(
                params["limit"], params["offset"], sort_by, sort_order
            )

            response = {
                "@context": "https://w3c.github.io/wot-discovery/context/discovery-context.jsonld",
                "@type": "ThingCollection",
                "total": number_total,
                "members": all_tds,
                "@id": f"/things?{create_link_params(params)}&format=collection",
                "etag": get_collection_etag(),
            }

            next_offset = params["offset"] + params["limit"]
            if next_offset < number_total:
                new_params = {**params, "offset": next_offset}
                response[
                    "next"
                ] = f"/things?{create_link_params(new_params)}&format=collection"
            response = Response(
                json.dumps(response), content_type="application/ld+json"
            )
            response.headers["Link"] = (
                '</things?format=collection>; rel="canonical";'
                f' etag="{get_collection_etag()}"'
            )
            return response

    @app.route("/things/<id>", methods=["GET"])
    def describe_td(id):
        mime_type_negociated = negociate_mime_type(
            request, default_mimetype="application/td+json"
        )
        description = get_td_description(id, mime_type_negociated)
        if mime_type_negociated == "application/td+json":
            description = json.dumps(description)
        return Response(description, content_type=mime_type_negociated)

    @app.route("/search/sparql", methods=["GET"])
    def query_sparql():
        query = request.args.get("query", "")
        return sparql_query(query)

    @app.route("/search/sparql", methods=["POST"])
    def query_sparql_post():
        query = request.get_data().decode("utf-8")
        return sparql_query(query)
