
.PHONY : load_regions load_data empty_data dump_fixtures load_fixtures distill

DISTILL=True
export

load_regions:
	python manage.py shell --command="from egon.utils import data_processing; data_processing.load_regions()"

load_data:
	python manage.py shell --command="from enershelf.utils import data_processing; data_processing.load_data()"

empty_regions:
	python manage.py shell --command="from egon.utils import data_processing; data_processing.empty_data(models=data_processing.REGIONS)"

empty_data:
	python manage.py shell --command="from enershelf.utils import data_processing; data_processing.empty_data()"

dump_fixtures:
	bash enershelf/utils/dump_fixtures.sh

load_fixtures:
	bash enershelf/utils/load_fixtures.sh

distill:
	python manage.py distill-local --force --exclude-staticfiles ./distill
