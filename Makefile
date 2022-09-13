
.PHONY : load_regions load_data empty_data dump_fixtures load_fixtures distill

DISTILL=True
export

load_regions:
	python manage.py shell --command="from digiplan.utils import data_processing; data_processing.load_regions()"

load_data:
	python manage.py shell --command="from digiplan.utils import data_processing; data_processing.load_data()"

load_raster:
	python manage.py shell --command="from digiplan.utils import data_processing; data_processing.load_raster()"

build_clusters:
	python manage.py shell --command="from digiplan.utils import data_processing; data_processing.build_cluster_geojson()"

empty_regions:
	python manage.py shell --command="from digiplan.utils import data_processing; data_processing.empty_data(models=data_processing.REGIONS)"

empty_data:
	python manage.py shell --command="from digiplan.utils import data_processing; data_processing.empty_data()"

empty_raster:
	python manage.py shell --command="from digiplan.utils import data_processing; data_processing.empty_raster()"

dump_fixtures:
	bash digiplan/utils/dump_fixtures.sh

load_fixtures:
	bash digiplan/utils/load_fixtures.sh

distill:
	python manage.py distill-local --force --exclude-staticfiles ./digiplan/static/mvts

local_env_file:
	python merge_local_dotenvs_in_dotenv.py

update_vendor_assets:
	# Select2: https://select2.org/
	rm -r digiplan/static/vendors/select2/css/*
	cp node_modules/select2/dist/css/select2.min.css digiplan/static/vendors/select2/css/
	rm -r digiplan/static/vendors/select2/js/*
	cp node_modules/select2/dist/js/select2.min.js digiplan/static/vendors/select2/js/
