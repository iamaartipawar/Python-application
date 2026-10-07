# python-app

A responsive HarshalTechOps landing page built with Flask, semantic HTML, and
custom CSS. The interface has no JavaScript or frontend build step.

## Setup and test (Windows)

1. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Run the tests:

   ```powershell
   py -m unittest discover -s tests
   ```

## Run the app

On Windows, run the Flask development server:

```powershell
py app.py
```

Open <http://127.0.0.1:5000/>. The default port is `5000`; set `PORT` to
override it.

On Linux, `python app.py` starts Gunicorn. You can also start it directly:

```sh
gunicorn --bind "0.0.0.0:${PORT:-5000}" app:app
```

Use either command as the production start command. Gunicorn does not support
Windows, so use `py app.py` there for local development.
