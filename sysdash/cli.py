from __future__ import annotations
import argparse
import json
from pathlib import Path
from typing import Any, Dict

from . import __version__
from .collector import collect
from .render import render_html


def _write_text(path: str, text: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _write_json(path: str, data: Dict[str, Any], pretty: bool = True) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2 if pretty else None), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="sysdash",
        description="System Health Dashboard (CPU/Mem/Disk/Net + top processes) with JSON/HTML export."
    )
    ap.add_argument("--top", type=int, default=5, help="Top N processes to include (default: 5)")
    ap.add_argument("--interval", type=float, default=1.0, help="Sampling interval for CPU%% (default: 1.0)")
    ap.add_argument("--json", dest="json_out", help="Write JSON report to this path")
    ap.add_argument("--html", dest="html_out", help="Write HTML report to this path")
    ap.add_argument("--pretty", action="store_true", help="Pretty-print JSON to stdout if no --json is given")
    ap.add_argument("--no-procs", action="store_true", help="Skip process listing")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = ap.parse_args()

    data = collect(interval=args.interval, top_n=args.top, include_procs=(not args.no_procs))

    # Write outputs if requested
    if args.json_out:
        _write_json(args.json_out, data, pretty=True)
    if args.html_out:
        tpl = Path(__file__).resolve().parent.parent / "templates" / "report_template.html"
        html = render_html(data, template_path=str(tpl))
        _write_text(args.html_out, html)

    # Default console behavior
    if not args.json_out and not args.html_out:
        print(json.dumps(data, indent=2 if args.pretty else None))
