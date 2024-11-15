@echo off

::REM echo 安裝 requirements.txt 中的庫...
::REM pip install -r requirements.txt

echo 執行 internal_hdd.py...
python src\internal_hdd.py

echo 開啟 internal-hdd.html...
start res\html\internal-hdd.html

pause
