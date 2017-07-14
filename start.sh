#!/bin/bash

mkdir archive
cp config.example.yaml config.yaml
nano config.yaml
docker-compose up -d
