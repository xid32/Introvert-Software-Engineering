#!/bin/bash
python chat.py
export FLASK_APP=chat.py
flask initdb
flask run