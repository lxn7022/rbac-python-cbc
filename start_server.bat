@echo off
echo Starting RBAC Python API Server...
echo.
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
