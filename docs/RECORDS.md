# Experiment contract v1

The executable validator is `researchos_hf/records.py`. Duplicate JSON keys, NaN and Infinity are rejected. Booleans cannot stand in for numeric fields. Unknown metadata is retained.

| Field | Contract |
| --- | --- |
| schema_version | Integer 1 |
| id | 1–80 lowercase letters/digits/underscores/hyphens, starts alphanumeric |
| title, owner, hypothesis | Nonempty strings |
| protocol_reference, differentiation | Nonempty versioned protocol and honest novelty/overlap notes |
| data_kind | synthetic, simulation or experimental; describes inputs |
| link | Parameters below |
| scenarios | 1–20 unique scenario objects |
| sounding | Declared delays and timing uncertainty |
| measurements | Array, possibly empty for nonexperimental input |
| evidence | Evidence declarations |

`link` requires finite tx_power_dbm, tx_gain_dbi, rx_gain_dbi and required_snr_db in ±300; system_loss_db in [0,300]; positive noise_bandwidth_hz up to 10⁶; frequencies_mhz array and ground_distances_km array within the documented bounds.

Each scenario has a unique safe id (same pattern as record ID), nonempty label/assumption_reference, virtual_height_km, critical_frequency_mhz, inband_noise_dbm (±300), and additional_loss_db ([0,300]). No field implies a geographic/time-specific ionospheric observation.

`sounding` requires assumed_round_trip_delays_ms, timing_uncertainty_us and nonempty assumption_reference. The model treats delays as assumed vertical group round trips, not acquired signals.

Every measurement has metric/unit/method, finite value within ±10¹⁵, finite nonnegative uncertainty and evidence_ids referencing declarations. State calibration, confidence/coverage, acquisition conditions and uncertainty interpretation in method/metadata. Experimental records require at least one measurement and evidence file, and every measurement needs an evidence reference. This enforces links, not authenticity or scientific validity.

Each evidence declaration has unique nonempty id, unique relative path, lowercase 64-character sha256 and nonempty description. Use `researchos-hf hash <file>`. Absolute/drive paths, traversal and symlinks outside the record directory fail. The runner verifies and captures original bytes under generated filenames mapped to evidence IDs in its manifest.

The CLI rejects existing output directories. Verification checks file hashes, evidence-to-record consistency and reproduction of JSON results, Markdown report and link CSV. The original evidence files are not needed after successful capture; their bytes are retained in the bundle.
