# JSearch Internship Scanner

Automated scanner for SWE and Data Science internships in **NYC** and **Remote USA** via the [JSearch API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) (aggregates LinkedIn, Indeed, Glassdoor, ZipRecruiter).

## How it works

- Runs **Mon–Fri, every hour 8am–5pm EDT**
- Searches for software engineer and data science internships
- Filters for NYC metro or Remote USA only, excludes PhD roles
- Cross-repo deduplication with 4 sibling internship repos
- Posts new listings to Discord with `@everyone` ping

[![Discord](https://img.shields.io/badge/Discord-Live_Demo-5865F2?logo=discord&logoColor=white)](https://discord.gg/GfSRFugKd)

## Setup

Add these secrets to the repo (Settings → Secrets → Actions):

| Secret | Description |
|--------|-------------|
| `RAPIDAPI_KEY_1` | RapidAPI key from account 1 (handles SWE query) |
| `RAPIDAPI_KEY_2` | RapidAPI key from account 2 (handles Data Science query) |
| `DISCORD_WEBHOOK_URL` | Discord webhook URL for the target channel |
