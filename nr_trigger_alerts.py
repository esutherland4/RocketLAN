#!/usr/bin/env python3
"""
RocketLAN - Alert Trigger Script
Sends data values that breach every alert condition threshold.

Usage:
  export NR_LICENSE_KEY=<your ingest license key>
  export NR_ACCOUNT_ID=<your account ID>
  python3 nr_trigger_alerts.py

Optional:
  NR_REGION=US (default) or EU

Expected delay: alerts fire ~3-4 minutes after running, once the
60s aggregation window closes and the 120s aggregation delay passes.

Thresholds being breached:
  orbital_latency_ms      > 500  (CRITICAL) — sending 750
  fuse_burn_rate_pct      > 7.0  (CRITICAL) — sending 9.5
  lost_capsule_count      > 50   (CRITICAL) — sending 120
  solo_flight_duration_sec > 600 (CRITICAL) — sending 900
  Hostile_Environment_Detected count > 0    — sending 1 event
  Log FATAL count > 0                       — sending 1 FATAL log line
"""

import json
import os
import time
import urllib.request
import urllib.error

LICENSE_KEY = os.environ["NR_LICENSE_KEY"]
ACCOUNT_ID  = os.environ["NR_ACCOUNT_ID"]
REGION      = os.environ.get("NR_REGION", "US").upper()

if REGION == "EU":
    METRIC_ENDPOINT = "https://metric-api.eu.newrelic.com/metric/v1"
    EVENT_ENDPOINT  = f"https://insights-collector.eu01.nr-data.net/v1/accounts/{ACCOUNT_ID}/events"
    LOG_ENDPOINT    = "https://log-api.eu.newrelic.com/log/v1"
else:
    METRIC_ENDPOINT = "https://metric-api.newrelic.com/metric/v1"
    EVENT_ENDPOINT  = f"https://insights-collector.newrelic.com/v1/accounts/{ACCOUNT_ID}/events"
    LOG_ENDPOINT    = "https://log-api.newrelic.com/log/v1"

APP_NAME = "RocketLAN"


def post_json(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Api-Key": LICENSE_KEY},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def trigger_metrics():
    now_ms = int(time.time() * 1000)
    common = {
        "attributes": {
            "service.name": APP_NAME,
            "instrumentation.provider": "rocketlan-mission-control",
        }
    }
    metrics = [
        {
            "name": "orbital_latency_ms",
            "type": "gauge",
            "value": 750,           # threshold: 500 CRITICAL
            "timestamp": now_ms,
            "attributes": {"app": APP_NAME, "host": "mission-node-1"},
        },
        {
            "name": "fuse_burn_rate_pct",
            "type": "gauge",
            "value": 9.5,           # threshold: 7.0 CRITICAL
            "timestamp": now_ms,
            "attributes": {"app": APP_NAME, "host": "mission-node-1"},
        },
        {
            "name": "lost_capsule_count",
            "type": "count",
            "value": 120,           # threshold: 50 CRITICAL
            "timestamp": now_ms,
            "interval.ms": 60000,
            "attributes": {"app": APP_NAME},
        },
        {
            "name": "solo_flight_duration_sec",
            "type": "count",
            "value": 900,           # threshold: 600 CRITICAL
            "timestamp": now_ms,
            "interval.ms": 60000,
            "attributes": {"app": APP_NAME},
        },
    ]
    status, body = post_json(METRIC_ENDPOINT, [{"common": common, "metrics": metrics}])
    print(f"  Metrics  → HTTP {status}  (orbital_latency=750, fuse_burn=9.5, lost_capsules=120, solo_flight=900)")
    if status >= 400:
        print(f"    Error: {body[:200]}")


def trigger_event():
    now_sec = int(time.time())
    event = {
        "eventType": "Hostile_Environment_Detected",
        "timestamp": now_sec,
        "app": APP_NAME,
        "entity.name": APP_NAME,
        "entity.type": "SERVICE",
        "network_name": "Starbucks_Guest_WiFi",
        "environment": "Mars",
        "download_speed_mbps": 0.04,
        "is_place_to_raise_kids": False,
    }
    status, body = post_json(EVENT_ENDPOINT, [event])
    print(f"  Event    → HTTP {status}  (Hostile_Environment_Detected)")
    if status >= 400:
        print(f"    Error: {body[:200]}")


def trigger_log():
    now_ms = int(time.time() * 1000)
    payload = [{
        "common": {
            "attributes": {
                "service.name": APP_NAME,
                "entity.name": APP_NAME,
            }
        },
        "logs": [{
            "timestamp": now_ms,
            "message": "[FATAL]  [WIFI] Mars ain't the kind of place to route your packets. In fact, it's cold as hell.",
            "level": "FATAL",
            "component": "WIFI",
            "app": APP_NAME,
        }],
    }]
    status, body = post_json(LOG_ENDPOINT, payload)
    print(f"  Log      → HTTP {status}  (FATAL: Mars ain't the kind of place to route your packets)")
    if status >= 400:
        print(f"    Error: {body[:200]}")


if __name__ == "__main__":
    print(f"RocketLAN — triggering all alert conditions in account {ACCOUNT_ID} ({REGION})")
    print()
    trigger_metrics()
    trigger_event()
    trigger_log()
    print()
    print("All threshold breaches sent. Alerts should fire in ~3-4 minutes.")
    print("(60s aggregation window + 120s aggregation delay)")
    print()
    print("Check: New Relic → Alerts → Alert Conditions → RocketLAN Mission Control")
