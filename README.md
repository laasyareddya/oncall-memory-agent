On-Call Incident Response Agent

An AI-powered on-call assistant that uses persistent memory to help engineers diagnose recurring incidents faster.

Problem

On-call engineers often encounter the same or similar incidents repeatedly. Without reliable memory, they may spend time rediscovering previous root causes, successful fixes, and approaches that did not work.

This project gives an on-call engineer an assistant that remembers previous incidents and uses that experience when a new alert appears.

What It Does

The agent follows a simple workflow:

An engineer provides an alert or error log.

The agent searches Hindsight for relevant previous incidents.

Previous root causes, successful fixes, and failed approaches are used to inform the response.

The agent suggests a diagnosis and potential resolution.

After the incident is resolved, the engineer records the outcome.

The new outcome is retained in memory and can help with future incidents.

Example

A new Redis connection error can be compared with a previous incident involving Redis connection-pool exhaustion.

Instead of giving only a generic troubleshooting response, the agent can surface the previous incident, explain what fixed it, and mention an approach that failed previously.

Architecture
                 ┌─────────────────────┐
                 │   On-Call Engineer  │
                 └──────────┬──────────┘
                            │
                     Alert / Error Log
                            │
                            ▼
                 ┌─────────────────────┐
                 │   Agent / LLM       │
                 └──────────┬──────────┘
                            │
                     Recall memories
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Hindsight Memory    │
                 │                     │
                 │ Past incidents      │
                 │ Root causes         │
                 │ Successful fixes    │
                 │ Failed approaches   │
                 └──────────┬──────────┘
                            │
                     Relevant memories
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Diagnosis + Fix     │
                 └──────────┬──────────┘
                            │
                       Resolution
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Retain new outcome  │
                 │ in Hindsight        │
                 └─────────────────────┘

How Hindsight Memory Is Used

Hindsight provides the agent with persistent memory across incidents.

Retain

The application stores information about incidents such as:

Error messages and logs

Root causes

Successful fixes

Troubleshooting attempts that failed

Resolution outcomes

Relevant service information

This allows the agent to learn from resolved incidents.

Recall

When a new incident is submitted, the application queries Hindsight for memories that are relevant to the new alert.

The retrieved memories are provided to the agent along with the current incident so that the response can incorporate previous experience.

Continuous Improvement

After an incident is resolved, the new outcome is retained.

This creates a feedback loop:

Incident
   ↓
Recall previous experience
   ↓
Suggest resolution
   ↓
Resolve incident
   ↓
Retain outcome
   ↓
Better context for future incidents

Before and After Memory

The project can demonstrate the effect of memory by comparing two situations.

Without memory:
The agent has only the current alert and provides general troubleshooting suggestions.

With memory:
The agent can identify a similar historical incident and use its documented root cause, successful fix, and failed attempts to provide more contextual guidance.

Setup
Requirements

Python 3.x

Hindsight account/API access

Groq API key

Git

Installation

Clone the repository and enter the project directory:

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd oncall-memory-agent


Create a virtual environment:

python -m venv venv


Activate it on Windows:

venv\Scripts\activate


Install the dependencies:

pip install -r requirements.txt


Create a .env file containing your local API credentials.

Do not commit .env or API keys to GitHub.

A .env.example file should contain placeholder values only.

Running the Application

Start the application using the project's configured entry point, for example:

streamlit run app.py


The exact command may vary depending on the final project structure.

Demo Flow

The recommended demonstration is:

Submit an incident without historical memory and show the generic response.

Seed historical incidents into Hindsight.

Submit a similar new incident.

Show the memories retrieved from Hindsight.

Show how the previous incident influences the suggested resolution.

Mark the incident as resolved.

Retain the new resolution.

Explain how that new memory can help with future incidents.

Project Goal

The goal is to demonstrate that persistent incident memory can turn an AI assistant from a generic troubleshooting tool into an assistant that can make use of an organization's accumulated incident-response experience.