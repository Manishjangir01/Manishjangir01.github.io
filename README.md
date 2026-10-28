# Manish Jangir, portfolio website

[![site checks](https://github.com/Manishjangir01/Manishjangir01.github.io/actions/workflows/check.yml/badge.svg)](https://github.com/Manishjangir01/Manishjangir01.github.io/actions/workflows/check.yml)
![License](https://img.shields.io/badge/license-MIT-green)

The source of my portfolio site: six data projects, all my GitHub repositories, skills, resume and contact details on one page. Plain HTML, CSS and a little JavaScript. No build step, no framework, no tracking.

Live site: https://manishjangir01.github.io

## What is on the page

| Section | What it shows |
|---------|---------------|
| Top | Name, one-line pitch, resume download, links |
| One pipeline run | Real counts from my PySpark project (202,000 rows read, 2,000 duplicates, 10,631 rejected, 189,369 clean) as a table and a bar |
| Projects | Six projects with the key number, tech, what is inside and a link to the code |
| All repositories | Every public repo. The list is in the HTML, and JavaScript adds language and last-updated date from the GitHub API |
| Skills, Contact | Grouped skills (what the projects used, and what I am still learning) and ways to reach me |

## Design choices

- **Works without JavaScript.** The page and the repository list are plain HTML. JavaScript only adds the theme switch and live repo details.
- **If the GitHub API is down or rate limited**, the saved list stays and a short note says so. Answers are cached in the browser for 30 minutes to stay under the API limit for visitors who are not signed in.
- **Dark theme by default**, with a light theme switch. The switch remembers the choice.
- **Accessible by default:** skip link, visible keyboard focus, text contrast checked for both themes, reduced motion respected, no horizontal scrolling on phones.
- **Honest labels:** the data behind all projects is synthetic or from practice sites, and the page says so. Projects 4, 5 and 6 say they were built with guidance from an AI mentor.

## Run it locally

```bash
python -m http.server 8000
# open http://localhost:8000
```

## Test it

```bash
pip install -r requirements-dev.txt
pytest -v
```

The tests read `index.html` and check that:

- every local link, anchor and file exists
- every GitHub link points at a repo that belongs to this account
- each repo is listed exactly once
- the pipeline numbers add up (202,000 - 2,000 - 10,631 = 189,369) and the bar widths match them
- the resume is a one-page PDF
- no phone number is written in the page

They do not open a browser. I checked the layout by hand at desktop and phone width, in light and dark theme, with the GitHub API both answering and blocked.

## Project layout

```
index.html              the whole page
assets/style.css        design tokens, light and dark theme, layout
assets/app.js           theme switch and live repository details
assets/favicon.svg
assets/Manish_Jangir_Resume.pdf
tests/test_site.py
.github/workflows/check.yml
```

## Publish with GitHub Pages

1. Name the repository exactly `Manishjangir01.github.io`.
2. Settings, Pages, Source: "Deploy from a branch", Branch: `main`, folder `/ (root)`, Save.
3. After a minute the site is at https://manishjangir01.github.io.

## Limitations

- The repository descriptions in the HTML are saved copies. If a repo is renamed or deleted, update `index.html`. The test fails until the list and the links agree.
- The page has no social preview image yet.
- Projects use synthetic data, so the numbers show how the pipelines behave, not results on a real business.

## License

MIT, see [LICENSE](LICENSE). The resume PDF is my own document and is not covered by the licence.
