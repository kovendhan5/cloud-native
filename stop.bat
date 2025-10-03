@echo off
REM Stop all Cloud Native services

echo Stopping application services...
docker compose down

echo Stopping infrastructure services...
docker compose -f docker-compose.infrastructure.yml down

echo.
echo All services stopped!
echo.
echo To remove volumes, run:
echo docker compose -f docker-compose.infrastructure.yml down -v
