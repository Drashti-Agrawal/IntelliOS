python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\backend\requirements.txt
pip install "uvicorn[standard]" fastapi

$env:PORT=8000
uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload

$env:PORT=8000
python .\backend\server.py

$env:PYTHONPATH=(Resolve-Path .\backend).Path
uvicorn backend.server:app --host 0.0.0.0 --port 8000 --reload

pip install -e .\path\to\vector_db_pkg
