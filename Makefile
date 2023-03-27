
.PHONY : load_regions load_data empty_data dump_fixtures load_fixtures distill check_distill_coordinates

DISTILL=True
export

load_regions:
	python manage.py shell --command="from digiplan.utils import data_processing; data_processing.load_regions()"

load_data:
	python manage.py shell --command="from digiplan.utils import data_processing; data_processing.load_data()"

load_population:
	python manage.py shell --command="from digiplan.utils import data_processing; data_processing.load_population()"

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

distill:
	python manage.py distill-local --force --exclude-staticfiles ./digiplan/static/mvts

check_distill_coordinates:
	python manage.py shell --command="from digiplan.utils import distill; print(distill.check_distill_coordinates())"

local_env_file:
	python merge_local_dotenvs_in_dotenv.py

update_vendor_assets:
	# Note: call this command from the same folder your Makefile is located
	# Note: this run only update minor versions.
	# Update major versions manually, you can use "ncu" for this.
	# https://nodejs.dev/en/learn/update-all-the-nodejs-dependencies-to-their-latest-version/#update-all-packages-to-the-latest-version

	# Update
	npm update

	# Bootstrap https://github.com/twbs/bootstrap
	rm -r digiplan/static/vendors/bootstrap/scss/*
	cp -r node_modules/bootstrap/scss/* digiplan/static/vendors/bootstrap/scss/
	rm -r digiplan/static/vendors/bootstrap/js/*
	cp node_modules/bootstrap/dist/js/bootstrap.min.js* digiplan/static/vendors/bootstrap/js/

	# eCharts https://echarts.apache.org/en/index.html
	rm -r digiplan/static/vendors/echarts/js/*
	cp node_modules/echarts/dist/echarts.min.js digiplan/static/vendors/echarts/js/

	# Ion.RangeSlider https://github.com/IonDen/ion.rangeSlider
	rm -r digiplan/static/vendors/ionrangeslider/js/*
	cp node_modules/ion-rangeslider/js/ion.rangeSlider.min.js digiplan/static/vendors/ionrangeslider/js/
	rm -r digiplan/static/vendors/ionrangeslider/css/*
	cp node_modules/ion-rangeslider/css/ion.rangeSlider.min.css digiplan/static/vendors/ionrangeslider/css/

	# jQuery https://github.com/jquery/jquery
	rm -r digiplan/static/vendors/jquery/js/*
	cp node_modules/jquery/dist/jquery.min.* digiplan/static/vendors/jquery/js/

	# MapLibre GL JS https://github.com/maplibre/maplibre-gl-js
	rm -r digiplan/static/vendors/maplibre/js/*
	cp node_modules/maplibre-gl/dist/maplibre-gl.js digiplan/static/vendors/maplibre/js/
	cp node_modules/maplibre-gl/dist/maplibre-gl.js.map digiplan/static/vendors/maplibre/js/
	rm -r digiplan/static/vendors/maplibre/css/*
	cp node_modules/maplibre-gl/dist/maplibre-gl.css digiplan/static/vendors/maplibre/css/

	# PubSubJS https://github.com/mroderick/PubSubJS
	rm -r digiplan/static/vendors/pubsub/js/*
	cp node_modules/pubsub-js/src/pubsub.js digiplan/static/vendors/pubsub/js/

	# Select2: https://select2.org/
	rm -r digiplan/static/vendors/select2/css/*
	cp node_modules/select2/dist/css/select2.min.css digiplan/static/vendors/select2/css/
	rm -r digiplan/static/vendors/select2/js/*
	cp node_modules/select2/dist/js/select2.min.js digiplan/static/vendors/select2/js/
	mkdir -p digiplan/static/vendors/select2/js/i18n/ && \
	cp node_modules/select2/dist/js/i18n/de.js digiplan/static/vendors/select2/js/i18n/

	# Done
