# Goal

Design and implement a **multi-agent system** that automates part of KRNL’s **employee onboarding workflow**. The system must:

- Orchestrate **multiple agents** that handle different onboarding tasks.
- Integrate with **common enterprise tools** (mock or real APIs like Google Drive, Calendar, Slack/Email).
- Ensure **verifiability** (logs, traceability).
- Be modular enough that additional agents could be added later.

# Requirements

## 1. Data Input (HR Forms)

- Accept **employee onboarding forms** (CSV/JSON upload or simple web form).
  - Example fields: name, email, role, start_date, department.
- Store raw data in a database (Postgres/MySQL/Firebase).

## 2. Multi-Agent Workflow

At least 3 - 4 distinct **agents**, working independently but coordinated:

- **Agent A → Validator**
  - Cleans input and checks for missing/invalid fields.
- **Agent B → Account Setup Agent**
  - Generates a mock system account (just store in DB).
  - Assigns default role-based permissions.
- **Agent C → Scheduler Agent**
  - Creates a calendar event for Day-1 orientation (real Google Calendar API or mock JSON).
- **Agent D → Notifier Agent**
  - Sends a Slack/Email message to HR with confirmation (can simulate with console output if no real integration).

Bonus: Wrap each agent as a service/module and **simulate AZA communication** (e.g., JSON messages over a queue). Show the use case of MCP within this system.

## 3. Verifiability & Logging

- Each agent must produce structured logs:
  - Input → Processing steps → Output.
- Store logs in a DB or JSON file for later auditing.
- Provide an API/dashboard to trace a single onboarding request across agents.

## 4. MCP / A2A Concepts (Applied)

- **MCP**: Create a simple “manifest” (JSON/YAML) for one agent (e.g., Scheduler) that describes its capabilities, inputs, and outputs.
- **A2A**: Demonstrate one example where Agent B calls Agent C directly (without going back to the orchestrator)

## 5. Frontend / Dashboard

- A simple admin dashboard (web or Flutter) with:
  - Upload form (or file upload).
  - List of new employees + their onboarding status.
  - Log viewer (traceability per employee).

## 6. Engineering Quality

- Deliver as a Dockerized project with docker-compose.
- Provide README with setup instructions.
- Include tests for at least one agent.
- Keep repo organized with clear commits.

# Deliverables

- GitHub repo (code, Dockerfile, README).
- Short demo video (5–10 mins) showing:
  - Upload employee data → agents run → results visible in dashboard.
  - Logs showing each agent’s actions.
- A 2 - 3 page design doc including:
  - Architecture diagram.
  - Explanation of agent communication.
  - Where MCP/A2A ideas were applied.
  - What would be needed to scale this in production.