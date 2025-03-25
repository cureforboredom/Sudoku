#!/bin/sh
poetry install
poetry run flask --app sudoku init-db