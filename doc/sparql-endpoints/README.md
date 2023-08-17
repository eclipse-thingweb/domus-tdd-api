# Configuring SparTDD for different SPARQL endpoints

## General requirements

You can either use a distant SPARQL server or use a SPARQL server locally.

The SPARQL endpoint you configure must:

- Allow SPARQL UPDATE queries
- Allow named graphs
- Be configured in the manner that the default graph is the union of the named graphs
- Allow CORS

## Using Apache Jena Fuseki

We propose to use Apache Jena Fuseki, which has a nice administration interface.
Download the Fuseki projet (apache-jena-fuseki-X.Y.Z.zip) from
https://jena.apache.org/download/index.cgi

Then unzip the downloaded archive.
To launch the server, in the apache-jena-fuseki-X.Y.Z folder, run

```
./fuseki-server
```

The server will run on http://localhost:3030.
If you want to create the dataset with the right configuration, you can copy-paste
`fuseki-docker/configuration/things.ttl` into `apache-jena-fuseki-X.Y.Z/run/configuration`

```
cp fuseki-docker/configuration/things.ttl path/to/apache-jena-fuseki-X.Y.Z/run/configuration
```

More documentation on Fuseki in this project is available in [fuseki.md](fuseki.md)
(for further configuration or docker configuration).

## Using Virtuoso

More documentation on Fuseki in this project is available in [virtuoso.md](virtuoso.md)

## Using GraphDb
