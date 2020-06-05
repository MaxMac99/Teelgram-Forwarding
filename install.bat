PUSHD %~dp0
@ECHO OFF
pip install virtualenv

virtualenv -p python3 .venv
call .venv\Scripts\activate

pip install -r requirements.txt
POPD
PAUSE
