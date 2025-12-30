#!/bin/bash

# Database Migration Helper Script
# Usage: ./migrate.sh [command]

set -e

cd "$(dirname "$0")"

case "$1" in
  create)
    if [ -z "$2" ]; then
      echo "Error: Please provide a migration message"
      echo "Usage: ./migrate.sh create \"Your migration message\""
      exit 1
    fi
    echo "Creating new migration: $2"
    alembic revision --autogenerate -m "$2"
    echo "✓ Migration created. Review it in alembic/versions/ before applying."
    ;;
    
  upgrade)
    echo "Applying migrations..."
    alembic upgrade head
    echo "✓ Migrations applied successfully"
    ;;
    
  downgrade)
    echo "Rolling back last migration..."
    alembic downgrade -1
    echo "✓ Rolled back successfully"
    ;;
    
  history)
    echo "Migration history:"
    alembic history
    ;;
    
  current)
    echo "Current database version:"
    alembic current
    ;;
    
  check)
    echo "Checking for pending migrations..."
    alembic check
    ;;
    
  *)
    echo "Database Migration Helper"
    echo ""
    echo "Usage: ./migrate.sh [command]"
    echo ""
    echo "Commands:"
    echo "  create \"message\"  - Create a new migration"
    echo "  upgrade          - Apply all pending migrations"
    echo "  downgrade        - Rollback the last migration"
    echo "  history          - Show migration history"
    echo "  current          - Show current database version"
    echo "  check            - Check for pending migrations"
    echo ""
    echo "Examples:"
    echo "  ./migrate.sh create \"Add email column to users\""
    echo "  ./migrate.sh upgrade"
    echo "  ./migrate.sh history"
    ;;
esac
