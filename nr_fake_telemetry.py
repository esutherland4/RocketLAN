#!/usr/bin/env python3
"""
RocketLAN - Mission Control Telemetry Generator
"Burning out your router up here alone."

Sends fake metrics, events, and logs to New Relic for alert testing.

Usage:
  export NR_LICENSE_KEY=<your ingest license key>
  export NR_ACCOUNT_ID=<your account ID>
  python3 nr_fake_telemetry.py

Optional env vars:
  NR_REGION=US (default) or EU
  NR_DATAPOINTS=20 (default, applied to metrics; events and logs are fixed sequences)
"""

import json
import os
import random
import time
import urllib.request
import urllib.error

# --- Config ---
LICENSE_KEY = os.environ["NR_LICENSE_KEY"]
ACCOUNT_ID  = os.environ["NR_ACCOUNT_ID"]
REGION      = os.environ.get("NR_REGION", "US").upper()
DATAPOINTS  = int(os.environ.get("NR_DATAPOINTS", "20"))

if REGION == "EU":
    METRIC_ENDPOINT = "https://metric-api.eu.newrelic.com/metric/v1"
    EVENT_ENDPOINT  = f"https://insights-collector.eu01.nr-data.net/v1/accounts/{ACCOUNT_ID}/events"
    LOG_ENDPOINT    = "https://log-api.eu.newrelic.com/log/v1"
else:
    METRIC_ENDPOINT = "https://metric-api.newrelic.com/metric/v1"
    EVENT_ENDPOINT  = f"https://insights-collector.newrelic.com/v1/accounts/{ACCOUNT_ID}/events"
    LOG_ENDPOINT    = "https://log-api.newrelic.com/log/v1"

APP_NAME = "RocketLAN"


def post_json(url, payload, headers=None):
    data = json.dumps(payload).encode()
    req_headers = {"Content-Type": "application/json", "Api-Key": LICENSE_KEY}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def send_metrics(n):
    """
    Core vital signs sent back to Mission Control:
      orbital_latency_ms  - round-trip ping time (gauge); >500ms triggers Deep Space Delay
      fuse_burn_rate_pct  - battery drain rate while scanning for signal (gauge)
      lost_capsule_count  - cumulative dropped packets floating in the digital void (counter)
      solo_flight_duration_sec - continuous time fully disconnected from the LAN (counter)
    """
    now_ms = int(time.time() * 1000)
    interval = (30 * 60 * 1000) // n

    # Simulate a realistic outage arc: latency spikes, then recovers
    def latency_for(i):
        mid = n // 2
        if i < mid:
            # climbing toward deep space
            return round(random.uniform(20, 50) + (i / mid) * 600, 2)
        else:
            # touchdown: recovering
            return round(random.uniform(20, 50) + ((n - i) / mid) * 200, 2)

    metrics = []
    lost_capsules = 0
    solo_seconds = 0

    for i in range(n):
        ts = now_ms - (n - i) * interval
        latency = latency_for(i)
        battery_drain = round(random.uniform(1.0, 8.5), 2)
        lost_capsules += random.randint(0, 12)
        solo_seconds += interval // 1000

        metrics += [
            {
                "name": "orbital_latency_ms",
                "type": "gauge",
                "value": latency,
                "timestamp": ts,
                "attributes": {"app": APP_NAME, "host": f"mission-node-{random.randint(1, 3)}"},
            },
            {
                "name": "fuse_burn_rate_pct",
                "type": "gauge",
                "value": battery_drain,
                "timestamp": ts,
                "attributes": {"app": APP_NAME, "host": f"mission-node-{random.randint(1, 3)}"},
            },
            {
                "name": "lost_capsule_count",
                "type": "count",
                "value": lost_capsules,
                "timestamp": ts,
                "interval.ms": interval,
                "attributes": {"app": APP_NAME},
            },
            {
                "name": "solo_flight_duration_sec",
                "type": "count",
                "value": solo_seconds,
                "timestamp": ts,
                "interval.ms": interval,
                "attributes": {"app": APP_NAME},
            },
        ]

    payload = [{"metrics": metrics}]
    status, body = post_json(METRIC_ENDPOINT, payload)
    print(f"  Metrics  → HTTP {status} ({n} datapoints × 4 metrics = {n * 4} series points)")
    if status >= 400:
        print(f"    Error: {body[:200]}")


