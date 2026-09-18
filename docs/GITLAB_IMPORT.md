# GitLab migration snapshot

This branch captures the complete selected local Open FMEA working tree, including uncommitted development, as an isolated migration commit. Its parent is 95f975be94637e639d89f6e1eba4218a8be26440 from codex/phase-b-django-poc.

Included editions: standalone HTML and portable container data; Django application and portable domain model; SharePoint demo source and its installable package. Architecture documents, tests, sample inputs, legacy code, and historical source snapshots are also retained.

Dependency directories, operational SQLite databases, uploads, caches, Windows metadata, and a third-party standards reference PDF are excluded from the current snapshot. Portable JSON/container and SQL demo sources are retained. Historical Git commits have not been rewritten.

No changes were made to application behavior for this migration. The SharePoint edition still uses personal browser storage; shared SharePoint Lists storage is not implemented.

The original local checkout and its staging area remain unchanged. The migration does not transfer GitHub issues, pull requests, or account settings.
