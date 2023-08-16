import json
from jsoncomparison import Compare
from rdflib import Graph

from tests.conftest import (
    DATA_PATH,
    assert_only_on_known_errors,
)


def test_tdd_route(test_client):
    tdd_response = test_client.get("/")
    assert tdd_response.status_code == 200
    assert tdd_response.content_type == "application/td+json"
    with open(DATA_PATH / "tdd-description.json") as fp:
        assert tdd_response.json == json.load(fp)


def test_GET_thing_OK(test_client, mock_sparql_with_one_td):
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    with open(DATA_PATH / "smart-coffee-machine.ld.json") as fp:
        already_present_td = json.load(fp)
    get_response = test_client.get(f"/things/{td_id}")
    assert get_response.status_code == 200
    td = get_response.json
    td["registration"] = already_present_td[
        "registration"
    ]  # use the proper registration since this test does not test this
    diff = Compare().check(already_present_td, td)
    assert_only_on_known_errors(diff)


def test_GET_thing_content_negociation(test_client, mock_sparql_with_one_td):
    td_id = "urn:uuid:55f01138-5c96-4b3d-a5d0-81319a2db677"
    for mime_type, file_extension in [
        ("text/turtle", "ttl"),
        ("application/rdf+xml", "xml"),
        ("text/n3", "n3"),
        ("application/ld+json", "ld.json"),
    ]:
        with open(DATA_PATH / f"smart-coffee-machine.{file_extension}") as fp:
            already_present_td = fp.read()
        get_response = test_client.get(
            f"/things/{td_id}", headers={"Accept": mime_type}
        )
        assert get_response.status_code == 200
        td = get_response.get_data()
        g_expected = Graph()
        g_expected.parse(data=already_present_td, format=mime_type)
        g = Graph()
        g.parse(data=td, format=mime_type)
        g == g_expected
