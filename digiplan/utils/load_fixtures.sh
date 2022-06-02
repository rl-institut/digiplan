#!/usr/bin/env bash

# Execute this script in your project root folder with activated virtualenv:
#
# $ bash digiplan/utils/load_fixture.sh

set -e

python manage.py loaddata digiplan/map/fixtures/region.json
python manage.py loaddata digiplan/map/fixtures/district.json

python manage.py loaddata digiplan/map/fixtures/nightlight.json
python manage.py loaddata digiplan/map/fixtures/hospitals.json
python manage.py loaddata digiplan/map/fixtures/hospitalssimulated.json
python manage.py loaddata digiplan/map/fixtures/cluster.json