def send_events():
    """
    Custom lifecycle events from the Mission Commander AI.
    Sent in chronological order to simulate a single outage + recovery session.
    """
    now_sec = int(time.time())
    # Anchor to a fake 9 AM session ~13 minutes ago
    t0 = now_sec - (13 * 60)

    events = [
        # T+0: user opens app and kicks off diagnostics
        {
            "eventType": "Pre_Flight_Check_Initiated",
            "timestamp": t0,
            "app": APP_NAME,
            "gateway_status": "checking",
            "thrusters": "online",
            "coffee_level": "critical",
        },
        # T+2s: the scheduled 9 AM cron fires
        {
            "eventType": "Zero_Hour_Execution",
            "timestamp": t0 + 2,
            "app": APP_NAME,
            "cron_status": "success",
            "user_awake": False,
        },
        # T+5min: stumbles onto captive portal hell
        {
            "eventType": "Hostile_Environment_Detected",
            "timestamp": t0 + (5 * 60),
            "app": APP_NAME,
            "network_name": "Hotel_Guest",
            "environment": "Mars",
            "download_speed_mbps": round(random.uniform(0.05, 0.9), 3),
            "is_place_to_raise_kids": False,
        },
        # T+12min: Mission Commander guides them home
        {
            "eventType": "Touchdown_Brings_Me_Round",
            "timestamp": t0 + (12 * 60),
            "app": APP_NAME,
            "connection_type": "ethernet",
            "relief_level": "high",
            "orbital_latency_ms": round(random.uniform(8.0, 22.0), 2),
        },
    ]

    status, body = post_json(EVENT_ENDPOINT, events)
    print(f"  Events   → HTTP {status} (4 events: Pre_Flight_Check_Initiated, Zero_Hour_Execution, Hostile_Environment_Detected, Touchdown_Brings_Me_Round)")
    if status >= 400:
        print(f"    Error: {body[:200]}")


def send_logs():
    """
    Raw system log lines as a DevOps engineer would see them tailing the server
    during a live RocketLAN outage session.
    """
    now_ms = int(time.time() * 1000)
    # Anchor log sequence to T-13 minutes (same session as events)
    t0_ms = now_ms - (13 * 60 * 1000)

    log_sequence = [
        (t0_ms + 0,          "INFO",  "INIT",   "Preparing daily diagnostic cron job."),
        (t0_ms + 2_000,      "INFO",  "CRON",   "Zero hour: 9 AM. Ignition sequence start."),
        (t0_ms + 4_000,      "DEBUG", "PING",   "Pinging 8.8.8.8. Awaiting telemetry..."),
        (t0_ms + 17_000,     "WARN",  "UPLINK", "Connection lost to primary gateway. Burning out his router up here alone."),
        (t0_ms + 32_000,     "ERROR", "DNS",    "Host unreachable. I think it's gonna be a long, long ping."),
        (t0_ms + 105_000,    "WARN",  "AUTH",   "Sudo privileges rejected. User is not the admin they think he is at home. Oh, no, no, no."),
        (t0_ms + 302_000,    "FATAL", "WIFI",   'Auto-connected to "Starbucks_Guest_WiFi". Network environment is hostile.'),
        (t0_ms + 303_000,    "FATAL", "WIFI",   "Mars ain't the kind of place to route your packets. In fact, it's cold as hell."),
        (t0_ms + 722_000,    "INFO",  "UPLINK", "Handshake re-established. Touchdown brings me round to find I'm not so far from home."),
    ]

    logs = [
        {
            "timestamp": ts,
            "message": f"[{level}]  [{component}] {message}",
            "level": level,
            "component": component,
            "app": APP_NAME,
        }
        for ts, level, component, message in log_sequence
    ]

    payload = [{"logs": logs}]
    status, body = post_json(LOG_ENDPOINT, payload)
    print(f"  Logs     → HTTP {status} ({len(logs)} log lines)")
    if status >= 400:
        print(f"    Error: {body[:200]}")


if __name__ == "__main__":
    print(f"RocketLAN Mission Control — transmitting telemetry to New Relic ({REGION} region)")
    print(f"  Account : {ACCOUNT_ID}")
    print(f"  Tagline : \"Burning out your router up here alone.\"")
    print()
    send_metrics(DATAPOINTS)
    send_events()
    send_logs()
    print()
    print("Touchdown. NRQL to verify:")
    print(f"  SELECT average(orbital_latency_ms) FROM Metric WHERE app = '{APP_NAME}' TIMESERIES SINCE 1 hour ago")
    print(f"  SELECT average(fuse_burn_rate_pct), sum(lost_capsule_count) FROM Metric WHERE app = '{APP_NAME}' SINCE 1 hour ago")
    print(f"  SELECT * FROM Pre_Flight_Check_Initiated, Zero_Hour_Execution, Hostile_Environment_Detected, Touchdown_Brings_Me_Round SINCE 1 hour ago")
    print(f"  SELECT message FROM Log WHERE app = '{APP_NAME}' SINCE 1 hour ago")
