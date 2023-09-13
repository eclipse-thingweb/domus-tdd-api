# Configuring TDD API for different SPARQL endpoints

## General requirements

You can either use a remote SPARQL server or use a SPARQL server locally.

The SPARQL endpoint you configure must:

- Allow SPARQL UPDATE queries
- Allow named graphs
- Be configured in the manner that the default graph is the union of the named graphs
- Allow CORS

## Apache Jena Fuseki

Apache Jena Fuseki is the SPARQL endpoint shipped in the docker-compose file.
You can also set it locally.
We provide you with a default configuration so that it meets the general
requirements for a SPARQL endpoint.

Read about how to configure and launch your local Fuseki in [fuseki.md](fuseki.md)

## OpenLink Software Virtuoso

You can use Virtuoso as a SPARQL endpoint by providing the right permissions
and configuring the TDD API.

Read about how to configure and launch your local Virtuoso in [virtuoso.md](virtuoso.md)

## Ontotext GraphDB

You can use GraphDB as a SPARQL endpoint by configuring the TDD API.

Read about how to configure and launch your local GraphDB in [graphdb.md](graphdb.md)

## AWS Neptune Cloud Deployment

It is possible to deploy the TDD API on AWS using Lambda functions and Neptune (Serverless).

An overview about this can be found in the [AWS samples repository](https://aws-samples.github.io/aws-dbs-refarch-graph/src/accessing-from-aws-lambda/).

Besides avoiding several pitfalls and using the Serverless Framework, a special attention must be put on the communication between the core (deployed as a Python Lambda) and `frame-jsonld.js` / `transform-to-nt.js` (deployed as JavaScript Lambdas).
