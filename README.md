# sysdash — System Health Dashboard (CLI)

Cross-platform system health **CLI** written in Python.  
Reports **CPU, memory, disk, network** stats and **top processes**.  
Exports **JSON** and **HTML** reports.

> Works on Windows, macOS, Linux. Requires Python 3.9+.

## Install
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix/macOS:
. .venv/bin/activate
pip install -e .
```
## Usage
```bash
sysdash --pretty
sysdash --json out/report.json --html out/report.html
```
