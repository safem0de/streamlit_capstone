#### reference : https://github.com/streamlit/streamlit-example.git

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
python -m venv venv
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

### Deployment
1. build image using nerdctl
2. push to registry
3. create namespace and deploy

localhost
```bash
nerdctl build -t my-streamlit-app .
nerdctl run -it --rm -p 8501:8501 my-streamlit-app
```

production
```bash
nerdctl build -t 43.209.49.162:32000/streamlit:latest .
nerdctl build --no-cache -t streamlit:latest .
#
nerdctl images
nerdctl push --insecure-registry 43.209.49.162:32000/streamlit:latest
curl -X GET http://43.209.49.162:32000/v2/_catalog
```
Tag image ไปยัง local registry
nerdctl tag <image> <private-registry>/<image>
nerdctl tag streamlit:latest 127.0.0.1:32000/streamlit:latest

วิธีที่ถูกต้องคือ: ตั้งค่าใน config (daemon.json) ก่อน แล้ว push แบบปกติ
📁 แก้ /etc/docker/daemon.json
```bash
sudo nano /etc/docker/daemon.json
```

```bash
{
  "insecure-registries": ["43.209.49.162:32000"]
}
```

สร้างหรือแก้ /etc/rancher/k3s/registries.yaml
```bash
sudo mkdir -p /etc/rancher/k3s
sudo nano /etc/rancher/k3s/registries.yaml
```
ใส่เนื้อหานี้:
```bash
mirrors:
  "43.209.49.162:32000":
    endpoint:
      - "http://43.209.49.162:32000"
```

```bash
curl -X GET http://43.209.49.162:32000/v2/_catalog
```

```bash
kubectl create namespace streamlit
kubectl apply -f ./ --namespace=streamlit
```

### ลบทุกอย่าง
```bash
kubectl delete all --all -n streamlit
```
---
## inspect-registry
executable
```bash
chmod +x inspect-registry.sh
```
ติดตั้ง jq
```bash
sudo apt install jq 
```
run
```bash
./inspect-registry.sh
```
---
### docker without sudo วิธีทำบน Ubuntu / Debian
* สร้าง group docker (ถ้ายังไม่มี)
```bash
sudo groupadd docker
```
(ถ้ามีอยู่แล้วจะขึ้นว่า group มีอยู่แล้ว ไม่เป็นไร)

* เพิ่ม user ปัจจุบันเข้า group docker
```bash
sudo usermod -aG docker $USER
```
หรือระบุชื่อ user ตรง ๆ:
```bash
sudo usermod -aG docker ubuntu
```
* รีโหลด session หรือ logout/login
คุณต้อง ออกจาก shell แล้วเข้ากลับมาใหม่ หรือรันคำสั่งนี้:
```bash
newgrp docker
```
เพื่อโหลด group ใหม่แบบไม่ต้อง logout

* ทดสอบ
```bash
docker ps
```

### Postgres Extesion (Needed)
```bash
dblink
```

#### How to backup view or schema fom database
ถ้าคุณใช้ DBeaver:
1. คลิกขวาที่ชื่อ View
2. เลือก ➜ Generate SQL ➜ DDL
3. Copy แล้วบันทึกลงไฟล์ .sql