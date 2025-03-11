python -m venv env
.\env\Scripts\Activate.ps1

pip install -r requirements.txt

SET-Location "./app"

python "main.py"

deactivate