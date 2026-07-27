# Privacy and safety boundaries

- Repository screenshots and interface fixtures use synthetic demo records.
- Do not commit real patient, customer, employer, or research-lab data.
- Local uploads, exports, databases, model files, logs, and environment secrets are ignored.
- The default credentials and secret are development-only and must be replaced before any shared deployment.
- Automated output must remain reviewable and must not be presented as medical advice.
- Production use would require a separate security, privacy, legal, and clinical validation process.

If sensitive data is committed accidentally, remove public access, rotate affected credentials, and use an approved history-rewrite and disclosure process.
