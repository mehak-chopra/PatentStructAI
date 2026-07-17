"""
PatentStructAI HTML Search Report.

Generates a visual HTML report for search results.

The report is intended for:

- Developer debugging
- Result verification
- Manual inspection
- Demonstrations

Every search execution can optionally generate
one standalone HTML file.
"""

from __future__ import annotations

from datetime import datetime

from pathlib import Path

from search.search_result import (
    SearchResult,
)

import webbrowser


# ============================================================
# HTML Report
# ============================================================

class HTMLReport:
    """
    Generates HTML reports for search results.
    """

    def __init__(
        self,
        output_directory: str | Path = "reports",
    ):

        self.output_directory = Path(
            output_directory
        )

        self.output_directory.mkdir(

            parents=True,

            exist_ok=True,

        )


    # ============================================================
    # Report Path
    # ============================================================

    def _report_path(
        self,
    ) -> Path:
        """
        Create a unique output path for the report.
        """

        timestamp = datetime.now().strftime(

            "%Y%m%d_%H%M%S"

        )

        filename = (

            f"search_report_{timestamp}.html"

        )

        return self.output_directory / filename


    # ============================================================
    # HTML Document
    # ============================================================

    def _document(
        self,
        *,
        query: str,
        search_type: str,
        results: list[SearchResult],
        cards: str,
    ) -> str:
        """
        Build the complete HTML document.
        """

        exact_matches = sum(

            result.search_type.value == "exact"

            for result in results

        )

        similarity_matches = sum(

            result.search_type.value == "similarity"

            for result in results

        )

        substructure_matches = sum(

            result.search_type.value == "substructure"

            for result in results

        )

        unique_patents = len(

            {result.patent_number for result in results}

        )

        generated_at = datetime.now().strftime(

            "%d %B %Y %H:%M:%S"

        )

        return f"""
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>

PatentStructAI Search Report

</title>

<style>

:root {{

    --text: #c753a3;

    --background: #f8f1AE;

    --primary: #c54da7;

    --secondary: #c2db90;

    --accent: #76d172;

    --ink: #2b2620;

    --muted: #7a6f5c;

    --card: #ffffff;

    --border: rgba(43, 38, 32, 0.08);

    --shadow: 0 10px 30px rgba(197, 77, 167, 0.12);

}}

* {{

    box-sizing: border-box;

}}

body {{

    font-family: "Segoe UI", Arial, Helvetica, sans-serif;

    background: var(--background);

    margin: 0;

    padding: 0;

    color: var(--ink);

}}

.container {{

    max-width: 1500px;

    margin: auto;

    padding: 32px 32px 80px 32px;

}}

/* -------------------- header -------------------- */

.header {{

    background: var(--card);

    padding: 30px;

    border-radius: 18px;

    box-shadow: var(--shadow);

    margin-bottom: 26px;

    border: 1px solid var(--border);

}}

.header h1 {{

    margin: 0 0 4px 0;

    color: var(--text);

    letter-spacing: 0.3px;

}}

.header .subtitle {{

    color: var(--muted);

    margin: 0 0 22px 0;

    font-size: 14px;

}}

.query-grid {{

    display: grid;

    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));

    gap: 16px;

}}

.query-field {{

    background: var(--background);

    border-radius: 12px;

    padding: 14px 16px;

    border: 1px solid var(--border);

}}

.query-field .field-label {{

    color: var(--muted);

    font-size: 12px;

    text-transform: uppercase;

    letter-spacing: 0.6px;

    margin-bottom: 6px;

}}

.query-field pre {{

    margin: 0;

    white-space: pre-wrap;

    word-break: break-word;

    font-size: 13.5px;

}}

/* -------------------- stats -------------------- */

.summary {{

    display: grid;

    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));

    gap: 18px;

    margin-bottom: 26px;

}}

.summary-card {{

    background: var(--card);

    border-radius: 14px;

    padding: 18px;

    text-align: center;

    box-shadow: var(--shadow);

    border: 1px solid var(--border);

    border-top: 4px solid var(--primary);

}}

.summary-card.accent {{

    border-top-color: var(--accent);

}}

.summary-card.secondary {{

    border-top-color: var(--secondary);

}}

.summary-title {{

    color: var(--muted);

    font-size: 13px;

    text-transform: uppercase;

    letter-spacing: 0.5px;

}}

.summary-value {{

    font-size: 28px;

    font-weight: 700;

    margin-top: 8px;

    color: var(--ink);

}}

/* -------------------- sticky nav / tabs -------------------- */

.nav-bar {{

    position: sticky;

    top: 0;

    z-index: 50;

    background: var(--card);

    border-radius: 14px;

    box-shadow: var(--shadow);

    border: 1px solid var(--border);

    padding: 14px 18px;

    margin-bottom: 26px;

    display: flex;

    flex-wrap: wrap;

    align-items: center;

    gap: 12px;

}}

.tabs {{

    display: flex;

    gap: 8px;

    flex-wrap: wrap;

}}

.tab-btn {{

    border: 1px solid var(--border);

    background: var(--background);

    color: var(--ink);

    padding: 9px 16px;

    border-radius: 999px;

    font-size: 13.5px;

    font-weight: 600;

    cursor: pointer;

    transition: all 0.15s ease;

}}

.tab-btn:hover {{

    transform: translateY(-1px);

}}

.tab-btn.active {{

    background: var(--primary);

    color: white;

    border-color: var(--primary);

}}

.tab-btn .count {{

    opacity: 0.75;

    margin-left: 4px;

}}

.search-box {{

    margin-left: auto;

    flex: 1 1 220px;

    max-width: 320px;

}}

.search-box input {{

    width: 100%;

    padding: 9px 14px;

    border-radius: 999px;

    border: 1px solid var(--border);

    background: var(--background);

    font-size: 13.5px;

    outline: none;

}}

.search-box input:focus {{

    border-color: var(--primary);

}}

.back-to-top {{

    border: none;

    background: var(--accent);

    color: white;

    padding: 9px 14px;

    border-radius: 999px;

    font-size: 13px;

    font-weight: 600;

    cursor: pointer;

}}

/* -------------------- badges -------------------- */

.badge {{

    display: inline-block;

    padding: 5px 12px;

    border-radius: 999px;

    color: white;

    font-size: 12px;

    font-weight: 700;

    letter-spacing: 0.4px;

    text-transform: uppercase;

}}

.badge.exact {{

    background: var(--accent);

}}

.badge.similarity {{

    background: var(--primary);

}}

.badge.substructure {{

    background: #b7913a;

    background: var(--secondary);

    color: #3c4a25;

}}

/* -------------------- result cards -------------------- */

.results {{

    display: grid;

    grid-template-columns:

        repeat(auto-fill,minmax(320px,1fr));

    gap: 22px;

}}

.card {{

    background: var(--card);

    border-radius: 16px;

    overflow: hidden;

    box-shadow: var(--shadow);

    border: 1px solid var(--border);

    display: flex;

    flex-direction: column;

    transition: transform 0.15s ease, box-shadow 0.15s ease;

}}

.card:hover {{

    transform: translateY(-3px);

    box-shadow: 0 16px 34px rgba(197, 77, 167, 0.2);

}}

.card .img-wrap {{

    background: var(--background);

    cursor: zoom-in;

}}

.card img {{

    width: 100%;

    height: 240px;

    object-fit: contain;

    display: block;

}}

.card-body {{

    padding: 16px 18px 18px 18px;

}}

.card-body h3 {{

    margin: 0 0 4px 0;

    color: var(--text);

    font-size: 16px;

}}

.card-body .title {{

    color: var(--muted);

    font-size: 13px;

    margin: 0 0 10px 0;

}}

.meta-row {{

    display: flex;

    flex-wrap: wrap;

    gap: 6px 14px;

    font-size: 12.5px;

    color: var(--muted);

    margin: 10px 0;

}}

.meta-row b {{

    color: var(--ink);

}}

.smiles-box {{

    background: var(--background);

    border-radius: 10px;

    padding: 10px 12px;

    position: relative;

    border: 1px solid var(--border);

}}

.smiles-box .label {{

    font-size: 11px;

    text-transform: uppercase;

    letter-spacing: 0.5px;

    color: var(--muted);

    margin-bottom: 4px;

    display: block;

}}

.smiles-box pre {{

    margin: 0;

    white-space: pre-wrap;

    word-break: break-word;

    font-size: 12.5px;

    padding-right: 56px;

}}

.copy-btn {{

    position: absolute;

    top: 10px;

    right: 10px;

    border: none;

    background: var(--primary);

    color: white;

    font-size: 11px;

    font-weight: 600;

    padding: 5px 10px;

    border-radius: 8px;

    cursor: pointer;

}}

.copy-btn.copied {{

    background: var(--accent);

}}

.no-results {{

    grid-column: 1 / -1;

    text-align: center;

    color: var(--muted);

    padding: 40px 0;

    font-size: 15px;

}}

/* -------------------- lightbox -------------------- */

.lightbox {{

    display: none;

    position: fixed;

    inset: 0;

    background: rgba(43, 38, 32, 0.82);

    z-index: 100;

    align-items: center;

    justify-content: center;

    cursor: zoom-out;

}}

.lightbox.open {{

    display: flex;

}}

.lightbox img {{

    max-width: 90%;

    max-height: 88%;

    border-radius: 10px;

    box-shadow: 0 20px 50px rgba(0,0,0,0.4);

    background: white;

}}

</style>

</head>

<body>

<div class="container">

<div class="header">

<h1>🧪 PatentStructAI Search Report</h1>

<p class="subtitle">Chemical structure search — generated on <b>{generated_at}</b></p>

<div class="query-grid">

<div class="query-field">

<div class="field-label">Query</div>

<pre>{query}</pre>

</div>

<div class="query-field">

<div class="field-label">Search Mode</div>

<pre>{search_type.title()}</pre>

</div>

</div>

</div>

<div class="summary">

<div class="summary-card">

<div class="summary-title">Total Matches</div>

<div class="summary-value">{len(results)}</div>

</div>

<div class="summary-card accent">

<div class="summary-title">Exact</div>

<div class="summary-value">{exact_matches}</div>

</div>

<div class="summary-card">

<div class="summary-title">Similarity</div>

<div class="summary-value">{similarity_matches}</div>

</div>

<div class="summary-card secondary">

<div class="summary-title">Substructure</div>

<div class="summary-value">{substructure_matches}</div>

</div>

<div class="summary-card accent">

<div class="summary-title">Unique Patents</div>

<div class="summary-value">{unique_patents}</div>

</div>

</div>

<div class="nav-bar" id="navBar">

<div class="tabs" id="tabs">

<button class="tab-btn active" data-filter="all">All <span class="count">{len(results)}</span></button>

<button class="tab-btn" data-filter="exact">Exact <span class="count">{exact_matches}</span></button>

<button class="tab-btn" data-filter="similarity">Similarity <span class="count">{similarity_matches}</span></button>

<button class="tab-btn" data-filter="substructure">Substructure <span class="count">{substructure_matches}</span></button>

</div>

<div class="search-box">

<input
    type="text"
    id="searchInput"
    placeholder="Search patent number, title, or SMILES..."
>

</div>

<button class="back-to-top" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})">↑ Top</button>

</div>

<div class="results" id="results">

{cards}

<div class="no-results" id="noResults" style="display:none;">No results match your search.</div>

</div>

</div>

<div class="lightbox" id="lightbox">

<img id="lightboxImg" src="" alt="Full size structure">

</div>

<script>

(function () {{

    const tabs = document.querySelectorAll(".tab-btn");

    const cards = document.querySelectorAll(".card");

    const searchInput = document.getElementById("searchInput");

    const noResults = document.getElementById("noResults");

    let activeFilter = "all";

    function applyFilters() {{

        const query = searchInput.value.trim().toLowerCase();

        let visibleCount = 0;

        cards.forEach(function (card) {{

            const matchesTab = activeFilter === "all" || card.dataset.type === activeFilter;

            const matchesSearch = !query || card.dataset.search.indexOf(query) !== -1;

            const show = matchesTab && matchesSearch;

            card.style.display = show ? "" : "none";

            if (show) visibleCount += 1;

        }});

        noResults.style.display = visibleCount === 0 ? "block" : "none";

    }}

    tabs.forEach(function (tab) {{

        tab.addEventListener("click", function () {{

            tabs.forEach(function (t) {{ t.classList.remove("active"); }});

            tab.classList.add("active");

            activeFilter = tab.dataset.filter;

            applyFilters();

        }});

    }});

    searchInput.addEventListener("input", applyFilters);

    // Lightbox

    const lightbox = document.getElementById("lightbox");

    const lightboxImg = document.getElementById("lightboxImg");

    document.querySelectorAll(".img-wrap").forEach(function (wrap) {{

        wrap.addEventListener("click", function (e) {{

            e.preventDefault();

            lightboxImg.src = wrap.querySelector("img").src;

            lightbox.classList.add("open");

        }});

    }});

    lightbox.addEventListener("click", function () {{

        lightbox.classList.remove("open");

        lightboxImg.src = "";

    }});

    document.addEventListener("keydown", function (e) {{

        if (e.key === "Escape") {{

            lightbox.classList.remove("open");

            lightboxImg.src = "";

        }}

    }});

    // Copy SMILES buttons

    document.querySelectorAll(".copy-btn").forEach(function (btn) {{

        btn.addEventListener("click", function () {{

            const text = btn.dataset.smiles;

            navigator.clipboard.writeText(text).then(function () {{

                const original = btn.textContent;

                btn.textContent = "Copied!";

                btn.classList.add("copied");

                setTimeout(function () {{

                    btn.textContent = original;

                    btn.classList.remove("copied");

                }}, 1200);

            }});

        }});

    }});

}})();

</script>

</body>

</html>
"""


    # ============================================================
    # Result Card
    # ============================================================

    def _result_card(
        self,
        result: SearchResult,
    ) -> str:
        """
        Generate one HTML card representing a search result.
        """

        image = Path(
            result.image_path
        ).as_posix()

        similarity = "-"

        if result.similarity_score is not None:

            similarity = (

                f"{result.similarity_score:.3f}"

            )

        search_text = " ".join(
            [
                str(result.patent_number),
                str(result.patent_title),
                str(result.canonical_smiles),
            ]
        ).lower().replace('"', "&quot;")

        smiles_attr = str(
            result.canonical_smiles
        ).replace('"', "&quot;")

        return f"""
<div class="card" data-type="{result.search_type.value}" data-search="{search_text}">

<a
    class="img-wrap"
    href="../{image}"
    title="Click to view full size"
>

<img
    src="../{image}"
    alt="Chemical Structure"
    loading="lazy"
>

</a>

<div class="card-body">

<h3>{result.patent_number}</h3>

<p class="title">{result.patent_title}</p>

<p>

<span class="badge {result.search_type.value}">

{result.search_type.value.title()}

</span>

</p>

<div class="meta-row">

<span><b>Similarity:</b> {similarity}</span>

<span><b>Page:</b> {result.page_number}</span>

<span><b>Crop:</b> {result.crop_index}</span>

<span><b>Structure ID:</b> {result.structure_id}</span>

</div>

<div class="smiles-box">

<span class="label">SMILES</span>

<pre>{result.canonical_smiles}</pre>

<button class="copy-btn" data-smiles="{smiles_attr}">Copy</button>

</div>

</div>

</div>
"""


    # ============================================================
    # Save Report
    # ============================================================

    def save(
        self,
        *,
        results: list[SearchResult],
        query: str,
        search_type: str,
    ) -> Path:
        """
        Generate and save an HTML search report.

        Parameters
        ----------
        results
            Search results.

        query
            Original user query.

        search_type
            exact / similarity / substructure / combined

        Returns
        -------
        Path
            Path to the generated HTML report.
        """

        cards = "\n".join(

            self._result_card(result)

            for result in results

        )

        html = self._document(

            query=query,

            search_type=search_type,

            results=results,

            cards=cards,

        )

        report_path = self._report_path()

        report_path.write_text(

            html,

            encoding="utf-8",

        )

        webbrowser.open(

            report_path.resolve().as_uri()

        )

        return report_path