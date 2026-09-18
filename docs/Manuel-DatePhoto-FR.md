DATE PHOTO — MANUEL

1. Principe
Date Photo ajoute un préfixe AAAA_MM_JJ_ au nom des photos :
IMG_4587.jpg → 2023_09_23_IMG_4587.jpg.
L’application travaille localement, sans compte ni transmission de données.

2. Date utilisée
Priorité : DateTimeOriginal (prise de vue), puis DateTimeDigitized
(numérisation), puis DateTime (modification EXIF). La première date valide
est retenue, y compris dans le sous-répertoire EXIF. Une date valide se situe
entre le 1er janvier 1990 et aujourd’hui inclus. Les dates du système de
fichiers ne sont jamais utilisées. Les photos sans date valide restent en place.
La date EXIF de modification n’est pas nécessairement la date de prise de vue.
ATTENTION : si les métadonnées indiquent une date erronée mais valide, le
préfixe et les dossiers de classement reprendront cette date erronée.
Le programme ne peut pas vérifier la date réelle de prise de vue.

3. Deux modes
Préfixer sans classer (par défaut) : renomme dans le dossier actuel.
Préfixer et classer : déplace vers le dossier parent choisi, dans
photos_annees / AAAA / AAAA_MM / AAAA_MM_JJ_nom.ext.
Un préfixe AAAA_MM_JJ_ déjà présent est conservé, sans vérifier sa concordance
avec les métadonnées. En mode préfixage seul, le fichier reste inchangé.

4. Marche à suivre
Choisissez la source et l’option sous-dossiers. Choisissez le mode et, pour
le classement, la destination. Cliquez sur Analyser et consultez le tableau.
Appliquer demande confirmation. Modifier les réglages invalide l’analyse.
Un suffixe _001, _002… distingue les noms en conflit dès l’aperçu.
Si la destination devient occupée après l’analyse, le fichier est laissé
en place et une erreur est affichée : aucun fichier existant n’est écrasé.

5. Arrêt et erreurs
Échap ou Arrêter interrompt après le fichier en cours. Les opérations déjà
réalisées restent effectuées. Les erreurs apparaissent dans le tableau ;
le traitement continue pour les autres fichiers. Il n’y a pas d’annulation
automatique : gardez une sauvegarde avant un classement important.
Le contenu des images est copié à l’identique, sans réencodage.
Les liens symboliques et les dossiers de destination sont exclus du parcours.

6. Formats et dépendances
JPEG, PNG, WebP, TIFF avec Pillow. HEIC/HEIF avec pillow-heif, facultatif.
Un format accepté ne garantit pas la présence d’une date EXIF.
Installation : py -m pip install Pillow
HEIC/HEIF : py -m pip install pillow-heif
Lancement : py EigrutelDatePhoto.py
F1 : manuel. Échap : arrêter. Double-clic sur une ligne : ouvrir son dossier.
FR/EN change l’interface et le manuel ; les noms des dossiers restent identiques.

7. Eigrutel Lab
Programme conçu et développé par Simon Léturgie dans le cadre d’Eigrutel BD Academy.
Version 1.0.0 — 18-09-2026
Code : GNU AGPL v3.0 ou version ultérieure.
Documentation et modèles : CC BY-SA 4.0, sauf mention contraire.
Marques, logos et signes distinctifs Eigrutel / Eigrutel Lab /
Eigrutel BD Academy : réservés.
