from __future__ import annotations
import html
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

def render_html(data: Dict[str, Any], template_path: str) -> str:
    tpl = Path(template_path).read_text(encoding="utf-8")

    def human_bytes(n: int) -> str:
        step = 1024.0
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if n < step:
                return f"{n:,.0f} {unit}"
            n /= step
        return f"{n:,.0f} PB"

    meta = data.get("meta", {})
    cpu = data.get("cpu", {})
    mem = data.get("memory", {})
    disks = data.get("disks", [])
    nics = data.get("network", [])
    procs = data.get("processes", [])

    disks_rows = "\n".join(
        f"<tr><td>{html.escape(d['device'])}</td>"
        f"<td>{html.escape(d['mountpoint'])}</td>"
        f"<td>{html.escape(d['fstype'])}</td>"
        f"<td>{human_bytes(d['total'])}</td>"
        f"<td>{human_bytes(d['used'])}</td>"
        f"<td>{human_bytes(d['free'])}</td>"
        f"<td>{d['percent']}%</td></tr>"
        for d in disks
    )

    nic_rows = "\n".join(
        f"<tr><td>{html.escape(n['name'])}</td>"
        f"<td>{n['bytes_sent']:,}</td>"
        f"<td>{n['bytes_recv']:,}</td>"
        f"<td>{n.get('packets_sent',0):,}</td>"
        f"<td>{n.get('packets_recv',0):,}</td></tr>"
        for n in nics
    )

    proc_rows = "\n".join(
        f"<tr><td>{p['pid']}</td>"
        f"<td>{html.escape(p['name'])}</td>"
        f"<td>{html.escape(p.get('username') or '')}</td>"
        f"<td>{p['cpu_percent']:.1f}%</td>"
        f"<td>{p['memory_percent']:.1f}%</td>"
        f"<td>{p['rss']:,}</td></tr>"
        for p in procs
    )

    per_core = ", ".join(f"{v:.1f}%" for v in cpu.get("per_core_percent", []))

    out = tpl.replace("{{TITLE}}", "System Health Report")              .replace("{{DATETIME}}", datetime.utcfromtimestamp(meta.get("timestamp", 0)).strftime("%Y-%m-%d %H:%M:%S UTC"))              .replace("{{PLATFORM}}", html.escape(meta.get("platform", "")))              .replace("{{SYSTEM}}", html.escape(meta.get("system", "")))              .replace("{{RELEASE}}", html.escape(meta.get("release", "")))              .replace("{{MACHINE}}", html.escape(meta.get("machine", "")))              .replace("{{PYTHON}}", html.escape(meta.get("python_version", "")))              .replace("{{CPU_LOAD}}", f"{cpu.get('load_percent', 0):.1f}%")              .replace("{{CPU_CORES}}", f"{cpu.get('physical_cores',0)} phys / {cpu.get('logical_cores',0)} logical")              .replace("{{CPU_FREQ}}", f"{cpu.get('freq_current_mhz') or 0:.0f} MHz")              .replace("{{CPU_PER_CORE}}", per_core)              .replace("{{MEM_USED}}", f"{mem.get('percent',0):.1f}%")              .replace("{{DISKS_ROWS}}", disks_rows or "<tr><td colspan='7'>No disks</td></tr>")              .replace("{{NICS_ROWS}}", nic_rows or "<tr><td colspan='5'>No network interfaces</td></tr>")              .replace("{{PROCS_ROWS}}", proc_rows or "<tr><td colspan='6'>Process list disabled</td></tr>")

    return out
