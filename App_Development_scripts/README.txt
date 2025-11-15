Worky Development Scripts
=========================

All scripts for managing Worky services.

MASTER CONTROL SCRIPT
---------------------
./worky.sh [service] [action]

Services: ui, db, api, ui-api, all
Actions: start, stop, restart

Examples:
  ./worky.sh all start      # Start everything
  ./worky.sh ui restart     # Restart UI
  ./worky.sh db stop        # Stop database

INDIVIDUAL SCRIPTS
------------------

UI Scripts:
  ./start_ui.sh
  ./stop_ui.sh
  ./restart_ui.sh

Database Scripts:
  ./start_db.sh
  ./stop_db.sh
  ./restart_db.sh

API Scripts:
  ./start_api.sh
  ./stop_api.sh
  ./restart_api.sh

UI + API Scripts:
  ./start_ui_api.sh
  ./stop_ui_api.sh
  ./restart_ui_api.sh

All Services Scripts:
  ./start_all.sh
  ./stop_all.sh
  ./restart_all.sh

PORTS
-----
UI:  3007
API: 8007
DB:  5437

QUICK START
-----------
cd /Users/ravikiranponduri/Desktop/WIP/worky/App_Development_scripts
./worky.sh all start

Then open: http://localhost:3007
Login: admin@datalegos.com / password
