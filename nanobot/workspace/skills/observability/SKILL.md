---
name: observability
description: Diagnose errors using logs and traces
always: true
---

# Observability Skill

Use the observability MCP tools to diagnose errors and investigate issues by querying VictoriaLogs and VictoriaTraces.

## Available tools

| Tool | When to use | Parameters |
|------|-------------|------------|
| `logs_error_count` | User asks about errors, failures, or what went wrong. Use this first to check if there are any recent errors at all. | `service` (default: "Learning Management Service"), `minutes` (default: 60) |
| `logs_search` | Inspect specific log entries after `logs_error_count` shows errors, or user asks about a specific event. | `query` (LogsQL string), optional `limit` |
| `traces_list` | User wants to see recent request traces for a service. | `service`, optional `limit` |
| `traces_get` | You found a `trace_id` in logs and need the full span hierarchy to understand what happened. | `trace_id` |

## Strategy

- **If the user asks about errors or failures:** call `logs_error_count` first with a scoped service name and a recent time window (e.g. last 10 minutes for fresh data). This tells you whether there are any errors at all.
- **If `logs_error_count` shows errors:** call `logs_search` with a query targeting the affected service and time window to inspect individual log entries. Look for `trace_id` fields in the results.
- **If you find a `trace_id` in the logs:** call `traces_get` with that ID to see the full span hierarchy. Identify where the failure occurred by looking at spans with errors or high latency.
- **Summarize findings concisely.** Don't dump raw JSON. Tell the user what service had errors, what the error was, and where in the request flow it failed.
- **If the user asks about a specific time range:** use `_time:Nm` or `_time:Nh` in the LogsQL query (e.g. `_time:10m` for last 10 minutes, `_time:1h` for last hour).
- **Useful field filters:** `service.name:"Learning Management Service"`, `severity:ERROR`, `event:db_query`.
- **If no errors are found:** report that clearly — "No errors found in the last N minutes for the LMS backend."
- **When narrowing scope:** prefer specific service names and short time windows (10 minutes) to avoid surfacing unrelated historical errors from other services.
