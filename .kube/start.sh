#!/bin/bash

helm secrets install forum-release app/ -f app/values.yaml -f app/credentials.yaml
