
load_data:
	python manage.py shell --command="from enershelf.utils import load_gpkgs; load_gpkgs.run()"
