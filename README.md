# Scope dorker

Scope dorker is a tool to perform Google dorks across all or specific programs on bug bounty platforms. Any programs with domain scope that matches the Google dork will be printed in the results.

## Requirements

This tool makes use of the following API's and as such requires API keys to be setup.

- Hackerone programs/scopes list API (`https://api.hackerone.com/hacker-resources/#programs-get-programs` and `https://api.hackerone.com/hacker-resources/#programs-get-structured-scopes`)
- Google Custom Search API `https://developers.google.com/custom-search/v1/overview` - API Key and Custom Search Engine ID (cse-id)

## Setup

1. Clone the repository and change into it:
	```powershell
	git clone https://github.com/pdstat/scope-dorker.git
	cd scope-dorker
	```
2. Install Python dependencies from `requirements.txt`:
	```powershell
	python -m pip install -r requirements.txt
	```
3. Configure API credentials by editing the file created at `~/.config/scope-dorker/config.json`.

## Configuration

When you first run the tool it creates `config.json` under `~/.config/scope-dorker/`. Populate the values with the API keys and limits the script should use. The same directory also contains `search-count.json`, which the program updates to track how many Custom Search queries have run each day.

| Property | Description | Default value |
| --- | --- | --- |
| `apis.h1.username` | HackerOne username used to authenticate the program API. | `<insert-your-h1-username>` |
| `apis.h1.api-key` | HackerOne API key (secret token) paired with the username. | `<insert-your-h1-api-key>` |
| `apis.google.api-key` | Google Custom Search API key. | `<insert-your-google-api-key>` |
| `apis.google.cse-id` | Google Custom Search Engine (CSE) ID, also known as the `cx` parameter. | `<insert-your-google-cse-id>` |
| `apis.google.program-result-limit` | Max results to collect per program before stopping the search. | `20` |
| `apis.google.search-limit` | Daily limit for Custom Search queries; first 100 queries are free, every 1000 queries past this a chargeable (at time of writing this was $5). | `1000` |


## Program use

```powershell
python scope-dorker.py --query "inurl:/content/dam" --programs goldmansachs --exclude-out-of-scope
```

Arguments:

- `--query` / `-q`: required search fragment to append to each scoped `site:` clause.
- `--programs` / `-p`: optional list of HackerOne handles to narrow the search (defaults to all programs).
- `--exclude-out-of-scope` / `-eos`: when present, only assets eligible for bounty are included; by default all scoped assets are considered.

Sample console output (when matches exist):

```
# Results for Program goldmansachs matching query 'inurl:/content/dam'
https://www.gsam.com/content/dam/gsam/pdfs/international/en/prospectus-and-regulatory/annual-financial-statement/ar_ii_plc_en.pdf?sa=n&rd=n
https://www.gsam.com/content/dam/gsam/pdfs/common/en/public/articles/2022/am-gender-retirement-report-2022.pdf?sa=n&rd=n
https://www.gsam.com/content/dam/gsam/pdfs/common/en/public/miscellaneous/GSAM_Stewardship_Report.pdf?sa=n&rd=n
https://www.gsam.com/content/dam/gsam/pdfs/common/en/public/articles/global-equity-outlook/investing-in-the-millennial-effect.pdf?sa=n&rd=n
https://www.gsam.com/content/dam/gsam/pdfs/institutions/en/articles/2017/indexing-and-the-evolution-of-active-management.pdf?sa=n&rd=n
https://www.gsam.com/content/dam/gsam/pdfs/us/en/tax-information/tax_guide.pdf?sa=n&rd=n
```



