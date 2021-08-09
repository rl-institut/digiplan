#!/usr/bin/env bash

# Execute this script in your project root folder with activated virtualenv:
#
# $ bash enershelf/utils/dump_fixtures.sh

set -e

python manage.py dumpdata map.region --indent=2 --format=json > enershelf/map/fixtures/region.json
python manage.py dumpdata map.district --indent=2 --format=json > enershelf/map/fixtures/district.json

python manage.py dumpdata map.cluster --indent=2 --format=json > enershelf/map/fixtures/cluster.json
python manage.py dumpdata map.nightlight --indent=2 --format=json > enershelf/map/fixtures/nightlight.json
python manage.py dumpdata map.hospitals --indent=2 --format=json > enershelf/map/fixtures/hospitals.json
python manage.py dumpdata map.hospitalssimulated --indent=2 --format=json > enershelf/map/fixtures/hospitalssimulated.json
