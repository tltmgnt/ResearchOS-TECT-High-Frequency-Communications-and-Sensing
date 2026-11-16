# ResearchOS TECT — High-Frequency Communications and Sensing

Independent research workspace for HF communications and sensing, supporting reproducible propagation modeling, ionospheric channel studies, link-budget analysis, experiment design, and evidence-linked assessment of performance, uncertainty, and research differentiation.

## Implemented foundation

- Educational single-virtual-layer geometry and a simplified secant-law cutoff screen across 3–30 MHz.
- Multiple declared height, critical-frequency, loss and in-band-noise scenarios.
- Geometric reference path loss, received power, SNR and owner-defined margins, with threshold assessment withheld above the toy cutoff.
- Virtual-height calculations from assumed vertical sounding delays, including a timing-only uncertainty term.
- Strict experiment records, protocol/differentiation notes, signed declared measurements with uncertainty, evidence references and SHA-256 checks.
- Portable captured-evidence bundles, JSON/CSV/Markdown exports and reproduction verification.

This is an educational research foundation, not a propagation forecast or frequency recommendation. It does not implement ITU-R P.533, VOACAP, live ionospheric data, ray tracing, groundwave prediction, radio hardware or field validation. A frequency below the toy cutoff is not thereby usable. No novelty, reliability, DARPA affiliation, award, endorsement, eligibility or submission is claimed. TECT remains the project identifier without an assumed expansion.

## Quick start

Python 3.10 or newer; no third-party runtime dependencies:

```bash
python -m researchos_hf validate examples/synthetic-hf.json
python -m researchos_hf run examples/synthetic-hf.json --output runs/demo
python -m researchos_hf verify runs/demo
python -m researchos_hf report runs/demo
python -m unittest discover -s tests -v
```

Optional installation:

```bash
python -m pip install .
researchos-hf --help
```

The synthetic fixture compares three declared scenarios, four frequencies and four ground distances. With a 250 km virtual layer and zero ground distance, geometric path length is 500 km and the toy cutoff is 5 MHz. At 500 km ground distance the same model gives approximately 7.071 MHz. Raising declared noise by 10 dB lowers reference SNR by 10 dB without changing the cutoff. An assumed 1 ms vertical round trip gives 149.896229 km virtual height. These are software checks, not measurements or propagation evidence.

## Research workflow

1. Copy the example; assign a unique ID, owner, hypothesis, protocol reference and honest input basis.
2. Define frequencies, distances and declared scenarios. Record sources for virtual height, critical frequency, in-band noise and additional loss. Check [model limitations](docs/MODEL.md).
3. Ensure declared noise describes total receiver-input noise in the stated bandwidth. Bandwidth is metadata here; the tool does not infer noise from it.
4. Document the proposed distinction and review related literature/programs before making novelty or nonduplication claims.
5. Add declared measurements with units, method, uncertainty and evidence IDs. Models do not fit or validate them.
6. Put evidence below the record directory. Use `researchos-hf hash <file>` and declare relative path, digest, description and unique ID.
7. Validate, run into a new directory, verify, and review assumptions, screens and missing scientific evidence.

Experimental input records require measurements and supporting evidence references; computed output stays educational. Paths cannot escape the record directory, including through symlinks. Verified evidence bytes are captured in the bundle. Hashes verify byte consistency, not authenticity or calibration. Local runs are ignored by Git; keep credentials and unpublished partner data out of this public repository.

## Bundle output

| File | Purpose |
| --- | --- |
| `record.json` | Exact original input bytes |
| `results.json` | Scenario/link screens, reference budgets, virtual heights and limitations |
| `link.csv` | All scenario/frequency/distance combinations |
| `report.md` | Human-readable results and differentiation notes |
| `evidence/0000.bin`, … | Captured original evidence bytes |
| `manifest.json` | File digests, evidence mapping and Python version |

Existing output directories are rejected. Verification checks hashes, evidence-to-record consistency and recomputes results/report/CSV. Identical inputs under the same runner/runtime yield identical bundles. This is not a signed or tamper-proof audit service.

## Documentation and CI

- [Equations and model limits](docs/MODEL.md)
- [Record contract](docs/RECORDS.md)
- [Research roadmap](docs/RESEARCH_PLAN.md)
- [Primary sources](docs/SOURCES.md)
- [Contributing](CONTRIBUTING.md)

CI installs the package, runs tests and the complete example workflow, and uploads its synthetic bundle on Python 3.10–3.13. The existing [license](LICENSE) is preserved.

## Interactive browser app

The `web/` directory contains a local-first HF scenario editor, toy-cutoff and reference-SNR plots, frequency selection, virtual-height charts, experiment library/imports, parameter templates, evidence checksum tools and JSON/CSV/Markdown exports. Calculations run in a background worker. Serve with `python -m http.server 8000 --directory web`, then open `http://localhost:8000`. Use localhost or HTTPS for modules, workers and Web Crypto. Run web-model checks with `node web/tests/model.test.mjs`.

Records stay in the current browser and origin; export regularly. No cross-device, GitHub or CLI synchronization is configured. Record JSON exports work with the CLI. Browser results/reports are summaries, not complete CLI evidence bundles. Original files are not uploaded, retained or automatically re-verified on import/reload. The form creates synthetic/simulation records; experimental records can be imported with their measurements/evidence declarations. Reusing parameters as a new record changes experimental input basis to simulation and omits source measurements/evidence, leaving the original saved record intact.

The web model is checked against Python across ordinary and boundary geometry/delay cases. Floating-point differences may still affect exact boundary decisions. All app calculations remain educational, not propagation forecasts or frequency recommendations.

Private hosted app: https://researchos-tect-hf.troturn31.chatgpt.site
