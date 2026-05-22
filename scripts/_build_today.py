#!/usr/bin/env python3
"""Build today's per-category JSON files + summary.json from the analysis
written manually in this file. Designed for the 2026-05-21 run."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DATE = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
RAW = Path("/tmp/collected_raw.json")
OUT_DIR = Path(__file__).resolve().parent.parent / "frontend" / "static" / "data" / DATE
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Analysis records keyed by article id.
# Each: importance (1-100), summary (el, en), tags (el, en list), sentiment
ANALYSIS = {
    # ===== POLITICS =====
    "558daf615eec": {
        "importance": 72,
        "summary": {
            "el": "Ο Γκράχαμ Αλισον, εμπνευστής της «Παγίδας του Θουκυδίδη», μιλά στην «Κ» για το αν ΗΠΑ και Κίνα μπορούν να αποφύγουν τη σύγκρουση. Η συνέντευξη συνοδεύει την κυκλοφορία του βιβλίου του με την Καθημερινή της Κυριακής, με αφορμή και την πρόσφατη σύνοδο Σι-Τραμπ στο Πεκίνο.",
            "en": "Graham Allison, originator of the 'Thucydides Trap' concept, speaks with Kathimerini about whether the US and China can avoid conflict. The interview accompanies the Greek edition of his book being distributed with the Sunday paper, in the wake of the recent Xi-Trump summit in Beijing."
        },
        "tags": {
            "el": ["Αλισον", "Παγίδα Θουκυδίδη", "ΗΠΑ-Κίνα", "γεωπολιτική", "Σι Τζινπίνγκ"],
            "en": ["Allison", "Thucydides Trap", "US-China", "geopolitics", "Xi Jinping"]
        },
        "sentiment": "neutral",
    },
    "f0d3c07b7eb6": {
        "importance": 80,
        "summary": {
            "el": "Ρεπορτάζ για το νέο κόμμα της Μαρίας Καρυστιανού και τους «παλιούς αριστερούς» που εργάζονται για αυτό, καθώς και τις κατηγορίες περί φιλορωσικού προσανατολισμού. Τα υπόλοιπα κόμματα παρακολουθούν με αμηχανία την εκκίνηση που στοχεύει να ταρακουνήσει το πολιτικό σύστημα.",
            "en": "A report on Maria Karystianou's new party, the 'old leftists' working for it, and accusations of a pro-Russian leaning. Other parties watch warily as her launch threatens to shake up the political system."
        },
        "tags": {
            "el": ["Καρυστιανού", "νέο κόμμα", "Ρωσία", "πολιτική αναδιάταξη", "Τέμπη"],
            "en": ["Karystianou", "new party", "Russia", "political realignment", "Tempi"]
        },
        "sentiment": "neutral",
    },
    "5af4979d24ca": {
        "importance": 70,
        "summary": {
            "el": "Ο υπουργός Υγείας Άδωνις Γεωργιάδης ζητά την απομάκρυνση από το ΕΣΥ αναισθησιολόγου του ογκολογικού «Άγιοι Ανάργυροι», ο οποίος καταγράφηκε σε βίντεο να ζητά φακελάκι 100-150 ευρώ από ασθενή. Ο υπουργός ζήτησε δημόσια συγγνώμη και διέταξε άμεσες πειθαρχικές και νόμιμες ενέργειες.",
            "en": "Health Minister Adonis Georgiadis is demanding the removal from the public health service (ESY) of an anesthesiologist at the Agioi Anargyroi cancer hospital, after a video showed him asking a patient for a €100-150 bribe. The minister apologized publicly and ordered immediate disciplinary and legal action."
        },
        "tags": {
            "el": ["Γεωργιάδης", "φακελάκι", "ΕΣΥ", "Άγιοι Ανάργυροι", "διαφθορά"],
            "en": ["Georgiadis", "bribery", "public health", "Agioi Anargyroi", "corruption"]
        },
        "sentiment": "negative",
    },
    "45b8ca7efaf8": {
        "importance": 78,
        "summary": {
            "el": "Στην Ολομέλεια της Βουλής συζητείται η πρόταση του ΠΑΣΟΚ και η κοινή πρόταση ΣΥΡΙΖΑ-Νέας Αριστεράς για σύσταση προανακριτικής επιτροπής σχετικά με τους πρώην υπουργούς Λιβανό και Αραμπατζή για την υπόθεση του ΟΠΕΚΕΠΕ. Η συζήτηση γίνεται με ζωντανή κάλυψη.",
            "en": "Parliament is debating opposition proposals from PASOK and SYRIZA/Nea Aristera for a preliminary investigation committee against former ministers Spilios Livanos and Foteini Arampatzi over the OPEKEPE farm-subsidy scandal. The session is being covered live."
        },
        "tags": {
            "el": ["ΟΠΕΚΕΠΕ", "προανακριτική", "Βουλή", "Λιβανός", "Αραμπατζή"],
            "en": ["OPEKEPE", "preliminary inquiry", "Parliament", "Livanos", "Arampatzi"]
        },
        "sentiment": "negative",
    },
    "f2250965cefe": {
        "importance": 88,
        "summary": {
            "el": "Σε συνέντευξή του στο podcast «The Rachman Review» των Financial Times, ο Κυριάκος Μητσοτάκης απορρίπτει κατηγορηματικά τυχόν τέλη διέλευσης στο Στενό του Ορμούζ ως «εκβιασμό» που η Ευρώπη δεν μπορεί να αποδεχθεί. Υπερασπίστηκε επίσης τη στρατηγική σχέση Ελλάδας-Ισραήλ, ασκώντας παράλληλα κριτική για Γάζα και Λίβανο.",
            "en": "In an FT 'Rachman Review' podcast interview, PM Kyriakos Mitsotakis flatly rejects any toll on shipping through the Strait of Hormuz as 'extortion' Europe cannot accept. He defended the Greece-Israel strategic relationship while restating public criticism of operations in Gaza and Lebanon."
        },
        "tags": {
            "el": ["Μητσοτάκης", "Ορμούζ", "Financial Times", "Ισραήλ", "Μέση Ανατολή"],
            "en": ["Mitsotakis", "Hormuz", "Financial Times", "Israel", "Middle East"]
        },
        "sentiment": "neutral",
    },
    "9a2ac094edda": {
        "importance": 75,
        "summary": {
            "el": "Στον ΣΥΡΙΖΑ επικρατεί αναμονή ενόψει της 26ης Μαΐου, όταν ο Αλέξης Τσίπρας θα ανακοινώσει το νέο του κόμμα. Στελέχη συζητούν αν θα ενσωματωθεί τμήμα της Κουμουνδούρου και τι θα κάνει ο Παύλος Πολάκης μετά τη διαγραφή του.",
            "en": "SYRIZA is in wait-and-see mode ahead of May 26, when Alexis Tsipras will unveil his new party. Cadres are weighing whether part of Koumoundourou will be absorbed and what expelled MP Pavlos Polakis will do next."
        },
        "tags": {
            "el": ["ΣΥΡΙΖΑ", "Τσίπρας", "νέο κόμμα", "Φάμελλος", "Πολάκης"],
            "en": ["SYRIZA", "Tsipras", "new party", "Famellos", "Polakis"]
        },
        "sentiment": "neutral",
    },
    "608a94d3ad4b": {
        "importance": 65,
        "summary": {
            "el": "Η στήλη Θεωρείο σχολιάζει τα επικείμενα ονόματα των νέων κομμάτων Τσίπρα («Πυξίδα») και Καρυστιανού («Ελπίδα»), αλλά και τις γέφυρες κυβέρνησης-Βενιζέλου μέσω του συνεδρίου του Κύκλου Ιδεών. Σύντομες πολιτικές παρασκηνιακές πληροφορίες.",
            "en": "The Theoreio column comments on the likely names of the new parties — Tsipras's 'Pyxida' (Compass) and Karystianou's 'Elpida' (Hope) — and on government-Venizelos bridges via the Circle of Ideas conference. Brief inside-baseball political color."
        },
        "tags": {
            "el": ["Πυξίδα", "Ελπίδα", "Τσίπρας", "Καρυστιανού", "Βενιζέλος"],
            "en": ["Pyxida", "Elpida", "Tsipras", "Karystianou", "Venizelos"]
        },
        "sentiment": "neutral",
    },
    "15d8558121fa": {
        "importance": 78,
        "summary": {
            "el": "Η στήλη «Εντός και Εκτός» αναφέρει ότι η Αθήνα κράτησε σταθερή στάση στο τουρκικό νομοσχέδιο για τη «Γαλάζια Πατρίδα» και προχώρησε σε αυστηρό διάβημα προς το Ισραήλ για τη συμπεριφορά του υπουργού Ασφάλειας Μπεν Γκβιρ στους Έλληνες ακτιβιστές του Sumud Flotilla. Αναμένονται πιθανές υψηλόβαθμες αμερικανικές επισκέψεις στη Σούδα.",
            "en": "The 'Entos kai Ektos' column reports that Athens maintained its firm line on Turkey's 'Blue Homeland' bill and lodged a strong protest to Israel over Security Minister Ben-Gvir's treatment of Greek activists in the Sumud Flotilla. Possible high-level US visits to Souda Bay are also expected."
        },
        "tags": {
            "el": ["Γαλάζια Πατρίδα", "Σούδα", "Μπεν Γκβιρ", "Global Sumud Flotilla", "ΥΠΕΞ"],
            "en": ["Blue Homeland", "Souda Bay", "Ben-Gvir", "Global Sumud Flotilla", "MFA"]
        },
        "sentiment": "neutral",
    },
    "5262593c8739": {
        "importance": 82,
        "summary": {
            "el": "Σκληρή αντιπαράθεση ΝΔ-ΠΑΣΟΚ για τις υποκλοπές, μετά τη δημοσιοποίηση διαλόγου Ανδρουλάκη-Δεμίρη (ΕΥΠ) στην απόρρητη συνεδρίαση της Επιτροπής Θεσμών. Σήμερα η Ολομέλεια αποφασίζει για το αίτημα του ΠΑΣΟΚ για εξεταστική επιτροπή.",
            "en": "Sharp ND-PASOK clash over the wiretaps affair after the leak of dialogue between Androulakis and EYP chief Demiris from the closed Institutions committee session. The Plenary today decides on PASOK's request for a parliamentary inquiry committee."
        },
        "tags": {
            "el": ["υποκλοπές", "ΕΥΠ", "Ανδρουλάκης", "Δεμίρης", "εξεταστική"],
            "en": ["wiretaps", "EYP", "Androulakis", "Demiris", "inquiry committee"]
        },
        "sentiment": "negative",
    },
    "c2765b7ed2ad": {
        "importance": 80,
        "summary": {
            "el": "Πώς βλέπει το Μαξίμου τη διαμόρφωση του πολιτικού σκηνικού με τα δύο νέα κόμματα Τσίπρα και Καρυστιανού. Κυβερνητικά στελέχη εκτιμούν ότι η ΝΔ δεν θα έχει απώλειες και επαναφέρουν εκλογές μετά τη συνταγματική θητεία.",
            "en": "How Maximos Mansion is approaching the emerging political landscape with the two new Tsipras and Karystianou parties. Government insiders argue ND will not lose ground, and PM Mitsotakis reiterates that elections will come at the end of the constitutional term."
        },
        "tags": {
            "el": ["Μαξίμου", "Μητσοτάκης", "νέα κόμματα", "εκλογές", "ΝΔ"],
            "en": ["Maximos", "Mitsotakis", "new parties", "elections", "ND"]
        },
        "sentiment": "neutral",
    },
    "42b0ebe05e03": {
        "importance": 82,
        "summary": {
            "el": "Στην τελική ευθεία οι προετοιμασίες για την παρουσίαση του νέου κόμματος Τσίπρα στο Θησείο την Τρίτη 26 Μαΐου. Εκατοντάδες εθελοντές οργανώνουν την εκδήλωση και ετοιμάζεται πλατφόρμα όπου οι πολίτες θα υπογράφουν την ιδρυτική διακήρυξη.",
            "en": "Final preparations are under way for the launch of Alexis Tsipras's new party at Theseion on Tuesday 26 May. Hundreds of volunteers are organizing the event and a digital platform is being readied so citizens can sign the founding declaration online minutes after the launch."
        },
        "tags": {
            "el": ["Τσίπρας", "νέο κόμμα", "Θησείο", "26 Μαΐου", "ιδρυτική διακήρυξη"],
            "en": ["Tsipras", "new party", "Theseion", "May 26", "founding declaration"]
        },
        "sentiment": "neutral",
    },
    "ec9e935ec271": {
        "importance": 78,
        "summary": {
            "el": "Ο υπουργός Άμυνας Νίκος Δένδιας ζητά συγγνώμη και διαβεβαιώσεις από το Κίεβο για το ναυτικό drone που εντοπίστηκε στη Λευκάδα, λέγοντας πως θα μπορούσε να βυθίσει κρουαζιερόπλοιο στο Ιόνιο. Οι έρευνες του ΓΕΕΘΑ καταλήγουν ότι το drone ναυπηγήθηκε για λογαριασμό της Ουκρανίας.",
            "en": "Defense Minister Nikos Dendias demands an apology and assurances from Kyiv over the naval drone found off Lefkada, warning it could have sunk a cruise ship in the Ionian. The Greek General Staff's investigation concludes the drone was built for Ukraine."
        },
        "tags": {
            "el": ["Δένδιας", "Ουκρανία", "drone", "Λευκάδα", "Ιόνιο"],
            "en": ["Dendias", "Ukraine", "drone", "Lefkada", "Ionian"]
        },
        "sentiment": "negative",
    },
    "e69f78faf462": {
        "importance": 65,
        "summary": {
            "el": "Η Κεντρική Επιτροπή του ΣΥΡΙΖΑ συνεδριάζει στις 6 Ιουνίου, μετά τις ανακοινώσεις του κόμματος Τσίπρα. Αμφίβολη η συμμετοχή του διαγραμμένου Παύλου Πολάκη, με ανοιχτό το ζήτημα αν διατηρεί τη θέση του στα κομματικά όργανα.",
            "en": "SYRIZA's Central Committee will meet on 6 June, after Tsipras's party launch. The attendance of expelled MP Pavlos Polakis is uncertain, with party officials divided on whether he keeps his organizational seat after losing his parliamentary group post."
        },
        "tags": {
            "el": ["ΣΥΡΙΖΑ", "Κεντρική Επιτροπή", "Πολάκης", "Φάμελλος", "διαγραφή"],
            "en": ["SYRIZA", "Central Committee", "Polakis", "Famellos", "expulsion"]
        },
        "sentiment": "neutral",
    },
    "ce220ab6e5a8": {
        "importance": 68,
        "summary": {
            "el": "Παρασκηνιακή ερμηνεία της viral πρόσκλησης του Ευάγγελου Βενιζέλου προς τον πρωθυπουργό «να μας πει ποιον θα πάρει τηλέφωνο» σε περίπτωση κρίσης. Υποστηρικτές του απαντούν ότι αντανακλά την ανησυχία του για πολιτική πόλωση και έλλειψη εθνικής συνεννόησης στα εξωτερικά.",
            "en": "Background interpretation of Evangelos Venizelos's viral challenge to the PM to 'tell us whom he will call' in a crisis. Allies say it reflects his concern over political polarization and the absence of national consensus on foreign policy."
        },
        "tags": {
            "el": ["Βενιζέλος", "Μητσοτάκης", "εξωτερική πολιτική", "Κύκλος Ιδεών", "Τουρκία"],
            "en": ["Venizelos", "Mitsotakis", "foreign policy", "Circle of Ideas", "Turkey"]
        },
        "sentiment": "neutral",
    },

    # ===== ECONOMY =====
    "d7ffeb30c8f2": {
        "importance": 70,
        "summary": {
            "el": "Σχόλιο για την προεκλογική στάση της κυβέρνησης απέναντι στις μεταρρυθμίσεις, με αφορμή τα νέα χωροταξικά για τουρισμό, ΑΠΕ και βιομηχανία. Παρά την παράδοση να «μη δυσαρεστήσει κανέναν», αναγνωρίζεται ότι έθεσε σε διαβούλευση θέματα που εκκρεμούσαν 18 χρόνια.",
            "en": "Commentary on the government's pre-election stance on reforms, prompted by new spatial plans for tourism, renewables, and industry. Despite the tradition of 'not upsetting anyone,' it deserves credit for opening for consultation issues pending for 18 years."
        },
        "tags": {
            "el": ["μεταρρυθμίσεις", "χωροταξικά", "ΑΠΕ", "προεκλογικά", "τουρισμός"],
            "en": ["reforms", "spatial planning", "renewables", "pre-election", "tourism"]
        },
        "sentiment": "neutral",
    },
    "fa640e9014bd": {
        "importance": 85,
        "summary": {
            "el": "Η Κομισιόν αναθεωρεί προς τα κάτω τις προβλέψεις ανάπτυξης για το 2026 και προβλέπει πληθωρισμό 3,7% στην Ελλάδα και 3% στην ευρωζώνη, λόγω της νέας ενεργειακής κρίσης από τη Μέση Ανατολή. Η Ελλάδα συνεχίζει ταχύτερη ανάπτυξη από τον μέσο όρο, αλλά εμφανίζει σαφή επιβράδυνση.",
            "en": "The European Commission cuts its 2026 growth forecasts and now projects 3.7% inflation in Greece and 3% in the eurozone, blamed on the new energy crisis spilling from the Middle East. Greece still grows faster than the eurozone average but shows a clear slowdown."
        },
        "tags": {
            "el": ["Κομισιόν", "πληθωρισμός", "ανάπτυξη", "ενεργειακή κρίση", "ευρωζώνη"],
            "en": ["Commission", "inflation", "growth", "energy crisis", "eurozone"]
        },
        "sentiment": "negative",
    },
    "f56d6c8356a8": {
        "importance": 45,
        "summary": {
            "el": "Η Briq Properties ΑΕΕΑΠ ανακοίνωσε αύξηση καθαρών κερδών κατά 21,3% στα 3,58 εκατ. ευρώ το α' τρίμηνο και χαρτοφυλάκιο ακινήτων 288 εκατ. ευρώ. Προχώρησε σε αγορά οικοπέδου στη Μεταμόρφωση Αττικής για νέο βιομηχανικό ακίνητο.",
            "en": "Briq Properties REIC reported a 21.3% jump in Q1 net profits to €3.58 million and a €288 million real estate portfolio. It acquired a plot in Metamorfosi, Attica for a new high-spec industrial property."
        },
        "tags": {
            "el": ["Briq Properties", "ΑΕΕΑΠ", "κερδοφορία", "ακίνητα", "EBITDA"],
            "en": ["Briq Properties", "REIC", "profits", "real estate", "EBITDA"]
        },
        "sentiment": "positive",
    },
    "ce7f87e37e2f": {
        "importance": 55,
        "summary": {
            "el": "Πρόσθετη επιβάρυνση 3-3,5 εκατ. ευρώ ενδέχεται να υποστεί ο όμιλος Fourlis από ενεργειακή ακρίβεια και πληθωρισμό. Η Ρουμανία υποχωρεί 30% στο β' τρίμηνο λόγω πολιτικής αστάθειας, ενώ οι λοιπές αγορές (Ελλάδα, Κύπρος, Βουλγαρία) παραμένουν θετικές. Από τον Ιούνιο ξεκινά το κέντρο διανομής Inter IKEA στον Ασπρόπυργο.",
            "en": "Fourlis Group may face an additional €3-3.5M cost from energy price rises and inflation. Romania is down 30% in Q2 amid political instability, while Greece, Cyprus and Bulgaria remain positive. Inter IKEA's distribution center in Aspropyrgos starts operating in June."
        },
        "tags": {
            "el": ["Fourlis", "IKEA", "Ρουμανία", "ενεργειακή ακρίβεια", "Ασπρόπυργος"],
            "en": ["Fourlis", "IKEA", "Romania", "energy costs", "Aspropyrgos"]
        },
        "sentiment": "neutral",
    },
    "097e66d5c6bd": {
        "importance": 65,
        "summary": {
            "el": "Οι ξένες επενδύσεις επιστρέφουν στην Κίνα καθώς η οικονομία των 20 τρισ. δολαρίων σταθεροποιήθηκε μετά την κατάρρευση των ακινήτων. Η σύνοδος Σι-Τραμπ αντανακλά την επιστροφή κεφαλαίου, αν και οι επενδυτές παραμένουν σε ετοιμότητα φυγής.",
            "en": "Foreign investment is returning to China as its $20 trillion economy stabilizes after the real-estate collapse. The Xi-Trump summit reflects renewed capital flow, though investors remain ready to pull out at the first sign of trouble."
        },
        "tags": {
            "el": ["Κίνα", "ξένες επενδύσεις", "Σι Τζινπίνγκ", "Τραμπ", "ακίνητα"],
            "en": ["China", "FDI", "Xi Jinping", "Trump", "real estate"]
        },
        "sentiment": "positive",
    },
    "b481b29b3778": {
        "importance": 40,
        "summary": {
            "el": "Η August Robotics του ελληνικής καταγωγής Άλεξ Ουάιατ άντλησε 30 εκατ. δολάρια. Έχει αναπτύξει στόλο αυτόνομων ρομπότ που αναλαμβάνουν εργασίες κατακόρυφης διάτρησης σε εργοτάξια, με αρχική εφαρμογή στην κατασκευή data centers ΑΙ.",
            "en": "August Robotics, founded by Greek-American Alex Wyatt, raised $30 million. It has developed a fleet of autonomous robots that perform vertical drilling tasks on large construction sites, initially focused on AI data-center builds."
        },
        "tags": {
            "el": ["August Robotics", "ρομπότ", "data centers", "AI", "venture"],
            "en": ["August Robotics", "robotics", "data centers", "AI", "venture"]
        },
        "sentiment": "positive",
    },
    "410057269feb": {
        "importance": 48,
        "summary": {
            "el": "Ο όμιλος Quest του Θεόδωρου Φέσσα κατέγραψε το α' τρίμηνο έσοδα 365,5 εκατ. ευρώ (+11,4%), EBITDA 19,67 εκατ. (+4,3%) και καθαρά κέρδη 11,4 εκατ. (+14,3%). Ισχυρή ανάπτυξη σε εμπόριο, πληροφορική, ταχυμεταφορές και ενέργεια.",
            "en": "Theodoros Fessas's Quest group posted Q1 revenue of €365.5M (+11.4%), EBITDA of €19.67M (+4.3%) and net profits of €11.4M (+14.3%). Strong growth across its commercial, IT, courier and energy units."
        },
        "tags": {
            "el": ["Quest", "Φέσσας", "πληροφορική", "α' τρίμηνο", "κερδοφορία"],
            "en": ["Quest", "Fessas", "IT", "Q1", "profits"]
        },
        "sentiment": "positive",
    },
    "919c60d73683": {
        "importance": 55,
        "summary": {
            "el": "Η ΜΕΤΚΑ, θυγατρική του ομίλου Metlen, στοχεύει σε λειτουργικά κέρδη EBITDA 140-150 εκατ. ευρώ φέτος, αύξηση 50% έναντι του 2025 και 200% έναντι του 2024. Διατηρεί ανεκτέλεστο υπόλοιπο έργων 2,2 δισ. ευρώ.",
            "en": "METKA, the Metlen group's infrastructure and concessions arm, targets €140-150M of EBITDA this year — up 50% from 2025 and 200% from 2024 — with a €2.2B order backlog."
        },
        "tags": {
            "el": ["ΜΕΤΚΑ", "Metlen", "EBITDA", "υποδομές", "παραχωρήσεις"],
            "en": ["METKA", "Metlen", "EBITDA", "infrastructure", "concessions"]
        },
        "sentiment": "positive",
    },
    "d132ea8fd163": {
        "importance": 50,
        "summary": {
            "el": "Η Skroutz επεκτείνει το δίκτυο αυτοματοποιημένων θυρίδων στις 110.000 ως το τέλος του έτους και εγκαινιάζει ρομποτική αποθήκη 1.000 τ.μ. στην Ελευσίνα με 30 ρομπότ και χωρητικότητα 1,2 εκατ. τεμαχίων. Το 55% των παραγγελιών της διακινείται μέσω θυρίδων.",
            "en": "Skroutz will expand its automated locker network to 110,000 points by year-end and is opening a 1,000 m² robotic warehouse in Eleusis with 30 robots and capacity for 1.2M items. 55% of its orders already move through lockers."
        },
        "tags": {
            "el": ["Skroutz", "θυρίδες", "ρομποτική αποθήκη", "Ελευσίνα", "ηλεκτρονικό εμπόριο"],
            "en": ["Skroutz", "lockers", "robotic warehouse", "Eleusis", "e-commerce"]
        },
        "sentiment": "positive",
    },
    "fdf0279cb8d1": {
        "importance": 85,
        "summary": {
            "el": "Η ΔΕΗ άντλησε 4,5 δισ. ευρώ από την αύξηση κεφαλαίου, με προσφορές 18 δισ. ευρώ (υπερκάλυψη 4,5 φορές) — η μεγαλύτερη προσέλκυση κεφαλαίων στην ιστορία της ελληνικής κεφαλαιαγοράς. Στους νέους μετόχους Blackrock, CVC, Capital, Covalis και το QIA του Κατάρ.",
            "en": "PPC (DEH) raised €4.5 billion in its share capital increase, with €18B in bids — a 4.5x oversubscription and the largest capital raise in Greek market history. New shareholders include BlackRock, CVC, Capital, Covalis and Qatar's QIA."
        },
        "tags": {
            "el": ["ΔΕΗ", "αύξηση κεφαλαίου", "Blackrock", "CVC", "QIA"],
            "en": ["PPC", "share issue", "BlackRock", "CVC", "QIA"]
        },
        "sentiment": "positive",
    },
    "2feb853ccbbd": {
        "importance": 65,
        "summary": {
            "el": "Η Alpha Bank κατέγραψε καθαρά κέρδη 181,5 εκατ. ευρώ (221 εκατ. χωρίς την επιβάρυνση από εθελουσία) στο α' τρίμηνο, στηριζόμενη σε αύξηση 10,4% των βασικών τραπεζικών εσόδων. Στρατηγική μετασχηματισμού σε «οικοσύστημα» τραπεζικών, επενδυτικών και ασφαλιστικών υπηρεσιών.",
            "en": "Alpha Bank posted Q1 net profits of €181.5M (€221M excluding voluntary-exit charges), supported by a 10.4% rise in core banking revenue. The bank is pursuing a transformation into an 'ecosystem' of banking, investment and insurance services."
        },
        "tags": {
            "el": ["Alpha Bank", "α' τρίμηνο", "κερδοφορία", "Ψάλτης", "εθελουσία"],
            "en": ["Alpha Bank", "Q1", "profits", "Psaltis", "voluntary exit"]
        },
        "sentiment": "positive",
    },
    "049a72455915": {
        "importance": 60,
        "summary": {
            "el": "Το υπουργείο Εργασίας ετοιμάζει νομοθετική παρέμβαση για να αλλάξει τον νόμο Κατρούγκαλου ώστε να μην υπάρξει αλλαγή στις πολλαπλές συντάξεις μετά από απόφαση του ΣτΕ. Συνταξιουχικές οργανώσεις ζητούν ταυτόχρονα παρεμβάσεις για συντάξεις χηρείας.",
            "en": "The labor ministry is preparing legislation to amend the Katrougalos law so that the Council of State ruling does not change the multiple-pensions regime. Pensioner groups simultaneously demand protection for widows' pensions."
        },
        "tags": {
            "el": ["συντάξεις", "Κατρούγκαλος", "ΣτΕ", "χηρεία", "υπουργείο Εργασίας"],
            "en": ["pensions", "Katrougalos", "Council of State", "widows", "labor ministry"]
        },
        "sentiment": "neutral",
    },
    "de578e9b89ab": {
        "importance": 75,
        "summary": {
            "el": "Το νέο ειδικό χωροταξικό για τις ΑΠΕ απαγορεύει νέα αιολικά πάρκα σε νησιά κάτω των 300 τ.χλμ. και σε υψόμετρο άνω των 1.200 μ., καθώς και φωτοβολταϊκά σε Natura και δασικές εκτάσεις. Ωστόσο, τα ώριμα και υπό αδειοδότηση έργα δεκάδων χιλιάδων μεγαβάτ εξαιρούνται από τον νέο νόμο.",
            "en": "The new spatial framework for renewables bans new wind farms on islands under 300 km² and at altitudes above 1,200 m, and forbids solar in Natura sites and forested areas. But tens of thousands of MW already under development are exempt from the new rules."
        },
        "tags": {
            "el": ["ΑΠΕ", "χωροταξικό", "αιολικά", "φωτοβολταϊκά", "Natura"],
            "en": ["renewables", "spatial planning", "wind", "solar", "Natura"]
        },
        "sentiment": "neutral",
    },
    "2bf48ac82cfe": {
        "importance": 72,
        "summary": {
            "el": "Η αμερικανική Επιτροπή Αγοράς Προθεσμιακών Συμβολαίων (CFTC) διεξάγει έρευνα για ύποπτες συναλλαγές στην αγορά πετρελαίου στις 23 Μαρτίου, λίγα λεπτά πριν την ανακοίνωση Τραμπ για αναβολή πληγμάτων στο Ιράν. Άλλαξαν χέρια προθεσμιακά αξίας 800 εκατ. δολ. και τουλάχιστον πέντε εταιρείες κέρδισαν πάνω από 5 εκατ. δολ. η καθεμία.",
            "en": "The US Commodity Futures Trading Commission is investigating suspicious oil trades on March 23, minutes before Trump's announcement postponing strikes on Iran. $800M of futures contracts changed hands and at least five firms each made over $5M when prices fell 13%."
        },
        "tags": {
            "el": ["CFTC", "πετρέλαιο", "Τραμπ", "Ιράν", "ύποπτες συναλλαγές"],
            "en": ["CFTC", "oil", "Trump", "Iran", "suspicious trades"]
        },
        "sentiment": "negative",
    },

    # ===== SOCIETY =====
    "6b8e6afdf1ed": {
        "importance": 78,
        "summary": {
            "el": "Μεγάλη επιχείρηση της ΕΛ.ΑΣ. στην Κρήτη με 16 συλλήψεις σε τρεις οικογένειες εγκληματικής οργάνωσης· συνολικά οι εμπλεκόμενοι ανέρχονται σε 76. Έχουν κατασχεθεί όπλα, ναρκωτικά, χρηματικά ποσά, 12 αυτοκίνητα και ενώτια προβάτων, ενώ προέκυψε και σύνδεση με το σκάνδαλο του ΟΠΕΚΕΠΕ.",
            "en": "Major Hellenic Police operation in Crete with 16 arrests across three crime-family clans, with 76 people linked overall. Police seized weapons, narcotics, cash, 12 vehicles and sheep ear-tags — and the case has revealed a link to the OPEKEPE subsidies scandal."
        },
        "tags": {
            "el": ["Κρήτη", "ΕΛ.ΑΣ.", "ναρκωτικά", "εγκληματική οργάνωση", "ΟΠΕΚΕΠΕ"],
            "en": ["Crete", "Hellenic Police", "narcotics", "organized crime", "OPEKEPE"]
        },
        "sentiment": "negative",
    },
    "e7fb0f007fbc": {
        "importance": 35,
        "summary": {
            "el": "Η Hellenic Train αναστέλλει προσωρινά από το Σάββατο 23 Μαΐου όλα τα σιδηροδρομικά δρομολόγια στη γραμμή Αλεξανδρούπολης-Ορμενίου-Ορεστιάδας λόγω εργασιών εγκατάστασης του συστήματος γεωεντοπισμού HEPOS. Τα δρομολόγια θα υποκατασταθούν από λεωφορεία.",
            "en": "Hellenic Train will temporarily suspend all rail services on the Alexandroupoli-Ormenio-Orestiada line starting Saturday May 23 to install the HEPOS geolocation system. Buses will replace the suspended trains."
        },
        "tags": {
            "el": ["Hellenic Train", "Αλεξανδρούπολη", "HEPOS", "σιδηρόδρομος", "Έβρος"],
            "en": ["Hellenic Train", "Alexandroupoli", "HEPOS", "rail", "Evros"]
        },
        "sentiment": "neutral",
    },
    "6ce483c0b2e3": {
        "importance": 25,
        "summary": {
            "el": "Τροχαίο ατύχημα στην Αττική Οδό μετά τον κόμβο Κηφισίας προκάλεσε σοβαρά κυκλοφοριακά προβλήματα, με καθυστερήσεις 20-25 λεπτών προς Ελευσίνα από τον κόμβο Πλακεντίας έως τον κόμβο Κηφισίας. Παραμένουν κλειστές οι αριστερές λωρίδες.",
            "en": "A traffic accident on the Attiki Odos after the Kifissias junction caused major delays — 20-25 minutes westbound to Eleusis from the Plakentias to Kifissias junctions, with the left lanes still closed."
        },
        "tags": {
            "el": ["Αττική Οδός", "τροχαίο", "κυκλοφορία", "Κηφισιά", "Ελευσίνα"],
            "en": ["Attiki Odos", "accident", "traffic", "Kifissia", "Eleusis"]
        },
        "sentiment": "negative",
    },
    "ad5ce3ba55a3": {
        "importance": 45,
        "summary": {
            "el": "Ο ΕΦΕΤ ανακαλεί παρτίδα κατεψυγμένου μπιφτεκιού κοτόπουλου χωρίς γλουτένη της εταιρείας «Α. Καραγιαννάκης Α.Ε.» λόγω παρουσίας σαλμονέλας. Οι καταναλωτές που το έχουν προμηθευτεί καλούνται να μην το καταναλώσουν.",
            "en": "EFET, Greece's food safety authority, is recalling a batch of gluten-free frozen chicken patties from A. Karagiannakis SA due to salmonella contamination. Consumers are advised not to eat the product."
        },
        "tags": {
            "el": ["ΕΦΕΤ", "ανάκληση", "σαλμονέλα", "κοτόπουλο", "Καραγιαννάκης"],
            "en": ["EFET", "recall", "salmonella", "chicken", "Karagiannakis"]
        },
        "sentiment": "negative",
    },
    "45b65e8d87a3": {
        "importance": 55,
        "summary": {
            "el": "Στην Αμαλιάδα, τρεις 13χρονες συνελήφθησαν μετά από επεισόδιο στο οποίο η μία τραυματίστηκε σοβαρά και νοσηλεύεται στο «Καραμανδάνειο» Πατρών. Συνελήφθησαν επίσης τρεις γονείς για παραμέληση εποπτείας ανηλίκων.",
            "en": "In Amaliada, three 13-year-old girls were arrested after a fight in which one was seriously injured and is hospitalized at Karamandaneio in Patras. Three parents were also arrested for failing to supervise their minors."
        },
        "tags": {
            "el": ["Αμαλιάδα", "σχολική βία", "ανήλικοι", "παραμέληση εποπτείας", "Καραμανδάνειο"],
            "en": ["Amaliada", "school violence", "minors", "neglect of supervision", "Karamandaneio"]
        },
        "sentiment": "negative",
    },
    "bf9e6179c7ae": {
        "importance": 60,
        "summary": {
            "el": "Διασωληνωμένος στο νοσοκομείο Πατρών νοσηλεύεται μαθητής ειδικού σχολείου από την Ηλεία, που εμφάνισε συμπτώματα μηνιγγίτιδας. Η κατάστασή του είναι σοβαρή αλλά σταθερή.",
            "en": "A special-needs school pupil from Ilia is on a ventilator at Rio University Hospital in Patras with suspected meningitis. His condition is described as serious but stable."
        },
        "tags": {
            "el": ["Ηλεία", "μηνιγγίτιδα", "Πάτρα", "ειδικό σχολείο", "διασωλήνωση"],
            "en": ["Ilia", "meningitis", "Patras", "special school", "ventilator"]
        },
        "sentiment": "negative",
    },
    "fb56ec141af8": {
        "importance": 45,
        "summary": {
            "el": "Επεισόδιο σε γυμνάσιο του Ηρακλείου, όπου 14χρονος επιτέθηκε σε 13χρονο συμμαθητή του. Συνελήφθη η 39χρονη μητέρα του 14χρονου για παραμέληση εποπτείας ανηλίκου.",
            "en": "An incident at a Heraklion middle school where a 14-year-old attacked a 13-year-old classmate. The 14-year-old's 39-year-old mother was arrested for neglect of supervision of a minor."
        },
        "tags": {
            "el": ["Ηράκλειο", "σχολική βία", "γυμνάσιο", "παραμέληση εποπτείας", "ανήλικοι"],
            "en": ["Heraklion", "school violence", "middle school", "neglect of supervision", "minors"]
        },
        "sentiment": "negative",
    },
    "787a161cd6d3": {
        "importance": 30,
        "summary": {
            "el": "Στη Θεσσαλονίκη, μια 40χρονη τραυματίστηκε στο κεφάλι όταν έσπασε ο στύλος πινακίδας ποδηλατόδρομου και έπεσε πάνω της έξω από το κτίριο της ΧΑΝΘ. Μεταφέρθηκε σε νοσοκομείο για εξετάσεις.",
            "en": "In Thessaloniki, a 40-year-old woman was injured in the head when a bike-lane sign post broke and fell on her outside the YMCA building. She was taken to hospital for tests."
        },
        "tags": {
            "el": ["Θεσσαλονίκη", "ΧΑΝΘ", "ατύχημα", "πινακίδα", "ποδηλατόδρομος"],
            "en": ["Thessaloniki", "YMCA", "accident", "sign", "bike lane"]
        },
        "sentiment": "negative",
    },
    "5916612d15a2": {
        "importance": 65,
        "summary": {
            "el": "Νέα μεγάλη αντι-ναρκωτική επιχείρηση της ΕΛ.ΑΣ. με 200 αστυνομικούς στις περιφέρειες Ηρακλείου, Ρεθύμνου και Λασιθίου. 15 προσαγωγές, κατάσχεση κοκαΐνης, κάνναβης και όπλων· η υπόθεση συνδέεται και με το σκάνδαλο επιδοτήσεων ΟΠΕΚΕΠΕ.",
            "en": "A major new anti-narcotics operation in Crete by 200 officers across Heraklion, Rethymno and Lasithi regions. 15 detentions, seizures of cocaine, cannabis and weapons — and the probe also links to the OPEKEPE subsidies scandal."
        },
        "tags": {
            "el": ["Κρήτη", "ναρκωτικά", "ΕΛ.ΑΣ.", "Ζωνιανά", "ΟΠΕΚΕΠΕ"],
            "en": ["Crete", "narcotics", "Hellenic Police", "Zoniana", "OPEKEPE"]
        },
        "sentiment": "negative",
    },
    "12bc82695e7c": {
        "importance": 70,
        "summary": {
            "el": "Η Ένωση Δικαστών και Εισαγγελέων χαιρετίζει την άρση ασυλίας της Ζωής Κωνσταντοπούλου από τη Βουλή, υπογραμμίζοντας ότι η βουλευτική ασυλία δεν είναι προνόμιο συγκάλυψης αδικημάτων. Ανοίγει η οδός ποινικής διερεύνησης για κακουργηματικές ενέργειες.",
            "en": "The Greek Judges and Prosecutors Union welcomes Parliament's lifting of Zoe Konstantopoulou's immunity, stressing that parliamentary immunity is not a privilege for concealing crimes. The path is now open for criminal investigation of felony allegations."
        },
        "tags": {
            "el": ["Κωνσταντοπούλου", "βουλευτική ασυλία", "ΕνΔΕ", "Βουλή", "δικαιοσύνη"],
            "en": ["Konstantopoulou", "parliamentary immunity", "judges union", "Parliament", "justice"]
        },
        "sentiment": "neutral",
    },
    "b62d13dd5fee": {
        "importance": 55,
        "summary": {
            "el": "Η ΕΛ.ΑΣ. ανακοίνωσε αυξημένα μέτρα ασφαλείας για το Final 4 της Euroleague την Κυριακή στο ΟΑΚΑ, με Ολυμπιακό, Φενέρμπαχτσε, Ρεάλ Μαδρίτης και Βαλένθια. Θα αξιοποιηθούν τεχνικά μέσα επιτήρησης και ειδικό σχέδιο για τη Fan Zone στο Ζάππειο.",
            "en": "The Hellenic Police announced enhanced security measures for the Euroleague Final Four on Sunday at the OAKA stadium, hosting Olympiacos, Fenerbahce, Real Madrid and Valencia. Surveillance technology will be used and a special plan covers the Zappeion Fan Zone."
        },
        "tags": {
            "el": ["Final 4", "Euroleague", "ΟΑΚΑ", "Ολυμπιακός", "ασφάλεια"],
            "en": ["Final Four", "Euroleague", "OAKA", "Olympiacos", "security"]
        },
        "sentiment": "neutral",
    },
    "1aa2d651b487": {
        "importance": 75,
        "summary": {
            "el": "Πόρισμα της Εθνικής Αρχής Διαφάνειας αποκαλύπτει στημένους διαγωνισμούς για ψηφιακά υδρόμετρα μέσω ΕΣΠΑ, με υπερκοστολόγηση που φτάνει το 700%. Την υπόθεση ερευνούν επίσης η Επιτροπή Ανταγωνισμού και η Ευρωπαϊκή Εισαγγελία.",
            "en": "A National Transparency Authority report reveals rigged tenders for smart water meters funded by EU structural funds, with markups of up to 700%. The case is also being investigated by the Competition Commission and the European Public Prosecutor."
        },
        "tags": {
            "el": ["Αρχή Διαφάνειας", "υδρόμετρα", "ΕΣΠΑ", "Ευρωπαϊκή Εισαγγελία", "διαφθορά"],
            "en": ["Transparency Authority", "water meters", "EU funds", "European Prosecutor", "corruption"]
        },
        "sentiment": "negative",
    },
    "68ca73104616": {
        "importance": 30,
        "summary": {
            "el": "Ένοπλη ληστεία σε ψιλικατζίδικο στην Τριανδρία της Θεσσαλονίκης τα ξημερώματα. Τρεις καλυμμένοι δράστες ακινητοποίησαν τον υπάλληλο και άρπαξαν περίπου 400 ευρώ και καπνικά προϊόντα.",
            "en": "An armed robbery at a convenience store in Triandria, Thessaloniki in the early hours. Three masked perpetrators immobilized the clerk and made off with about €400 in cash and tobacco products."
        },
        "tags": {
            "el": ["Θεσσαλονίκη", "ληστεία", "Τριανδρία", "ψιλικατζίδικο", "καπνικά"],
            "en": ["Thessaloniki", "robbery", "Triandria", "convenience store", "tobacco"]
        },
        "sentiment": "negative",
    },

    # ===== WORLD =====
    "f7d371933c5a": {
        "importance": 78,
        "summary": {
            "el": "Οι ακτιβιστές του στολίσκου αλληλεγγύης για τη Γάζα, που συνελήφθησαν από το Ισραήλ και υπέστησαν τον χλευασμό του υπουργού Ασφάλειας Μπεν Γκβιρ, αφέθηκαν ελεύθεροι και απελαύνονται προς την Τουρκία. Η μεταχείρισή τους προκάλεσε διεθνή κατακραυγή και αντίδραση ακόμη και του Νετανιάχου.",
            "en": "Activists from the Gaza solidarity flotilla, arrested by Israel and mocked by Far-Right Security Minister Itamar Ben-Gvir, have been released and are being deported to Turkey. Their treatment drew international condemnation and even rebuke from PM Netanyahu."
        },
        "tags": {
            "el": ["Γάζα", "στολίσκος", "Ισραήλ", "Μπεν Γκβιρ", "Sumud Flotilla"],
            "en": ["Gaza", "flotilla", "Israel", "Ben-Gvir", "Sumud Flotilla"]
        },
        "sentiment": "negative",
    },
    "cef9c067ae5f": {
        "importance": 70,
        "summary": {
            "el": "Η SpaceX του Έλον Μασκ ανακοίνωσε σχέδιο εισαγωγής στη Wall Street, αναμενόμενο να είναι το μεγαλύτερο IPO στην ιστορία. Με αποτίμηση 1,25 τρισ. δολαρίων, ο Μασκ θα μπορούσε να γίνει ο πρώτος τρισεκατομμυριούχος, με μερίδιο άνω των 600 δισ. δολ.",
            "en": "Elon Musk's SpaceX announced plans for a Wall Street IPO expected to be the largest in history. Valued at $1.25 trillion, the listing could make Musk the world's first trillionaire, with his stake potentially worth over $600B."
        },
        "tags": {
            "el": ["SpaceX", "Μασκ", "IPO", "Wall Street", "Starlink"],
            "en": ["SpaceX", "Musk", "IPO", "Wall Street", "Starlink"]
        },
        "sentiment": "positive",
    },
    "d2f97de61a17": {
        "importance": 82,
        "summary": {
            "el": "Ο Ντόναλντ Τραμπ δήλωσε ότι θα μιλήσει με τον πρόεδρο της Ταϊβάν Λάι Τσινγκ-τε, κίνηση άνευ προηγουμένου που μπορεί να διαταράξει τις σχέσεις με την Κίνα. Οι ηγέτες ΗΠΑ-Ταϊβάν δεν έχουν επικοινωνήσει απευθείας από το 1979.",
            "en": "Donald Trump said he will speak with Taiwan's president Lai Ching-te, an unprecedented move that could rattle US-China relations. US and Taiwanese leaders have not communicated directly since Washington recognized Beijing in 1979."
        },
        "tags": {
            "el": ["Τραμπ", "Ταϊβάν", "Λάι Τσινγκ-τε", "Κίνα", "διπλωματία"],
            "en": ["Trump", "Taiwan", "Lai Ching-te", "China", "diplomacy"]
        },
        "sentiment": "negative",
    },
    "8ac56f7d2057": {
        "importance": 55,
        "summary": {
            "el": "Το ECDC ανακοινώνει ότι τα κρούσματα βακτηριακών σεξουαλικά μεταδιδόμενων λοιμώξεων έφτασαν το 2024 σε επίπεδα ρεκόρ στην Ευρώπη. Η γονόρροια αυξήθηκε 303% από το 2015 (106.331 κρούσματα), η σύφιλη υπερδιπλασιάστηκε στα 45.577.",
            "en": "The ECDC reports that bacterial STI cases in Europe hit record levels in 2024. Gonorrhea cases rose 303% since 2015 to 106,331, syphilis more than doubled to 45,577."
        },
        "tags": {
            "el": ["ECDC", "STIs", "γονόρροια", "σύφιλη", "Ευρώπη"],
            "en": ["ECDC", "STIs", "gonorrhea", "syphilis", "Europe"]
        },
        "sentiment": "negative",
    },
    "859be8e1fff7": {
        "importance": 45,
        "summary": {
            "el": "Στο Λονδίνο κλάπηκαν 70.000 smartphones το 2025 (σχεδόν 200 τη μέρα), με πολλά να καταλήγουν στην Κίνα. Η Μητροπολιτική Αστυνομία προειδοποιεί για οργανωμένα κυκλώματα που στρατολογούν νέους με μηχανάκια και αμοιβές 400-500 λιρών ανά κινητό.",
            "en": "About 70,000 smartphones were stolen in London in 2025 (nearly 200/day), many ending up in China. The Met warns of organized rings recruiting youths on scooters and paying them £400-500 per stolen phone."
        },
        "tags": {
            "el": ["Λονδίνο", "κλοπές κινητών", "Κίνα", "Met Police", "κυκλώματα"],
            "en": ["London", "phone theft", "China", "Met Police", "rings"]
        },
        "sentiment": "negative",
    },
    "50c22e855b5d": {
        "importance": 55,
        "summary": {
            "el": "Η εκπρόσωπος του ρωσικού ΥΠΕΞ Μαρία Ζαχάροβα δήλωσε ότι η Ρωσία θα συνεχίσει να στηρίζει την Κούβα, καταγγέλλοντας την αμερικανική πολιτική κυρώσεων και τη δίωξη κατά του πρώην προέδρου Ραούλ Κάστρο για φόνο.",
            "en": "Russian Foreign Ministry spokeswoman Maria Zakharova said Russia will continue to back Cuba, denouncing US sanctions and the murder charges filed against former president Raul Castro."
        },
        "tags": {
            "el": ["Ρωσία", "Κούβα", "Ζαχάροβα", "Ραούλ Κάστρο", "κυρώσεις"],
            "en": ["Russia", "Cuba", "Zakharova", "Raul Castro", "sanctions"]
        },
        "sentiment": "neutral",
    },
    "6583ee7e7146": {
        "importance": 50,
        "summary": {
            "el": "Πτήση της Air France Παρίσι-Ντιτρόιτ εκτράπηκε στο Μόντρεαλ αφού οι ΗΠΑ απαγόρευσαν την είσοδο επικαλούμενες νέους περιορισμούς για άτομα που έχουν ταξιδέψει σε τρεις χώρες της ανατολικής Αφρικής όπου έχει ξεσπάσει θανατηφόρα επιδημία Έμπολα. Ο ΠΟΥ καταγράφει 600 ύποπτα κρούσματα και 139 θανάτους.",
            "en": "An Air France Paris-Detroit flight was diverted to Montreal after the US denied entry, citing new restrictions for people who recently traveled to three East African countries hit by a deadly Ebola outbreak. The WHO counts about 600 suspected cases and 139 deaths."
        },
        "tags": {
            "el": ["Έμπολα", "Air France", "Καναδάς", "ΗΠΑ", "ΠΟΥ"],
            "en": ["Ebola", "Air France", "Canada", "US", "WHO"]
        },
        "sentiment": "negative",
    },
    "5d9863b56c49": {
        "importance": 80,
        "summary": {
            "el": "Ο Τσέχος πρόεδρος Πετρ Πάβελ, απόστρατος στρατηγός του ΝΑΤΟ, προειδοποίησε στο GLOBSEC ότι «η ειρήνη στην Ευρώπη δεν είναι πλέον δεδομένη» και πως η Ευρώπη πρέπει να είναι αρκετά ισχυρή ώστε να σταθεί μόνη της. Η δήλωση γίνεται καθώς οι ΗΠΑ απομακρύνονται από ιστορικές εγγυήσεις ασφάλειας.",
            "en": "Czech President Petr Pavel, a retired NATO general, warned at GLOBSEC that 'peace in Europe can no longer be taken for granted' and that Europe must be strong enough to stand alone. His remarks come as the US pulls back from long-standing security guarantees."
        },
        "tags": {
            "el": ["Πάβελ", "Τσεχία", "GLOBSEC", "ΝΑΤΟ", "Ευρώπη"],
            "en": ["Pavel", "Czechia", "GLOBSEC", "NATO", "Europe"]
        },
        "sentiment": "negative",
    },
    "2cde73bed362": {
        "importance": 75,
        "summary": {
            "el": "Σύμφωνα με τη Washington Post, ο Πούτιν απέτυχε ξανά να πείσει τον Σι Τζινπίνγκ να υπογράψει συμφωνία για την κατασκευή του αγωγού «Δύναμη της Σιβηρίας-2» δυναμικότητας 50 δισ. κυβ. μ. ετησίως. Υπογραμμίζονται οι περιορισμοί της αυξανόμενης εξάρτησης της Ρωσίας από την Κίνα στην ενέργεια.",
            "en": "According to the Washington Post, Putin once again failed to convince Xi Jinping to sign off on the 'Power of Siberia 2' gas pipeline (50 bcm/year). The episode highlights the limits of Russia's growing energy dependence on China."
        },
        "tags": {
            "el": ["Πούτιν", "Σι Τζινπίνγκ", "Δύναμη της Σιβηρίας-2", "αγωγός", "Κίνα-Ρωσία"],
            "en": ["Putin", "Xi Jinping", "Power of Siberia 2", "pipeline", "China-Russia"]
        },
        "sentiment": "neutral",
    },
    "961fb3eee67b": {
        "importance": 80,
        "summary": {
            "el": "Το CNN, επικαλούμενο αμερικανικές υπηρεσίες πληροφοριών, αναφέρει ότι το Ιράν ανασυγκροτείται ταχύτερα από το αναμενόμενο. Έχει ήδη επανεκκινήσει μέρος της παραγωγής drones κατά την εξάμηνη εκεχειρία που ξεκίνησε στις αρχές Απριλίου.",
            "en": "CNN, citing US intelligence sources, reports that Iran is rebuilding faster than expected. It has already restarted part of its drone production during the six-month ceasefire that began in early April."
        },
        "tags": {
            "el": ["Ιράν", "CNN", "drones", "ανασυγκρότηση", "εκεχειρία"],
            "en": ["Iran", "CNN", "drones", "rebuilding", "ceasefire"]
        },
        "sentiment": "negative",
    },
    "1bf6969c89c6": {
        "importance": 40,
        "summary": {
            "el": "Σεισμός 4,4 βαθμών της κλίμακας Ρίχτερ καταγράφηκε το πρωί στα Φλεγραία Πεδία έξω από τη Νάπολη. Δεν υπάρχουν τραυματίες ή σημαντικές ζημιές· τα σχολεία παραμένουν προληπτικά κλειστά στην ευρύτερη περιοχή.",
            "en": "A 4.4 magnitude earthquake struck the Phlegraean Fields outside Naples this morning. No injuries or significant damage reported; schools in the broader area remain closed as a precaution."
        },
        "tags": {
            "el": ["Ιταλία", "σεισμός", "Νάπολη", "Φλεγραία Πεδία", "σχολεία"],
            "en": ["Italy", "earthquake", "Naples", "Phlegraean Fields", "schools"]
        },
        "sentiment": "neutral",
    },
    "d6cd3eba6d7d": {
        "importance": 60,
        "summary": {
            "el": "Η Κίνα αντιτίθεται σθεναρά στις ΗΠΑ για την «κατάχρηση δικαστικών μέσων» μετά τη δίωξη κατά του πρώην προέδρου της Κούβας Ραούλ Κάστρο με κατηγορίες για ανθρωποκτονία. Καλεί την Ουάσιγκτον να σταματήσει τη χρήση κυρώσεων ως εργαλείου καταπίεσης.",
            "en": "China strongly objects to what it calls US 'abuse of judicial means' after Washington's murder charges against former Cuban president Raul Castro. Beijing urges the US to stop using sanctions as instruments of oppression."
        },
        "tags": {
            "el": ["Κίνα", "ΗΠΑ", "Ραούλ Κάστρο", "Κούβα", "κυρώσεις"],
            "en": ["China", "US", "Raul Castro", "Cuba", "sanctions"]
        },
        "sentiment": "negative",
    },
    "ec8ba893abf4": {
        "importance": 72,
        "summary": {
            "el": "Ανάλυση για το αμερικανικό κατηγορητήριο κατά του Ραούλ Κάστρο και τη στρατηγική Τραμπ απέναντι στην Κούβα. Η Αβάνα βρίσκεται σε ασφυκτικές συνθήκες με διακοπές ρεύματος, ελλείψεις καυσίμων και κλιμακούμενο αμερικανικό αποκλεισμό, εγείροντας ερωτήματα αν το κομμουνιστικό καθεστώς απειλείται.",
            "en": "Analysis of the US indictment of Raul Castro and the Trump strategy toward Cuba. Havana is in dire straits — power cuts, fuel shortages, and an escalating US blockade — raising the question of whether the 67-year-old communist regime is now at risk."
        },
        "tags": {
            "el": ["Κούβα", "Ραούλ Κάστρο", "Τραμπ", "αποκλεισμός", "Αβάνα"],
            "en": ["Cuba", "Raul Castro", "Trump", "blockade", "Havana"]
        },
        "sentiment": "negative",
    },

    # ===== OPINION =====
    "8b8ad187bc7d": {
        "importance": 50,
        "summary": {
            "el": "Συντακτικό σχόλιο για τη νομοθετική προσπάθεια να αναγνωριστούν εκ νέου ως βαρέα και ανθυγιεινά επαγγέλματα που είχαν εξαιρεθεί στην κρίση. Καλεί σε σύνεση ώστε να μη «ξεχειλώσει» πάλι ο ορισμός και να προστατεύονται όσοι όντως κάνουν βαριά δουλειά.",
            "en": "Editorial on the legislative effort to re-recognize as 'heavy and unhealthy' professions excluded during the crisis. Calls for restraint so the definition is not stretched again, and protection focuses on those who really do heavy work."
        },
        "tags": {
            "el": ["βαρέα", "ανθυγιεινά", "συντάξεις", "νομοθεσία", "εργασία"],
            "en": ["heavy occupations", "unhealthy occupations", "pensions", "legislation", "labor"]
        },
        "sentiment": "neutral",
    },
    "9a575d14ef0e": {
        "importance": 55,
        "summary": {
            "el": "Άρθρο γνώμης που επαινεί το ντοκιμαντέρ «Στο Χιλιοστό» και τη δημόσια υπάλληλο Σταυρούλα Μηλιάκου, που υπερασπίστηκε το Γενικό Λογιστήριο του Κράτους το 2014-18. Επιχειρηματολογεί ότι αθόρυβοι δημόσιοι λειτουργοί αποτελούν την «ραχοκοκαλιά» του κράτους.",
            "en": "Op-ed praising the documentary 'Sto Hiliosto' and civil servant Stavroula Miliakou, who defended the General Accounting Office of the State in 2014-18. Argues that quiet public servants are the country's true 'backbone.'"
        },
        "tags": {
            "el": ["δημόσιοι υπάλληλοι", "ντοκιμαντέρ", "Στο Χιλιοστό", "Γενικό Λογιστήριο", "κρίση"],
            "en": ["civil servants", "documentary", "Sto Hiliosto", "GAO", "crisis"]
        },
        "sentiment": "positive",
    },
    "47f14ba22f51": {
        "importance": 45,
        "summary": {
            "el": "Λογοτεχνικό-φιλοσοφικό άρθρο για τον Όμηρο και την αντίληψη της ομορφιάς στην αρχαία ελληνική παράδοση. Ο συγγραφέας επιχειρηματολογεί ότι οι Έλληνες ποιητές έπλασαν αξιακό κόσμο που υπερβαίνει τους περιγραφικούς χαρακτηρισμούς και τη «φυλή».",
            "en": "A literary-philosophical piece on Homer and the conception of beauty in the ancient Greek tradition. The author argues that Greek poets created a value-world that transcends descriptive characterizations and the concept of 'race.'"
        },
        "tags": {
            "el": ["Όμηρος", "αρχαία Ελλάδα", "ομορφιά", "φυλή", "λογοτεχνία"],
            "en": ["Homer", "ancient Greece", "beauty", "race", "literature"]
        },
        "sentiment": "neutral",
    },
    "103e8be3ce77": {
        "importance": 65,
        "summary": {
            "el": "Πολιτικό σχόλιο που υποστηρίζει ότι ο Παύλος Πολάκης ενσαρκώνει ό,τι έχει απομείνει από τον ΣΥΡΙΖΑ, και η σημασία του δεν αναδείχθηκε τώρα αλλά υπήρξε διαρκής. Η διαγραφή του φέρει το βάρος του τέλους μιας πολιτικής εποχής.",
            "en": "Political commentary arguing that Pavlos Polakis embodies what remains of SYRIZA, and that his significance was not invented now but has been constant. His expulsion carries the weight of the end of a political era."
        },
        "tags": {
            "el": ["Πολάκης", "ΣΥΡΙΖΑ", "διαγραφή", "πολιτική", "Φάμελλος"],
            "en": ["Polakis", "SYRIZA", "expulsion", "politics", "Famellos"]
        },
        "sentiment": "neutral",
    },
    "8610faecc51d": {
        "importance": 40,
        "summary": {
            "el": "Λογοτεχνικό αφήγημα γύρω από έναν παππού που λύνει το κλασικό πρόβλημα της κάλπικης λίρας από τη «Νέα γενική πρακτική αριθμητική» του Σμυρνιωτάκη, ως τεστ μνήμης. Στοχαστικό κείμενο για τη γήρανση και την αντοχή του μυαλού.",
            "en": "A literary vignette about a grandfather solving the classic counterfeit-coin puzzle from Smyrniotakis's mathematics textbook as a memory test. A reflective piece on aging and mental resilience."
        },
        "tags": {
            "el": ["μνήμη", "Σμυρνιωτάκης", "γρίφος", "γήρανση", "λογοτεχνία"],
            "en": ["memory", "Smyrniotakis", "puzzle", "aging", "literature"]
        },
        "sentiment": "neutral",
    },
    "345f53c87d1a": {
        "importance": 60,
        "summary": {
            "el": "Άρθρο γνώμης που σχολιάζει το πέρασμα της κοινωνίας από την «περίοδο της υπερευαισθησίας» των μνημονιακών χρόνων στην «κατάσταση αναλγησίας» σήμερα, με αφορμή το περιστατικό με τα έξι ανήλικα στο Περιστέρι.",
            "en": "Op-ed arguing that society has moved from the 'period of hypersensitivity' of the bailout years to today's 'state of indifference,' prompted by the incident involving six minors in Peristeri."
        },
        "tags": {
            "el": ["υπερευαισθησία", "Περιστέρι", "ανήλικοι", "κοινωνία", "μνημόνια"],
            "en": ["hypersensitivity", "Peristeri", "minors", "society", "bailouts"]
        },
        "sentiment": "negative",
    },
    "751a8bdb81e4": {
        "importance": 70,
        "summary": {
            "el": "Άρθρο γνώμης που παραλληλίζει την Αριστερά του Τσίπρα με την αναθεωρητική στιγμή του Μπαντ Γκόντεσμπεργκ των Γερμανών Σοσιαλδημοκρατών το 1959. Υποστηρίζει ότι το νέο κόμμα του πρώην πρωθυπουργού οφείλει να αναθεωρήσει ιδεολογικές συντεταγμένες αν θέλει εξουσία.",
            "en": "Op-ed drawing a parallel between Tsipras's Left and the German SPD's 1959 Bad Godesberg revisionist moment. Argues the former PM's new party must rethink its ideological coordinates if it wants to govern again."
        },
        "tags": {
            "el": ["Τσίπρας", "Αριστερά", "Μπαντ Γκόντεσμπεργκ", "ιδεολογία", "νέο κόμμα"],
            "en": ["Tsipras", "Left", "Bad Godesberg", "ideology", "new party"]
        },
        "sentiment": "neutral",
    },
    "053b34a8a709": {
        "importance": 30,
        "summary": {
            "el": "Λογοτεχνικό σημείωμα για την ιστορία του ποδοσφαίρου με αφορμή το βιβλίο του Εδουάρδο Γκαλεάνο «Το ποδόσφαιρο στη σκιά και στο φως». Από την αρχαία Κίνα και τις Αιγύπτιους, στους Αζτέκους που έπαιζαν «πολύ άγρια μπάλα».",
            "en": "A literary note on the history of football, prompted by Eduardo Galeano's book 'Soccer in Sun and Shadow.' From ancient China and Egypt to the Aztecs who played 'very wild ball.'"
        },
        "tags": {
            "el": ["ποδόσφαιρο", "Γκαλεάνο", "Αζτέκοι", "ιστορία", "αθλητισμός"],
            "en": ["football", "Galeano", "Aztecs", "history", "sport"]
        },
        "sentiment": "neutral",
    },
    "f67b81b5530a": {
        "importance": 55,
        "summary": {
            "el": "Άρθρο γνώμης για την αυξανόμενη έλξη που ασκεί ο αρχαίος ελληνικός πολιτισμός στην Άπω Ανατολή, με αφορμή την αναφορά Σι Τζινπίνγκ στον Θουκυδίδη. Παρουσιάζει το βιβλίο του Τόνι Σπόφορθ «Τι οφείλουμε στους αρχαίους Έλληνες».",
            "en": "Op-ed on the growing attraction of ancient Greek civilization in the Far East, prompted by Xi Jinping's reference to Thucydides. It introduces Tony Spawforth's book 'What We Owe the Ancient Greeks.'"
        },
        "tags": {
            "el": ["αρχαία Ελλάδα", "Σπόφορθ", "Σι Τζινπίνγκ", "Άπω Ανατολή", "Θουκυδίδης"],
            "en": ["ancient Greece", "Spawforth", "Xi Jinping", "Far East", "Thucydides"]
        },
        "sentiment": "positive",
    },
    "978292808e31": {
        "importance": 65,
        "summary": {
            "el": "Σχόλιο για τη θετική αναφορά Τραμπ στον Μητσοτάκη και τη στρατηγική ισορροπίας της Αθήνας ανάμεσα στις ΗΠΑ και την «αντιδημοφιλία» του πολέμου στο Ιράν. Αντιπαραβολή με την Ισπανία, που αρνήθηκε την αύξηση αμυντικών δαπανών και επικρίθηκε από τους Αμερικανούς.",
            "en": "Commentary on Trump's positive remarks about Mitsotakis and Athens's balancing act between the US alliance and the unpopular war in Iran. Contrasted with Spain, which refused to raise defense spending to 5% of GDP and drew US criticism."
        },
        "tags": {
            "el": ["Τραμπ", "Μητσοτάκης", "Ισπανία", "ΝΑΤΟ", "αμυντικές δαπάνες"],
            "en": ["Trump", "Mitsotakis", "Spain", "NATO", "defense spending"]
        },
        "sentiment": "neutral",
    },
    "67516a960b21": {
        "importance": 55,
        "summary": {
            "el": "Σατιρικό σχόλιο για τη Ζωή Κωνσταντοπούλου, της οποίας η Βουλή ψήφισε δύο φορές την άρση ασυλίας. Επικρίνει τις «ηχορρυπαντικές» παραστάσεις και την κωμική «τεκμηρίωση» μεροληψίας του προεδρεύοντος.",
            "en": "Satirical commentary on Zoe Konstantopoulou, whose parliamentary immunity was lifted twice in one day. Mocks her 'noise-polluting' performances and the comical 'evidence' she presented of bias by the presiding chair."
        },
        "tags": {
            "el": ["Κωνσταντοπούλου", "βουλευτική ασυλία", "Πλεύση", "σάτιρα", "Γεωργαντάς"],
            "en": ["Konstantopoulou", "immunity", "Plefsi", "satire", "Georgantas"]
        },
        "sentiment": "negative",
    },
    "1e0b77fd9c86": {
        "importance": 55,
        "summary": {
            "el": "Άρθρο γνώμης που κριτικάρει το σύστημα των Πανελλαδικών εξετάσεων ως μηχανισμό «εθισμού στην υπαλληλική λογική». Υποστηρίζει ότι μεταφράζει την οικονομική ανάγκη σε «επιλογή» και διδάσκει τους ανθρώπους να βλέπουν τους εαυτούς τους μονοδιάστατα.",
            "en": "Op-ed criticizing the national university entrance exams (Panelladikes) as a mechanism that 'addicts us to the salaried-employee mindset.' Argues the system reframes economic necessity as 'choice' and teaches people to see themselves one-dimensionally."
        },
        "tags": {
            "el": ["Πανελλαδικές", "παιδεία", "εργασία", "Νομική Αθηνών", "νέοι"],
            "en": ["Panelladikes", "education", "work", "Athens Law", "youth"]
        },
        "sentiment": "neutral",
    },

    # ===== CULTURE =====
    "2bad26bc4d45": {
        "importance": 70,
        "summary": {
            "el": "Πέθανε σε ηλικία 71 ετών η ιστορικός τέχνης Άννα Καφέτση, πρώτη διευθύντρια του Εθνικού Μουσείου Σύγχρονης Τέχνης (ΕΜΣΤ). Καθοριστική προσωπικότητα πίσω από τη δημιουργία του Μουσείου, ανέλαβε τη διεύθυνση το 2000 και έχτισε από το μηδέν τη συλλογή και τη θεσμική του ταυτότητα.",
            "en": "Art historian Anna Kafetsi, founding director of Greece's National Museum of Contemporary Art (EMST), has died aged 71. She took over the museum in 2000 and built its collection and institutional identity from scratch."
        },
        "tags": {
            "el": ["ΕΜΣΤ", "Καφέτση", "νεκρολογία", "σύγχρονη τέχνη", "μουσείο"],
            "en": ["EMST", "Kafetsi", "obituary", "contemporary art", "museum"]
        },
        "sentiment": "negative",
    },
    "e675d8302c2b": {
        "importance": 65,
        "summary": {
            "el": "Ιστορικό ρεκόρ πώλησης για ελληνικό έργο τέχνης του 20ού αιώνα: το μνημειακό «Ποίηση (Ευαγγελισμός)» του Κωνσταντίνου Παρθένη πωλήθηκε στο 1 εκατ. ευρώ στη δημοπρασία Bonhams Greek Sales στο Παρίσι, ξεπερνώντας κατά πολύ την εκτίμηση των 300-500 χιλ. ευρώ.",
            "en": "Historic record for a 20th-century Greek artwork: Konstantinos Parthenis's monumental 'Poetry (Annunciation)' sold for €1 million at the Bonhams Greek Sale in Paris, far above the €300-500K estimate."
        },
        "tags": {
            "el": ["Παρθένης", "Bonhams", "δημοπρασία", "ρεκόρ", "ελληνική τέχνη"],
            "en": ["Parthenis", "Bonhams", "auction", "record", "Greek art"]
        },
        "sentiment": "positive",
    },
    "979826643d52": {
        "importance": 45,
        "summary": {
            "el": "Παρουσίαση των νέων ταινιών της εβδομάδας. Πρωταγωνιστής το «Η ομηρία» του Γκας βαν Σαντ με Πατσίνο και Σκάρσγκαρντ, βασισμένο στην αληθινή ιστορία του Τόνι Κιρίτσις που πήρε ομήρους σε εταιρεία υποθηκών το 1977.",
            "en": "Weekly new-film roundup. Headlined by Gus Van Sant's 'The Hostage' with Pacino and Skarsgård, based on the true story of Greek-American Tony Kiritsis, who took hostages at a mortgage company in 1977."
        },
        "tags": {
            "el": ["σινεμά", "Γκας βαν Σαντ", "Πατσίνο", "Σκάρσγκαρντ", "Κιρίτσις"],
            "en": ["cinema", "Gus Van Sant", "Pacino", "Skarsgård", "Kiritsis"]
        },
        "sentiment": "neutral",
    },
    "d95022e28b79": {
        "importance": 55,
        "summary": {
            "el": "Ο Τούρκος νομπελίστας Ορχάν Παμούκ στα Χανιά, ως προσκεκλημένος του Φεστιβάλ Βιβλίου που κλείνει την πενταετία του με τίτλο «Κόσμοι σε σύγκρουση». Ξεναγήθηκε στην προσωπική συλλογή βιβλίων του Ελευθερίου Βενιζέλου στη Δημοτική Βιβλιοθήκη.",
            "en": "Nobel laureate Orhan Pamuk visits Chania as guest of the Book Festival, which closes its five-year run under the title 'Worlds in Conflict.' He toured Eleftherios Venizelos's personal library at the Municipal Library."
        },
        "tags": {
            "el": ["Παμούκ", "Χανιά", "Φεστιβάλ Βιβλίου", "Βενιζέλος", "λογοτεχνία"],
            "en": ["Pamuk", "Chania", "Book Festival", "Venizelos", "literature"]
        },
        "sentiment": "positive",
    },
    "22f12510ab10": {
        "importance": 40,
        "summary": {
            "el": "Το «The Adventures of Cliff Booth», σίκουελ του «Once Upon a Time in Hollywood» του Ταραντίνο με τον Μπραντ Πιτ, θα κάνει πρεμιέρα σε IMAX στις 25 Νοεμβρίου και θα είναι διαθέσιμο στο Netflix από τις 23 Δεκεμβρίου.",
            "en": "'The Adventures of Cliff Booth,' Tarantino's sequel to 'Once Upon a Time in Hollywood' starring Brad Pitt, will premiere in IMAX on November 25 and arrive on Netflix on December 23."
        },
        "tags": {
            "el": ["Ταραντίνο", "Πιτ", "Once Upon a Time in Hollywood", "Netflix", "IMAX"],
            "en": ["Tarantino", "Pitt", "Once Upon a Time in Hollywood", "Netflix", "IMAX"]
        },
        "sentiment": "positive",
    },
    "d2ae23b206da": {
        "importance": 50,
        "summary": {
            "el": "Το «Taiwan Travelogue» της Γιανγκ Σουάνγκ-Ζι κέρδισε το Διεθνές Βραβείο Booker, το πρώτο βιβλίο γραμμένο στα Μανδαρινικά που το αποκτά. Παρουσιάζεται ως μετάφραση ημερολογίου ταξιδιού στην ιαπωνικά κατεχόμενη Ταϊβάν του 1938.",
            "en": "Yang Shuang-zi's 'Taiwan Travelogue' won the International Booker Prize — the first book written in Mandarin to do so. It is presented as the translation of a travel diary set in Japanese-occupied Taiwan in 1938."
        },
        "tags": {
            "el": ["Booker", "Ταϊβάν", "λογοτεχνία", "Yang Shuang-zi", "βιβλίο"],
            "en": ["Booker", "Taiwan", "literature", "Yang Shuang-zi", "book"]
        },
        "sentiment": "positive",
    },
    "bc50e11eba89": {
        "importance": 25,
        "summary": {
            "el": "Πολιτιστική ατζέντα με προτάσεις για θέατρο, συναυλίες, εκθέσεις και εκδηλώσεις της Πέμπτης. Επιστρέφει το φεστιβάλ παραδοσιακής μουσικής «Ρίζες» στην Τεχνόπολη και εγκαινιάζεται η έκθεση «Human in the loop» στο Onassis Ready.",
            "en": "Cultural agenda with Thursday's theatre, concert, exhibition and event recommendations. The 'Roots' traditional music festival returns to Technopolis, and the 'Human in the loop' exhibition opens at Onassis Ready."
        },
        "tags": {
            "el": ["ατζέντα", "Τεχνόπολη", "Ρίζες", "Onassis Ready", "ΕΜΣΤ"],
            "en": ["agenda", "Technopolis", "Roots", "Onassis Ready", "EMST"]
        },
        "sentiment": "neutral",
    },
    "8e91911f0d15": {
        "importance": 35,
        "summary": {
            "el": "Επετειακό αφιέρωμα στον Χάρρυ Κλυνν (Βασίλη Τριανταφυλλίδη), τον Καλαμαριώτη σατιρικό ηθοποιό που έφυγε στις 21 Μαΐου 2018. Αναφορές στις λαϊκές συναυλίες της δεκαετίας του '80 και τη σύνδεσή του με τον Στέλιο Καζαντζίδη.",
            "en": "Anniversary tribute to Harry Klynn (Vasilis Triantafyllidis), the satirical actor from Kalamaria who died on May 21, 2018. The piece recalls his 1980s 'laiko' concerts and connection with Stelios Kazantzidis."
        },
        "tags": {
            "el": ["Χάρρυ Κλυνν", "Καζαντζίδης", "σάτιρα", "λαϊκή μουσική", "επέτειος"],
            "en": ["Harry Klynn", "Kazantzidis", "satire", "Greek folk music", "anniversary"]
        },
        "sentiment": "neutral",
    },
    "8dd363246011": {
        "importance": 45,
        "summary": {
            "el": "Αναδρομική έκθεση του Γιάννη Ψυχοπαίδη με 70 έργα στο Μουσείο του Ιδρύματος Γουλανδρή υπό τον τίτλο «Τοπία της Μνήμης. Αυτά που κράτησα», σε επιμέλεια του Κυριάκου Κουτσομάλλη. Πρόκειται για προσωπική παρακαταθήκη έργων που ο ζωγράφος διέσωσε από κάθε περίοδό του.",
            "en": "Retrospective of Yannis Psychopedis with 70 works at the Goulandris Foundation Museum titled 'Landscapes of Memory: What I Kept,' curated by Kyriakos Koutsomallis. A personal legacy of works the painter preserved from each period of his career."
        },
        "tags": {
            "el": ["Ψυχοπαίδης", "Γουλανδρή", "ζωγραφική", "αναδρομική", "Κουτσομάλλης"],
            "en": ["Psychopedis", "Goulandris", "painting", "retrospective", "Koutsomallis"]
        },
        "sentiment": "positive",
    },
    "a7eeefa90c81": {
        "importance": 25,
        "summary": {
            "el": "Πρόοδος πλοκής της κωμικής σειράς «Το σόι σου»: η Πόπη Μπουτζούκα επιστρέφει στη ζωή του Σάββα, ενώ ξεκαρδιστικές καταστάσεις περιμένουν τους Χαμπέα και Τριαντάφυλλου στα νέα επεισόδια Πέμπτης και Παρασκευής.",
            "en": "Plot teasers for the comedy series 'To Soi Sou': Popi Boutzouka returns into Savvas's life, with hilarious twists in store for the Hambeas and Triantafyllou families in this week's Thursday and Friday episodes."
        },
        "tags": {
            "el": ["Το σόι σου", "τηλεόραση", "κωμωδία", "σειρά", "ψυχαγωγία"],
            "en": ["To Soi Sou", "TV", "comedy", "series", "entertainment"]
        },
        "sentiment": "neutral",
    },
    "b7f99d181841": {
        "importance": 40,
        "summary": {
            "el": "Παρουσίαση της νέας μυθιστορηματικής βιογραφίας «Σοφία ντε Μαρβουά, Δουκέσσα της Πλακεντίας» του Γιώργου Γιαννικόπουλου από τις εκδόσεις Εστία. Καλύπτει χρονικά από την ναπολεόντεια Γαλλία έως την Αθήνα του 1830-1850 και τον θάνατο της Δούκισσας το 1854.",
            "en": "Review of George Giannikopoulos's new novelized biography 'Sophia de Marbois, Duchess of Plaisance' from Estia Editions. It spans Napoleonic France and 1830-1850 Athens up to the Duchess's death in 1854."
        },
        "tags": {
            "el": ["Πλακεντία", "βιογραφία", "Γιαννικόπουλος", "Εστία", "φιλελληνισμός"],
            "en": ["Plaisance", "biography", "Giannikopoulos", "Estia", "philhellenism"]
        },
        "sentiment": "positive",
    },
    "6dc239f9683a": {
        "importance": 30,
        "summary": {
            "el": "Ξεκίνησαν τα γυρίσματα της νέας σειράς του ΣΚΑΪ «Μπλε ώρες» στο Πήλιο, σε σκηνοθεσία Ανδρέα Γεωργίου. Συνδυάζει ερωτικό και αστυνομικό στοιχείο με φόντο τη φυσική ομορφιά της περιοχής.",
            "en": "Filming has begun on SKAI's new series 'Blue Hours' in Pelion, directed by Andreas Georgiou. The drama combines romance and crime against the natural beauty of the region."
        },
        "tags": {
            "el": ["ΣΚΑΪ", "Μπλε ώρες", "Πήλιο", "τηλεόραση", "Γεωργίου"],
            "en": ["SKAI", "Blue Hours", "Pelion", "TV", "Georgiou"]
        },
        "sentiment": "neutral",
    },
    "2f35f5587d6b": {
        "importance": 30,
        "summary": {
            "el": "Αναφορά στην πολιτιστική επίδραση του χαρακτήρα Grogu (Baby Yoda) του Star Wars, καθώς ετοιμάζεται η ταινία «Mandalorian and Grogu». Από γιγαντοοθόνες στην Times Square έως κόκκινο χαλί, η αγάπη του κοινού ανανεώνεται.",
            "en": "Feature on the cultural impact of Star Wars's Grogu (Baby Yoda) as the film 'Mandalorian and Grogu' approaches. From Times Square billboards to red-carpet appearances, fan affection is renewed."
        },
        "tags": {
            "el": ["Grogu", "Star Wars", "Baby Yoda", "Mandalorian", "ποπ κουλτούρα"],
            "en": ["Grogu", "Star Wars", "Baby Yoda", "Mandalorian", "pop culture"]
        },
        "sentiment": "positive",
    },
    "149a007595c5": {
        "importance": 30,
        "summary": {
            "el": "Το ABC ανακοίνωσε spin-off του «Grey's Anatomy» σε αγροτικό ιατρικό κέντρο του Δυτικού Τέξας, με πρεμιέρα τη σεζόν 2026-2027. Στους παραγωγούς η δημιουργός Σόντα Ράιμς και η Έλεν Πομπέο.",
            "en": "ABC has greenlit a 'Grey's Anatomy' spin-off set in a rural West Texas medical center, premiering in the 2026-2027 season. Series creator Shonda Rhimes and Ellen Pompeo join as producers."
        },
        "tags": {
            "el": ["Grey's Anatomy", "spin-off", "Τέξας", "ABC", "Ράιμς"],
            "en": ["Grey's Anatomy", "spin-off", "Texas", "ABC", "Rhimes"]
        },
        "sentiment": "positive",
    },
}


THEMES = {
    "politics": {
        "el": ["Νέα κόμματα Τσίπρα & Καρυστιανού", "Γαλάζια Πατρίδα & άμυνα", "Υποκλοπές & ΕΥΠ", "ΟΠΕΚΕΠΕ"],
        "en": ["Tsipras & Karystianou new parties", "Blue Homeland & defense", "Wiretaps & EYP", "OPEKEPE"]
    },
    "economy": {
        "el": ["ΑΜΚ ΔΕΗ 4,5 δισ.", "Νέα ενεργειακή κρίση", "Χωροταξικό ΑΠΕ", "α' τρίμηνο εισηγμένων"],
        "en": ["PPC €4.5B capital raise", "New energy crisis", "Renewables spatial plan", "Q1 corporate results"]
    },
    "society": {
        "el": ["Επιχείρηση Κρήτης", "Σχολική βία", "Σκάνδαλο υδρομέτρων", "ΟΠΕΚΕΠΕ"],
        "en": ["Crete police operation", "School violence", "Water meter scandal", "OPEKEPE"]
    },
    "world": {
        "el": ["Κούβα-ΗΠΑ-Ρωσία", "Ασφάλεια Ευρώπης", "Μέση Ανατολή & Ιράν", "ΗΠΑ-Κίνα-Ταϊβάν"],
        "en": ["Cuba-US-Russia", "European security", "Middle East & Iran", "US-China-Taiwan"]
    },
    "opinion": {
        "el": ["Πολιτική αναδιάταξη", "Σχολική βία & κοινωνία", "Ελληνοαμερικανικές σχέσεις", "Παιδεία & εργασία"],
        "en": ["Political realignment", "School violence & society", "US-Greece relations", "Education & work"]
    },
    "culture": {
        "el": ["Απώλεια Καφέτση (ΕΜΣΤ)", "Ρεκόρ Παρθένη", "Λογοτεχνία (Παμούκ, Booker)", "Κινηματογράφος & τηλεόραση"],
        "en": ["Loss of Kafetsi (EMST)", "Parthenis auction record", "Literature (Pamuk, Booker)", "Cinema & TV"]
    },
}


def build_category_files(raw):
    from collections import defaultdict
    by_cat = defaultdict(list)
    for art in raw["articles"]:
        by_cat[art["category_hint"]].append(art)

    cats = ["politics", "economy", "society", "world", "opinion", "culture"]
    counts = {}
    for cat in cats:
        items = []
        for art in by_cat[cat]:
            an = ANALYSIS.get(art["id"])
            if not an:
                print(f"WARN: no analysis for {art['id']} {art['title'][:60]}", file=sys.stderr)
                continue
            items.append({
                "id": art["id"],
                "title": art["title"],
                "url": art["url"],
                "author": art.get("author", ""),
                "published": art.get("published"),
                "source": art.get("source", "Kathimerini"),
                "source_type": art.get("source_type", "scrape"),
                "category": cat,
                "importance": an["importance"],
                "content": art["content"][:2000],
                "summary": an["summary"],
                "tags": an["tags"],
                "sentiment": an["sentiment"],
            })
        # Sort by importance descending
        items.sort(key=lambda x: x["importance"], reverse=True)
        counts[cat] = len(items)
        out = {
            "date": DATE,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "category": cat,
            "item_count": len(items),
            "themes": THEMES[cat],
            "items": items,
        }
        (OUT_DIR / f"{cat}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
        print(f"Wrote {cat}.json ({len(items)} items)")
    return counts


def build_summary(raw, counts):
    total = sum(counts.values())
    exec_el = (
        "Η ημερήσια ειδησεογραφία κυριαρχείται από την επικείμενη αναδιάταξη του πολιτικού σκηνικού: ο Αλέξης Τσίπρας ανακοινώνει το νέο του κόμμα την Τρίτη 26 Μαΐου στο Θησείο, ενώ η Μαρία Καρυστιανού αναμένεται να φέρει το δικό της εγχείρημα την ίδια εβδομάδα. Στον ΣΥΡΙΖΑ επικρατεί αναμονή για το αν θα ενσωματωθεί η Κουμουνδούρου, η Κεντρική Επιτροπή συνεδριάζει στις 6 Ιουνίου, ενώ ο διαγραμμένος Παύλος Πολάκης παραμένει αγκάθι. Παράλληλα, οι υποκλοπές επανέρχονται με σκληρή σύγκρουση ΝΔ-ΠΑΣΟΚ μετά τη διαρροή του διαλόγου Ανδρουλάκη-Δεμίρη της ΕΥΠ, ενώ η Βουλή συζητά την προανακριτική για τους πρώην υπουργούς Λιβανό-Αραμπατζή για τον ΟΠΕΚΕΠΕ.\n\nΣτο εξωτερικό μέτωπο, ο Μητσοτάκης απορρίπτει στους FT τυχόν τέλη διέλευσης στο Ορμούζ ως «εκβιασμό», ενώ ο Δένδιας απαιτεί συγγνώμη από το Κίεβο για το ναυτικό drone της Λευκάδας. Η Αθήνα κρατά σταθερή στάση στο τουρκικό νομοσχέδιο «Γαλάζια Πατρίδα» και προχωρά σε αυστηρό διάβημα προς το Ισραήλ για τη συμπεριφορά του Μπεν Γκβιρ στους Έλληνες ακτιβιστές του Sumud Flotilla, που σήμερα απελαύνονται προς την Τουρκία. Διεθνώς, ο Τραμπ δηλώνει ότι θα μιλήσει με τον πρόεδρο της Ταϊβάν —άνευ προηγουμένου κίνηση— και αναγγέλλει κατηγορίες κατά του Ραούλ Κάστρο. Ο Τσέχος πρόεδρος Πάβελ προειδοποιεί από το GLOBSEC ότι «η ειρήνη στην Ευρώπη δεν είναι πλέον δεδομένη», ενώ το CNN αναφέρει ότι το Ιράν ανασυγκροτείται ταχύτερα από το αναμενόμενο.\n\nΣτην οικονομία, η ΔΕΗ ολοκλήρωσε ιστορική αύξηση μετοχικού κεφαλαίου 4,5 δισ. ευρώ με υπερκάλυψη 4,5 φορές, προσελκύοντας BlackRock, CVC και το QIA του Κατάρ — η μεγαλύτερη προσέλκυση κεφαλαίων στην ιστορία της ελληνικής κεφαλαιαγοράς. Η Κομισιόν αναθεωρεί όμως προς τα κάτω την ανάπτυξη και προβλέπει πληθωρισμό 3,7% στην Ελλάδα λόγω της νέας ενεργειακής κρίσης από τη Μέση Ανατολή. Το νέο ειδικό χωροταξικό για τις ΑΠΕ προκαλεί αντιδράσεις: απαγορεύει αιολικά σε μικρά νησιά, αλλά εξαιρεί τα ώριμα έργα δεκάδων χιλιάδων μεγαβάτ. Στις εισηγμένες, ισχυρά α' τρίμηνα από Alpha Bank (181,5 εκατ. ευρώ), Quest (+14,3%) και Briq Properties.\n\nΣτην κοινωνία, μεγάλη επιχείρηση της ΕΛ.ΑΣ. στην Κρήτη με 16 συλλήψεις σε 76 εμπλεκόμενους, με σύνδεση στο σκάνδαλο ΟΠΕΚΕΠΕ. Πόρισμα της Αρχής Διαφάνειας αποκαλύπτει στημένους διαγωνισμούς ψηφιακών υδρομέτρων με υπερκοστολόγηση 700% — η Ευρωπαϊκή Εισαγγελία ερευνά. Νέα κρούσματα σχολικής βίας σε Αμαλιάδα και Ηράκλειο επανεκκινούν τη συζήτηση για την ψυχική υγεία των ανηλίκων. Στον πολιτισμό, έφυγε σε ηλικία 71 ετών η Άννα Καφέτση, ιδρυτική διευθύντρια του ΕΜΣΤ· πίνακας του Παρθένη πωλήθηκε στο 1 εκατ. ευρώ σε δημοπρασία Bonhams, ρεκόρ για το 20ό αιώνα."
    )
    exec_en = (
        "The day's news is dominated by the imminent realignment of the Greek political landscape: Alexis Tsipras will unveil his new party on Tuesday May 26 at Theseion, while Maria Karystianou is expected to launch hers the same week. SYRIZA is in wait-and-see mode about whether part of Koumoundourou will be absorbed, its Central Committee meets on June 6, and expelled MP Pavlos Polakis remains a thorn. The wiretaps affair has also re-erupted, with a sharp ND-PASOK clash after the leak of dialogue between Androulakis and EYP chief Demiris, while Parliament debates a preliminary inquiry against former ministers Livanos and Arampatzi over the OPEKEPE farm-subsidies scandal.\n\nOn the foreign front, PM Mitsotakis tells the FT that any toll on Hormuz traffic would be 'extortion' Europe cannot accept, while Defense Minister Dendias demands an apology from Kyiv over the naval drone found off Lefkada. Athens maintains its firm line on Turkey's 'Blue Homeland' bill and lodges a strong protest to Israel over Security Minister Ben-Gvir's treatment of Greek activists on the Sumud Flotilla, who are being deported to Turkey today. Internationally, Trump says he will speak with Taiwan's president — an unprecedented move — and brings murder charges against Raul Castro. Czech president Pavel warns at GLOBSEC that 'peace in Europe can no longer be taken for granted,' and CNN reports Iran is rebuilding faster than expected.\n\nOn the economy, PPC (DEH) closed a historic €4.5B capital raise with 4.5x oversubscription, drawing in BlackRock, CVC and Qatar's QIA — the largest capital raise in Greek market history. The European Commission, however, cuts its 2026 growth forecasts and projects 3.7% inflation in Greece due to the new Middle East-driven energy crisis. The new spatial framework for renewables is contentious: it bans wind farms on small islands but exempts already-mature projects totaling tens of thousands of MW. Listed-company Q1 results are strong from Alpha Bank (€181.5M), Quest (+14.3%) and Briq Properties.\n\nIn society, a major Hellenic Police operation in Crete delivered 16 arrests in a 76-strong organized crime network linked to the OPEKEPE scandal. A National Transparency Authority report exposes rigged smart-water-meter tenders with up to 700% markups — under European Public Prosecutor investigation. Fresh school-violence incidents in Amaliada and Heraklion reopen the conversation on youth mental health. In culture, Anna Kafetsi, founding director of Greece's National Museum of Contemporary Art (EMST), has died at 71; a Parthenis painting sold for €1M at Bonhams, a record for any 20th-century Greek artwork."
    )

    top_topics = [
        {
            "name": {
                "el": "Αναδιάταξη πολιτικού σκηνικού & νέα κόμματα",
                "en": "Political realignment & new parties"
            },
            "description": {
                "el": "Σε μία εβδομάδα ξεκινούν δύο νέα κόμματα (Τσίπρα στις 26/5 στο Θησείο και Καρυστιανού), ο ΣΥΡΙΖΑ συγκαλεί την Κ.Ε. στις 6/6 και η ΝΔ-ΠΑΣΟΚ προετοιμάζονται για τη μάχη της β' θέσης.",
                "en": "Within a week two new parties enter the field (Tsipras on May 26 at Theseion, Karystianou), SYRIZA convenes its Central Committee on June 6, and ND-PASOK gear up for the battle over second place."
            },
            "related_items": ["f0d3c07b7eb6", "9a2ac094edda", "608a94d3ad4b", "c2765b7ed2ad", "42b0ebe05e03", "e69f78faf462", "103e8be3ce77", "751a8bdb81e4"],
            "importance": 84
        },
        {
            "name": {
                "el": "Υποκλοπές, ΟΠΕΚΕΠΕ & δικαιοσύνη",
                "en": "Wiretaps, OPEKEPE & justice"
            },
            "description": {
                "el": "Νέα σύγκρουση ΝΔ-ΠΑΣΟΚ μετά τη διαρροή Ανδρουλάκη-Δεμίρη (ΕΥΠ)· συζήτηση στη Βουλή για προανακριτική Λιβανού-Αραμπατζή για ΟΠΕΚΕΠΕ· επιχείρηση Κρήτης με σύνδεση σε ΟΠΕΚΕΠΕ· πόρισμα Αρχής Διαφάνειας για στημένους διαγωνισμούς υδρομέτρων.",
                "en": "Fresh ND-PASOK clash after the leaked Androulakis-Demiris (EYP) dialogue; Parliament debates a preliminary inquiry against ex-ministers Livanos and Arampatzi over OPEKEPE; the Crete police operation links to OPEKEPE; and a Transparency Authority report exposes rigged smart-water-meter tenders."
            },
            "related_items": ["5262593c8739", "45b8ca7efaf8", "6b8e6afdf1ed", "5916612d15a2", "1aa2d651b487", "12bc82695e7c"],
            "importance": 82
        },
        {
            "name": {
                "el": "Γεωπολιτική: Μέση Ανατολή, Κίνα-Ταϊβάν, Κούβα",
                "en": "Geopolitics: Middle East, China-Taiwan, Cuba"
            },
            "description": {
                "el": "Ο Μητσοτάκης απορρίπτει τυχόν διόδια στο Ορμούζ· το CNN αναφέρει ταχύτερη ανασυγκρότηση Ιράν· ο Τραμπ δηλώνει ότι θα μιλήσει με τον πρόεδρο Ταϊβάν· κατηγορίες ΗΠΑ κατά Ραούλ Κάστρο με αντιδράσεις από Κίνα και Ρωσία· Πάβελ προειδοποιεί για ασφάλεια Ευρώπης.",
                "en": "Mitsotakis rejects any Hormuz tolls; CNN reports Iran is rebuilding faster than expected; Trump says he will speak with Taiwan's president; US murder charges against Raul Castro draw Chinese and Russian objections; Czech president Pavel warns on European security."
            },
            "related_items": ["f2250965cefe", "961fb3eee67b", "d2f97de61a17", "ec8ba893abf4", "d6cd3eba6d7d", "50c22e855b5d", "5d9863b56c49", "f7d371933c5a", "2cde73bed362"],
            "importance": 80
        },
        {
            "name": {
                "el": "Οικονομία: ΑΜΚ ΔΕΗ & ενεργειακή κρίση",
                "en": "Economy: PPC capital raise & energy crisis"
            },
            "description": {
                "el": "Η ΔΕΗ άντλησε ιστορικά 4,5 δισ. ευρώ με υπερκάλυψη 4,5 φορές. Παράλληλα η Κομισιόν αναθεωρεί κάτω την ανάπτυξη και προβλέπει πληθωρισμό 3,7% στην Ελλάδα λόγω νέας ενεργειακής κρίσης από τη Μέση Ανατολή. Νέο χωροταξικό ΑΠΕ σε διαβούλευση.",
                "en": "PPC raised a historic €4.5B with 4.5x oversubscription. The European Commission cut its 2026 growth forecast and now projects 3.7% inflation in Greece due to the new Middle East-driven energy crisis. New renewables spatial framework is in public consultation."
            },
            "related_items": ["fdf0279cb8d1", "fa640e9014bd", "de578e9b89ab", "d7ffeb30c8f2", "2bf48ac82cfe", "2feb853ccbbd"],
            "importance": 78
        },
    ]

    summary = {
        "date": DATE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_note": f"Articles scraped from kathimerini.gr. {raw['article_count']} articles over 24h.",
        "executive_summary": {"el": exec_el, "en": exec_en},
        "top_topics": top_topics,
        "article_count": raw["article_count"],
        "categories": counts,
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Wrote summary.json ({raw['article_count']} total articles)")


def main():
    raw = json.loads(RAW.read_text())
    counts = build_category_files(raw)
    build_summary(raw, counts)


if __name__ == "__main__":
    main()
