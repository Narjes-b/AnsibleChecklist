import os
import time
import csv
import re
import requests

# =========================================================
# CONFIG
# =========================================================
GITHUB_API = "https://api.github.com"
#TOKEN = os.getenv("GITHUB_TOKEN")
TOKEN = "add your token here"
if not TOKEN:
    raise RuntimeError("Set GITHUB_TOKEN first, e.g. export GITHUB_TOKEN='...'")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "User-Agent": "tf-repo-crawler"
}

# Search only repositories created from 2020 onward
REPO_QUERY = "language:HCL stars:>1 archived:false created:>=2020-01-01"

PAGES = 5
PER_PAGE = 100
MIN_COMMITS = 1
MIN_CONTRIBUTORS = 1

SLEEP_BETWEEN_CALLS = 0.25
PRINT_RATE_LIMIT_EVERY = 25

OUT_CSV = "/Users/narjes/Documents/Research/JointResearch/SecurityReverts/TF_Projects.csv"

LINK_LAST_RE = re.compile(r'page=(\d+)>;\s*rel="last"')

# =========================================================
# HTTP / RATE LIMIT HELPERS
# =========================================================
def gh_get(url, params=None, max_retries=6, timeout=30):
    """
    GitHub GET with handling for:
    - primary rate limits
    - secondary rate limits / abuse protection
    - transient server errors
    """
    delay = 5
    last_error = None

    for attempt in range(max_retries):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=timeout)
        except requests.RequestException as e:
            last_error = e
            print(f"[network] {e}; sleeping {delay}s")
            time.sleep(delay)
            delay = min(delay * 2, 120)
            continue

        remaining = r.headers.get("X-RateLimit-Remaining")
        reset = r.headers.get("X-RateLimit-Reset")
        retry_after = r.headers.get("Retry-After")

        # Primary rate limit exhausted
        if r.status_code in (403, 429) and remaining == "0":
            wait = max(0, int(reset or "0") - int(time.time()) + 2)
            print(f"[primary-rate-limit] sleeping {wait}s")
            time.sleep(wait)
            continue

        # Secondary rate limit or abuse protection
        if r.status_code in (403, 429):
            if retry_after is not None:
                wait = int(retry_after) + 2
            else:
                wait = delay
                delay = min(delay * 2, 120)
            print(f"[secondary-limit] status={r.status_code}, sleeping {wait}s")
            time.sleep(wait)
            continue

        # Transient GitHub errors
        if r.status_code in (500, 502, 503, 504):
            print(f"[server-error] status={r.status_code}, sleeping {delay}s")
            time.sleep(delay)
            delay = min(delay * 2, 120)
            continue

        r.raise_for_status()
        return r

    if last_error:
        raise last_error
    raise RuntimeError(f"Request failed after retries: {url}")

def gh_get_json(url, params=None):
    return gh_get(url, params=params).json()

def get_rate_limit():
    return gh_get_json(f"{GITHUB_API}/rate_limit")

def print_rate_limit():
    try:
        data = get_rate_limit()
        resources = data.get("resources", {})
        for bucket in ["core", "search", "code_search", "graphql"]:
            if bucket in resources:
                b = resources[bucket]
                print(
                    f"[rate-limit] {bucket}: "
                    f"remaining={b.get('remaining')} / {b.get('limit')} "
                    f"reset={b.get('reset')}"
                )
    except Exception as e:
        print(f"[rate-limit] could not fetch: {e}")

# =========================================================
# API HELPERS
# =========================================================
def search_repositories(query, pages=1, per_page=100):
    """
    Search repositories page by page.
    """
    for page in range(1, pages + 1):
        data = gh_get_json(
            f"{GITHUB_API}/search/repositories",
            params={
                "q": query,
                "sort": "stars",
                "order": "desc",
                "page": page,
                "per_page": per_page,
            },
        )
        items = data.get("items", [])
        print(f"[search] page={page} repos={len(items)}")
        if not items:
            break
        yield from items

