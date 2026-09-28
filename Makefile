PYTHON = python3
MAIN = main.py

.PHONY: install run run-color run-linear run-linear-color debug clean lint lint-strict test

install:
	pip install -r requirements.txt

run:
	$(PYTHON) $(MAIN)

run-color:
	$(PYTHON) $(MAIN) --color

run-capacity:
	$(PYTHON) $(MAIN) --capacity_info

run-linear:
	$(PYTHON) $(MAIN) maps/easy/01_linear_path.txt

run-linear-color:
	$(PYTHON) $(MAIN) maps/easy/01_linear_path.txt --color

debug:
	$(PYTHON) -m pdb $(MAIN)

test:
	$(PYTHON) -m unittest discover -s tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	flake8 .
	mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
