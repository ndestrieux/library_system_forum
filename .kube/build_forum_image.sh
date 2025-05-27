#!/bin/bash

cd ..

eval "$(minikube docker-env)"

docker build -t forum -f deployment/prod/Dockerfile .
