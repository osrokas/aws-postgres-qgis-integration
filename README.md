# AWS Postgres QGIS Integration

# Project Setup

This project uses LocalStack to simulate AWS services locally. Follow these steps to set up your environment

## 1. Install LocalStack via Docker (for local development)

```
docker run --rm -it -p 4566:4566 -p 4571:4571 localstack/localstack
```

## 2. Create virtual environment

```
python -m venv .venv
```

## 3. Activate virtual environment

### For Windows

```
.venv\Scripts\activate
```

### For Linux/Mac

```
source .venv/bin/activate
```

## 4. Install Python Dependencies

```
pip install -r requirements.txt
```