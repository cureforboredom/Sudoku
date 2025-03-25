#!/bin/sh
poetry install
flask --app sudoku init-db