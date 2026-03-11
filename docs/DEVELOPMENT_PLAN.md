# PitWall — Plan de Développement

## Phase 1 — MVP Core (Semaines 1-3)

### Objectifs
- Connexion irsdk fonctionnelle
- Serveur FastAPI avec WebSocket
- Dashboard minimal (speed, RPM, gear, fuel)
- Classement en direct

### Livrables
- [ ] Backend: collecteur télémétrie irsdk
- [ ] Backend: serveur WebSocket broadcast
- [ ] Backend: API REST basique (sessions)
- [ ] Frontend: connexion WebSocket
- [ ] Frontend: composants gauges (speed, RPM)
- [ ] Frontend: tableau classement
- [ ] Tests unitaires backend

---

## Phase 2 — Live Race Complet (Semaines 4-6)

### Objectifs
- Carte circuit dynamique
- Radar de proximité
- Indicateurs pneus et carburant complets
- Gestion des drapeaux

### Livrables
- [ ] Track map SVG/Canvas dynamique
- [ ] Radar proximité avec positions relatives
- [ ] Heatmap températures pneus
- [ ] Jauge carburant avec estimation laps restants
- [ ] Indicateurs de drapeaux (yellow, blue, black)
- [ ] Optimisation rendu 30fps

---

## Phase 3 — Stratégie (Semaines 7-9)

### Objectifs
- Calculateur de fenêtre pit
- Simulations undercut/overcut
- Estimation impact safety car

### Livrables
- [ ] Modèle de calcul pit window
- [ ] Simulation undercut/overcut basée sur dégradation pneus
- [ ] Module safety car (estimation delta)
- [ ] UI stratégie avec timeline visuelle
- [ ] Historique stratégies en base

---

## Phase 4 — Performance (Semaines 10-12)

### Objectifs
- Graphiques throttle/brake overlay
- Delta sectoriel
- Comparaison tour à tour
- Analyse de grip

### Livrables
- [ ] Graphiques Recharts temps réel (throttle, brake)
- [ ] Tableau comparatif secteurs
- [ ] Overlay comparaison de tours
- [ ] Heatmap points de freinage sur la carte
- [ ] Détection de perte de grip (écart sectoriel)

---

## Phase 5 — Communication (Semaines 13-15)

### Objectifs
- Radio WebRTC LAN fonctionnelle
- Push-to-talk
- Messages prédéfinis
- Screen sharing

### Livrables
- [ ] Serveur de signaling WebRTC
- [ ] Codec audio avec effet radio
- [ ] Push-to-talk clavier configurable
- [ ] Bibliothèque de messages prédéfinis
- [ ] Screen share WebRTC 1080p 60fps
- [ ] Fallback Discord/TeamSpeak documenté

---

## Phase 6 — Analyse & IA (Semaines 16-18)

### Objectifs
- Rapport post-course automatique
- Module IA d'alertes
- Export PDF

### Livrables
- [ ] Génération rapport PDF (ReportLab)
- [ ] Graphiques embarqués dans le rapport
- [ ] Analyse automatique des incidents
- [ ] Module IA : surchauffe pneus, fuel risk
- [ ] Suggestions d'amélioration basées sur les données
- [ ] Export données CSV/JSON

---

## Phase 7 — Polish & Desktop (Semaines 19-21)

### Objectifs
- Application Tauri pour macOS
- Optimisations performance
- Tests end-to-end
- Documentation utilisateur

### Livrables
- [ ] Build Tauri macOS
- [ ] Optimisation mémoire et CPU
- [ ] Tests E2E (Playwright)
- [ ] Guide utilisateur
- [ ] Guide d'installation réseau

---

## Points Critiques Techniques

### Performance
- **WebSocket throughput** : 30 Hz × ~500 bytes = ~15 KB/s — léger mais le
  parsing JSON côté client doit être optimisé (éviter re-renders inutiles)
- **Canvas vs DOM** : utiliser Canvas/WebGL pour la track map et le radar,
  DOM pour les tableaux et jauges
- **Worker threads** : déporter le parsing télémétrie dans un Web Worker
- **Buffer ring** : côté Python, utiliser un ring buffer pour ne pas surcharger
  la mémoire lors des longues courses (>2h)

### Réseau
- **Découverte LAN** : mDNS/Bonjour pour trouver le serveur automatiquement
- **Reconnexion** : backoff exponentiel sur déconnexion WebSocket
- **Latence WebRTC** : le serveur STUN n'est pas nécessaire en LAN, connexion
  directe peer-to-peer via IP locale

### Fiabilité
- **Crash iRacing** : le collecteur doit gérer la perte de connexion irsdk
  et se reconnecter automatiquement
- **Persistance** : écriture SQLite asynchrone pour ne pas bloquer la boucle
  de télémétrie
- **Watchdog** : heartbeat entre backend et frontend pour détecter les
  déconnexions

### Optimisations Recommandées
1. **MessagePack** au lieu de JSON pour réduire la bande passante de ~40%
2. **Delta compression** : n'envoyer que les valeurs qui changent
3. **Throttling adaptatif** : réduire la fréquence si le client est lent
4. **GPU acceleration** : utiliser OffscreenCanvas pour les rendus lourds
5. **Lazy loading** : charger les onglets Strategy/Performance à la demande
