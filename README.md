# TomeLinea V4

**TomeLinea — La ligne éditoriale jusqu'au livre**

TomeLinea est un atelier éditorial de construction de livres. L'auteur fournit son contenu ; TomeLinea l'importe, l'analyse, applique les règles techniques certaines après validation, construit la mise en page du Livre puis accompagne les décisions particulières pendant le Survol.

## Architecture active

Le parcours de référence est désormais :

**Source intacte → import fidèle du contenu → contrôle d'intégrité → corrections techniques sûres → réglages généraux du Livre → pagination TomeLinea → Survol → Visionneur → Sortie.**

L'import DOCX n'a plus pour objectif de reproduire Word page par page. Il doit conserver sans perte ni invention le texte, l'ordre, les paragraphes, titres, listes, tableaux, images, ruptures, liens et autres objets utiles. Les propriétés de mise en forme de la Source restent des informations d'origine ; elles ne sont pas des contraintes obligatoires de la composition TomeLinea.

Une police neutre de travail peut être utilisée pendant la préparation. TomeLinea distingue toujours la **police Source**, la **police de travail** et la **police du Livre**. Le choix de la police du Livre intervient avant la stabilisation de la pagination.

## Moteur de travail

- Interface : Python / Tkinter.
- Édition et composition courante : Canvas Editor dans WebView2 via le runtime `tkwry` embarqué.
- Unité de travail : Canvas par chapitre pour conserver une frappe fluide.
- Source DOCX : analyse factuelle indépendante de la copie de travail.
- Images : original extrait conservé, repère logique Source conservé, implantation TomeLinea décidée ensuite.
- Persistance : copie de travail TomeLinea ; la Source DOCX n'est jamais réécrite silencieusement.

## Répertoires utiles

- `main_v4.py` : lancement de TomeLinea V4.
- `src/gui_v4/` : interface active et hôte Canvas/WebView2.
- `src/v4/` : modèle, import, analyse, composition, Structure, Survol et contrôles.
- `src/gui_v4/web_canvas/` : application Canvas Editor embarquée.
- `runtime/` : runtime local nécessaire à WebView2/tkwry.
- `resources/` : ressources éditoriales TomeLinea.
- `assets/` : identité visuelle et ressources réellement utilisées par la V4.
- `tests/` : tests ciblés de non-régression.

## Règles de développement

- Ne pas empiler des correctifs pour compenser un moteur mal choisi.
- Ne pas réintroduire RichEdit, RTF, Word, LibreOffice ou un autre traitement de texte comme moteur de composition.
- Ne pas modifier la Source originale pour conserver les changements du Livre.
- Une correction automatique ne concerne que ce qui est objectivement sûr et reste traçable.
- Les décisions éditoriales particulières appartiennent au Survol.
- Protéger les acquis validés : Canvas par chapitre, frappe fluide, navigation, persistance et synchronisation du Livre.

## Dépendances Python

La dépendance externe active déclarée est Pillow. Tkinter est fourni avec Python et le runtime WebView2 utilisé par TomeLinea est embarqué dans le projet.

Voir `NETTOYAGE_2026-09-15.md` pour le ménage architectural réalisé lors du changement de cap vers l'import du contenu et la composition native TomeLinea.
