#!/bin/bash

echo "🐘 Connecting to Worky Database..."

docker-compose exec db psql -U postgres -d worky
