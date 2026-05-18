import json
import os
import hashlib
import urllib.request
import urllib.parse

RAPIDAPI_KEY_1 = os.environ.get("RAPIDAPI_KEY_1", "")
RAPIDAPI_KEY_2 = os.environ.get("RAPIDAPI_KEY_2", "")
NOTIFIED_PATH = ".github/data/notified_hashes.json"

SIBLING_HASH_URLS = [
    "https://raw.githubusercontent.com/skarazan/Summer2027-Internships/dev/.github/scripts/notified_hashes.json",
    "https://raw.githubusercontent.com/skarazan/Summer2026-Internships-NYC/dev/.github/scripts/notified_hashes.json",
    "https://raw.githubusercontent.com/skarazan/Internships-2026/main/.github/data/notified_hashes.json",
    "https://raw.githubusercontent.com/skarazan/southeast-tech-internships-2026-2027/main/.github/data/notified_hashes.json",
]

QUERIES = [
    ("software engineer intern in new york OR remote", RAPIDAPI_KEY_1),
    ("data science intern in new york OR remote USA", RAPIDAPI_KEY_2),
]

def job_hash(company, title):
    key = f"{company.lower().strip()}|{title.lower().strip()}"
    return hashlib.md5(key.encode()).hexdigest()[:12]

def is_phd(title):
    t = title.lower()
    return "phd" in t or "ph.d" in t

def is_nyc_or_remote(job):
    city = (job.get("job_city") or "").lower()
    country = (job.get("job_country") or "").lower()
    remote = job.get("job_is_remote", False)

    if country and country not in ("us", "usa", "united states"):
        return False

    nyc = any(kw in city for kw in ("new york", "nyc", "brooklyn"))
    if "manhattan" in city and "beach" not in city:
        nyc = True

    remote_usa = remote and country in ("us", "usa", "united states", "")

    return nyc or remote_usa

def fetch_sibling_hashes():
    hashes = set()
    for url in SIBLING_HASH_URLS:
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                hashes.update(json.loads(resp.read()))
        except Exception:
            pass
    return hashes

def search_jsearch(query, api_key):
    url = "https://jsearch.p.rapidapi.com/search"
    params = urllib.parse.urlencode({
        "query": query,
        "date_posted": "today",
        "page": "1",
        "num_pages": "1",
    })
    req = urllib.request.Request(
        f"{url}?{params}",
        headers={
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read()).get("data", [])

notified = set()
if os.path.exists(NOTIFIED_PATH):
    with open(NOTIFIED_PATH) as f:
        notified = set(json.load(f))
sibling_hashes = fetch_sibling_hashes()
all_known = notified | sibling_hashes

all_jobs = []
seen_ids = set()

for q, api_key in QUERIES:
    print(f"Searching: {q}")
    try:
        results = search_jsearch(q, api_key)
        for job in results:
            jid = job.get("job_id", "")
            if jid in seen_ids:
                continue
            seen_ids.add(jid)
            title = job.get("job_title", "")
            company = job.get("employer_name", "")
            if is_phd(title):
                continue
            if not is_nyc_or_remote(job):
                continue
            h = job_hash(company, title)
            if h in all_known:
                continue
            all_jobs.append(job)
    except Exception as e:
        print(f"  Error: {e}")

print(f"Found {len(all_jobs)} new jobs after filtering + dedup")

output_file = os.environ.get("GITHUB_OUTPUT", "/dev/null")
if all_jobs:
    for job in all_jobs:
        notified.add(job_hash(job["employer_name"], job["job_title"]))
    os.makedirs(os.path.dirname(NOTIFIED_PATH), exist_ok=True)
    with open(NOTIFIED_PATH, "w") as f:
        json.dump(sorted(notified), f)

    MAX_SHOW = 5
    lines = []
    for job in all_jobs[:MAX_SHOW]:
        company = job["employer_name"]
        title = job["job_title"]
        city = job.get("job_city", "")
        state = job.get("job_state", "")
        loc = f"{city}, {state}".strip(", ")
        if job.get("job_is_remote"):
            loc = f"{loc} (Remote)" if loc else "Remote"
        url = job.get("job_apply_link", "")
        lines.append(f"🆕 **{company}** — {title}\n📍 {loc}\n🔗 <{url}>")
    extra = len(all_jobs) - len(lines)
    if extra > 0:
        lines.append(f"...and **{extra} more** — check the README")
    message = "@everyone\n\n" + "\n\n".join(lines)
    with open(".github/data/discord_message.txt", "w") as f:
        f.write(message)
    with open(output_file, "a") as f:
        f.write("has_jsearch=true\n")
else:
    with open(output_file, "a") as f:
        f.write("has_jsearch=false\n")
    print("No new listings to notify.")
