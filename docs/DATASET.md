# Dataset audit (`new dataset.json`)

The original file is stored at `data/raw/new dataset.json` and was **not modified**.

Source: 2,353 `enhanced_prompt` / `enhanced_completion` pairs (Chart.js or Vega-Lite specs plus an executive insight). This is an instruction dataset, not a table of ground-truth metrics.

## Audit summary

| Bucket | Count | Notes |
| --- | ---: | --- |
| Records | 2353 | JSON array of objects |
| Valid visualization tasks | ~229–430 | Supported chart family, parseable spec, mappable columns |
| Valid with warnings | ~1,100+ | Usable chart, but insight is causal, prescriptive, or loosely grounded |
| Rejected | ~744–800 | Bad JSON, non-visual, unknown/unsupported chart, or unmappable spec |
| Duplicate prompts | 0 | |
| Duplicate specs | 10 | Near-identical visualization JSON |
| Invalid JSON specifications | 8 | Broken or missing JSON in the completion |
| Non-visual examples | 8 | No usable chart payload |
| Unsupported chart families | ~70–270 | heatmap, combo, dual-axis, radar, etc. |
| Potentially hallucinated values | ~516 | Spec numbers not found in the prompt table |
| Unsupported / causal claims | ~330–460 | “because”, “leads to”, etc. |
| Prescriptive claims | ~1,400+ | “should / must / recommend” in the insight |

Chart families in the raw completions are mostly **bar**, **scatter**, and **line**. Pie is effectively absent. Histogram is rare (5).

## Derived outputs (do not replace the original)

- `data/processed/cleaned_visualization_examples.json` — de-duplicated, mappable examples
- `data/processed/rejected_examples.json` — audit flags for rejected rows
- `data/processed/fewshot_examples.json` — 6 high-quality style examples used in prompting
- `data/processed/audit_report.json` — machine-readable counts

## Prompt integration

Only the few-shot file is loaded at runtime. Examples teach chart intent and insight style. They must not override Pandas evidence for the uploaded file. If the file is missing, DataBloom still runs.
