# Configuring SparTDD for different SPARQL endpoints

## General requirements

You can either use a distant SPARQL server or use a SPARQL server locally.

The SPARQL endpoint you configure must:

- Allow SPARQL UPDATE queries
- Allow named graphs
- Be configured in the manner that the default graph is the union of the named graphs
- Allow CORS

## Using Apache Jena Fuseki

Apache Jena Fuseki is the SPARQL endpoint shipped in the docker-compose file.
You can also set it locally.
We provide you with a default configuration so that it meets the general
requirements for a SPARQL endpoint.

Read about how to configure and launch your local Fuseki in [fuseki.md](fuseki.md)

## Using Virtuoso

You can use Virtuoso as a SPARQL endpoint by providing the right permissions
and configuring SparTDD.

Read about how to configure and launch your local Virtuoso in [virtuoso.md](virtuoso.md)

## Using GraphDB
