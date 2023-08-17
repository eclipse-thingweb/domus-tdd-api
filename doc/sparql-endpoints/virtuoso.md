## Notes on Virtuoso - TODO Change to a general section about tested Triplestores (Jena, GraphDB, Virtuoso and include this as a subsection)

https://vos.openlinksw.com/owiki/wiki/VOS

`/Applications/Virtuoso Open Source Edition v7.2.app/Contents/virtuoso-opensource/bin` -> `./virtuoso-t +foreground +configfile ../database/virtuoso.ini`

`/Applications/Virtuoso\ Open\ Source\ Edition\ v7.2.app/Contents/virtuoso-opensource/bin/isql localhost:1111 -U dba -P dba`

```
GRANT EXECUTE ON DB.DBA.SPARQL_INSERT_DICT_CONTENT TO "SPARQL";
GRANT EXECUTE ON DB.DBA.SPARQL_DELETE_DICT_CONTENT TO "SPARQL";
DB.DBA.RDF_DEFAULT_USER_PERMS_SET ('nobody', 7);
GRANT EXECUTE ON DB.DBA.SPARUL_RUN TO "SPARQL";
GRANT EXECUTE ON DB.DBA.SPARQL_INSERT_QUAD_DICT_CONTENT TO "SPARQL";
GRANT EXECUTE ON DB.DBA.L_O_LOOK TO "SPARQL";
GRANT EXECUTE ON DB.DBA.SPARUL_CLEAR TO "SPARQL";
GRANT EXECUTE ON DB.DBA.SPARUL_DROP TO "SPARQL";
GRANT EXECUTE ON DB.DBA.SPARQL_UPDATE TO "SPARQL";
```

http://127.0.0.1:8890/sparql  
http://127.0.0.1:8890/conductor

| User Name | Default Password | Usage                                                                                                       |
| :-------- | :--------------- | :---------------------------------------------------------------------------------------------------------- |
| dba       | dba              | Default Database Administrator account.                                                                     |
| dav       | dav              | WebDAV Administrator account.                                                                               |
| vad       | vad              | WebDAV account for internal usage in VAD (disabled by default).                                             |
| demo      | demo             | Default demo user for the demo database. This user is the owner of the Demo catalogue of the demo database. |
| soap      | soap             | SQL User for demonstrating SOAP services.                                                                   |
| fori      | fori             | SQL user account for 'Forums' tutorial application demonstration in the Demo database.                      |

Problem: Virtuoso 37000 Error SP031: SPARQL compiler: Blank node '\_:b0' is not allowed in a constant clause  
https://github.com/openlink/virtuoso-opensource/issues/126

Go to the Virtuoso administration UI, i.e., http://host:port/conductor

- Log in as user dba
- Go to System Admin → User Accounts → Users
- Click the Edit link
- Set User type to SQL/ODBC Logins and WebDAV
- From the list of available Account Roles, select SPARQL_UPDATE and click the >> button to add it to the right-hand list
- Click the Save button
