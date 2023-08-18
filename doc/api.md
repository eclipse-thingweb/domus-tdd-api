# API Documentation

## Testing script

We created a small script to import a TD or a folder of TDs `scripts/import_all_plugfest.py`.
This script takes two arguments:

- the path towards the TD file or TD folder
- the tdd-api import route (e.g., http://localhost:5000/things)

```
python scripts/import_all_plugfest.py /path/to/TD http://localhost:5000/things
```

Note: when importing a folder of TDs, only the files with the `.td.json` extension
will be uploaded.

## API Routes

The routes follow the description in `tdd/data/tdd-description.json`.
It implements the [WoT-Discovery Exploration Mechanisms](https://w3c.github.io/wot-discovery/#exploration-mech).

Its compliance has been tested in PlugFest/TestFest events.
The results are listed here:

- 2022.03: https://github.com/w3c/wot-testing/blob/main/events/2022.03.Online/Discovery/Results/logilabtdd.csv
- 2022.06: https://github.com/w3c/wot-testing/tree/main/events/2022.06.Online/Discovery/Inputs/siemens-logilab
- 2022.07: https://github.com/w3c/wot-testing/tree/main/events/2022.07.Online/TD/siemens-logilab
- final 2022: https://github.com/w3c/wot-testing/tree/main/data/input_2022/Discovery/siemens-logilab

## Routes and schemas

The list of routes and how they were implemented can be viewed in [routes-diagrams.odg](routes-diagrams.odg).

Some schemas to describe how the JSON and RDF are dealt with in the TDD API
can be found in [schemas.odg](schemas.odg).
