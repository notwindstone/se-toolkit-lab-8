# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**"What is the agentic loop?"**

The agent explained the agentic loop as a 5-step cycle:
1. **Perceive** — The agent receives input and understands the current state.
2. **Reason/Plan** — The agent thinks about what to do next, decides whether it has enough information.
3. **Act** — The agent executes an action, typically by calling a tool.
4. **Observe** — The agent receives the result of that action.
5. **Repeat** — Steps 2–4 loop until the task is complete or a stopping condition is met.

The agent gave a concrete example (finding latest Python version and saving to a file) and explained that the agentic loop is what separates a simple chatbot from an agent that can break down complex tasks, use tools, self-correct, and iterate.

**"What labs are available in our LMS?"**

Without MCP tools, the agent inspected local repo files (task markdown files) and listed the course tasks from `lab/tasks/required/`. It correctly noted that for actual LMS backend data (lab-01, lab-02, etc.), the MCP server would need to be configured. It did NOT return real backend data — exactly as expected for a bare agent.

## Task 1B — Agent with LMS tools

**"What labs are available?"**

With MCP tools configured, the agent called `mcp_lms_lms_labs` and returned real lab names from the backend:
1. Lab 01 – Products, Architecture & Roles
2. Lab 02 — Run, Fix, and Deploy a Backend Service
3. Lab 03 — Backend API: Explore, Debug, Implement, Deploy
4. Lab 04 — Testing, Front-end, and AI Agents
5. Lab 05 — Data Pipeline and Analytics Dashboard
6. Lab 06 — Build Your Own Agent
7. Lab 07 — Build a Client with an AI Coding Agent
8. Lab 08 — lab-08

**"Is the LMS backend healthy?"**

The agent called `mcp_lms_lms_health` and reported: "Yes, the LMS backend is healthy! It's running normally with 56 items in the system and no errors reported."

**"Which lab has the lowest pass rate?"**

The agent demonstrated multi-step tool chaining:
1. Called `mcp_lms_lms_pass_rates` for all 8 labs
2. Called `mcp_lms_lms_completion_rate` for additional context
3. Produced a formatted table showing Lab 02 has the lowest pass rate at 88.5% (131/148)

## Task 1C — Skill prompt

**"Show me the scores" (without specifying a lab)**

With the LMS skill prompt in place, the agent followed the strategy rules:
1. Called `lms_labs` first to discover available labs (as instructed by the skill)
2. Listed all 8 labs with their full titles (e.g. "Lab 01 – Products, Architecture & Roles")
3. Asked the user to choose which lab they want scores for, offering to pull a quick overview of all labs as an alternative

This is the correct behavior — the skill prompt taught the agent to call `lms_labs` first when a lab-specific metric is requested without a lab name, and to ask the user to choose rather than guessing.

## Task 2A — Deployed agent

<!-- Paste a short nanobot startup log excerpt showing the gateway started inside Docker -->

## Task 2B — Web client

<!-- Screenshot of a conversation with the agent in the Flutter web app -->

## Task 3A — Structured logging

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->
