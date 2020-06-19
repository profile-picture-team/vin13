@echo off

set LOG_DIR=log
set ENV_FILE=.env

echo.
echo       :::     ::: ::::::::::: ::::    :::    :::   ::::::::
echo      :+:     :+:     :+:     :+:+:   :+:  :+:+:  :+:    :+:
echo     +:+     +:+     +:+     :+:+:+  +:+    +:+         +:+ 
echo    +#+     +:+     +#+     +#+ +:+ +#+    +#+       +#++:  
echo    +#+   +#+      +#+     +#+  +#+#+#    +#+         +#+   
echo    #+#+#+#       #+#     #+#   #+#+#    #+#  #+#    #+#    
echo     ###     ########### ###    ####  #######  ########     
echo.
echo                  Start fucking batch
echo.

call :init ^
&& call :createLogFolder ^
&& call :createEnvFile ^
&& call :installPipenv ^
&& call :installDependences ^
&& call :end
del %STDERR%
del EMPTY_FILE

echo.
pause


goto EOF

:init
	set NAME="Batch: "
	set NAME=%NAME:~1,-1%
	set LOG_OUT=%~nx0.log
	set STDERR=%~nx0.stderr
	type nul > %LOG_OUT%
	type nul > %STDERR%
	call :setESC
	echo %NAME%Init complete >> %LOG_OUT%
exit /b 0


:end
	echo %NAME%DONE >> %LOG_OUT%
	echo %NAME%DONE!
	echo %ESC%[33m%NAME%WARNING: Don't forget to install ffmpeg if it's not installed%ESC%[m
exit /b 0


:createLogFolder
	if not exist %LOG_DIR% (
		mkdir %LOG_DIR% >> %LOG_OUT% 2> %STDERR% ^
		&& echo %NAME%Created log folder ^
		|| (
			echo %NAME%Error >> %LOG_OUT%
			echo %ESC%[91m%NAME%Some kind of error while creating log folder :P%ESC%[m
			echo %ESC%[91m%NAME%Installation log in %LOG_OUT%%ESC%[m
		)
	) else (
		echo %NAME%Log folder already exists
		echo %NAME%Log folder already exists >> %LOG_OUT%
	)
	call :writeStderr "function :createLogFolder"
exit /b 0


:createEnvFile
	if not exist %ENV_FILE% (
		(echo BOT_TOKEN=PlAcE-toKEn-HErE && echo PREFIX=.) > %ENV_FILE% 2> %STDERR% ^
		&& echo %NAME%Created and init env file ^(please check this file^) ^
		|| (
			echo %NAME%Error >> %LOG_OUT%
			echo %ESC%[91m%NAME%Some kind of error while creating env file :P%ESC%[m
			echo %ESC%[91m%NAME%Installation log in %LOG_OUT%%ESC%[m
		)
	) else (
		echo %NAME%Env file already exists ^(please check this file^)
		echo %NAME%Env file already exists ^(please check this file^) >> %LOG_OUT%
	)
	call :writeStderr "function :createEnvFile"
exit /b 0


:installPipenv
	echo %NAME%Installing pipenv using pip...
	(echo %NAME%Installing pipenv using pip... && pip install pipenv) >> %LOG_OUT% 2> %STDERR% ^
	|| (
		call :writeStderr pip install pipenv
		echo %NAME%Error code 1 >> %LOG_OUT%
		echo %ESC%[91m%NAME%Some kind of error while installing pipenv :P%ESC%[m
		echo %ESC%[91m%NAME%Installation log in %LOG_OUT%%ESC%[m
		exit /b 1
	)
	call :writeStderr "pip install pipenv"
exit /b 0


:installDependences
	echo %NAME%Installing dependencies using pipenv...
	(echo %NAME%Installing dependencies using pipenv... && pipenv install) >> %LOG_OUT% 2> %STDERR% ^
	|| (
		call :writeStderr "pipenv install"
		echo %NAME%Error code 2 >> %LOG_OUT%
		echo %ESC%[91m%NAME%Some kind of error while installing dependencies :P%ESC%[m
		echo %ESC%[91m%NAME%Installation log in %LOG_OUT%%ESC%[m
		exit /b 2
	)
	call :writeStderr "pipenv install"
exit /b 0


:writeStderr
	rem Дублирует STDERR в файл и если он не пустой, то и в консоль
	rem Принимает один параметр в КАВЫЧКАХ
	set author=%1
	set author=%author:~1,-1%
	if not exist EMPTY_FILE type nul > EMPTY_FILE
	fc %STDERR% EMPTY_FILE > nul
	set /a IS_NOT_EMPTY=%errorlevel%
	if %IS_NOT_EMPTY% == 1 (
		echo %NAME%STDERR from: %author%
		type %STDERR%
		echo %NAME%STDERR end
		(
			echo %NAME%STDERR from: %author%
			type %STDERR%
			echo %NAME%STDERR end
		) >> %LOG_OUT%
	)
exit /b 0


:setESC
	rem Записывает код клавиши Escape в ESC
	for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
	  set ESC=%%b
	  exit /b 0
	)
exit /b 0
