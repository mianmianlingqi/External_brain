# Server Target serves Agent HTTP and View HTTP with Init secrets

On a server Target, one process serves the View (GET, view secret) and Brain commands (POST `/brain`, agent secret). Agents call `connect(address, agent_secret)` and keep using the Brain interface. A local Target still uses `file://` and `load`. Cloud volume `state.json` is the single source of truth.
