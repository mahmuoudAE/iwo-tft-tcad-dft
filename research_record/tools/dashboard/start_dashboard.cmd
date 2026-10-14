@echo off
rem IWO Mission Control: start the read-only dashboard server inside WSL Ubuntu and open it in the browser.
rem The server binds 127.0.0.1:8765 in WSL; WSL forwards http://localhost:8765 to it. Close the server window to stop it.
setlocal
set "PORT=8765"
set "SERVER=/mnt/c/Users/moham/Downloads/IWO_Local_Codex_Handoff (1)/iwo-tft-research-private/tools/dashboard/server.py"

rem Already running? Then only open the browser.
curl.exe -s -o nul -m 3 "http://localhost:%PORT%/api/status" && goto open

start "IWO Mission Control server" /min wsl.exe -d Ubuntu -- python3 "%SERVER%" --port %PORT%
rem wait until the server answers (up to about 30 s), then open the page; the page itself retries every few s
set /a N=0
:wait
timeout /t 1 /nobreak >nul
curl.exe -s -o nul -m 2 "http://localhost:%PORT%/api/status" && goto open
set /a N+=1
if %N% lss 30 goto wait

:open
start "" "http://localhost:%PORT%/"
endlocal
