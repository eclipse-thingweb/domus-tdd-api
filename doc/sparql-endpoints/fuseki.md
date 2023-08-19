# Apache Jena Fuseki

We propose to use Apache Jena Fuseki, which has a nice administration interface.
Download the Fuseki project (apache-jena-fuseki-X.Y.Z.zip) from
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

## Deployment

We rely on the [secoresearch/fuseki](https://hub.docker.com/r/secoresearch/fuseki/)
docker image to deploy the fuseki.

As there is a bug in Fuseki 4.0 where URNs with UUIDs raise an exception
(see [a related issue](https://issues.apache.org/jira/browse/JENA-2097)).
This bug will be fixed in version 4.1 according to the issue.

For now, the version 3.17 (latest version before the 4.0) is used.

The port of the image is 3030.

## Fuseki docker image environment variables

We have set the following variables for the fuseki docker image :

- **ENABLE_UPLOAD**: "true" -- to allow file upload (needed to import all triples)
- **ASSEMBLER**: "/fuseki-base/configuration/things.ttl" -- this file, which in
  this repository in under `fuseki-docker/configuration/things.ttl` will create
  a `things` service with a TDB dataset in the fuseki endpoint at launch time.
- **ADMIN_PASSWORD**: _your desired password_

We have set three shared volumes on the image:

- **/fuseki-base/configuration** folder where the configurations of the services
  are read and stored by the fuseki endpoint
- **/fuseki-base/databases** folder where the TDB files (persistent RDF databases)
  are read and stored by the fuseki endpoint
- **/fuseki-base/config.ttl** the configuration file for the whole endpoint. This
  file will only be read by the fuseki server as no modification of this file
  is possible at runtime.

## Fuseki Service Configuration

We propose a default configuration for a `/things` service on the fuseki sparql
endpoint. This configuration file is in `fuseki-docker/configuration/things.ttl`.

Two points are important in this configuration:

- The dataset must be persistent (TDB or TDB2) so that the data is not lost on restart
- The default graph must be the union of all graphs (`unionDefaultGraph` option)
  so that all named graphs can be queried without adding a GRAPH keyword everywhere.

For a TDB Dataset :

```
<#service> rdf:type fuseki:Service ;
    ...
    fuseki:dataset           <#dataset> .

<#dataset> rdf:type tdb:DatasetTDB ;
    tdb:location "/location/of/TDB/files" ;
    tdb:unionDefaultGraph true ;

```

For a TDB2 Dataset :

```
<#service> rdf:type fuseki:Service ;
    ...
    fuseki:dataset           <#dataset> .

<#dataset> rdf:type tdb2:DatasetTDB2 ;
    tdb2:location "/location/of/TDB2/files" ;
    tdb2:unionDefaultGraph true ;

```
