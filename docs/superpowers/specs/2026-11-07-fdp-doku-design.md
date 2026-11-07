# Design: Doku „Der Fall der FDP“ (Flexibilizar, Video 3)

Stand 07.11.2026. Anthony hat Thema, Kaltstart, Stimme (Gemini) und RunPod vorgegeben. Alles andere hat er mir überlassen („mach so wie du denkst, der Film soll so gut sein“). Meine Entscheidungen sind mit **[Claude]** markiert.

## 1. Absicht
Ein Dokumentarfilm über den Absturz der FDP: von der Regierungspartei 2021 zum Aus im Bundestag am 23.02.2025, eingeordnet in die Geschichte seit dem ersten Rauswurf 2013. Machart nach der Stilstudie `docs/stilstudie-simplicissimus.md`: Kaltstart mit Szene und Frage, Chronologie im Präsens, Ermittlungswand, Archiv, 3D-Nachstellung, Schwarz mit einer Signalfarbe.

**Warum:** Anthony will den Kanal auf diese Machart ausrichten. Die Zuschauerkritik an der AfD-Doku (Memory `feedback-doku-roter-faden`) ist der wichtigste Maßstab: Der Film darf nicht zwischen Themen springen und keine Skandale aneinanderreihen.

## 2. Leitfrage und roter Faden
**Leitfrage:** Wie konnte eine Regierungspartei in drei Jahren so tief fallen, dass sie aus dem Bundestag fliegt?

Regeln:
- Jedes Kapitel beantwortet ein Stück der Leitfrage und endet mit einem „Zwischenstand“ in einem Satz, danach eine offene Frage zum nächsten Kapitel.
- Rückgrat ist die Chronologie. Rückblenden gibt es nur einmal, direkt nach dem Kaltstart.
- Ein Ereignis kommt nur vor, wenn es die Leitfrage voranbringt.
- Eine wiederkehrende **Ermittlungswand** sammelt die Ursachen. Pro Kapitel kommt ein Zettel dazu. Im Schluss liegen alle Ursachen nebeneinander, mit Selbstsicht der FDP und Gegensicht.

## 3. Aufbau (Ziel 25 min, **[Claude]**; erlaubt 22–28 min)
| # | Kapitel | Zeit | Frage, die es beantwortet |
|---|---|---|---|
| 0 | Kaltstart: Wahlabend 23.02.2025 | 2:00 | Ausgangslage und Leitfrage |
| – | Kanal-Ident (Falz-F, ca. 4 s) | 0:04 | |
| 1 | 2013: Der erste Absturz | 2:30 | Was hat die FDP damals gelernt? |
| 2 | 2013–2017: Neuaufbau als Lindner-Partei | 3:00 | Worauf beruhte das Comeback? |
| 3 | 2017: „Lieber nicht regieren …“ | 2:00 | Woher stammt der Ruf als unsicherer Partner? |
| 4 | 2021: Die Ampel und das Finanzministerium | 2:30 | Was hatten Wähler erwartet, was hat die FDP verhandelt? |
| 5 | 2022–2024: Regieren gegen die eigene Basis | 4:30 | Wo hat die Ampel die FDP Wähler gekostet? (Landtagswahlen, Umfragen, Mitgliederbefragung, Schuldenbremse, BVerfG-Urteil 11/2023) |
| 6 | Herbst 2024: Der Bruch | 4:00 | Wer hat das Ende geplant, und wie wurde es öffentlich? (Wirtschaftspapier, 06.11.2024, „D-Day“-Papier, Rücktritte) |
| 7 | Wahlkampf 2025 | 2:30 | Warum reichte es nicht? (Wählerwanderung, Gründe laut Umfragen, Abstimmung 29.01.2025) |
| 8 | Danach bis heute | 1:30 | Was ist aus der Partei geworden? |
| 9 | Auflösung an der Wand | 1:00 | Die Ursachen nebeneinander, beide Seiten |
| – | Abspann mit Quellen | 0:30 | |

Die Zahlen und Daten in der Tabelle sind aus dem Gedächtnis und werden in der Recherche geprüft. Ändert sich ein Fakt, passt sich die Kapitelaufteilung an, die Leitfrage bleibt.

