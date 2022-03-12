# Lab3 Http service

## Server

### Usage

Port is 9009. Filename is provided via url. Example: <http://127.0.0.1:9009/server.py>

### Launch

```bash
python server.py --max_threads <number of threads>
```

## Client

### Usage

```bash
python client.py <host> <port> <filename>
```

Example:

```bash
python client.py 127.0.0.1 9009 server.py
```
