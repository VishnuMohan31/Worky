#!/bin/bash
python -m uvicorn app.main:app --reload --port 8007 --host 0.0.0.0
