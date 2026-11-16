# Flat-layer HF and virtual-height model v1

## Geometry and toy cutoff

Assume a flat Earth and one virtual layer of height h with a symmetric single-hop ground span D, both in km.

- Geometric reference path length L = sqrt(D² + (2h)²).
- Incidence angle from vertical = atan2(D, 2h).
- Secant factor = L/(2h).
- Toy secant cutoff = declared critical frequency × secant factor.
- Geometric reference delay = L × 1000 / c seconds, with c = 299792458 m/s.

At zero ground span, incidence is vertical and the cutoff equals the supplied critical frequency. At equality a test frequency is labeled `not-above-toy-cutoff`; above it, `above-toy-cutoff`. These labels describe arithmetic only. Being below the cutoff does not establish propagation support, a lowest usable frequency, reliability or a usable channel.

Bounds are 3–30 MHz test frequencies, 0–1000 km ground distance, 100–500 km virtual height and 1–20 MHz declared critical frequency. These are software/model input bounds, not a validated operating domain. Earth curvature and spatial ionospheric structure become important; no path-length validity or real-world accuracy follows from staying inside the bounds.

The secant relationship is a simplified theoretical baseline. The layer's virtual height is assumed constant across frequency, even though actual virtual height is frequency dependent. No O/X modes, magnetic effects, collisions, D/E/F-layer absorption, multi-hop paths, groundwave, scattering, fading, geomagnetic/solar variation or interference are modeled. There are no coordinates, dates, ionosonde data or live forecasts in the calculation.

## Declared-noise reference budget

For each scenario/frequency/distance, wavelength λ = c/f and geometric free-space reference loss is 20 log10(4πL/λ), with L and λ in meters. Reference received power is declared transmit power plus fixed antenna gains, minus system loss, that geometric loss and declared additional scenario loss. Reference SNR is power minus the scenario's declared in-band noise; margin subtracts an owner-defined SNR criterion.

This free-space reference is not a validated skywave attenuation model. Additional loss is a declared placeholder, not computed absorption or a calibrated ionospheric channel. Antenna patterns, frequency-dependent gain, polarization, bandwidth/time spreading and noise statistics are omitted. The owner must establish consistency between scenario assumptions and the intended experiment.

`noise_bandwidth_hz` records the bandwidth to which the declared total receiver-input noise applies. Changing this metadata does not automatically rescale noise. This is deliberate: external HF noise cannot generally be inferred from a simple receiver kTB calculation alone. No environmental noise model or receiver cascade is implemented.

Above the toy cutoff, reference numeric budget fields remain for diagnosis but `threshold_status` is `not-assessed-above-toy-cutoff`. At or below it, the status only compares reference SNR to the owner criterion. Neither result predicts an available frequency or working link.

## Assumed vertical sounding delays

Virtual height in km = c × assumed round-trip delay in milliseconds × 10⁻³ / 2000. Timing-only virtual-height uncertainty uses the supplied timing uncertainty in microseconds with the same c/2 scale. The factor of two assumes a vertical round trip. Delays are owner-supplied, not extracted from detected echoes.

Actual ionospheric group velocity differs from free-space speed; the cτ/2 convention yields apparent/virtual height, not true physical layer height. This tool performs no true-height inversion, waveform processing, mode identification, calibration or detection. The propagated uncertainty term covers only declared timing uncertainty, not model/environment error or a complete confidence interval. Delays support 0–10 ms and timing uncertainty 0–1000 μs.

## Reproduction and integrity

Limits: up to 20 scenarios, 100 frequencies, 100 distances and 20000 total combinations; up to 1000 sounding delays. Inputs are bounded/validated, and nonfinite derived artifacts are rejected. Declared measurements remain separate from calculated output.

Run bundles capture exact input/evidence bytes, hashes and Python version. Verification recomputes exact artifacts under the current runner; numerical/version differences may reject historical bundles. Preserve runtime and runner revision for long-lived studies. Hashes are not signatures; replacing all records and hashes can forge a self-consistent bundle.
