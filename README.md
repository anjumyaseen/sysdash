# sysdash — System Health Dashboard (CLI)

Cross-platform system health **CLI** written in Python.  
Reports **CPU, memory, disk, network** stats and **top processes**.  
Exports **JSON** and **HTML** reports.

> Works on Windows, macOS, Linux. Requires Python 3.9+.

## Features

- CPU load (overall + per-core), logical/physical cores
- Memory (used/available), swap
- Disk usage per mount
- Network I/O per interface
- Top N processes by CPU and memory
- Exports: **JSON** and **HTML**
- Single binary-style entry point: `sysdash`

## Install

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix/macOS:
. .venv/bin/activate
pip install -e .
```

## Usage

```
sysdash [options]

Options:
  --top N              Number of top processes (default: 5)
  --interval SECONDS   Sampling interval for CPU% (default: 1.0)
  --json PATH          Write JSON report to PATH
  --html PATH          Write HTML report to PATH (uses templates/report_template.html)
  --pretty             Pretty-print JSON to stdout (if no --json provided)
  --no-procs           Skip process listing (faster)
  --version            Show version and exit
```

### Examples

- Quick view to console:
  ```bash
  sysdash --pretty
  ```

- Save **JSON** and **HTML**:
  ```bash
  sysdash --json out/report.json --html out/report.html
  ```

- Limit processes and use a longer sample:
  ```bash
  sysdash --top 10 --interval 2.5 --pretty
  ```

## HTML Template

The HTML report is rendered from `templates/report_template.html`.  
You can customize branding/colors freely—no templating dependency required.

## Why this project?

- Simple, safe, and useful.
- Great DevOps portfolio piece (system introspection + packaging + CI).
- Clean code, no vendor lock-in.

## License

MIT © 2025 Anjum Yaseen — see [LICENSE](LICENSE).
