@echo off
REM View logs for a specific service or all services

if "%1"=="" (
    echo Showing logs for all application services...
    docker compose logs -f
) else (
    echo Showing logs for %1...
    docker compose logs -f %1
)
