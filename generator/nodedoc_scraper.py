"""Scrape the node documentation of a device from the online user manual.

The LabOne Data Server provides the node documentation of a connected device
through ``listNodesJSON``. To generate type stubs without access to a device,
this module extracts the same information from the "Device Node Tree" chapter
of the user manual on https://docs.zhinst.com and stores it in the
``listNodesJSON`` format.

Index placeholders (``n``) in the documented paths are replaced by ``0`` and
the device id placeholder by ``DEVICE_SERIAL``.
"""

from __future__ import annotations

import datetime
import html
import json
import re
import urllib.request
from pathlib import Path
from typing import Any

import click

NODEDOC_URL = "https://docs.zhinst.com/{device}_user_manual/nodedoc.html"
NODEDOC_DIR = Path(__file__).parent / "nodedocs"
DEVICE_SERIAL = "dev0"

_NODE_BLOCK = re.compile(r'<details class="node">(.*?)</details>', re.DOTALL)
_SUMMARY = re.compile(r"<summary>\s*(/dev[^\s<]*)")
_TABLE = re.compile(r'<table class="node_info">(.*?)</table>', re.DOTALL)
_INFO_ROW = re.compile(r"<td><strong>(\w+):</strong></td>\s*<td>(.*?)</td>", re.DOTALL)
_OPTION_ROW = re.compile(r"<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>", re.DOTALL)
_PARAGRAPH = re.compile(r"<p>(?!</p>)(.*?)</p>", re.DOTALL)
_TAG = re.compile(r"<[^>]+>")


def _to_text(raw_html: str) -> str:
    """Convert an HTML fragment into plain text."""
    # The docs are rendered from markdown, where a ``*`` in formulas sometimes
    # gets interpreted as emphasis (e.g. ``P*Error + I*Int``).
    raw_html = raw_html.replace("<em>", "*").replace("</em>", "*")
    text = html.unescape(_TAG.sub("", raw_html))
    return " ".join(text.split())


def _to_node_path(documented_path: str) -> str:
    """Convert a documented node path into a concrete node path.

    Args:
        documented_path: Path as documented, e.g. ``/dev..../demods/n/freq``.

    Returns:
        Concrete path, e.g. ``/dev0/demods/0/freq``.
    """
    segments = documented_path.strip("/").split("/")
    segments[0] = DEVICE_SERIAL
    return "/" + "/".join("0" if s == "n" else s for s in segments)


def parse_nodedoc_html(page: str) -> dict[str, dict[str, Any]]:
    """Parse the node documentation html page into the ``listNodesJSON`` format.

    Args:
        page: Content of the ``nodedoc.html`` page of a user manual.

    Returns:
        Node documentation keyed by lower case node path.

    Raises:
        ValueError: If a node entry could not be parsed or no node was found.
    """
    nodes: dict[str, dict[str, Any]] = {}
    for block in _NODE_BLOCK.findall(page):
        summary = _SUMMARY.search(block)
        tables = _TABLE.findall(block)
        if summary is None or not tables:
            raise ValueError(f"Unable to parse node entry:\n{block}")
        path = _to_node_path(summary.group(1))
        info = {key: _to_text(value) for key, value in _INFO_ROW.findall(tables[0])}
        missing = {"Properties", "Type", "Unit"} - info.keys()
        if missing:
            raise ValueError(f"{path} misses {sorted(missing)}")
        description = " ".join(
            text for text in (_to_text(p) for p in _PARAGRAPH.findall(block)) if text
        )
        entry: dict[str, Any] = {
            "Node": path.upper(),
            "Description": description,
            "Properties": info["Properties"],
            "Type": info["Type"],
            "Unit": info["Unit"],
        }
        if len(tables) > 1:
            entry["Options"] = {
                _to_text(key): _to_text(value)
                for key, value in _OPTION_ROW.findall(tables[1])
            }
        nodes[path] = entry
    if not nodes:
        raise ValueError("No nodes found in the provided page.")
    return nodes


def fetch_nodedoc(device: str) -> dict[str, Any]:
    """Download and parse the node documentation of a device.

    Args:
        device: Device type, e.g. ``MFLI``.

    Returns:
        Dictionary with the source url, the retrieval date and the nodes.
    """
    url = NODEDOC_URL.format(device=device.lower())
    with urllib.request.urlopen(url) as response:  # noqa: S310 (fixed https url)
        page = response.read().decode("utf-8")
    return {
        "source": url,
        "retrieved": datetime.date.today().isoformat(),
        "nodes": parse_nodedoc_html(page),
    }


def nodedoc_path(device: str) -> Path:
    """Path of the stored node documentation for a device."""
    return NODEDOC_DIR / f"{device.lower()}.json"


def load_nodedoc(device: str) -> dict[str, dict[str, Any]]:
    """Load the stored node documentation for a device.

    Args:
        device: Device type, e.g. ``MFLI``.

    Returns:
        Node documentation in the ``listNodesJSON`` format.
    """
    with nodedoc_path(device).open(encoding="utf-8") as file:
        return json.load(file)["nodes"]


@click.command()
@click.argument("device", type=str)
def main(device: str) -> None:
    """Scrape the node documentation of DEVICE (e.g. MFLI) from docs.zhinst.com."""
    nodedoc = fetch_nodedoc(device)
    target = nodedoc_path(device)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(nodedoc, file, indent=2, ensure_ascii=False)
        file.write("\n")
    click.echo(f"Wrote {len(nodedoc['nodes'])} nodes to {target}")


if __name__ == "__main__":
    main()
