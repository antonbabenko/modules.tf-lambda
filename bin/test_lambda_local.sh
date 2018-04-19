#!/usr/bin/env bash

export AWS_PROFILE=private-anton

/usr/local/bin/python-lambda-local -f $1 $2 $3