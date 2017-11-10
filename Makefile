all:
	python3 main.py

check:
	pep8 *.py

fix:
	autopep8 -i *.py

kill:
	pkill Python
