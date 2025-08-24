# sysdash — System Health Dashboard (CLI)

Cross-platform system health **CLI** written in Python.  
Reports **CPU, memory, disk, network** stats and **top processes**.  
Exports **JSON** and **HTML** reports.

> Works on Windows, macOS, Linux. Requires Python 3.9+.

## Install
```bash
cd sysdash   # repo root
python -m venv .venv
# activate
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# install in editable mode
pip install -e .
```
## Usage
```bash
sysdash --pretty
sysdash --json out/report.json --html out/report.html
```
