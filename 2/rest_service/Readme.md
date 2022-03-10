# Lab 2

## Installation

```bash
pip isntall fastapi 
```

```bash
pip install "uvicorn[standard]"
```

## Usage

Launch server:

```bash
uvicorn main:app --reload
```

Server would be responding at <http://127.0.0.1:8000>.

Read image and print it in base64:

```bash
python read_image.py
```

Write image from **image_base64** file as jpg:

```bash
python save_image.py
```
