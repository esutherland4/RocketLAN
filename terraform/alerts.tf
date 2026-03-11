locals {
  app = "RocketLAN"
}

# ---------------------------------------------------------------------------
# Alert Policy
# ---------------------------------------------------------------------------

resource "newrelic_alert_policy" "rocketlan" {
  name                = "RocketLAN Mission Control"
  incident_preference = "PER_CONDITION"
}

# ---------------------------------------------------------------------------
# Metric Conditions
# ---------------------------------------------------------------------------

resource "newrelic_nrql_alert_condition" "deep_space_delay" {
  account_id                   = var.account_id
  policy_id                    = newrelic_alert_policy.rocketlan.id
  name                         = "Deep Space Delay — orbital_latency_ms"
  enabled                      = true
  violation_time_limit_seconds = 86400
  aggregation_window           = 60
  aggregation_method           = "event_flow"
  aggregation_delay            = 120

  nrql {
    query = "SELECT average(orbital_latency_ms) FROM Metric WHERE app = '${local.app}'"
  }

  critical {
    operator              = "above"
    threshold             = 500
    threshold_duration    = 60
    threshold_occurrences = "at_least_once"
  }

  warning {
    operator              = "above"
    threshold             = 250
    threshold_duration    = 60
    threshold_occurrences = "at_least_once"
  }
}

resource "newrelic_nrql_alert_condition" "fuse_burn_rate" {
  account_id                   = var.account_id
  policy_id                    = newrelic_alert_policy.rocketlan.id
  name                         = "Fuse Burn Rate Critical — battery drain"
  enabled                      = true
  violation_time_limit_seconds = 86400
  aggregation_window           = 60
  aggregation_method           = "event_flow"
  aggregation_delay            = 120

  nrql {
    query = "SELECT average(fuse_burn_rate_pct) FROM Metric WHERE app = '${local.app}'"
  }

  critical {
    operator              = "above"
    threshold             = 7.0
    threshold_duration    = 60
    threshold_occurrences = "at_least_once"
  }

  warning {
    operator              = "above"
    threshold             = 5.0
    threshold_duration    = 60
    threshold_occurrences = "at_least_once"
  }
}

resource "newrelic_nrql_alert_condition" "packet_void_overflow" {
  account_id                   = var.account_id
  policy_id                    = newrelic_alert_policy.rocketlan.id
  name                         = "Packet Void Overflow — lost capsules"
  enabled                      = true
  violation_time_limit_seconds = 86400
  aggregation_window           = 60
  aggregation_method           = "event_flow"
  aggregation_delay            = 120

  nrql {
    query = "SELECT sum(lost_capsule_count) FROM Metric WHERE app = '${local.app}'"
  }

  critical {
    operator              = "above"
    threshold             = 50
    threshold_duration    = 60
    threshold_occurrences = "at_least_once"
  }
}

resource "newrelic_nrql_alert_condition" "solo_flight_duration" {
  account_id                   = var.account_id
  policy_id                    = newrelic_alert_policy.rocketlan.id
  name                         = "Solo Flight Too Long — disconnection duration"
  enabled                      = true
  violation_time_limit_seconds = 86400
  aggregation_window           = 60
  aggregation_method           = "event_flow"
  aggregation_delay            = 120

  nrql {
    query = "SELECT max(solo_flight_duration_sec) FROM Metric WHERE app = '${local.app}'"
  }

  critical {
    operator              = "above"
    threshold             = 600
    threshold_duration    = 60
    threshold_occurrences = "at_least_once"
  }

  warning {
    operator              = "above"
    threshold             = 300
    threshold_duration    = 60
    threshold_occurrences = "at_least_once"
  }
}

# ---------------------------------------------------------------------------
# Event Conditions
# ---------------------------------------------------------------------------

resource "newrelic_nrql_alert_condition" "hostile_environment" {
  account_id                   = var.account_id
  policy_id                    = newrelic_alert_policy.rocketlan.id
  name                         = "Hostile Environment Detected — captive portal"
  enabled                      = true
  violation_time_limit_seconds = 86400
  aggregation_window           = 60
  aggregation_method           = "event_flow"
  aggregation_delay            = 120

  nrql {
    query = "SELECT count(*) FROM Hostile_Environment_Detected WHERE app = '${local.app}'"
  }

  critical {
    operator              = "above"
    threshold             = 0
    threshold_duration    = 60
    threshold_occurrences = "at_least_once"
  }
}

# ---------------------------------------------------------------------------
# Log Condition
# ---------------------------------------------------------------------------

resource "newrelic_nrql_alert_condition" "long_long_ping" {
  account_id                   = var.account_id
  policy_id                    = newrelic_alert_policy.rocketlan.id
  name                         = "I think it's gonna be a long, long ping — FATAL errors"
  enabled                      = true
  violation_time_limit_seconds = 86400
  aggregation_window           = 60
  aggregation_method           = "event_flow"
  aggregation_delay            = 120

  nrql {
    query = "SELECT count(*) FROM Log WHERE app = '${local.app}' AND level = 'FATAL'"
  }

  critical {
    operator              = "above"
    threshold             = 0
    threshold_duration    = 60
    threshold_occurrences = "at_least_once"
  }
}
