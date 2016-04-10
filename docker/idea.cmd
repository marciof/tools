START x11.xlaunch
docker-machine start default
FOR /F "tokens=*" %%i IN ('docker-machine env default --shell cmd') DO %%i
FOR /F %%i IN ('hostname') DO SET DISPLAY=%%i:0
docker-compose -f idea\docker-compose.yml up -d
