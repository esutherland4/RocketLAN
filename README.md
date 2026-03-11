# RocketLAN 🚀

> **"Burning out your router up here alone."**

A highly advanced Wi-Fi and network troubleshooting app for IT professionals. When your server goes down or your connection drops, the app uses an AI **Mission Commander** to help you re-establish an uplink.

> *If the app detects a fatal network error, the screen turns pitch black with floating stars, and a pop-up simply reads:*
> ### "I think it's gonna be a long, long ping."

---

## Mission Control Telemetry (`nr_fake_telemetry.py`)

Generates fake metrics, events, and logs into New Relic to simulate a live RocketLAN outage session — useful for building dashboards and testing alert conditions.

### Setup

```bash
export NR_LICENSE_KEY=<your ingest license key>
export NR_ACCOUNT_ID=<your account ID>
python3 nr_fake_telemetry.py
```

### Optional env vars

| Variable | Default | Description |
|---|---|---|
| `NR_REGION` | `US` | Set to `EU` for EU data center |
| `NR_DATAPOINTS` | `20` | Number of metric datapoints (spread over 30 min) |

---

## Telemetry Reference

### Core Metrics

| Metric | Type | Description |
|---|---|---|
| `orbital_latency_ms` | Gauge | Round-trip ping time. >500ms triggers **Deep Space Delay** warning. |
| `fuse_burn_rate_pct` | Gauge | Battery drain rate while aggressively scanning for signal. |
| `lost_capsule_count` | Counter | Total dropped packets floating in the digital void. |
| `solo_flight_duration_sec` | Counter | Continuous time fully disconnected from the LAN. |

### Custom Events

| Event | Trigger |
|---|---|
| `Pre_Flight_Check_Initiated` | User taps "Run Network Diagnostics" |
| `Zero_Hour_Execution` | Scheduled automated network test at 9:00 AM |
| `Hostile_Environment_Detected` | Captive portal detected with <1 Mbps download |
| `Touchdown_Brings_Me_Round` | Device re-establishes stable gateway handshake |

### Sample Log Output

```
[INFO]  [INIT]   Preparing daily diagnostic cron job.
[INFO]  [CRON]   Zero hour: 9 AM. Ignition sequence start.
[DEBUG] [PING]   Pinging 8.8.8.8. Awaiting telemetry...
[WARN]  [UPLINK] Connection lost to primary gateway. Burning out his router up here alone.
[ERROR] [DNS]    Host unreachable. I think it's gonna be a long, long ping.
[WARN]  [AUTH]   Sudo privileges rejected. User is not the admin they think he is at home. Oh, no, no, no.
[FATAL] [WIFI]   Auto-connected to "Starbucks_Guest_WiFi". Network environment is hostile.
[FATAL] [WIFI]   Mars ain't the kind of place to route your packets. In fact, it's cold as hell.
[INFO]  [UPLINK] Handshake re-established. Touchdown brings me round to find I'm not so far from home.
```

---

### NRQL to Verify

```sql
SELECT average(orbital_latency_ms) FROM Metric WHERE app = 'RocketLAN' TIMESERIES SINCE 1 hour ago
SELECT average(fuse_burn_rate_pct), sum(lost_capsule_count) FROM Metric WHERE app = 'RocketLAN' SINCE 1 hour ago
SELECT * FROM Pre_Flight_Check_Initiated, Zero_Hour_Execution, Hostile_Environment_Detected, Touchdown_Brings_Me_Round SINCE 1 hour ago
SELECT message FROM Log WHERE app = 'RocketLAN' SINCE 1 hour ago
```
