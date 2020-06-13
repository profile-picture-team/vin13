@ECHO OFF

SET logDIR=log
SET envFILE=.env

ECHO please wait a moment... && ECHO.

IF not exist %logDIR% (
mkdir %logDIR%
ECHO created ./%logDIR%/
) ELSE ( ECHO ./%logDIR%/ already exists! )

IF not exist %envFILE% (
ECHO BOT_TOKEN=PlAcE-toKEn-HErE  >%envFILE%
ECHO PREFIX=.                    >>%envFILE%
ECHO created and wrote %envFILE%!
) ELSE ( ECHO %envFILE% already exists! )

ECHO. && ECHO pip install pipenv && ECHO.
pip install pipenv

ECHO. && ECHO pipenv install && ECHO.
pipenv install

ECHO. && ECHO   ^|^| && ECHO   ^|^| && ECHO   \/ && ECHO  DONE! (DO NOT FORGET to install ffmpeg if you have not done so already) && ECHO   /\ && ECHO   ^|^| && ECHO   ^|^| && ECHO.

PAUSE