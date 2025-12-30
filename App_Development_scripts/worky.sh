#!/bin/bash
# Worky Master Control Script

SCRIPT_DIR="$(dirname "$0")"

show_usage() {
    echo "Worky Control Script"
    echo ""
    echo "Usage: ./worky.sh [service] [action]"
    echo ""
    echo "Services:"
    echo "  ui       - React UI (port 3007)"
    echo "  db       - PostgreSQL Database (port 5437)"
    echo "  api      - FastAPI Backend (port 8007)"
    echo "  ui-api   - UI + API together"
    echo "  all      - All services (DB + API + UI)"
    echo ""
    echo "Actions:"
    echo "  start    - Start the service"
    echo "  stop     - Stop the service"
    echo "  restart  - Restart the service"
    echo ""
    echo "Examples:"
    echo "  ./worky.sh ui start"
    echo "  ./worky.sh api restart"
    echo "  ./worky.sh all start"
    echo "  ./worky.sh db stop"
}

if [ $# -lt 2 ]; then
    show_usage
    exit 1
fi

SERVICE=$1
ACTION=$2

case "$SERVICE" in
    ui)
        case "$ACTION" in
            start) "$SCRIPT_DIR/start_ui.sh" ;;
            stop) "$SCRIPT_DIR/stop_ui.sh" ;;
            restart) "$SCRIPT_DIR/restart_ui.sh" ;;
            *) echo "Invalid action: $ACTION"; show_usage; exit 1 ;;
        esac
        ;;
    db)
        case "$ACTION" in
            start) "$SCRIPT_DIR/start_db.sh" ;;
            stop) "$SCRIPT_DIR/stop_db.sh" ;;
            restart) "$SCRIPT_DIR/restart_db.sh" ;;
            *) echo "Invalid action: $ACTION"; show_usage; exit 1 ;;
        esac
        ;;
    api)
        case "$ACTION" in
            start) "$SCRIPT_DIR/start_api.sh" ;;
            stop) "$SCRIPT_DIR/stop_api.sh" ;;
            restart) "$SCRIPT_DIR/restart_api.sh" ;;
            *) echo "Invalid action: $ACTION"; show_usage; exit 1 ;;
        esac
        ;;
    ui-api)
        case "$ACTION" in
            start) "$SCRIPT_DIR/start_ui_api.sh" ;;
            stop) "$SCRIPT_DIR/stop_ui_api.sh" ;;
            restart) "$SCRIPT_DIR/restart_ui_api.sh" ;;
            *) echo "Invalid action: $ACTION"; show_usage; exit 1 ;;
        esac
        ;;
    all)
        case "$ACTION" in
            start) "$SCRIPT_DIR/start_all.sh" ;;
            stop) "$SCRIPT_DIR/stop_all.sh" ;;
            restart) "$SCRIPT_DIR/restart_all.sh" ;;
            *) echo "Invalid action: $ACTION"; show_usage; exit 1 ;;
        esac
        ;;
    *)
        echo "Invalid service: $SERVICE"
        show_usage
        exit 1
        ;;
esac
