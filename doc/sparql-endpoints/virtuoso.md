# OpenLink Software Virtuoso

Dowload the latest version https://vos.openlinksw.com/owiki/wiki/VOS

Unzip the archive.
Create a virtuoso.ini config file in the database folder.
For example, copy the virtuoso.ini.sample file.

```
cd virtuoso-opensource/database
cp virtuoso.ini.sample virtuoso.ini
```

Launch the virtuoso server

```
cd ../bin
./virtuoso-t +foreground +configfile ../database/virtuoso.ini
```

Check that you have access to :

- the SPARQL editor: http://127.0.0.1:8890/sparql
- the server administration: http://127.0.0.1:8890/conductor (see list of default users and passwords below)

Give the following permissions (in bin folder) while the server is
still running in another terminal.

```
./isql localhost:1111 -U dba -P dba
```

Once in the isql

```
GRANT "SPARQL_UPDATE" TO "SPARQL";
DB.DBA.RDF_DEFAULT_USER_PERMS_SET ('nobody', 7);
```

If you want to allow for SERVICE queries (querying other SPARQL endpoints), run:

```
GRANT SELECT ON DB.DBA.SPARQL_SINV_2 TO "SPARQL";
GRANT EXECUTE ON DB.DBA.SPARQL_SINV_IMP TO "SPARQL";
```

## Default users and password of Virtuoso

| User Name | Default Password | Usage                                                                                                       |
| :-------- | :--------------- | :---------------------------------------------------------------------------------------------------------- |
| dba       | dba              | Default Database Administrator account.                                                                     |
| dav       | dav              | WebDAV Administrator account.                                                                               |
| vad       | vad              | WebDAV account for internal usage in VAD (disabled by default).                                             |
| demo      | demo             | Default demo user for the demo database. This user is the owner of the Demo catalogue of the demo database. |
| soap      | soap             | SQL User for demonstrating SOAP services.                                                                   |
| fori      | fori             | SQL user account for 'Forums' tutorial application demonstration in the Demo database.                      |

## Problems so far

Problem: Virtuoso 37000 Error SP031: SPARQL compiler: Blank node '\_:b0' is not allowed in a constant clause
https://github.com/openlink/virtuoso-opensource/issues/126

This will be solved in Virtuoso V8, which is for now (2023) only available in commercial form.

In the mean time, we provide a workaround this issue.
To use the workaround, you need to set the `ENDPOINT_TYPE` configuration variable to `VIRTUOSO` (see how to do so in the main [README](../../README.md)).