def get_contributors_count(full_name):
    """
    Count contributors via pagination:
    per_page=1 + rel=last => approximately contributor count.
    """
    url = f"{GITHUB_API}/repos/{full_name}/contributors"
    r = gh_get(url, params={"per_page": 1, "anon": "true", "page": 1})

    link = r.headers.get("Link", "")
    if 'rel="last"' in link:
        m = LINK_LAST_RE.search(link)
        if m:
            return int(m.group(1))

    data = r.json()
    return len(data) if isinstance(data, list) else 0

def get_commit_count(full_name, branch):
    """
    Count commits via pagination:
    per_page=1 + rel=last => approximately commit count.
    """
    url = f"{GITHUB_API}/repos/{full_name}/commits"
    r = gh_get(url, params={"sha": branch, "per_page": 1, "page": 1})

    link = r.headers.get("Link", "")
    if 'rel="last"' in link:
        m = LINK_LAST_RE.search(link)
        if m:
            return int(m.group(1))

    data = r.json()
    return len(data) if isinstance(data, list) else 0

# =========================================================
# CSV / RESUME
# =========================================================
def load_seen_urls(csv_path):
    seen = set()
    if not os.path.exists(csv_path):
        return seen

    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = row.get("URL")
                if url:
                    seen.add(url)
        print(f"[resume] loaded {len(seen)} existing rows")
    except Exception as e:
        print(f"[resume] could not load existing CSV: {e}")

    return seen

def ensure_csv_header(csv_path):
    file_exists = os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
    if file_exists:
        return

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Name",
            "URL",
            "forks",
            "stars_count",
            "created_at",
            "updated_at",
            "fork",
            "archived",
            "contributors_count",
            "commits",
            "files_count",
            "tf_files_count",
        ])
    print(f"[csv] created {csv_path}")

# =========================================================
# MAIN
# =========================================================
def main():
    ensure_csv_header(OUT_CSV)
    seen = load_seen_urls(OUT_CSV)

    scanned = 0
    saved = 0
    enriched = 0

    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for repo in search_repositories(REPO_QUERY, pages=PAGES, per_page=PER_PAGE):
            scanned += 1

            url = repo["html_url"]
            full_name = repo["full_name"]

            if url in seen:
                continue

            # Cheap filters first, using fields already returned in search results
            if repo.get("archived", False):
                continue

            if repo.get("fork", False):
                # Keep or drop depending on your study design.
                # Dropping forks often reduces noise and API usage.
                continue

            created_at = repo.get("created_at", "")
            if not created_at.startswith(("2020", "2021", "2022", "2023", "2024", "2025", "2026")):
                continue

            try:
                default_branch = repo.get("default_branch") or "main"

                # Only now do extra API calls
                contributors_count = get_contributors_count(full_name)
                time.sleep(SLEEP_BETWEEN_CALLS)

                # Hard filter early to save one extra call when possible
                if contributors_count <= MIN_CONTRIBUTORS:
                    print(f"[skip] {full_name} | contributors={contributors_count}")
                    continue

                commit_count = get_commit_count(full_name, default_branch)
                time.sleep(SLEEP_BETWEEN_CALLS)

                enriched += 1

                if commit_count <= MIN_COMMITS:
                    print(f"[skip] {full_name} | commits={commit_count} | contributors={contributors_count}")
                    continue

                # You said these will be filled later after cloning/local analysis
                files_count = ""
                tf_files_count = ""

                writer.writerow([
                    repo["name"],
                    repo["html_url"],
                    repo["forks_count"],
                    repo["stargazers_count"],
                    repo["created_at"],
                    repo["updated_at"],
                    repo["fork"],
                    repo["archived"],
                    contributors_count,
                    commit_count,
                    files_count,
                    tf_files_count,
                ])
                f.flush()

                seen.add(url)
                saved += 1

                print(
                    f"[saved] {full_name} | "
                    f"stars={repo['stargazers_count']} | "
                    f"contributors={contributors_count} | "
                    f"commits={commit_count}"
                )

                if enriched % PRINT_RATE_LIMIT_EVERY == 0:
                    print_rate_limit()

            except requests.HTTPError as e:
                print(f"[http-error] {full_name}: {e}")
            except Exception as e:
                print(f"[error] {full_name}: {e}")

            time.sleep(SLEEP_BETWEEN_CALLS)

    print(f"Done. scanned={scanned}, enriched={enriched}, saved={saved}, output={OUT_CSV}")

if __name__ == "__main__":
    main()