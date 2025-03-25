#!/bin/sh
pyenv install 3.13
pyenv local 3.13
poetry install
poetry run flask --app sudoku init-db