#!/usr/bin/env bash

# Execute this script in your project root folder with activated virtualenv:
#
# $ bash enershelf/utils/load_fixture.sh

set -e

python manage.py loaddata djagora/map/fixtures/district.json

python manage.py loaddata djagora/map/fixtures/grid.json
python manage.py loaddata djagora/map/fixtures/nightlight.json
python manage.py loaddata djagora/map/fixtures/hc_facilities.json
