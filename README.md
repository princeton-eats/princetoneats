# Princeton Eats

Welcome to Princeton Eats.

## Set-up Instructions

### 1. Clone the Repository

First, clone the repository from GitHub to your local machine:

```bash
git clone https://github.com/princeton-eats/princetoneats.git
cd princetoneats
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up pre-commit hooks

```bash
pre-commit install
```

### 5. Fetch and checkout the current development version
```bash
git checkout -b dev origin/dev
```

## Run the app on localhost:8000

```bash
python src/princetoneats/app.py 8000
```

--
Created by Yusuf, Adham, Ndongo, Achilles, Akuei