## 4. Neutralität (bindend, wie AfD-Doku)
Es gelten die Regeln aus `afd-doku/docs/konzept.md`: jede Tatsache mit Quelle, Bewertungen zugeschrieben, beide Seiten, keine Kampfbegriffe. Dazu kommen:
- Die FDP-Sicht kommt ausdrücklich vor (Schuldenbremse als Versprechen, Ampel als Blockade), ebenso die Kritik (Unzuverlässigkeit, „D-Day“-Papier). Kein Kapitel ist Abrechnung.
- Lindner ist Hauptfigur, nicht Schuldiger. Ursachen werden nicht einer Person allein zugeschrieben, wenn Quellen das nicht tragen.
- Ursachen, die Forschung oder Umfragen nennen, sind belegt (z. B. Forschungsgruppe Wahlen, Infratest). Eigene Deutungen des Erzählers gibt es nicht.
- **Offenlegung [Claude]:** Anthonys Arbeit für einen AfD-Kreisverband steht kurz im Abspann und in der Beschreibung, weil die AfD im Film als Wettbewerber vorkommt (Abstimmung 29.01.2025).

## 4a. Entscheidungen Anthony (07.11.2026)
- **Keine Monetarisierung.** Bundestag-Ausschnitte sind damit nutzbar (Bedingung „keine Werbung“ erfüllt). Es gibt keinen Werbeblock.
- **Keine Stellungnahmen** vor der Veröffentlichung („wir sind zu unbekannt“). Ausgleich **[Claude]:** Kapitel 6 und alle Aussagen über Absichten einzelner Personen stützen sich nur auf veröffentlichte Dokumente (das von der FDP selbst veröffentlichte Papier, Rücktrittserklärungen, Reden) und auf benannte Medienberichte. Es gibt keine eigenen Verdachtsäußerungen.

## 5. Bildsprache
- **Farben [Claude]:** Es gilt die Markenregel aus `README.md`: kein Rot, weil Schwarz, Rot und Gelb zusammen die Deutschlandfarben ergeben, und kein Blau. Basis sind Fast-Schwarz (`TINTE`) und Elfenbein. **Signalfarbe für Fäden, Neonumrisse und Hervorhebungen ist Bernstein `#E4922A`** (aus der AfD-Doku). Das Marker-Gelb `#F7D63E` steht nur hinter Text als Leuchtstift und im Kanal-Ident. Es wird nie großflächig eingesetzt, weil es zu nah am FDP-Gelb liegt. FDP-Magenta und -Blau kommen nur dort vor, wo Originalmaterial sie zeigt.
- **Module (neu zu bauen):** Ermittlungswand mit Fäden, Zetteln und Fotos; Zeitungsausschnitt mit roter Markierung; Röhren-TV als Rahmen für Archivclips; nachgebaute Social-Media-Posts; dunkle 3D-Deutschlandkarte mit rotem Neonumriss; Wahlbalken und Umfragekurve im selben Look; Namenszettel als Bauchbinde.
- **3D-Nachstellungen (Blender, RunPod):** Nur dokumentierte Situationen, zum Beispiel ein leerer Kabinettssaal, das Kanzleramt am Abend, ein Flur mit Akten oder eine Wahlparty-Bühne. Menschen erscheinen als **gesichtslose, stilisierte Figuren**, nie als Abbild realer Politiker. Es gibt keine erfundenen Dialoge. Einblendung „Nachstellung“ oder „Abstrakte Darstellung“.
- **Erlaubte Quellen [Claude, vorsichtig]:** Bundestag-Mediathek, freie Fotos mit Lizenz (Wikimedia Commons), Dokumente und Schlagzeilen als Zitat (§ 51 UrhG, kurz und mit Quelle), nachgebaute Social-Media-Posts mit belegtem Wortlaut. **Keine TV-Mitschnitte** (ARD/ZDF/Talkshows) und keine Parteikanäle als Videoquelle, solange die Rechte nicht geklärt sind. Den Kaltstart tragen deshalb Hochrechnungsgrafik, Nachstellung der Wahlparty-Bühne (leer, Licht), Zitate als Text mit Stimme des Erzählers („Lindner sagt …“) und Bundestag-Reden. Statements vom 06.11.2024 kommen als Zitat-Tafeln.
- **Echtes Material:** Bundestag-Mediathek (Bedingungen wie bei der AfD-Doku: Quelle nennen, keine Grafik auf dem Clip, nicht sinnentstellend, Original-Einblendung mit „live“-Uhr wegschneiden oder im TV-Rahmen beschneiden), freie Fotos (Wikimedia Commons mit Lizenzangabe), Dokumente als Zitat.
- **Fehler der AfD-Doku vermeiden:** Grafiken dürfen keine Quellenzeile verdecken. Das wird in der Prüfung automatisch kontrolliert.

