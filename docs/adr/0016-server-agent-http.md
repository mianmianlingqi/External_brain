# Server Target serves Agent HTTP and View HTTP with Init secrets

On a server Target, one process serves the View (GET, view secret) and Brain commands (POST `/brain`, agent secret). Agents call `connect(address, agent_secret)` and keep using the Brain interface. A local Target still uses `file://` and `load`. Cloud volume `state.json` is the single source of truth.

The process Target is `/data`. A volume mounted there keeps `.brain/state.json` and the Init secrets across instance sleep and rebuild. In-container disk is rejected: scale-to-zero would wipe the Direction.
