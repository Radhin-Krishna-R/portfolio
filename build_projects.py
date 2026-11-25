"""
Scans projects/*.html for <meta name="project:*"> tags and writes projects-data.js.

Usage:  python build_projects.py
Run it after adding or editing a project page.
"""
import json
import pathlib
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent
PROJECTS_DIR = ROOT / "projects"
OUTPUT_FILE = ROOT / "projects-data.js"


class MetaReader(HTMLParser):
    """Collects <meta name="project:..." content="..."> tags."""

    def __init__(self):
        super().__init__()
        self.data = {}

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return
        attrs = dict(attrs)
        name = attrs.get("name", "") or ""
        if name.startswith("project:"):
            self.data[name[len("project:"):]] = attrs.get("content", "") or ""


def read_project(page: pathlib.Path):
    reader = MetaReader()
    reader.feed(page.read_text(encoding="utf-8"))
    meta = reader.data

    if not meta.get("title"):
        print(f"  skipped {page.name}: missing project:title")
        return None

    try:
        order = int(meta.get("order", 999))
    except ValueError:
        order = 999

    return {
        "_order": order,
        "title": meta["title"],
        "category": meta.get("category", "Uncategorized"),
        "description": meta.get("description", ""),
        "tags": [t.strip() for t in meta.get("tags", "").split(",") if t.strip()],
        "actionLabel": meta.get("action", "View Project"),
        "link": f"projects/{page.name}",
        "image": meta.get("image", ""),
    }


def main():
    if not PROJECTS_DIR.exists():
        raise SystemExit(f"Folder not found: {PROJECTS_DIR}")

    projects = []
    for page in sorted(PROJECTS_DIR.glob("*.html")):
        project = read_project(page)
        if project:
            projects.append(project)

    projects.sort(key=lambda p: (p["_order"], p["title"]))
    for p in projects:
        del p["_order"]

    js = "const projectsData = " + json.dumps(projects, indent=2, ensure_ascii=False) + ";\n"
    OUTPUT_FILE.write_text(js, encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE.name} with {len(projects)} project(s)")


if __name__ == "__main__":
    main()
