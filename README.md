# Digiplan

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg)](https://github.com/pydanny/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Getting started

First you have to decide, wether you want to run the application via Docker or simply
via python.
For backend developers, I would recommend to install it regulary with python.
For frontend developers it is simplier to just run docker and not to care about python
environment and dependencies.

Obviously, you have to clone this repo first.

## Prepare Data

In both cases, geometry packages have to be placed into folder _digiplan/data/_,
so that they can be found by the application and uploaded into database.
All packages are justed dropped into this folder (no hierarchy).

## Using standard python installation

### Setting up environment

Prerequisite: _conda_ ([Anaconda](https://docs.anaconda.com/anaconda/install/)
/[Miniconda](https://conda.io/en/latest/miniconda.html))
Enter repo folder and set up a conda environment and activate it:

```
conda env create -f environment.yml
conda activate digiplan
```

Install [poetry](https://python-poetry.org/) (python dependency manager used in this
project) and dependencies for the project (Note: Installing poetry via pip into same environment is not recommended and can cause trouble! Instead it should be installed system-wide via command below or [pipx](https://python-poetry.org/docs/#installing-with-pipx)):

```
curl -sSL https://install.python-poetry.org | python3 -
poetry install
```

The project uses [pre-commit](https://pre-commit.com/) in order to check for errors and
linting bugs before commits.
To activate pre-commit simply run:

```
pre-commit install
```

Now you should be ready to start the application by running:
(This will throw a database error, as we must set up a database)

```
python manage.py runserver
```

As the project uses a database you must have to set up a database first.
I highly recommend to use [postgresql](https://www.postgresql.org/) fot that.
Please follow online tutorials to set up database correctly and come back here, if
everything is set up.

In order to run oemof simulations using `django-oemof`,
you have to set up celery together with a locally running redis server.
You can find instructions at https://realpython.com/caching-in-django-with-redis/#install-redis on how to install redis.
Simplest solution to install and run redis it via _apt_:
```bash
sudo apt-get install redis-server
redis-server
```
Afterwards, make sure that following variable is set in your environment:
- `CELERY_BROKER_URL=redis://localhost:6379/0` (default port used here)
and run celery from your terminal:
```bash
export DJANGO_READ_DOT_ENV_FILE=True; celery -A config.celery worker -l INFO
```

### Configuration

Configuration is done by django configuration files in _config/settings/_ and by using
environment variables (for database, redis, etc.).
Environment variables have to be set using the following structure:

- `DATABASE_URL=postgis://<user>:<password>@<host>:<port>/<database>`
- `TILING_SERVICE_STYLE_ID=<URL to mapbox style>`
- `TILING_SERVICE_TOKEN=<token>`
- `PROJ_LIB=<path to folder _proj/_, needed for GDAL>`
- `REDIS_URL=redis://<host>:<port>` (if REDIS is used)
- `USE_DISTILLED_MVTS=<True/False>` (should be set to False at first)
- `USE_DOCKER=<True/False>`

You can set up environment variables either by using your IDE, or by setting them via
your system.
Please follow tutorials for this or ask your local IT-expert.

#### Example: local dev configuration without Docker

1. Merge given local env files into newly created root `.env`
   file: `make local_env_file`
2. Adjust values in root `.env` file to your needs. For example your hostname is
   probably `localhost` and not `postgres`. Maybe you want also use a different user or
   password.
3. Set environment variable DJANGO_READ_DOT_ENV_FILE to True, e.g. via simple
   export: `export DJANGO_READ_DOT_ENV_FILE=True`. You can persist the env export by
   putting it for example into your bashrc file (terminal restart needed afterwards):
    ```bash
    echo -e "\n# Use .env file for Digiplan in local dev environment\nexport DJANGO_READ_DOT_ENV_FILE=True" >> ~/.bashrc
    ```
4. Create in your local Postgres Database Management System a database like defined in
   your `.env` file (e.g. via `pgAdmin` or `psql`)
5. In your database create following extensions:
    ```postgresql
      CREATE EXTENSION postgis;
    ```

### Load data into application

First you have to set up all tables in the database by runnning:

```
python manage.py migrate
```

Afterwards you have to load in data. To simplify data commands a _Makefile_ has been
added, which can be used by command `make`.
You can load all data by running (or you can run them one-by-one):

```
make load_regions load_data
```

And you can empty all data by running:

```
make empty_data empty_regions
```

## Using Docker

Make sure you have [Docker](https://docs.docker.com/get-docker/)
and [Docker-Compose](https://docs.docker.com/compose/install/) installed.
You may have to put `sudo` in front of the commands.
While using the following commands, exchange _production.yml_ (production server) and _
local.yml_ (local development) accordingly to your needs!

### Start container

```
docker-compose -f production.yml up -d --build
```

Depending on your deployment (local/production), the server should be available
under `localhost:8000` (local) or
at docker container at port 5000 (production server needs to be forwarded by a proxy
server).
Sometimes the CSS is not loaded correctly in production mode, restarting the production server can help:
```
docker-compose -f production.yml restart
```

By now, no data is visible, as the geometries have to be loaded into database first by
the following steps.

### Load data into database

Following steps are necessary to refresh/load data on production server:

```
docker-compose -f production.yml run --rm django python manage.py migrate
docker-compose -f production.yml run --rm django make empty_data empty_regions
docker-compose -f production.yml run --rm django make load_regions load_data
```

In order to increase loading speed of vector tiles, the tiles can be prerenderd. This is
done by using distilled vector tiles.
You can create those vector tiles by using the following commands:
(Note: You have to recreate distilled vector tiles after each data update in order to
see changes on the map)

```
docker-compose -f production.yml run --name digiplan_distill -e DISTILL=True django /bin/bash -c "python manage.py collectstatic --noinput; python manage.py distill-local --force --exclude-staticfiles ./distill"
docker cp digiplan_distill:/app/distill/ ./digiplan/static/mvts/
# commit and push, afterwards remove temp container:
docker rm -f digiplan_distill
```

# Adding new (static) layers

> **Outdated!** - `django-mapengine` is used to set up map sources and layers instead!

In order to add new layers to the application following steps must be made:

- add geopackages containing vector layer data into folder _digiplan/data_.
- create a Django model in `digiplan/map/models.py` with following minimum requirements:

    - it must contain a `GeometryField` (Point/Polygon) named `geom`,
    - it must contain the default Django `Manager` as attribute `objects`,
    - it must contain a `MVTManager` derived from `digiplan/map/managers.py`.
      Normally, a `StaticMVTManager` (which activates filtering of vector tiles by given
      zoom level) should be chosen.

- run `makemigrations` and `migrate` (see commands above),
- add an entry for new layer in `MODELS` in `digiplan/utils/data_processing.py`
  ,
- load layer data into DB by running `load_data` or by loading only specific data.

Now the layer data is present in DB, but not yet served as vector tiles. This can be
accomplished with following steps:

- add mapbox layer information in `digiplan/map/layers.py` (either in existing category
  or by adding a new one)
- add layer to `STATIC_MVT_LAYERS` in `digiplan/map/mvt_layers`.

The layer and a related switch should now be visible on map and on the detail panel.

# Testing

We encourage all to build application tests. As best practice, this should be done immediately after documentation of the application being built, before starting on any coding.

## Pytest
This project uses the Pytest, a framework for easily building simple and scalable tests. After you have set up to develop locally, run the following commands to make sure the testing environment is ready:
`pytest`

You will get a readout of the users app that has already been set up with tests. If you do not want to run the pytest on the entire project, you can target a particular app by typing in its location:

`pytest <path-to-app-in-project/app>`

If you set up your project to develop locally with docker, run the following command:

`docker-compose -f local.yml run --rm django pytest`

Targeting particular apps for testing in docker follows a similar pattern as previously shown above.

## Coverage

You should build your tests to provide the highest level of code coverage. You can run the pytest with code coverage by typing in the following command:

`coverage run -m pytest`

Once the tests are complete, in order to see the code coverage, run the following command:

`coverage report`

If you're running the project locally with Docker, use these commands instead:

`docker-compose -f local.yml run --rm django coverage run -m pytest`
`docker-compose -f local.yml run --rm django coverage report`

Note

At the root of the project folder, you will find the pytest.ini file. You can use this to customize the pytest to your liking.

There is also the .coveragerc. This is the configuration file for the coverage tool.


# Useful commands

Example to only load specific data:

```
docker-compose -f production.yml run --rm django python -u manage.py shell --command="from djagora.utils import load_overlays; from djagora.utils.load_configs import DYNAMIC_OVERLAYS; overlays = [item for item in DYNAMIC_OVERLAYS if item['name'].startswith('settlement')]; load_overlays.run(overlays=overlays)"
```
