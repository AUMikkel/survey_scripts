import requests
import os
import json
import time
from urllib.parse import quote
from pathlib import Path


class ScopusCiterFetcher:
    def __init__(self, api_key=None, page_size=25, max_results=5000, delay=1.0):
        self.api_key = api_key or os.getenv("SCOPUS_API_KEY")
        self.page_size = page_size
        self.max_results = max_results
        self.delay = delay

        self.headers = {
            "Accept": "application/json",
            "X-ELS-APIKey": self.api_key
        }

    def clean_scopus_id(self, sid: str):
        """Normalize Scopus ID by removing prefixes."""
        return (
            str(sid)
            .replace("SCOPUS_ID:", "")
            .replace("2-s2.0-", "")
            .strip()
        )

    def fetch_page(self, scopus_id: str, start: int):
        """Fetch one paginated block of citing papers."""
        query = f"REF({scopus_id})"
        url = (
            "https://api.elsevier.com/content/search/scopus?"
            f"query={quote(query)}&start={start}&count={self.page_size}"
        )

        resp = requests.get(url, headers=self.headers)
        print("6")
        if resp.status_code != 200:
            print(f"⚠️ Error {resp.status_code} at start={start} for {scopus_id}")
            return None

        return resp.json()

    def extract_entries(self, data_json):
        """Extract citing-paper info from JSON."""
        if not data_json:
            return []

        entries = data_json.get("search-results", {}).get("entry", [])
        if len(entries) == 1 and "error" in entries[0]:
                return []  # Zero citations
        results = []

        for e in entries:
            results.append({
                "title": e.get("dc:title", ""),
                "doi": e.get("prism:doi", ""),
                "scopus_id": e.get("dc:identifier", "").replace("SCOPUS_ID:", ""),
                "year": e.get("prism:coverDate", "")[:4],
                "type": e.get("subtypeDescription", "")
            })

        return results

    def fetch_all_citers(self, scopus_id: str):
        """Fetch ALL citing documents for a single Scopus ID."""
        scopus_id = self.clean_scopus_id(scopus_id)
        print("4")
        all_results = []

        start = 0
        while start < self.max_results:
            print("5")
            data_json = self.fetch_page(scopus_id, start)
            #print(f"data_json: {data_json}")
            # Stop if no data or no entries
            if not data_json:
                break

            entries = self.extract_entries(data_json)
            #print(f"entries: {entries}")
            #print(not entries)
            if not entries:
                break

            all_results.extend(entries)

            start += self.page_size
            time.sleep(self.delay)

        return all_results


class HMLVCitationCollector:
    """Wrapper that loads HMLV papers, fetches citers, and saves results."""

    def __init__(self, input_json, output_json, fetcher: ScopusCiterFetcher):
        self.input_json = input_json
        self.output_json = output_json
        self.fetcher = fetcher

        # Load previously scraped data (incremental)
        if Path(output_json).exists():
            with open(output_json, "r") as f:
                self.citing_data = json.load(f)
        else:
            self.citing_data = {}

    def load_hmlv_papers(self):
        """Load list of HMLV papers."""
        with open(self.input_json, "r") as f:
            papers = json.load(f)
        return papers

    def save_progress(self):
        with open(self.output_json, "w") as f:
            json.dump(self.citing_data, f, indent=2)

    def run(self):
        """Fetch citing documents for all HMLV papers."""
        papers = self.load_hmlv_papers()
        print("1")
        print(f"📚 Loaded {len(papers)} HMLV papers")

        for i, paper in enumerate(papers, start=1):
            print("2")
            sid = paper.get("scopus_id")
            sid = self.fetcher.clean_scopus_id(sid)
            print("3")
            if not sid:
                continue

            if sid in self.citing_data:
                print(f"[{i}] Skipping {sid} (already fetched)")
                continue

            print(f"[{i}] Fetching citers for {sid}...")
            citers = self.fetcher.fetch_all_citers(sid)
            self.citing_data[sid] = citers

            print(f"    ✅ {len(citers)} citing documents saved\n")
            self.save_progress()
            time.sleep(1)

        print(f"🎉 All results saved to {self.output_json}")


if __name__ == "__main__":
    # Build the fetcher (configurable)
    fetcher = ScopusCiterFetcher(
        api_key="499c7adfaec4012d980a27113349857d",
        page_size=25,
        max_results=5000,
        delay=0.8,
    )

    collector = HMLVCitationCollector(
        input_json="hmlv_dss_results.json",      # your converted CSV
        output_json="citing_hmlv.json",
        fetcher=fetcher
    )

    collector.run()
