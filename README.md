# Openpoiservice 

[![Tests](https://github.com/GIScience/openpoiservice/workflows/run%20tests/badge.svg)](https://github.com/GIScience/openpoiservice/actions?query=workflow%3A%22run+tests%22)

Openpoiservice (ops) is a flask application which hosts a highly customizable points of interest database derived from 
OpenStreetMap.org data and thereby **exploits** its notion of tags...

> OpenStreetMap [tags](https://wiki.openstreetmap.org/wiki/Tags) consisting of a key and value describe specific features of 
> map elements (nodes, ways, or relations) or changesets.  Both items are free format text fields, but often represent numeric 
> or other structured items. 

This service consumes OSM tags on nodes, ways and relations by grouping them into predefined categories. 
If it picks up an OSM object tagged with one of the osm keys defined in `categories.yml` it will import this 
point of interest with specific additional tags which may be defined in `ops_settings.yml`. Any additional tag, 
for instance `wheelchair` or `smoking` may then be used to query the service via the API after import.

For instance, if you want to request all pois accessible by wheelchair within a geometry, you could add then add 
`wheelchair: ['yes', 'dedicated]` in `filters` within the body of your HTTP POST request. 

You may pass 3 different types of geometry within the request to the database. Currently, "Point" and "LineString" with
a corresponding and buffer are supported as well as a polygon. Points of interest will be returned within the given geometry.

You can control the maximum size of geometries and further restrictions in the settings file of this service.

#### Import Process 

The osm file(s) to be imported are parsed several times to extract points of interest from relations (osm_type 3), 
ways (osm_type 2) and nodes (osm_type 1) in order. Which type the specific point of interest originated from will be 
returned within the response - this will help you find the object directly on [OpenStreetMap.org](https://www.openstreetmap.org). 

## Installation

You can either run **openpoiservice** on your host machine in a virtual environment or simply with Docker. The Dockerfile 
provided installs a WSGI server (gunicorn) which starts the flask service on port 5000.


### Technical specs for storing and importing OSM files

##### Python version

As this service makes use of the python collections library, in particular the notion of deque's and its functions
it only supports python 3.5 and greater.

##### Database
This application uses a psql/postgis setup for storing the points of interest. We highly recommend [using this](https://github.com/kartoza/docker-postgis) 
docker container.

##### Importer
Please consider the following technical requirements for parsing & importing osm files.

| Region        | Memory        | 
| ------------- |:-------------:|
| Germany       | 8 GB         |
| Europe        | 32 GB         | 
| Planet        | 128 GB        | 

**Note:** Openpoiservice will import any osm pbf file located in the osm folder or subdirectory within. 
This way you can split the planet file into smaller regions (e.g. download from Geofabrik, scraper script for the download
links to be found in the osm folder) and use a *smaller* instance to import the global data set (as long as
the OSM files don't exceed 5 GB of disk space, 16 GB of memory will suffice to import the entire planet).

### Run as Docker Container (Flask + Gunicorn)

Make your necessary changes to the settings in the file `ops_settings_docker.yml` and to categories if you need inside `categories_docker.yml`. These files are mounted as volumes to the docker container.
If you are planning to import a different osm file, please download it to the `osm folder` (any folder within will be scanned
for osm files) as this will be a shared volume. 

### Docker Compose

#### All-in-one docker image

This docker-compose will allow you to run openpoiservice with `psql/postgis` image. This will allow you to deploy this project fast.

**Important :** The database is not exposed, you won't be able to access it from outside the container. If you want to acces it simply adds those lines to the database definition inside the `docker-compose-with-postgis.yml` (most propably `docker-compose.yml`?):

```sh
ports:
   - <PORT YOU WANT>:5432
```

Don't forget to change the host name and port inside `ops_settings_docker.yml` by the one given to docker container for database.

* Hostname default value : `psql_postgis_db`
* Port default value : `5432`


**Notes :** If openpoiservice can't connect to the database, it's probably because you don't have the same settings inside `ops_settings_docker.yml` and `docker-compose.yml` (see above).

Command to use to run all-in-one docker container

```sh
docker-compose -f /path/to/docker-compose.yml up api -d
docker-compose -f /path/to/docker-compose.yml up -d api  # at least on Win 10
```

#### Only deploy openpoiservice

This will only run openpoiservice inside a container, meaning that you will need to handle the database yourself and connect it to this container.

```sh
docker-compose -f /path/to/docker-compose-standalone.yml up -d api # see above
```

#### After deploy

Once the container is built you can either, create the empty database:

```sh
$ docker exec -it container_name /ops_venv/bin/python manage.py create-db #???
>  docker exec -it container_name /usr/local/bin/python manage.py create-db 
```

Delete the database:

```sh
$ docker exec -it container_name /usr/local/bin/python manage.py drop-db
```

Or import the OSM data:

```sh
$ docker exec -it container_name /usr/local/bin/python manage.py import-data
```

All OSM data in directory "osm" will be imported - new files can be downloaded from "https://download.geofabrik.de/" by using
the add-map command, e.g. (given that "container_name" is the default "ops-api"):
```sh
$ docker exec -it ops-api /usr/local/bin/python manage.py add-map "europe/germany/nordrhein-westfalen" 
```
to download NRW or

```sh
$ docker exec -it ops-api /usr/local/bin/python manage.py add-map "europe/germany/nordrhein-westfalen/koeln-regbez"
```
to download only Köln. 


### Init and Update DB with docker
You can initialize POI database with docker service init

```sh
docker-compose -f /path/to/docker-compose.yml up init
```

Or updating POI database
```sh
docker-compose -f /path/to/docker-compose.yml up update
```


### Protocol Buffers (protobuf) for imposm.parser 

This repository uses [imposm.parser](https://imposm.org/docs/imposm.parser/latest/index.html) to parse the 
OpenStreetMap pbf files which uses `google's protobuf library` under its hood.

**The imposm.parser requirement will not build with pip unless you are running [protobuf 3.0.0](https://github.com/protocolbuffers/protobuf/releases/tag/v3.0.0).** 

To this end, please make sure that you are running the aforementioned version of protobuf if `pip install -r requirements.txt` fails (install protobuf [from source](https://github.com/google/protobuf/blob/master/src/README.md)) 

### Prepare settings.yml

Update `openpoiservice/server/ops_settings.yml` with your necessary settings and then run one of the following
commands.

[
```sh
$ export APP_SETTINGS="openpoiservice.server.config.ProductionConfig|DevelopmentConfig"
```
]


### Create the POI DB

```sh
$ python manage.py create-db
```
### Drop the POI DB

```sh
$ python manage.py drop-db
```

### Download OSM data

```sh
python manage.py add-map "europe/germany/nordrhein-westfalen" 
```
to download a region like NRW or

```sh
python manage.py add-map "europe/germany/nordrhein-westfalen/koeln-regbez"
```
to download a smaller part, in this case "Köln".

### Parse and import OSM data

```sh
$ python manage.py import-data
```

### Run the Application with Flask-Werkzeug

```sh
$ python manage.py run
```

Per default you can access the application at the address [http://localhost:5000/](http://localhost:5000/)

> Want to specify a different port?

> ```sh
> $ python manage.py run -h 0.0.0.0 -p 8080
> ```

### Tests

```sh
$ export TESTING="True" && python manage.py test
```


### Category IDs and their configuration

`openpoiservice/server/categories/categories.yml` is a list of (**note:** not all!) OpenStreetMap tags with arbitrary category IDs. (see [Hint for changing name or location of config files](#changing-the-name-or-location-of-config-files) for further information on how the path can be changed).
If you keep the structure as follows, you can manipulate this list as you wish.
 
 ```yaml
 transport:
    id: 580
    children:
        aeroway:
            aerodrome: 581        
            aeroport: 582 
            helipad: 598         
            heliport: 599 
        amenity:
            bicycle_parking: 583  
            
 sustenance:
    id: 560             
    children:
        amenity:
            bar: 561             
            bbq: 562   
 ...
 ```
 
 Openpoiservice uses this mapping while it imports pois from the OpenStreetMap data and assigns the custom category IDs
 accordingly.

`column_mappings` in `openpoiservice/server/ops_settings.yml` controls which OSM information will be considered in the database and also if 
these may be queried by the user via the API , e.g.
(see [Hint for changing name or location of config files](#changing-the-name-or-location-of-config-files) for further information on how the path can be changed).
```yaml
wheelchair:

smoking:

fees:
```

For instance means that the OpenStreetMap tag [wheelchair](https://wiki.openstreetmap.org/wiki/Key:wheelchair) will be considered
during import and save to the database. A user may then add a list of common values in the filters object `wheelchair: ['yes', 'dedicated', ...]` 
which correspond to the OSM common values of the tag itself, e.g. 
[https://wiki.openstreetmap.org/wiki/Key:wheelchair](https://wiki.openstreetmap.org/wiki/Key:wheelchair).

### Changing the name or location of config files
Default path for configuration is openpoiservice/server/categories for categories, openpoiservice/server for ops_settings

If you want to unify / change the location of your config or change the name of the categories - file or OPS-Settings, you can use the (optional) environment variables
```
export POISERVICE_CONFIG_BASEDIR=<(Absolute) Path to base directory your config is stored>. 
export POISERVICE_CONFIG_CATEGORIES=<Name or path (relative to folder basedir) of categories file>
export POISERVICE_CONFIG_OPS_SETTINGS=<Name or path (relative to folder basedir) of ops_settings file>
```

### API Documentation

The documentation for this flask service is provided via [flasgger](https://github.com/rochacbruno/flasgger) and can be
accessed via `http://localhost:5000/apidocs/`.

Generally you have three different request types `pois`, `stats` and
`list`.

Using `request=pois` in the POST body will return a GeoJSON FeatureCollection
in your specified bounding box or geometry. 

Using `request=stats` will do the same but group by the categories, ultimately
returning a JSON object with the absolute numbers of pois of a certain group. 

Finally, `request=list` will return a JSON object generated from 
`openpoiservice/server/categories/categories.yml`.

### Endpoints

The default base url is `http://localhost:5000/`.

The openpoiservice holds the endpoint `/pois`:

| Method allowed | Parameter | Values \[optional\]                            			     |
|----------------|:----------|:----------------------------------------------------------------------|
| POST           | request   | pois, stats, list                 				     |
|                | geometry  | bbox, geojson, buffer             				     |
|                | filter    | category_group_ids, category_ids, \[name, wheelchair, smoking, fee\]  | 
|                | limit     | integer                           				     |
|                | sortby    | category, distance                				     |

### Examples

##### POIS around a buffered point

```sh
curl -X POST \
  http://localhost:5000/pois \
  -H 'Content-Type: application/json' \
  -d '{
  "request": "pois",
  "geometry": {
    "bbox": [
      [8.8034, 53.0756],
      [8.7834, 53.0456]
    ],
    "geojson": {
      "type": "Point",
      "coordinates": [8.8034, 53.0756]
    },
    "buffer": 250  
  }
}'
```

##### POIs of given categories
```sh
curl -X POST \
  http://localhost:5000/pois \
  -H 'Content-Type: application/json' \
  -d '{
  "request": "pois",
  "geometry": {
    "bbox": [
      [8.8034, 53.0756],
      [8.7834, 53.0456]
    ],
    "geojson": {
      "type": "Point",
      "coordinates": [8.8034, 53.0756]
    },
    "buffer": 100  
  },
  "limit": 200,
  "filters": {
    "category_ids": [180, 245]
  } 
}'
```

##### POIs of given category groups

```sh
curl -X POST \
  http://localhost:5000/pois \
  -H 'Content-Type: application/json' \
  -d '{
  "request": "pois",
  "geometry": {
    "bbox": [
      [8.8034, 53.0756],
      [8.7834, 53.0456]
    ],
    "geojson": {
      "type": "Point",
      "coordinates": [8.8034, 53.0756]
    },
    "buffer": 100  
  },
  "limit": 200,
  "filters": {
    "category_group_ids": [160]
  } 
}'
```

##### POI Statistics
```sh
curl -X POST \
  http://129.206.7.157:5005/pois \
  -H 'Content-Type: application/json' \
  -d '{
  "request": "stats",
  "geometry": {
    "bbox": [
      [8.8034, 53.0756],
      [8.7834, 53.0456]
    ],
    "geojson": {
      "type": "Point",
      "coordinates": [8.8034, 53.0756]
    },
    "buffer": 100  
  }
}'
```

##### POI Categories as a list

```sh
curl -X POST \
  http://127.0.0.1:5000/pois \
  -H 'content-type: application/json' \
  -d '{
	"request": "list"
}'
```

