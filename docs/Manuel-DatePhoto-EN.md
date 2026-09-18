DATE PHOTO — MANUAL

1. Purpose
Date Photo adds a YYYY_MM_DD_ prefix to photo filenames:
IMG_4587.jpg → 2023_09_23_IMG_4587.jpg.
The application works locally, without accounts or data transmission.

2. Date selection
Priority: DateTimeOriginal (capture), then DateTimeDigitized (digitization),
then DateTime (EXIF modification). The first valid date is used, including
values in the EXIF subdirectory. Valid dates range from January 1, 1990,
through today. Filesystem timestamps are never used. Photos without a valid
date are left in place. The EXIF modification date is not necessarily the
capture date.
WARNING: if metadata contains an incorrect but valid date, the filename prefix
and filing folders will use that incorrect date. The application cannot
verify the actual capture date.

3. Two modes
Add date prefix only (default): rename within the current folder.
Add date prefix and organize: move into the selected parent folder, under
photos_annees / YYYY / YYYY_MM / YYYY_MM_DD_name.ext.
An existing YYYY_MM_DD_ prefix is preserved without checking it against
metadata. In prefix-only mode, such files remain unchanged.

4. Workflow
Select a source and choose whether to include subfolders. Select the mode
and, for filing, a destination. Click Analyze and review the table.
Apply asks for confirmation. Changing settings invalidates the analysis.
A _001, _002… suffix resolves filename conflicts in the preview.
If a destination becomes occupied after analysis, the file stays in place
and an error is shown: existing files are never overwritten.

5. Stopping and errors
Escape or Stop stops after the current file. Completed operations remain
in effect. Errors appear in the table; other files continue processing.
There is no automatic undo: keep a backup before reorganizing many files.
Image content is copied unchanged, without re-encoding.
Symbolic links and destination folders are excluded from traversal.

6. Formats and dependencies
JPEG, PNG, WebP, TIFF through Pillow. HEIC/HEIF through optional pillow-heif.
A supported format does not guarantee that an EXIF date is present.
Install: py -m pip install Pillow
HEIC/HEIF: py -m pip install pillow-heif
Launch: py EigrutelDatePhoto.py
F1: manual. Escape: stop. Double-click a row: open its folder.
FR/EN changes the interface and manual; folder names stay identical.

7. Eigrutel Lab
Designed and developed by Simon Léturgie as part of Eigrutel BD Academy.
Version 1.0.0 — 2026-09-18
Code: GNU AGPL v3.0 or later.
Documentation and templates: CC BY-SA 4.0, unless otherwise specified.
Eigrutel / Eigrutel Lab / Eigrutel BD Academy trademarks, logos and
distinctive signs: reserved.
