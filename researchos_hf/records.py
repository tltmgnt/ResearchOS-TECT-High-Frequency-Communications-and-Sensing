"""HF research records and strict JSON handling."""
import hashlib
import json
import math
import re
from pathlib import Path


class ValidationError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ValidationError(message)


def dumps(value):
    return json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"


def parse_json(data):
    def constant(value):
        raise ValidationError(f"non-finite JSON constant: {value}")
    def unique(pairs):
        result = {}
        for k, v in pairs:
            require(k not in result, f"duplicate JSON key: {k}")
            result[k] = v
        return result
    return json.loads(data, parse_constant=constant, object_pairs_hook=unique)


def read_json(path):
    return parse_json(Path(path).read_text(encoding="utf-8"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text(v, name):
    require(isinstance(v, str) and bool(v.strip()), f"{name} must be a nonempty string")


def integer(v, name, minimum=0, maximum=10**12):
    require(type(v) is int and minimum <= v <= maximum, f"{name} must be an integer in [{minimum}, {maximum}]")


def number(v, name, positive=False):
    require(type(v) in (int, float), f"{name} must be numeric")
    try:
        finite = math.isfinite(v)
    except OverflowError:
        finite = False
    require(finite and (v > 0 if positive else v >= 0), f"{name} must be finite and {'positive' if positive else 'nonnegative'}")


def safe_path(value):
    text(value, "evidence path")
    require(not Path(value).is_absolute() and "\\" not in value and not re.match(r"^[A-Za-z]:", value)
            and not any(p in (".", "..") for p in value.split("/")), "evidence path must be relative without traversal")
    return Path(value)


def evidence_bytes(root, path):
    root = Path(root).resolve()
    dest = (root / safe_path(path)).resolve()
    require(dest.is_relative_to(root), "evidence resolves outside record directory")
    return dest.read_bytes()


def signed(value,name,minimum=-300,maximum=300):
    require(type(value) in (int,float) and minimum<=value<=maximum,f"{name} must be finite in [{minimum},{maximum}]")


def validate(r):
    require(isinstance(r,dict),"record must be an object")
    require(type(r.get("schema_version")) is int and r["schema_version"]==1,"schema_version must be integer 1")
    require(isinstance(r.get("id"),str) and bool(re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}",r["id"])),"invalid record id")
    for k in ("title","owner","hypothesis","protocol_reference","differentiation"):
        text(r.get(k),k)
    require(r.get("data_kind") in ("synthetic","simulation","experimental"),"invalid input basis")
    link=r.get("link")
    require(isinstance(link,dict),"link must be an object")
    for k in ("tx_power_dbm","tx_gain_dbi","rx_gain_dbi","required_snr_db"):
        signed(link.get(k),k)
    number(link.get("system_loss_db"),"system_loss_db")
    require(link["system_loss_db"]<=300,"system loss must be <=300 dB")
    number(link.get("noise_bandwidth_hz"),"noise_bandwidth_hz",True)
    require(link["noise_bandwidth_hz"]<=1e6,"noise bandwidth must be <=1e6 Hz")
    frequencies=link.get("frequencies_mhz")
    require(isinstance(frequencies,list) and 1<=len(frequencies)<=100,"provide 1–100 frequencies")
    for f in frequencies:
        signed(f,"frequency_mhz",3,30)
    distances=link.get("ground_distances_km")
    require(isinstance(distances,list) and 1<=len(distances)<=100,"provide 1–100 distances")
    for d in distances:
        signed(d,"ground_distance_km",0,1000)
    scenarios=r.get("scenarios")
    require(isinstance(scenarios,list) and 1<=len(scenarios)<=20,"provide 1–20 scenarios")
    require(len(scenarios)*len(distances)*len(frequencies)<=20000,"maximum 20000 scenario/frequency/distance combinations")
    seen=set()
    for s in scenarios:
        require(isinstance(s,dict),"scenario must be an object")
        require(isinstance(s.get("id"),str) and bool(re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}",s["id"])),"invalid scenario id")
        require(s["id"] not in seen,"duplicate scenario id")
        seen.add(s["id"])
        for k in ("label","assumption_reference"):
            text(s.get(k),k)
        signed(s.get("virtual_height_km"),"virtual_height_km",100,500)
        signed(s.get("critical_frequency_mhz"),"critical_frequency_mhz",1,20)
        signed(s.get("inband_noise_dbm"),"inband_noise_dbm")
        signed(s.get("additional_loss_db"),"additional_loss_db",0,300)
    sounding=r.get("sounding")
    require(isinstance(sounding,dict),"sounding must be an object")
    delays=sounding.get("assumed_round_trip_delays_ms")
    require(isinstance(delays,list) and 1<=len(delays)<=1000,"provide 1–1000 sounding delays")
    for delay in delays:
        signed(delay,"assumed delay ms",0,10)
    signed(sounding.get("timing_uncertainty_us"),"timing_uncertainty_us",0,1000)
    text(sounding.get("assumption_reference"),"sounding assumption_reference")
    evidence=r.get("evidence")
    require(isinstance(evidence,list),"evidence must be an array")
    refs,paths=set(),set()
    for e in evidence:
        require(isinstance(e,dict),"evidence entry must be an object")
        for k in ("id","description"):
            text(e.get(k),k)
        safe_path(e.get("path"))
        require(e["id"] not in refs and e["path"] not in paths,"duplicate evidence id/path")
        refs.add(e["id"]);paths.add(e["path"])
        require(isinstance(e.get("sha256"),str) and bool(re.fullmatch(r"[a-f0-9]{64}",e["sha256"])),"invalid evidence digest")
    measurements=r.get("measurements")
    require(isinstance(measurements,list),"measurements must be an array")
    for m in measurements:
        require(isinstance(m,dict),"measurement must be an object")
        for k in ("metric","unit","method"):
            text(m.get(k),k)
        signed(m.get("value"),"measurement value",-1e15,1e15)
        number(m.get("uncertainty"),"measurement uncertainty")
        ids=m.get("evidence_ids")
        require(isinstance(ids,list) and all(isinstance(x,str) and x in refs for x in ids),"unknown evidence reference")
        require(r["data_kind"]!="experimental" or bool(ids),"experimental measurements require evidence references")
    require(r["data_kind"]!="experimental" or bool(measurements) and bool(evidence),"experimental records require measurements and evidence")
    return r
