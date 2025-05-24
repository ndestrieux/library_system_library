#!/bin/bash

helm secrets install library-release app/ -f app/values.yaml -f app/credentials.yaml
