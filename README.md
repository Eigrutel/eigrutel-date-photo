# Date Photo · Eigrutel Lab

![Icône / Icon](favdate.png)

**FR** — Ajouter la date EXIF au nom des photos, avec classement chronologique facultatif. Application Windows locale et bilingue FR/EN. Version 1.0.0 — 18-09-2026.

**EN** — Add EXIF dates to photo filenames, with optional chronological filing. Local Windows application, with a French/English interface. Version 1.0.0 — 2026-09-18.

## Français

- Préfixage `AAAA_MM_JJ_`, dans le dossier actuel ou avec déplacement dans `photos_annees/AAAA/AAAA_MM`.
- Analyse et aperçu avant confirmation ; noms en conflit distingués par suffixe, sans écrasement.
- Dates EXIF de 1990 à aujourd’hui. Fichiers sans date valide laissés en place.
- **Une date erronée dans les métadonnées produit une date erronée dans le résultat. Le programme ne vérifie pas la date réelle de prise de vue.**
- Priorité EXIF : prise de vue, numérisation, modification. Jamais les dates du système de fichiers.
- JPEG, PNG, WebP, TIFF et HEIC/HEIF (inclus dans les dépendances de cette distribution).
- Arrêt par Échap ; manuel intégré (i / F1). Aucun compte, aucune collecte, aucun service distant.

### Utiliser et construire sous Windows

Python 3.10 ou plus récent est nécessaire pour les sources ; Python 3.11 est utilisé par le workflow.

1. Extraire le ZIP dans un dossier.
2. Double-cliquer sur `Construire_DatePhoto.cmd` (connexion Internet nécessaire pour installer les dépendances).
3. Attendre le message de succès. L’EXE se trouve dans `dist/DatePhoto-1.0.0.exe`.
4. Tester sur des copies de photos avant diffusion. Le programme fonctionne ensuite sans Python installé.

Ou lancer les sources :

```powershell
py -m pip install -r requirements.txt
py EigrutelDatePhoto.py
```

Ne pas séparer `favdate.png` et `favdate.ico` du programme source pour conserver les icônes. Elles sont intégrées à l’EXE lors de la construction. `ui_common.py` n’est pas nécessaire.

[Manuel FR](docs/Manuel-DatePhoto-FR.md) · [Manuel hors connexion](Manuel-DatePhoto.html) · [Mise en ligne](docs/MISE-EN-LIGNE.md)

## English

- `YYYY_MM_DD_` prefix, in place or moved into `photos_annees/YYYY/YYYY_MM`.
- Preview and confirmation; conflict suffixes, no overwriting of existing files.
- Valid EXIF dates range from 1990 through today. Undated files remain in place.
- **Incorrect metadata dates produce incorrect result dates. The application cannot verify the actual capture date.**
- EXIF priority: capture, digitization, modification. Never filesystem dates.
- JPEG, PNG, WebP, TIFF, HEIC/HEIF. Escape stops processing; i / F1 opens the manual.
- Local processing, no accounts, no data collection, no remote services.

### Windows build

Extract this archive and run `Construire_DatePhoto.cmd`. Python 3.10+ and Internet access for dependency installation are required; the workflow uses Python 3.11. The executable is created at `dist/DatePhoto-1.0.0.exe` and runs without a separate Python installation. Test on copies of photos before distributing.

To run the source, install `requirements.txt`, then run `EigrutelDatePhoto.py`. Keep the two `favdate` icons alongside it; no `ui_common.py` is required.

[English manual](docs/Manuel-DatePhoto-EN.md)

## Licences / Licenses

Programme conçu et développé par Simon Léturgie dans le cadre d’Eigrutel BD Academy.
Designed and developed by Simon Léturgie as part of Eigrutel BD Academy.

- Code : GNU AGPL v3.0 ou ultérieure / GNU AGPL v3.0 or later — [LICENSE](LICENSE).
- Documentation et modèles / Documentation and templates: CC BY-SA 4.0 — [LICENSE-DOCS](LICENSE-DOCS).
- Marques et logos Eigrutel réservés / Eigrutel trademarks and logos reserved — [TRADEMARKS.md](TRADEMARKS.md).

Le renommage et le classement modifient les chemins, pas le contenu des images. Pas d’annulation automatique : conservez vos sauvegardes.
Renaming and filing change paths, not image content. No automatic undo: keep your backups.