## 6. Ton
- **Erzähler: Gemini `gemini-3.8-flash-tts`** (Anthonys Vorgabe). Schlüssel: `~/.config/ddr-video/gemini.env`, nicht der Schlüssel des Discord-Bots. Tarif und Limit prüfe ich mit der ersten Stimmprobe. Bei Tageslimit werden die Takte über Nacht verteilt. Vor der Produktion bekommt Anthony 3 deutsche Stimmproben mit demselben Kaltstart-Absatz und wählt eine aus. **[Claude]:** gleicher Stilprompt für alle Takte (ernst, nah, ruhig, leicht gespannt), Sprechtempo Ziel 135 Wörter/min.
- QA wie bisher mit Whisper (Wortgleichheit, Zahlen, Namen), Nachgenerieren einzelner Takte.
- **Musik [Claude]:** weiter Eleven Music als Schleifen (spannungsvolle Flächen, Pulse), Sounddesign für Papier, Klebeband und Swooshes. Master −14 LUFS.

## 7. Technik
- **Neues Repo `supertony0403/fdp-doku`, privat [Claude]** (wie afd-doku, wegen echter Personen und laufender Prüfung). Code-Basis: Kopie der Pipeline aus `afd-doku` (`ton/`, `schnitt/`). Dort wird `ton/elevenlabs.py` für die Stimme durch ein Gemini-Modul ersetzt, und die neuen Grafikmodule werden ergänzt. Daten unter `/mnt/steam-library/fdp-doku/`.
- **RunPod** für Blender-Nachstellungen und den Gesamtrender. **[Claude]:** Budget bis 5 $, danach frage ich nach. Pods ohne SSH-Port nach 5 min ersetzen (bekannte Falle).
- Läuft gedrosselt neben Spielen (systemd-Dienste, AllowedCPUs 10–11), keine lokale GPU.
- Coding-Agents und Pflicht-Review laut CLAUDE.md.

## 8. Ergebnisse
`fdp_doku_v1.mp4` (1080p24), Teilen-Fassung, Thumbnail (Rot/Schwarz/Weiß, großes Motiv, 1–2 Wörter, kein Gesicht eines Politikers in Nahaufnahme **[Claude]**), Beschreibung mit Kapiteln, Quellen und Hashtags. **Kein Upload ohne Anthonys ausdrückliches Wort.**

## 9. Erfolg
- Ein Zuschauer kann danach die Leitfrage mit 3 bis 5 benannten, belegten Ursachen beantworten und kennt die Sicht der FDP dazu.
- Keine Themensprünge: Jede Szene lässt sich einem Kapitel und dessen Frage zuordnen (Prüfliste im Drehbuch).
- Faktencheck ohne offene `pruefen`-Felder vor dem Rendern. Bei der AfD-Doku blieben 10 offen.

## 10. Nicht-Ziele und Anti-Ziele
- Nicht: Lindner-Porträt, FDP-Programmgeschichte vollständig, Ampel-Doku über alle drei Parteien.
- Anti-Ziel: Der Film wirkt wie Häme oder wie FDP-Werbung. Das wäre ein Fehlschlag, selbst wenn er technisch gut ist.
- Anti-Ziel: Ein Element wirkt wie Simplicissimus selbst (Logo, „S“, Intro, deren Figuren oder Grafiken).
- Anti-Ziel: Realistische KI-Bilder echter Politiker oder erfundene Szenen ohne Kennzeichnung.

## 11. Offen für den Bauenden
Kapitellängen im Rahmen, Wahl der Musik-Cues, Schnittrhythmus (Einstieg dicht, 1–3 s; Erzählteile ruhiger), genaue Gestaltung der Grafikmodule im beschriebenen Look, Auswahl der Ausschnitte nach Rechtelage.

## 12. Checkpoints mit Anthony
1. Stimmprobe (3 Gemini-Stimmen) → Auswahl.
2. Drehbuch und Faktencheck → kurzer Blick (optional).
3. Vorschau Kaltstart mit Ton.
4. Fertiger Film → Abnahme, dann erst Thumbnail und Upload auf Anweisung.
