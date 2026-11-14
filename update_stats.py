import os, re, json, datetime, urllib.parse, urllib.request

# ---- EDIT THESE ----------------------------------------------------------
USER = os.environ.get("GH_USER", "YOUR_GITHUB_USERNAME")
HOST = "hunza"
EMAIL = "arkalibaig@gmail.com"
INFO = [
    ("Role", "BS-AI student and freelance data scientist"),
    ("School", "SZABIST Islamabad, Robotics & AI"),
    ("Based in", "Hunza, Gilgit-Baltistan, Pakistan"),
    ("Stack", "Python, TensorFlow, scikit-learn, pandas, NumPy"),
]
WORK = [
    ("NLP", "Burushaski parallel corpus + translation model"),
    ("Dataset", "Karakoram ERA5 climate data (Kaggle, Zenodo)"),
    ("Analysis", "Ultar Glacier NDSI with Earth Engine"),
]
# --------------------------------------------------------------------------

W = 64
TOKEN = os.environ.get("GITHUB_TOKEN")

def api(path):
    req = urllib.request.Request("https://api.github.com" + path)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "profile-readme-updater")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)

def total_stars():
    total, page = 0, 1
    while True:
        repos = api(f"/users/{USER}/repos?per_page=100&page={page}")
        if not repos:
            return total
        total += sum(r["stargazers_count"] for r in repos)
        page += 1

def row(label, value):
    dots = "." * max(2, W - len(label) - len(str(value)) - 4)
    return f". {label} {dots} {value}"

def head(title):
    return f"{title} " + "-" * max(2, W - len(title) - 1)

def build():
    u = api(f"/users/{USER}")
    year = datetime.date.today().year
    q = urllib.parse.quote(f"author:{USER} author-date:>={year}-01-01")
    commits = api(f"/search/commits?q={q}")["total_count"]
    lines = []
    if os.path.exists("art.txt"):
        lines += open("art.txt", encoding="utf-8").read().rstrip("\n").split("\n") + [""]
    lines += [head(f"{USER.lower()}@{HOST}")]
    lines += [row(k, v) for k, v in INFO]
    lines += ["", head("- Work")]
    lines += [row(k, v) for k, v in WORK]
    lines += ["", head("- Contact")]
    lines += [row("Email", EMAIL)]
    lines += ["", head("- GitHub Stats")]
    lines += [
        row("Repos", u["public_repos"]),
        row("Stars", total_stars()),
        row("Followers", u["followers"]),
        row(f"Commits ({year})", commits),
    ]
    return "\n".join(lines)

START, END = "<!-- STATS:START -->", "<!-- STATS:END -->"
text = open("README.md", encoding="utf-8").read()
block = f"{START}\n```\n{build()}\n```\n{END}"
new = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda m: block, text, flags=re.S)
if new != text:
    open("README.md", "w", encoding="utf-8").write(new)
    print("README updated")
else:
    print("no change")
