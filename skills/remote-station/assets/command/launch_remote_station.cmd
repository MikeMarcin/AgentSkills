@echo off
rem launch_remote_station: version-free forwarder installed by the remote-station skill.
rem It runs the current checkout's own pinned skill and contains no station logic.
setlocal
set "LRS_ROOT="
for /f "usebackq delims=" %%R in (`git rev-parse --show-toplevel 2^>nul`) do set "LRS_ROOT=%%R"
if not defined LRS_ROOT goto no_repository
set "LRS_TARGET=%LRS_ROOT%\.agents\skills\remote-station\scripts\launch_remote_station.py"
if not exist "%LRS_TARGET%" goto no_skill
py -3 "%LRS_TARGET%" %*
exit /b %ERRORLEVEL%
:no_repository
>&2 echo launch_remote_station: not inside a Git repository: %CD%
exit /b 3
:no_skill
>&2 echo launch_remote_station: %LRS_ROOT% has no remote-station skill at .agents\skills\remote-station; run: mask install remote-station
exit /b 4
