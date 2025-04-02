#!/usr/bin/env python

# -----------------------------------------------------------------------
# top.py
#
# This file is simply defines the flask app that app.py and auth.py will
# both access.
# -----------------------------------------------------------------------

import flask

app = flask.Flask(__name__)
