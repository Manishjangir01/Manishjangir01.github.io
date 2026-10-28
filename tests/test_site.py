"""Checks that the static site is consistent: no broken local links, every repo
link points at a real repo of this account, the numbers match, and the page has
the structure a visitor and a screen reader need. Standard library only."""

from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
USER = "Manishjangir01"

REPOS = {
    "big-data-analytics-pipeline",
    "web-scraping-data-pipeline",
    "sales-etl-pipeline",
    "ml-intern-portfolio",
    "Student-Management-SQL-Project",
    "SQL-Data-Analysis-Task-2",
    "SQL-Data-Analysis-Internship-Task-3",
    "Data-EDA-and-Visualization",
    "Pandas-Library-for-Data-Science",
    "NumPy-Basics-for-Data-Science",
    "DataFlow-ETL-Studio",
}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []          # (tag, attribute, value)
        self.ids = []
        self.headings = []       # (level, text)
        self.repo_items = []     # data-repo values
        self.images = []         # attrs of <img>
        self.html_lang = None
        self.title = ""
        self._in = None
        self._buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.html_lang = a.get("lang")
        if "id" in a:
            self.ids.append(a["id"])
        if tag in ("a", "link") and a.get("href"):
            self.links.append((tag, "href", a["href"]))
        if tag == "script" and a.get("src"):
            self.links.append((tag, "src", a["src"]))
        if tag == "img":
            self.images.append(a)
        if tag == "li" and "data-repo" in a:
            self.repo_items.append(a["data-repo"])
        if tag in ("h1", "h2", "h3", "title"):
            self._in, self._buf = tag, ""

    def handle_data(self, data):
        if self._in:
            self._buf += data

    def handle_endtag(self, tag):
        if tag == self._in:
            text = " ".join(self._buf.split())
            if tag == "title":
                self.title = text
            else:
                self.headings.append((int(tag[1]), text))
            self._in = None


def load():
    page = Page()
    page.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    return page


def test_page_basics():
    page = load()
    assert page.html_lang == "en"
    assert page.title
    h1 = [t for level, t in page.headings if level == 1]
    assert h1 == ["Manish Jangir"]
    assert len(page.ids) == len(set(page.ids)), "duplicate id"


def test_heading_levels_do_not_skip():
    levels = [level for level, _ in load().headings]
    for before, after in zip(levels, levels[1:]):
        assert after <= before + 1, f"heading jumps from h{before} to h{after}"


def test_local_links_and_anchors_resolve():
    page = load()
    for tag, attr, value in page.links:
        if value.startswith(("http://", "https://", "mailto:")):
            continue
        if value.startswith("#"):
            assert value[1:] in page.ids, f"missing anchor {value}"
        else:
            assert (ROOT / value).is_file(), f"missing file {value}"


def test_github_links_point_at_known_repos():
    page = load()
    pattern = re.compile(rf"^https://github\.com/{USER}(?:/([^/?#]+))?/?$")
    for _, _, value in page.links:
        if "github.com" not in value:
            continue
        match = pattern.match(value)
        assert match, f"unexpected GitHub link {value}"
        repo = match.group(1)
        assert repo is None or repo in REPOS, f"unknown repo {repo}"


def test_every_repo_is_listed_once():
    items = load().repo_items
    assert sorted(items) == sorted(REPOS)


def test_repo_links_match_their_list_item():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for repo in REPOS:
        assert f'<li data-repo="{repo}"><a href="https://github.com/{USER}/{repo}">{repo}</a>' in html


def test_pipeline_numbers_add_up():
    raw, dup, rejected, clean = 202_000, 2_000, 10_631, 189_369
    assert raw - dup - rejected == clean
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    for number in ("202,000", "2,000", "10,631", "189,369"):
        assert number in html
    widths = [float(w) for w in re.findall(r'style="--w:([0-9.]+)"', html)]
    assert len(widths) == 3
    assert abs(sum(widths) - 100) < 0.05
    assert abs(widths[0] - clean / raw * 100) < 0.05
    assert abs(widths[1] - rejected / raw * 100) < 0.05
    assert abs(widths[2] - dup / raw * 100) < 0.05


def test_resume_is_a_single_page_pdf():
    data = (ROOT / "assets" / "Manish_Jangir_Resume.pdf").read_bytes()
    assert data.startswith(b"%PDF")
    assert len(re.findall(rb"/Type\s*/Page[^s]", data)) == 1


def test_no_tool_attribution_anywhere():
    banned = re.compile(r"claude|anthropic|co-authored-by|generated with", re.I)
    for path in ROOT.rglob("*"):
        if path.is_file() and ".git" not in path.parts and path.suffix in {".html", ".css", ".js", ".md", ".yml", ".svg", ".py", ".txt"}:
            if path.name == "test_site.py":
                continue
            assert not banned.search(path.read_text(encoding="utf-8")), path


def test_page_does_not_publish_a_phone_number():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert not re.search(r"\b\d{10}\b", html)
