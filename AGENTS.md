# Codex instructions: RE3 N64 reference pipeline

1. Treat the original Classic Toolkit installer as an **untrusted binary**. Never execute it in CI or install it automatically.
2. Preserve the original installer in private Drive storage. Do not commit it, reconstructed installers, ROMs, game assets, or extracted proprietary content to a public repository.
3. The workflow audits scripts and metadata. It does NOT run the Toolkit, extract its internal files, or establish functionality of bundled modules.
4. Use `scripts/toolkit_pipeline.py inventory <extracted-directory> <output-directory>` after separately and safely obtaining an extracted directory on an isolated machine.
5. For approved redistribution, `split <file> <output-directory>` produces 24,000,000-byte chunks and a checksum manifest; `restore <directory> <output-file>` verifies every part and the full reconstructed file.
6. Record each technical assertion with source filename, exact version, evidence and confidence. Distinguish measured data from proposed RE3 port implementation.
7. Compare RE3 PS1 RDT, SCD, EMD/MD2, camera, collision and asset records with RE2 N64 extraction manifests, never equate their formats by assumption.
8. Keep asset inventories as JSON/CSV and documentation as Markdown. Only copy validated source-derived findings into the project.
9. Keep private inputs out of GitHub Actions logs and public artifacts. Pin third-party action SHAs before production deployment.
10. First target is verified ROM boot to splash boards and RE3 main menu; subsequent targets are rooms, camera/collision, inventory, animations and audio.
