#!/usr/bin/env bash

# Execute this script in your project root folder with activated virtualenv:
#
# $ bash enershelf/utils/load_fixture.sh

set -e

python manage.py loaddata enershelf/map/fixtures/region.json
python manage.py loaddata enershelf/map/fixtures/district.json

python manage.py loaddata enershelf/map/fixtures/nightlight.json
python manage.py loaddata enershelf/map/fixtures/hospitals.json
python manage.py loaddata enershelf/map/fixtures/hospitalssimulated.json
python manage.py loaddata enershelf/map/fixtures/cluster.json