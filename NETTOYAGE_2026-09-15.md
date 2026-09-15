# Nettoyage architectural — 15 septembre 2026

## Nouveau cap

TomeLinea ne cherche plus à reproduire un document Word page par page avant de pouvoir travailler. Le contrat actif est :

**Source intacte → import fidèle du contenu → contrôle d'intégrité → corrections sûres → réglages généraux → pagination TomeLinea → Survol.**

Le livre étalon peut faire 55 pages dans Word/LibreOffice sans que TomeLinea doive produire 55 pages. La pagination de référence devient celle construite par TomeLinea après les réglages du Livre.

## Code retiré

Le nettoyage a supprimé les couches devenues contraires ou inutiles :

- conversion OOXML → RTF ;
- hébergement Microsoft RichEdit par `ctypes` ;
- pagination et édition RichEdit ;
- ancien hôte Canvas mono-page devenu redondant avec Canvas par chapitre ;
- ancienne voie expérimentale `settings_shell` ;
- anciens arbres `src/core`, `src/engine`, `src/gui`, `src/gui_v3`, `src/library`, `src/modules`, `src/theme`, `src/widgets` ;
- anciens points d'entrée V1/V2 et fichiers racine non référencés ;
- modules V4 isolés sans aucun appel depuis l'application active ;
- anciens assets GUI V2/V3 et miniatures non référencés ;
- sauvegardes de patchs, caches, journaux et copies runtime ;
- tests devenus spécifiques aux anciennes interfaces de réglages.

Les moteurs d'analyse du texte, d'anomalies, de flux et les règles éditoriales n'ont pas été supprimés : ils servent au contrôle du Livre et au Survol. Ce qui a été retiré est la tentative de transformer TomeLinea en traitement de texte ou de faire d'un éditeur externe l'autorité de mise en page.

## Import DOCX actif

L'import enregistre la Source puis construit un modèle factuel. La copie de travail utilise le contrat `content_first`.

Les informations Source restent conservées comme métadonnées. La police de travail par défaut est Arial, tandis que la police Source est conservée séparément. Le choix de la police définitive du Livre peut donc être fait au début des réglages puis provoquer une vraie repagination TomeLinea.

Les images sont extraites avec leur original et leur repère logique. Elles arrivent initialement comme marqueurs Source ; leur implantation TomeLinea est décidée pendant le Survol au lieu de reproduire à l'avance la géométrie flottante de Word.

## Non-régressions protégées

Références historiques de l'ancien dépôt conservé dans `C:\Users\PC\projet` :

- Phase 1 DOCX : `eedd18b`
- Canvas par chapitre : `8f261c7`
- Persistance : `1aa3a1d`
- Pagination globale légère : `e71b174`
- Sauvegarde avant sortie de Composition : `b7f4539`
- Navigation propre validée : `6651865`

Le projet nettoyé repart sur un nouveau dépôt Git local afin de constituer une base lisible sans transporter les sauvegardes et objets Git historiques. L'ancien projet reste la référence d'archive et n'est pas modifié.

## Contrôle du livre étalon

Le test de référence vérifie maintenant l'intégrité du contenu et non le nombre de pages Word. Sur le livre étalon utilisé pendant le nettoyage :

- 520 paragraphes récupérés ;
- 19 images récupérées ;
- 6 sauts de page explicites récupérés ;
- rendu de travail en Arial ;
- Georgia conservée comme police Source ;
- les 19 images arrivent comme repères logiques en attente d'une décision TomeLinea.

## Tests à conserver

`tests/test_content_first_architecture.py` contrôle notamment :

- l'inventaire complet du contenu ;
- la conservation des images et paragraphes ;
- la distinction police de travail / police Source ;
- les marqueurs d'image Source ;
- l'absence de faux retraits par tabulation et de faux espacements par paragraphes vides ;
- la séparation entre mode lecture et mode édition dans les métadonnées Canvas.
