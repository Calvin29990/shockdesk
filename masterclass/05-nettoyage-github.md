# Nettoyage GitHub — 4 dépôts

Session shockdesk : on corrige **ce** dépôt. Les autres = checklist pour
toi après le zip, tu es owner.

---

## 1. `Calvin29990/shockdesk` — prioritaire

### Déjà faux pour un élite (corrigé dans cette session)

Le README et le guide vendaient encore les chiffres **synthétiques** comme
démo :

- +395 919 $ / −4 054 $
- miss = or
- signe 5/6, pic 1 jour

Le journal du 30/08 a mesuré sur **yfinance** :

- +337 887 $ / −279 633 $
- or = +53 k$
- misses = HYG, TLT
- signe 4/6, pic 7 j, Brent ×3,68

Un recruteur qui clone et lance sous Yahoo n'obtient pas 395 k$. C'est
disqualifiant. **Corrigé** dans `README.md` + bandeau de provenance dans
`docs/guide-utilisation.md`.

### Encore à faire (pas bloquant pour valider le programme)

| Item | Pourquoi | Quand |
|---|---|---|
| `shockdesk-v0.1.zip` à la racine | artefact mort, 6,6 ko | supprimer après validation |
| `deploy/github-actions-ci.yml` hors `.github/workflows/` | le README l'explique (token sans droit `workflows`) | le jour où tu as le droit, copier |
| README « 37 tests » dans la section Deploy vs « 44 tests » plus haut | reliquat | aligner à 44 partout |
| `docs/journal-de-bord-recherche.md` (76 ko) | précieux mais illisible en public | garder ; le pack masterclass ne le duplique pas |
| Description GitHub vide | `gh repo edit --description "…"` | 30/09 avec le pitch |

### Ce qu'on ne fait pas

- Recopier le Drive dans le repo (Z-Library = copyright).
- Fusionner exotic-desk dans shockdesk.
- Inventer des onglets ALM/Risk pour coller à l'ébauche.

---

## 2. `Calvin29990/calvin-exotic-desk`

État : propre, démo Netlify, cours dans `cours/`. Rôle septembre = lab
des jours 7, 8, 9, 12. **Ne pas y toucher pendant le sprint** sauf bug
bloquant.

---

## 3. `Calvin29990/ShockLab-Fade-or-Cascade-`

README clair, 1 PDF. C'est l'ancêtre public du scénario pétrole. Le
chiffre « Brent +5 % / +0,14 M$ » est le **r1**, pas le réalisé. Ajouter
une ligne (après le 30/09) :

> Réalisé yfinance juil. 2026 : Brent +18,4 % au pic, book ShockDesk
> +337 887 $ en sortant à J+7. Le +5 % était la prévision, pas le marché.

Ne pas réécrire l'historique du PDF.

---

## 4. `Calvin29990/calvinx-market-terminal`

**Hygiène :** `.env` (97 o) est **commité**, `.gitignore` vide. Même si
la clé est morte, un recruteur lit ça comme un junior qui pousse des
secrets.

Action (hors cette branche, à faire toi-même) :

```bash
# sur le dépôt terminal, pas ici
echo ".env" >> .gitignore
echo "node_modules/" >> .gitignore
git rm --cached .env
# si node_modules a été poussé : git rm -r --cached node_modules
```

Puis rotation de la clé si c'en était une.

---

## 5. Ordre après validation du programme

1. Tu dis « programme validé » (éventuellement avec 2–3 amendements).
2. Je sors le zip `masterclass-front-septembre-2026.zip` **sans livres**.
3. Tu crées le nouveau dépôt, tu y mets le zip.
4. ShockDesk reste le lab ; le nouveau dépôt est le cerveau + les
   livrables Python du mois.
5. Description + topics GitHub le 30/09, pas maintenant.
