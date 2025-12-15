# Scope dorker

Scope dorker is a tool to perform Google dorks across all or specific programs on bug bounty platforms. Any programs with domain scope that matches the Google dork will be printed in the results.

## Requirements

This tool makes use of the following API's and as such requires API keys to be setup.

- Hackerone programs/scopes list API (`https://api.hackerone.com/hacker-resources/#programs-get-programs` and `https://api.hackerone.com/hacker-resources/#programs-get-structured-scopes`) - `https://hackerone.com/settings/api_token/edit`
- A Google Customisable Search Engine (`https://programmablesearchengine.google.com/about/`) configured to search the entire web.
- A Google API key for the custom-search JSON API `https://developers.google.com/custom-search/v1/overview`

## Setup

## Part 1: Setting up a Google Programmable Search Engine and Getting the CSE-ID

The CSE-ID is a unique identifier for your search engine configuration.

### 1. Navigate to the PSE Platform

Go to the [Google Programmable Search Engine website](https://programmablesearchengine.google.com/) and sign in with your Google Account.

### 2. Create a New Search Engine

* Click the **"Add"** or **"Get Started"** button to begin the setup.

### 3. Configure the Engine

* **Sites to search:** Enter the domain(s) or URL pattern(s) you wish to index (e.g., `example.com/*`).
    * *Note: If you plan to search the entire web, you still must enter at least one site initially.*
* **Name of the search engine:** Provide a descriptive name (e.g., "My App Search").
* Click the **"Create"** button.

### 4. Retrieve the Search Engine ID (CSE-ID)

* After creation, you will be taken to the engine's **Overview** page.
* The **Search Engine ID** (CSE-ID) is displayed prominently on this page.
* **Copy and save this ID.** It is a long alphanumeric string (e.g., `a5b7c9d1e3f5g7h9i1j3k5l7`).

### 5. Enable Web Search

* Navigate to the **"Basics"** section.
* Ensure the setting for **"Search the entire web"** is toggled **ON**.

---

## Part 2: Creating an API Key in Google Cloud Console

The API key provides secure access to Google's Custom Search JSON API.

### Step A: Set up a Project and Enable the API

### 1. Go to Google Cloud Console

Navigate to the [Google Cloud Console](https://console.cloud.google.com/) and sign in.

### 2. Select or Create a Project

* Use the project selector dropdown at the top to select an existing project or create a **"New Project"**.

### 3. Enable the Custom Search API

* Use the **Search bar** at the top of the console.
* Search for **"Custom Search API"**.
* Click on the result and click the **"Enable"** button.

### Step B: Generate and Secure the API Key

### 4. Navigate to Credentials

* In the left-hand navigation menu, go to **"APIs & Services"** -> **"Credentials"**.

### 5. Generate the API Key

* Click the **"+ Create Credentials"** button.
* Select **"API key"** from the dropdown menu.
* A popup window will display the newly generated API key.
* **Copy and save this key immediately.**

### 6. Secure the API Key (Crucial Security Step)

* Click **"Restrict key"** on the generated key.
* Under **"API restrictions,"** select the radio button to restrict the key.
* Choose the **"Custom Search API"** from the list of available APIs.
* Click **"Save"**. This ensures the key can only be used for its intended purpose.

---

### ✅ Summary of Required Values

You are now ready to use the API with the following credentials:

* **Search Engine ID (CSE-ID):** *(From Part 1)*
* **API Key:** *(From Part 2)*


### Installation steps

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
| `apis.google.program-result-limit` | Max results to collect per program before stopping the search. (Google restricts each search to a maximum of 10 results per query) | `20` |
| `apis.google.search-limit` | Daily limit for Custom Search queries; first 100 queries are free, every 1000 queries past this is chargeable (at time of writing this was $5). | `1000` |


## Program use

### Search all scopes across all programs

Note this can be slow as it has to (a) fetch all program scopes from HackerOne and (b) perform multiple Google searches (which are restricted to 100 searches per minute).

```powershell
python scope-dorker.py --query "inurl:/content/dam"
```

### Search all scopes for specific programs

```powershell
python scope-dorker.py --query "inurl:/content/dam" --programs goldmansachs x 
```

### Output scopes to a file

Fetching scopes can be slow, so you can save the scopes to a file for later reuse.

```powershell
python scope-dorker.py --output-scopes /home/hacker/all-scopes.json
```

or 

```powershell
python scope-dorker.py --programs goldmansachs x --output-scopes /home/hacker/selected-scopes.json
```

### Reading scopes from a file

You can read previously saved scopes from a file instead of fetching them from HackerOne each time.

```powershell
python scope-dorker.py --query "inurl:/content/dam" --input-scopes /home/hacker/all-scopes.json
```

### Arguments:

- `--query` / `-q`: required search fragment to append to each scoped `site:` clause.
- `--programs` / `-p`: optional list of HackerOne handles to narrow the search, space separated (defaults to all programs).
- `--exclude-out-of-scope` / `-eos`: when present, only assets eligible for bounty are included; by default all scoped assets are considered.
- `--input-scopes` / `-is`: optional path to a JSON file containing previously saved program scopes.
- `--output-scopes` / `-os`: optional path to save fetched program scopes to a JSON file.

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



