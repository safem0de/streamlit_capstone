### Create Project 
```bash
python -m venv streamlit
cd streamlit
Script\activate                     # Win
source bin/activate                 # Mac
pip list                            # check lib
python -m pip install --upgrade pip # upgrade pip
pip install streamlit
```

### Best Practice Structure
```bash
my_streamlit_project/
│── .gitignore
│── requirements.txt
│── README.md
│── .streamlit/
│   ├── config.toml
│── app.py                 # Main entry point
│── pages/                 # Multi-page support (Streamlit's built-in)
│   ├── page1.py
│   ├── page2.py
│── components/            # Custom UI components
│   ├── sidebar.py
│   ├── navbar.py
│── services/              # Business logic / API handling
│   ├── data_loader.py
│   ├── auth.py
│── models/                # Data models (e.g., pydantic, pandas)
│   ├── user.py
│   ├── product.py
│── utils/                 # Utility functions
│   ├── helpers.py
│   ├── constants.py
│── static/                # Images, CSS, assets
│── data/                  # Local data storage
│── tests/                 # Unit tests
│── venv/                  # Virtual environment (should be in .gitignore)
```

### Create .gitignore (Windows)
```bash
(echo # Ignore Python cache files
echo __pycache__/
echo *.pyc
echo *.pyo
echo *.pyd
echo.
echo # Ignore virtual environments
echo venv/
echo env/
echo.
echo # Ignore Streamlit config & logs
echo .streamlit/
echo.
echo # Ignore macOS & Linux system files
echo .DS_Store
echo *.swp
echo.
echo # Ignore environment variables & secrets
echo .env
echo .secret
echo # Python Libs
echo Lib
echo Scripts
echo *.cfg
) > .gitignore
```

### Create Folders
```bash
type nul > "app.py"

mkdir ".streamlit"
type nul > ".streamlit/config.toml"

mkdir "pages"
type nul > "pages/page1.py"

mkdir "components"
type nul > "components/sidebar.py"

mkdir "services"
type nul > "services/data_loader.py"

mkdir "utils"
type nul > "utils/helpers.py"

mkdir "static"
mkdir "data"
mkdir "tests"
```

### Clone Project
```bash
git -c http.sslVerify=false clone https://github.com/safem0de/streamlit_capstone.git
cd streamlit
python -m venv .
```

### Run Project
```bash
streamlit run app.py
```

### Before Git Commit
```bash
pip freeze > requirements.txt
git -c http.sslVerify=false push origin main
```
