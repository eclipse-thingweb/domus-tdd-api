# Ontotext GraphDB

## Installation

### Install locally

You can follow the documentation provided by Ontotext to install GraphDB.
https://graphdb.ontotext.com/documentation/10.0/quick-start-guide.html

Download from https://www.ontotext.com/products/graphdb/download/

However, at the time of redaction of this documentation, the download page of GraphDB is empty.

### Docker image

Follow these steps in docker https://github.com/Ontotext-AD/graphdb-docker

## Endpoint Configuration

Once your GraphDB is running, you can go to http://localhost:7200

1. Create a repository by selecting "Setup > Repositories" in the menu and clicking on the "Create new repository" button

2. Choose GraphDB Repository

3. Give a name to your repository and select your preferred options for the repository: the default values are fine, but you may not need indexation at all nor inferrence. The repository must _not_ be read-only.

## Specificities

GraphDB has two distinct URLs for the SPARQL API:

- `http://localhost:7200/repositories/<YOUR-REPO-NAME>` for SPARQL SELECT/CONSTRUCT queries
- `http://localhost:7200/repositories/<YOUR-REPO-NAME>/statements` for SPARQL UPDATE queries

For this reason, we have to configure TDD-API.
Set the`ENDPOINT_TYPE` configuration variable to `GRAPHDB` (see how to do so in the main [README](../../README.md)).

The expected URL for the `SPARQLENDPOINT_URL` configuration variable is `http://localhost:7200/repositories/<YOUR-REPO-NAME>`.
