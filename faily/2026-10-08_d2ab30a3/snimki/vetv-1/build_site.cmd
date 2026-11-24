@echo off
rem The HWPh reader from the Markdown volumes: MD -> XML database -> XQuery -> static site.
rem
rem   build_site.cmd <folder with Bd01.md ...> [site folder]
rem
rem Settings (environment variables, all optional):
rem   PYTHON   python (3.8 or newer)            JAVA    java (8 or newer)
rem   SAXON    class path of Saxon-HE (default: the jars in saxon\, Saxon-HE 11.7)
rem   XMX      Java heap (3g)                   PARTS   groups of the word index (8)
rem   UI_LANG  language of the article pages (ru)
rem   DB       the XML database (<site folder>.xml)
setlocal enableextensions enabledelayedexpansion
if "%~1"=="" (
  echo usage: build_site.cmd ^<folder with Bd01.md ...^> [site folder]
  exit /b 2
)
set "HERE=%~dp0"
set "HERE=%HERE:~0,-1%"
set "SRC=%~f1"
set "OUT=%~f2"
if "%~2"=="" set "OUT=%CD%\site"
if not defined PYTHON set "PYTHON=python"
if not defined JAVA set "JAVA=java"
if not defined XMX set "XMX=3g"
if not defined PARTS set "PARTS=8"
if not defined UI_LANG set "UI_LANG=ru"
if not defined DB set "DB=%OUT%.xml"
if not defined SAXON (
  set "SAXON="
  for %%j in ("%HERE%\saxon\*.jar") do set "SAXON=!SAXON!%%~fj;"
)

echo == 1. Markdown -^> XML: %DB%  [%TIME%]
"%PYTHON%" "%HERE%\md2xml.py" "%SRC%" -o "%DB%" || goto :fail

if exist "%OUT%" rmdir /s /q "%OUT%"
mkdir "%OUT%" || goto :fail

echo == 2. articles: data\a, data\t, pages  [%TIME%]
call :query article.xq "%OUT%.articles" bands=* lang=%UI_LANG% "i18n=%HERE%\static\i18n.js" || goto :fail
"%PYTHON%" "%HERE%\split.py" "%OUT%.articles" "%OUT%" || goto :fail
del "%OUT%.articles"

echo == 3. word index: data\s, data\p, data\vocab.js, data\meta.js  [%TIME%]
call :query index.xq "%OUT%.index" parts=%PARTS% || goto :fail
"%PYTHON%" "%HERE%\split.py" "%OUT%.index" "%OUT%" || goto :fail
del "%OUT%.index"

echo == 4. register, graph, persons, lists, page index, reader  [%TIME%]
call :query global.xq "%OUT%.global" lang=%UI_LANG% "i18n=%HERE%\static\i18n.js" "ui=%HERE%\static\hwph_ui.html" || goto :fail
"%PYTHON%" "%HERE%\split.py" "%OUT%.global" "%OUT%" || goto :fail
del "%OUT%.global"

echo == 5. fixed files of the reader  [%TIME%]
copy /y "%HERE%\static\static_api.js" "%OUT%\" >nul || goto :fail
copy /y "%HERE%\static\i18n.js" "%OUT%\" >nul || goto :fail
xcopy /e /i /q /y "%HERE%\static\katex" "%OUT%\katex" >nul || goto :fail
copy /y "%HERE%\static\page.css" "%OUT%\pages\page.css" >nul || goto :fail

echo == 6. manifest.json (every file, for a crawler)  [%TIME%]
call :query manifest.xq "%OUT%\manifest.json" "site=%OUT%" || goto :fail
"%PYTHON%" "%HERE%\finish.py" "%OUT%" "%SRC%\img" || goto :fail

echo == done: %OUT%\index.html  [%TIME%]
exit /b 0

:query
rem :query <file.xq> <output> [name=value ...]
set "Q=%~1"
set "O=%~2"
shift
shift
set "ARGS="
:args
if "%~1"=="" goto :run
set ARGS=!ARGS! "%~1"
shift
goto :args
:run
"%JAVA%" -Xmx%XMX% -cp "%SAXON%" net.sf.saxon.Query "-s:%DB%" "-q:%HERE%\xq\%Q%" "-o:%O%" %ARGS%
exit /b %ERRORLEVEL%

:fail
echo == FAILED  [%TIME%]
exit /b 1
