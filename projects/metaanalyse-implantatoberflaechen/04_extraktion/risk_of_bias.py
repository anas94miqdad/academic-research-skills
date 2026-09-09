#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bewertung des Verzerrungsrisikos.

Tierexperimentelle Studien: SYRCLE's Risk of Bias Tool (Hooijmans et al. 2014, BMC Med Res Methodol 14:43)
Randomisierte klinische Studien: RoB 2 (Sterne et al. 2019, BMJ 366:l4898)
Nichtrandomisierte klinische Studien: ROBINS-I (Sterne et al. 2016, BMJ 355:i4919)

Die Bewertung stuetzt sich ausschliesslich auf die im Abstract bzw. im frei
zugaenglichen Volltext berichteten Angaben. Wird eine Domaene nicht berichtet,
lautet das Urteil 'unklar' - das ist bei tierexperimentellen Publikationen der
Regelfall und selbst ein Ergebnis dieser Arbeit.
"""

SYRCLE_DOMAENEN = [
    "1 Sequenzgenerierung", "2 Ausgangsmerkmale", "3 Verdeckte Zuteilung",
    "4 Randomisierte Unterbringung", "5 Verblindung Versuchsdurchführung",
    "6 Randomisierte Ergebniserhebung", "7 Verblindung Ergebniserhebung",
    "8 Unvollständige Ergebnisdaten", "9 Selektives Berichten", "10 Sonstige Verzerrung",
]
ROB2_DOMAENEN = [
    "D1 Randomisierungsprozess", "D2 Abweichungen von der Intervention",
    "D3 Fehlende Ergebnisdaten", "D4 Messung der Zielgröße",
    "D5 Selektion des berichteten Ergebnisses", "Gesamturteil",
]
ROBINS_DOMAENEN = [
    "D1 Confounding", "D2 Selektion der Teilnehmer", "D3 Klassifikation der Intervention",
    "D4 Abweichungen von der Intervention", "D5 Fehlende Daten",
    "D6 Messung der Zielgröße", "D7 Selektion des Ergebnisses", "Gesamturteil",
]

n, u, h = "niedrig", "unklar", "hoch"

# ---- Tierexperimentelle Studien (SYRCLE) --------------------------------
# Reihenfolge der Domaenen wie in SYRCLE_DOMAENEN
SYRCLE = {
 "Kohal 2004":      [u, n, u, u, u, u, u, n, n, n],
 "Weng 2003":       [u, n, u, u, u, u, u, n, n, n],
 "Veis 2004":       [u, n, u, u, u, u, u, n, n, u],
 "Depprich 2008":   [u, n, u, u, u, u, u, n, n, n],
 "Rong 2009":       [u, n, u, u, u, u, u, n, n, n],
 "Kim 2009":        [u, n, u, u, u, u, u, n, n, n],
 "Ribeiro 2009":    [n, n, u, u, u, u, u, n, n, n],
 "Lee 2009":        [u, n, u, u, u, u, u, n, n, n],
 "Xavier 2010":     [u, n, u, u, u, u, u, n, n, n],
 "Xiao 2011":       [u, n, u, u, u, u, u, n, n, n],
 "Gahlert 2012":    [u, n, u, u, u, u, u, u, u, u],
 "Ballo 2013":      [n, n, u, u, u, u, u, n, n, n],
 "Stübinger 2013": [u, n, u, u, u, u, u, n, n, u],
 "Thoma 2015":      [n, n, u, u, u, u, u, n, n, h],
 "Montero 2015":    [u, n, u, u, u, u, u, h, n, h],
 "Ou 2016":         [u, n, u, u, u, u, u, n, n, n],
 "Schmitt 2016":    [n, n, u, u, u, u, u, u, n, u],
 "Siddiqi 2016":    [u, n, u, u, u, u, u, h, n, u],
 "Fu 2017":         [u, n, u, u, u, u, u, n, n, n],
 "Cheng 2017":      [u, n, u, u, u, u, u, n, n, n],
 "Queiroz 2017":    [n, n, u, u, u, u, u, n, n, n],
 "Hou 2019":        [u, n, u, u, u, u, u, n, n, n],
 "Gehrke 2019":     [n, n, u, u, u, u, u, n, n, n],
 "Gehrke 2019b":    [n, n, u, u, u, u, u, n, n, n],
 "Thomé 2021":      [u, n, u, u, u, u, u, n, n, u],
 "Chacun 2021":     [u, n, u, u, u, u, u, n, n, n],
 "Kim 2021":        [u, u, u, u, u, u, u, u, n, h],
 "Duncan 2022":     [u, n, u, u, u, u, u, n, n, u],
 "Li 2022":         [u, n, u, u, u, u, u, n, n, n],
 "Park 2025":       [u, n, u, u, u, u, u, n, n, n],
 "Niu 2025":        [u, n, u, u, u, u, u, n, n, u],
}
SYRCLE_BEGRUENDUNG = {
 "Thoma 2015": "Domaene 10: hohe Frakturrate der Keramikimplantate waehrend der Studie",
 "Montero 2015": "Domaene 8: 43.8 % Verlustrate in der Keramikgruppe; Domaene 10: kein Mundhygieneregime",
 "Siddiqi 2016": "Domaene 8: Gesamtueberleben 87.5 %, ungleiche Verteilung der Verluste",
 "Kim 2021": "sehr kleine Stichprobe (n = 4 je Gruppe), Tiere auf Untergruppen aufgeteilt",
 "Gahlert 2012": "Zuordnung der berichteten Spannweiten zu Zeitpunkten nicht moeglich",
 "Schmitt 2016": "ungleiche Gruppengroessen (M/P n = 20, BP n = 40); Ergebnis richtungsinkonsistent",
 "Niu 2025": "Domaene 10: auffaellig kleine Streuungen bei n = 14",
 "Veis 2004": "Domaene 10: nur zwei Versuchstiere",
 "Duncan 2022": "Domaene 10: Poolung von Kiefer- und Femurlokalisation",
 "Thomé 2021": "Domaene 10: Non-Inferioritaets-Design, herstellerfinanziert",
}

# ---- Randomisierte klinische Studien (RoB 2) -----------------------------
ROB2 = {
 "Osman 2014":       [n, u, "einige Bedenken", n, u, "einige Bedenken"],
 "de Beus 2024":     [n, n, n, n, n, n],
 "de Beus 2026":     [n, n, "einige Bedenken", n, n, "einige Bedenken"],
 "Zuercher 2024":    [n, n, n, n, n, n],
 "Sterzenbach 2025": [n, n, n, n, n, n],
 "Balmer 2026":      [n, n, "einige Bedenken", n, n, "einige Bedenken"],
 "Kniha 2026":       [n, n, n, n, n, n],
 "Makary 2023":      [n, n, n, u, u, "einige Bedenken"],
}
ROB2_BEGRUENDUNG = {
 "Osman 2014": "Verdeckte Zuteilung nicht beschrieben; Ergebnisdarstellung nur als Prozentwerte",
 "de Beus 2026": "D3: 3 von 50 Teilnehmenden am 3-Jahres-Termin nicht verfuegbar",
 "Balmer 2026": "D3: 7 Ausschluesse und 5 Verluste in der Nachbeobachtung",
 "Makary 2023": "D4/D5: ungleiche Gruppengroessen (MAC n = 6 vs. SLA n = 13); Streuungsmasse sehr klein",
}

# ---- Nichtrandomisierte klinische Studien (ROBINS-I) ---------------------
ROBINS = {
 "Hassouna 2022": [u, n, n, n, n, u, u, u],
 "Sailo 2025":    [h, u, n, n, u, u, u, h],
 "Herber 2025":   [h, n, n, n, u, n, n, h],
 "Kaur 2026":     [h, n, n, n, n, n, u, h],
 "Duncan 2022":   [h, u, n, n, h, n, u, h],
}
ROBINS_BEGRUENDUNG = {
 "Sailo 2025": "keine Adjustierung fuer Confounder; Zuteilung zum Werkstoff nicht beschrieben",
 "Herber 2025": "stark ungleiche Gruppengroessen (22 vs. 11), keine Adjustierung",
 "Kaur 2026": "retrospektiv; Einheilprotokoll zwischen den Gruppen signifikant unterschiedlich",
 "Duncan 2022": "hohe Verlustrate zur Nachbeobachtung (33 % erreicht, 21 % verstorben)",
 "Hassouna 2022": "Streuungsangabe der Keramikgruppe implausibel",
}

if __name__ == "__main__":
    import os, sys, csv, json
    HERE = os.path.dirname(os.path.abspath(__file__))
    ROOT = os.path.dirname(HERE)
    sys.path.insert(0, os.path.join(ROOT, "06_abbildungen"))
    from plots import rob_traffic
    ABB = os.path.join(ROOT, "06_abbildungen")
    rob_traffic(list(SYRCLE), SYRCLE_DOMAENEN, list(SYRCLE.values()),
                "Abbildung 13: Verzerrungsrisiko der tierexperimentellen Studien (SYRCLE)",
                os.path.join(ABB, "abb13_rob_syrcle.png"),
                legend_note="+ niedriges Risiko   ? unklares Risiko   – hohes Risiko")
    rob_traffic(list(ROB2), ROB2_DOMAENEN, list(ROB2.values()),
                "Abbildung 14: Verzerrungsrisiko der randomisierten klinischen Studien (RoB 2)",
                os.path.join(ABB, "abb14_rob2.png"),
                legend_note="+ niedriges Risiko   ? einige Bedenken   – hohes Risiko")
    rob_traffic(list(ROBINS), ROBINS_DOMAENEN, list(ROBINS.values()),
                "Abbildung 15: Verzerrungsrisiko der nichtrandomisierten klinischen Studien (ROBINS-I)",
                os.path.join(ABB, "abb15_robins_i.png"),
                legend_note="+ niedriges Risiko   ? maessiges Risiko   – ernsthaftes Risiko")
    # CSV-Export
    for name, dom, tab, beg in [("syrcle", SYRCLE_DOMAENEN, SYRCLE, SYRCLE_BEGRUENDUNG),
                                ("rob2", ROB2_DOMAENEN, ROB2, ROB2_BEGRUENDUNG),
                                ("robins_i", ROBINS_DOMAENEN, ROBINS, ROBINS_BEGRUENDUNG)]:
        with open(os.path.join(HERE, f"rob_{name}.csv"), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Studie"] + dom + ["Begruendung"])
            for s, v in tab.items(): w.writerow([s] + v + [beg.get(s, "")])
    # Zusammenfassung
    from collections import Counter
    for name, tab in [("SYRCLE", SYRCLE), ("RoB 2", ROB2), ("ROBINS-I", ROBINS)]:
        c = Counter(x for v in tab.values() for x in v)
        tot = sum(c.values())
        print(f"{name}: {len(tab)} Studien | " +
              " | ".join(f"{k} {v} ({v/tot*100:.0f} %)" for k, v in c.most_common()))
