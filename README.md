# DOUBLE ACTION ONE – Admin Management System

This is the **admin panel** for Double Action, a luxury fashion brand for grooms and formal menswear.  
The system allows managing inventory, tracking customer orders, and viewing real-time analytics.

---

## 🚀 Getting Started

To run this system locally on your computer:

### 1. Clone the project
```bash
git clone https://github.com/GuyBD9/doubleactionproto.git
cd doubleactionproto
```

---

## 🧰 Setup Instructions (Mac & Windows)

### 📍 Prerequisite:
Make sure you have **Python 3.8+** installed. You can check with:
```bash
python3 --version  # or python --version on Windows
```

---

### 💻 Mac Users

#### 1. Open Terminal and navigate to the project folder:
Replace `/path/to/...` with the actual location where you saved the project.
```bash
cd /path/to/doubleactionproto
```

#### 2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install dependencies:
```bash
pip install -r requirements.txt
```

#### 4. Set up the database:
```bash
python database_setup.py
python seed_database.py
```

#### 5. Run the Flask server:
```bash
python app.py
```

#### 6. Open the system in your browser:
Open [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login) in Chrome

---

### 🪟 Windows Users

#### 1. Open CMD or PowerShell and go to the project folder:
Replace `path\to\...` with the actual location where you saved the project.
```bash
cd path\to\doubleactionproto
```

#### 2. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Install dependencies:
```bash
pip install -r requirements.txt
```

#### 4. Set up the database:
```bash
python database_setup.py
python seed_database.py
```

#### 5. Run the Flask server:
```bash
python app.py
```

#### 6. Open the system in your browser:
Open [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login) in Chrome

---

### ✅ Final Notes
- Do **NOT** double-click `login.html` or open with `file:///` — this will break the system.
- Make sure the Flask server is running before trying to access it from your browser.