---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

Use the LMS MCP tools to answer questions about the Learning Management System.

## Available tools

| Tool | When to use | Parameters |
|------|-------------|------------|
| `lms_health` | User asks about backend health, system status, or item count | None |
| `lms_labs` | User asks what labs exist, or you need lab IDs before querying lab-specific data | None |
| `lms_learners` | User asks who is enrolled or registered | None |
| `lms_pass_rates` | User asks about scores, pass rates, or task performance for a specific lab | `lab` (e.g. "lab-01") |
| `lms_timeline` | User asks about submission activity over time for a lab | `lab` |
| `lms_groups` | User asks about group performance or group comparisons | `lab` |
| `lms_top_learners` | User asks who is doing best in a lab | `lab`, optional `limit` (default 5) |
| `lms_completion_rate` | User asks how many students passed a lab | `lab` |
| `lms_sync_pipeline` | User asks to refresh data from the autochecker, or backend reports zero items | None |

## Strategy

- **If the user asks for scores, pass rates, completion, groups, timeline, or top learners without naming a lab:** call `lms_labs` first to discover available labs.
- **If multiple labs are available and the user didn't specify one:** use the shared `structured-ui` skill to present a choice of labs to the user. On channels that don't support structured UI, list the labs as plain text and ask the user to pick one.
- **Use each lab's title** (from `lms_labs`) as the default user-facing label unless the tool output gives a better identifier.
- **Format numeric results clearly:** show percentages with one decimal (e.g. 88.5%), counts as integers, and include the numerator/denominator when available (e.g. "131 / 148").
- **Keep responses concise.** Don't dump raw JSON. Summarize the data in a readable format — tables or bullet lists work well.
- **When the user asks "what can you do?":** explain that you can query live LMS data — lab listings, pass rates, scores, group performance, top learners, submission timelines, and completion rates. Mention that you need a lab name for most analytics queries.
- **If the backend reports zero items or the user suspects stale data:** suggest running `lms_sync_pipeline` to refresh, then retry their query.
- **If a lab parameter is needed and not provided:** ask the user which lab they want. Don't guess.
