#!/usr/bin/env bash

# Execute this script in your project root folder with activated virtualenv:
#
# $ bash enershelf/utils/dump_fixtures.sh

set -e

python manage.py dumpdata map.district --indent=2 --format=json > enershelf/map/fixtures/district.json
python manage.py dumpdata map.grid --indent=2 --format=json > enershelf/map/fixtures/grid.json
python manage.py dumpdata map.nightlight --indent=2 --format=json > enershelf/map/fixtures/nightlight.json
python manage.py dumpdata map.hc_facilities --indent=2 --format=json > enershelf/map/fixtures/hc_facilities.json
