# Pragmatic Trial Evaluation

A single-file, in-browser form for scoring proposed pragmatic trials on impact,
feasibility, and investigative team strength.

- Fill it out in the browser — **nothing is stored or transmitted**; answers live
  only in the open tab and disappear on reload or close.
- The overall score (0–30) totals automatically from the three 0–10 components.
- Click **Download PDF** to save a formatted copy of the completed form
  (generated locally with jsPDF).
- Every PDF also carries the responses as **machine-readable JSON** in its XMP
  metadata, so a folder of completed PDFs can be turned into a dataset.

## Building a dataset from completed PDFs

```
python3 extract_pte.py path/to/pdfs/ -o evaluations.csv
```

`extract_pte.py` (Python 3, standard library only) writes one row per PDF.
PDFs without embedded data (e.g., printed-and-scanned copies) are listed as skipped.

### Fields (schema `pte-evaluation`, version 1)

| Field | Content |
|---|---|
| `study_pi`, `study_name`, `evaluator_first`, `evaluator_last`, `date` | Study information (date as YYYY-MM-DD) |
| `imp_system`, `imp_clin`, `imp_pat`, `imp_ihc` | Impact to health system / clinicians / patients / IHC (1–5) |
| `fea_rand`, `fea_int`, `fea_n`, `fea_out`, `fea_work`, `fea_it` | Feasibility: randomization, intervention delivery, sample size, outcome data, workflow integration, IT build (1–5) |
| `team_complete`, `team_grants` | Investigative team: can complete trial / can obtain grants (1–5) |
| `g_uncert`, `g_riskpt`, `g_riskmd`, `g_current` | Guiding-consideration notes (free text) |
| `ov_ihc`, `ov_hosp`, `ov_feas` (+ `_comment`) | Overall component scores (0–10) and comments |
| `total_score` | Sum of the three components (blank if any is missing) |
| `generated_at` | UTC timestamp when the PDF was created |

Blank answers are stored as `null`. If the form's questions change, bump
`SCHEMA_VERSION` in `index.html` so older and newer PDFs can be told apart.

The entire tool is `index.html` — no build step, no server.

## Hosting

Served as a static page (e.g., GitHub Pages). Nothing to configure.
