# Security Policy

## Supported Versions

Open FMEA is currently in public demo stage. Security review and fixes focus on the current `main` branch and the latest published release.

| Version | Supported |
| --- | --- |
| Latest `main` | Yes |
| Latest release | Yes |
| Older demo builds | No |

## Reporting a Vulnerability

Please do not disclose security vulnerabilities publicly before they have been reviewed.

Preferred reporting path:

1. Use GitHub's private vulnerability reporting feature if it is available on this repository.
2. If private reporting is not available, open a GitHub issue with a minimal description and ask for a private contact path. Do not include exploit details, secrets, private data, or sensitive logs in the public issue.

Useful information to include privately:

- Affected version or commit.
- Reproduction steps.
- Expected impact.
- Whether the issue affects local demo use, container use, workbook import, AI provider integration, or generated files.

## Security Notes

- The current release is a local-first demo application, not a hardened hosted service.
- Do not upload sensitive production FMEA data into public issues or sample files.
- Keep local SQLite databases, uploads, logs, and generated build output out of commits.
- Optional Ollama integration is intended for local AI experiments. Review imported or AI-assisted data before treating it as controlled FMEA content.

