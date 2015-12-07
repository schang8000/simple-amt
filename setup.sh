#!/bin/bash

ENV_NAME="mturk"


if source activate $ENV_NAME; then
  echo "switched to dev env: ${ENV_NAME}"
else
  conda create --name $ENV_NAME python=2.7 anaconda
  source activate $ENV_NAME
  pip install -r requirements.txt
fi
