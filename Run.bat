@echo off

::REM echo 安裝 requirements.txt 中的庫...
::REM pip install -r requirements.txt

echo 執行 internal_hdd.py...
python src\internal_hdd.py

:: 取得今天的日期 
for /f "tokens=1-3 delims=/ " %%a in ('echo %date%') do (
    set today=%%a%%b%%c
)
:: 去除可能存在的斜槓或空格
set today=%today:/=%

echo 開啟 internal-hdd-%today%.html...
start res\html\internal-hdd-%today%.html

pause
