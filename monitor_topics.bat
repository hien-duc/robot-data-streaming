@echo off
echo Subscribing to all VDA5050 robot topics...
echo.

mosquitto_sub -h localhost -t "/vda5050/#" -v

pause