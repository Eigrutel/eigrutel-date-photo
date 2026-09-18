# GitHub — Mise en ligne / Publishing

Nom suggéré / Suggested repository name: `eigrutel-date-photo`

Description:
```text
Dater et classer ses photos via EXIF. / Date and organize photos using EXIF. Windows · FR/EN · Eigrutel Lab.
```

1. Créer un dépôt public sans README ni licence automatiques. / Create a public repository without generated README or license.
2. Déposer le contenu de ce dossier à la racine, y compris `.github`, `.gitignore` et `.gitattributes`. / Upload this folder’s contents to the repository root, including dotfiles.
3. Ne pas déposer `.venv`, `build`, `dist`, `__pycache__`. / Do not upload generated folders.
4. Construire sur Windows avec `Construire_DatePhoto.cmd` et tester l’EXE. / Build on Windows and test the executable.
5. Créer la release avec le tag `v1.0.0`. Titre et description : `docs/RELEASE-v1.0.0.md`. / Create release tag `v1.0.0`; use the release document for its title and description.
6. Joindre `dist/DatePhoto-1.0.0.exe`, `dist/SHA256SUMS.txt`, `LICENSE` et `LICENSE-DOCS`. / Attach the executable, checksums and licenses.
7. Télécharger l’EXE publié et tester son lancement, FR/EN, icône et renommage sur copies. / Download the published executable and test startup, languages, icon and renaming on copies.

Commit:
```text
Première version Date Photo / Initial Date Photo release — v1.0.0
```

Topics: `python`, `windows`, `tkinter`, `exif`, `photo-organizer`, `file-renamer`, `open-source`, `eigrutel-lab`.

Le workflow Actions peut être lancé manuellement ou sur un nouveau tag v*. Il produit un artefact téléchargeable, sans publier ni remplacer automatiquement la release. / Actions runs manually or on a new v* tag, producing a downloadable artifact without automatically publishing or replacing a release.

Si les fichiers commençant par un point manquent après l’envoi, utiliser Add file → Create new file, puis leur nom complet ; pour le workflow : `.github/workflows/build-windows.yml`. Copier le contenu exact du fichier de cette archive. / If dotfiles are missing, create them using their full paths and copy their exact contents from this archive.
