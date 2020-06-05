pushd %~dp0
call .venv\Scripts\activate
python run.py
popd
PAUSE
