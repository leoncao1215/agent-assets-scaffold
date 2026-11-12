# Selected native preferences

No model, provider, effort, permission mode, or update channel is preselected.
Add a small profile only after checking the actual client's supported settings.
Follow the [asset contract](../skills/sync-agent-assets/references/assets.md).

A profile has `version: 1`, an `agent` identifier, an `observedVersion` string,
and a `settings` object containing only selected native key/value pairs. Do not
copy a complete client configuration or translate keys into another client's
format by guessing. Preserve explicit local choices and unrelated settings.
