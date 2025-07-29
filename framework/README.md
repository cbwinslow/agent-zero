# Multi-Agent Development Framework

This directory contains a prototype workflow for building applications using cooperating AI agents.

It provides the following structure:

- **agents/** – agent templates and implementations
- **workflows/** – reusable task sequences
- **projects/** – saved project state and code
- **tools/** – scripts and utilities the agents may use
- **teams/** – definitions of agent teams
- **configs/** – environment and provider configuration
- **envs/** – isolated runtime environments (e.g., Docker images)

The framework is intended to work with open source LLM providers such as Ollama and local Mistral models via OpenRouter.

The ``orchestrator.py`` script can load a workflow configuration and spawn the listed agent processes. A sample workflow definition is provided in ``workflows/default.json`` which launches two dummy agents for demonstration purposes.
