"""Educational flat-layer geometry and declared-noise reference budgets."""
import math
from .records import dumps,validate
C=299792458.0
LIMITATIONS=("Educational declared-assumption calculations only; not a propagation forecast or frequency recommendation. A flat, single virtual layer and simplified secant-law cutoff are assumed. Free-space loss along the geometric path is only a reference budget with declared extra loss and in-band noise. No ITU-R P.533/VOACAP implementation, ray tracing, Earth curvature, D/E/F-layer absorption, multi-hop modes, geomagnetic effects, live ionospheric data, groundwave model, fading, interference or radio hardware is implemented. Sounding output is virtual height, not true physical height or validated detection. No reliability, novelty, field capability or DARPA compliance is established.")


def analyze(record):
    r=validate(record);link=r["link"];rows=[]
    for s in r["scenarios"]:
        h=s["virtual_height_km"]
        for distance in link["ground_distances_km"]:
            path_km=math.hypot(distance,2*h)
            secant=path_km/(2*h)
            cutoff=s["critical_frequency_mhz"]*secant
            for f in link["frequencies_mhz"]:
                wavelength=C/(f*1e6)
                loss=20*math.log10(4*math.pi*path_km*1000/wavelength)
                power=link["tx_power_dbm"]+link["tx_gain_dbi"]+link["rx_gain_dbi"]-link["system_loss_db"]-loss-s["additional_loss_db"]
                snr=power-s["inband_noise_dbm"]
                status="not-above-toy-cutoff" if f<=cutoff else "above-toy-cutoff"
                rows.append({"scenario_id":s["id"],"frequency_mhz":f,"ground_distance_km":distance,
                             "assumed_virtual_height_km":h,"geometric_path_km":path_km,
                             "incidence_from_vertical_deg":math.degrees(math.atan2(distance,2*h)),
                             "toy_secant_cutoff_mhz":cutoff,"toy_cutoff_status":status,
                             "geometric_delay_ms":path_km*1000/C*1000,
                             "geometric_reference_loss_db":loss,"reference_received_power_dbm":power,
                             "declared_inband_noise_dbm":s["inband_noise_dbm"],"reference_snr_db":snr,
                             "reference_margin_db":snr-link["required_snr_db"],
                             "threshold_status":("meets-declared-reference-snr" if snr>=link["required_snr_db"] else "below-declared-reference-snr") if status=="not-above-toy-cutoff" else "not-assessed-above-toy-cutoff"})
    sounding=[{"assumed_round_trip_delay_ms":t,"virtual_height_km":C*t*1e-3/2000,
               "timing_only_height_uncertainty_km":C*r["sounding"]["timing_uncertainty_us"]*1e-6/2000}
              for t in r["sounding"]["assumed_round_trip_delays_ms"]]
    result={"analysis":"flat-layer-hf-and-virtual-height-v1","runner_version":"0.1.0","input_data_kind":r["data_kind"],
            "output_kind":"educational-not-a-propagation-forecast","link_results":rows,"sounding_results":sounding,
            "declared_measurements":r["measurements"],"limitations":LIMITATIONS}
    dumps(result);return result
