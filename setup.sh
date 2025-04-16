#!/bin/bash

# This file sets up the environment to run the app

# Create virtual environment

python -m venv .venv
source .venv/bin/activate

# Install dependencies

pip install -r requirements.txt

# Create secret key and save to .env

ENV_FILE=".env"
APP_SECRET_KEY=$(openssl rand -hex 32)
rm -f "$ENV_FILE"
touch "$ENV_FILE"
echo "APP_SECRET_KEY=$APP_SECRET_KEY" >> "$ENV_FILE"
echo "App secret key saved to $ENV_FILE"
