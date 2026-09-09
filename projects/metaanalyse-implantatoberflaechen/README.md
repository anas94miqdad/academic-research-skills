# Metaanalyse: Keramische und metallische Dentalimplantate nach Oberflächenmodifikationen

Vollständiges Arbeitspaket einer systematischen Übersichtsarbeit mit Metaanalyse
nach PRISMA 2020, erstellt am 09.09.2026.

> **Wichtiger Hinweis.** Recherche, Screening, Datenextraktion, Auswertung und
> Textentwurf wurden KI-gestützt durch einen einzelnen Extraktor erstellt, **nicht**
> durch zwei unabhängige menschliche Reviewer. Jede Zahl ist über PMID und DOI auf die
> Primärquelle rückführbar; eine menschliche Verifikation gegen die Primärquellen hat
> jedoch nicht stattgefunden und ist vor jeder Verwendung erforderlich. Einzelheiten
> in `07_dissertation/Dissertation.md`, Abschnitt 10.1.

## Kernergebnisse

| Analyse | Zielgröße | k | Ergebnis | I² |
|---|---|---|---|---|
| **A1** | Knochen-Implantat-Kontakt, Keramik vs. Titan (präklinisch) | 13 | MD −2,34 Pp (−8,29; +3,61), n. s.<br>restriktiv (k = 10): **−4,61 Pp (−7,24; −1,99)** | 84,7 %<br>0 % |
| **B1** | Knochen-Implantat-Kontakt, modifiziert vs. maschiniert | 24 | **MD +14,64 Pp (+10,25; +19,03)**<br>Tier +15,06 · Mensch +11,66 (p = 0,387) | 86,8 % |
| **B2** | Biomechanische Verankerung, modifiziert vs. maschiniert | 11 | **Hedges' g = 3,30 (2,21; 4,39)** | 77,2 % |
| **C1** | Klinischer Implantatverlust, ZrO₂ vs. Ti | 7 | **RR 1,59 (0,96; 2,66)**, p = 0,067 | 0 % |
| **C2** | Marginaler Knochenverlust, ZrO₂ vs. Ti | 5 | **MD +0,069 mm (+0,019; +0,119)**, p = 0,018 | 0 % |
| **C3** | Überleben keramischer Implantate (3 694 Implantate) | 15 | **90,7 % (83,1; 96,4)** | 94,5 % |

**Kernaussage.** Die Oberflächenmodifikation ist die wirksamste bekannte
Einzelmaßnahme zur Verbesserung der Osseointegration, und ihr Effekt ist im Tiermodell
und beim Menschen gleich groß. Keramische Implantate weisen einen kleinen,
konsistenten Nachteil in der Osseointegration auf, der sich klinisch in einem etwa
1,6-fach erhöhten Verlustrisiko niederschlägt, nicht aber im periimplantären
Knochenniveau. Die Streuung zwischen einzelnen Keramiksystemen (61–100 % Überleben)
übertrifft den Werkstoffeffekt um ein Mehrfaches.

## Umfang

- **5 168** eindeutige Datensätze durchsucht (PubMed/MEDLINE, 09.09.2026)
- **543** Berichte im Detail geprüft, davon **215** als Volltext
- **103** Studien in der qualitativen, **69** in der quantitativen Synthese
- **6** Metaanalysen, **15** Abbildungen in 300 dpi
- **156** verifizierte Literaturangaben mit PMID und DOI

## Verzeichnisstruktur

```
01_protokoll/     Review-Protokoll (PROSPERO-Format), .md und .docx
02_suche/         Suchstrategie (ausführbar), Trefferzahlen, kompletter Suchkorpus
03_screening/     Regelbasiertes Vorscreening, Screening-Sheet (5 168 Zeilen)
04_extraktion/    Extraktionsdatensatz, Evidenztabelle, Risk-of-Bias-Bewertungen,
                  215 abgerufene Volltexte
05_analyse/       Metaanalyse-Bibliothek, Auswertungsskript, Ergebnisse (JSON)
06_abbildungen/   15 Abbildungen (PNG, 300 dpi) + Plot-Bibliothek
07_dissertation/  Dissertation (.md und .docx), Literaturverzeichnis
08_prisma/        PRISMA-2020-Checkliste
Arbeitsmappe_Metaanalyse.xlsx   Alle Arbeitsdokumente in einer Excel-Datei (14 Blätter)
```

## Hauptdokumente

| Dokument | Datei |
|---|---|
| **Dissertation** (Word) | `07_dissertation/Dissertation.docx` |
| Dissertation (Markdown) | `07_dissertation/Dissertation.md` |
| Literaturverzeichnis | `07_dissertation/Literaturverzeichnis.md` / `.docx` |
| Review-Protokoll | `01_protokoll/Review-Protokoll.md` / `.docx` |
| PRISMA-Checkliste | `08_prisma/PRISMA-2020-Checkliste.md` / `.docx` |
| Excel-Arbeitsmappe | `Arbeitsmappe_Metaanalyse.xlsx` |
| PRISMA-Flussdiagramm | `06_abbildungen/abb01_prisma_flow.png` |

## Reproduktion

```bash
pip install numpy scipy matplotlib openpyxl
python3 02_suche/search_strategy.py       # Suche wiederholen
python3 02_suche/fetch_records.py         # Datensätze abrufen
python3 02_suche/fix_ids.py               # DOI/PMCID korrigieren
python3 03_screening/stage1_autoscreen.py # Vorscreening
python3 04_extraktion/datensatz.py        # Extraktionstabellen erzeugen
python3 05_analyse/run_analysen.py        # Metaanalysen + Abbildungen
python3 04_extraktion/risk_of_bias.py     # RoB-Abbildungen
python3 07_dissertation/literaturverzeichnis.py
python3 03_screening/build_workbook.py    # Excel-Arbeitsmappe
```

Die Metaanalyse-Funktionen in `05_analyse/metaanalyse.py` sind eigenständig
implementiert (Random-Effects mit REML und DerSimonian-Laird, Hartung-Knapp-Sidik-
Jonkman-Konfidenzintervalle, Vorhersageintervalle, Subgruppen, Meta-Regression,
Egger, Begg, Trim-and-Fill, Leave-one-out); die Formeln folgen Viechtbauer (2010) und
dem Cochrane Handbook v6.5.

## Offene Punkte vor einer Einreichung

1. Verifikation aller 103 eingeschlossenen Studien gegen die Primärquellen
2. Nachextraktion der 34 mit **[Q]** gekennzeichneten Studien aus dem Volltext und
   Wiederholung der betroffenen Analysen
3. Unabhängige Zweitbewertung des Verzerrungsrisikos
4. Zweitscreening einer Stichprobe mit Berechnung der Übereinstimmung
5. Retrospektive Registrierung bei PROSPERO
6. Ergänzende Suche in Embase, Scopus, Web of Science und CENTRAL
