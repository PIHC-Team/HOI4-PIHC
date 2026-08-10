# Contributing to PIHC3

Thank you for helping develop The Pony in the High Castle. Writers,
translators, artists, testers, designers, and programmers are all welcome.

Start with the complete bilingual contributor guide:

- [English developer guide](docs/development/README.en.md)
- [中文开发指南](docs/development/README.zh.md)

Before opening a pull request:

1. Work from the current `master` branch and keep one focused purpose per pull
   request.
2. Use ParaDev to create or rename modules so object IDs, references, folders,
   localization, and resources stay synchronized.
3. Run the target module or family partial build while iterating, then run one
   whole-project cached build with no blocking diagnostics.
4. Run `git diff --check` and review every tracked file before committing.
5. Explain the gameplay intent, affected object IDs, localization status, and
   exact build or in-game testing in the pull request.

Do not commit generated output, caches, secrets, copied third-party work, or
assets you do not have permission to contribute. The repository currently has
no repository-wide open-source license; contribution does not imply unrelated
reuse or redistribution rights.
