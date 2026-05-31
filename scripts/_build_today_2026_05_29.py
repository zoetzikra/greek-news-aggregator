#!/usr/bin/env python3
"""Build per-category JSON + summary.json for 2026-05-29 from /tmp/collected_raw.json."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DATE = "2026-05-29"
RAW = Path("/tmp/collected_raw.json")
ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "frontend" / "static" / "data" / DATE
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Analysis records keyed by article id.
# importance 1-100; summary el+en; tags el+en; sentiment positive/negative/neutral
ANALYSIS = {
    # ===== POLITICS =====
    "11fec5d3e328": {
        "importance": 55,
        "summary": {
            "el": "Με αφορμή την έναρξη των Πανελλαδικών Εξετάσεων 2026, οι πολιτικοί αρχηγοί απηύθυναν μηνύματα στους υποψηφίους. Η υπουργός Παιδείας Σοφία Ζαχαράκη και άλλοι θεσμικοί παράγοντες ζητούν από τους μαθητές να προχωρήσουν με αυτοπεποίθηση, υπενθυμίζοντας ότι ο βαθμός δεν αντικατοπτρίζει την αξία τους.",
            "en": "As Greece's 2026 university entrance exams begin, political leaders sent messages of support to candidates. Education Minister Sofia Zacharaki and others urged students to proceed with confidence, stressing that a single grade does not define their worth."
        },
        "tags": {
            "el": ["Πανελλαδικές", "Ζαχαράκη", "παιδεία", "εξετάσεις", "νεολαία"],
            "en": ["Panhellenic exams", "Zacharaki", "education", "exams", "youth"]
        },
        "sentiment": "neutral",
    },
    "a17dc34ecc7d": {
        "importance": 78,
        "summary": {
            "el": "Στη στήλη «Θεωρείο» αναλύεται η έκθεση Τυχεροπούλου, που ήρθε στη δημοσιότητα μετά τη συζήτηση για την προανακριτική επιτροπή για τον ΟΠΕΚΕΠΕ. Το πόρισμα δείχνει ότι στις περισσότερες υποθέσεις δεν προκύπτει ζημία στα ευρωπαϊκά κονδύλια, στοιχείο που δυσκολεύει τη δίωξη. Παύλος Μαρινάκης απαίτησε συγγνώμη από την αντιπολίτευση που μιλούσε για «κυβέρνηση υποδίκων».",
            "en": "The Theoreio column examines the so-called Tycheropoulou report, made public after the OPEKEPE preliminary inquiry debate. It finds no actual EU-fund damage in most cases, weakening any potential prosecution. Government spokesman Pavlos Marinakis demanded an apology from the opposition for branding the cabinet a 'government of defendants'."
        },
        "tags": {
            "el": ["ΟΠΕΚΕΠΕ", "Θεωρείο", "Τυχεροπούλου", "Μαρινάκης", "προανακριτική"],
            "en": ["OPEKEPE", "Theoreio", "Tycheropoulou", "Marinakis", "preliminary inquiry"]
        },
        "sentiment": "negative",
    },
    "22333f9de63a": {
        "importance": 70,
        "summary": {
            "el": "Η στήλη «Εντός και Εκτός» καταγράφει τη συνάντηση Κακλαμάνη-Μπάιρ (Συμβούλιο της Ευρώπης) για την ποιότητα της ελληνικής Δημοκρατίας, και τη σύγκρουση στη Βουλή γύρω από τις μετατάξεις προσωπικού της ΕΥΠ. Σχολιάζεται και η ψυχραιμία του αντιπολιτευτικού λόγου εν μέσω εκλογικής περιόδου.",
            "en": "The 'Entos kai Ektos' column reports Speaker Kaklamanis's meeting with Council of Europe official Petra Bayr on the quality of Greek democracy, alongside the parliamentary clash over staff transfers from the EYP intelligence service. It also notes the opposition's tone in the pre-election period."
        },
        "tags": {
            "el": ["ΕΥΠ", "Κακλαμάνης", "Συμβούλιο Ευρώπης", "Βουλή", "μετατάξεις"],
            "en": ["EYP", "Kaklamanis", "Council of Europe", "Parliament", "personnel transfers"]
        },
        "sentiment": "neutral",
    },
    "d3430d6735bc": {
        "importance": 82,
        "summary": {
            "el": "Από το Gymnich της Κύπρου ο υπουργός Εξωτερικών Γιώργος Γεραπετρίτης έστειλε αυστηρό μήνυμα προς την Άγκυρα, τονίζοντας ότι η Αθήνα δεν θα αποδεχθεί καμία μορφή αναθεωρητισμού. Ζήτησε από τους Ευρωπαίους εταίρους «ενιαία, ισχυρή φωνή» απέναντι σε τέτοιες προσπάθειες σε εύθραυστο γεωπολιτικό περιβάλλον.",
            "en": "From the Gymnich foreign ministers' meeting in Cyprus, Greek FM Yiorgos Gerapetritis sent a stark message to Ankara: Athens will not tolerate any form of Turkish revisionism. He urged EU partners to speak with 'one strong voice' against such moves in a fragile geopolitical environment."
        },
        "tags": {
            "el": ["Γεραπετρίτης", "Ελληνοτουρκικά", "αναθεωρητισμός", "Gymnich", "Άγκυρα"],
            "en": ["Gerapetritis", "Greece-Turkey", "revisionism", "Gymnich", "Ankara"]
        },
        "sentiment": "negative",
    },
    "b1817b22c9bd": {
        "importance": 85,
        "summary": {
            "el": "Αντίστροφη μέτρηση για το ελληνικό διπλωματικό διάβημα προς το Κίεβο, με βάση το πόρισμα του ΓΕΕΘΑ για το ναυτικό drone που εντοπίστηκε στις 7 Μαΐου στη Λευκάδα. Ο Γιώργος Γεραπετρίτης ενημέρωσε την Κάγια Κάλας ότι το drone λειτουργούσε για λογαριασμό της Ουκρανίας.",
            "en": "Greece is finalizing a formal diplomatic démarche to Kyiv based on a Hellenic Armed Forces General Staff report on the naval drone found by fishermen off Lefkada on 7 May. FM Gerapetritis briefed EU foreign-policy chief Kaja Kallas that the drone was operated on Ukraine's behalf."
        },
        "tags": {
            "el": ["drone", "Λευκάδα", "Ουκρανία", "ΓΕΕΘΑ", "Γεραπετρίτης"],
            "en": ["drone", "Lefkada", "Ukraine", "Hellenic Armed Forces", "Gerapetritis"]
        },
        "sentiment": "negative",
    },
    "68188c7b9dcd": {
        "importance": 50,
        "summary": {
            "el": "Σχεδιαστές οπτικής επικοινωνίας και γραφίστες σχολιάζουν αισθητικά το λογότυπο του νέου κόμματος του Αλέξη Τσίπρα (ΕΛΑΣ — Ελληνική Αριστερή Συμπαράταξη), με αιχμή το γωνιώδες κόκκινο «Α» και τους συμβολισμούς που παραπέμπουν στον Εμφύλιο.",
            "en": "Designers and visual-communication experts critique the logo of Alexis Tsipras's new party (ELAS — Greek Left Coalition), focusing on the angular red 'A' and the historical Civil War connotations of the acronym."
        },
        "tags": {
            "el": ["Τσίπρας", "ΕΛΑΣ", "λογότυπο", "πολιτική επικοινωνία", "design"],
            "en": ["Tsipras", "ELAS", "logo", "political branding", "design"]
        },
        "sentiment": "neutral",
    },
    "03d580dc6c9c": {
        "importance": 80,
        "summary": {
            "el": "Διπλωματικές πηγές επιβεβαιώνουν ότι η Αθήνα ετοιμάζει επίσημο διάβημα προς το Κίεβο για το drone που εντοπίστηκε στη Λευκάδα. Ο Γιώργος Γεραπετρίτης ενημέρωσε σχετικά την Κάγια Κάλας στο περιθώριο του άτυπου συμβουλίου ΥΠΕΞ στη Λεμεσό.",
            "en": "Diplomatic sources confirm Athens is preparing a formal démarche to Kyiv over the drone found near Lefkada. FM Gerapetritis briefed EU foreign-policy chief Kaja Kallas on the margins of the informal EU foreign ministers' council in Limassol."
        },
        "tags": {
            "el": ["Κίεβο", "drone", "Λευκάδα", "Γεραπετρίτης", "Κάλας"],
            "en": ["Kyiv", "drone", "Lefkada", "Gerapetritis", "Kallas"]
        },
        "sentiment": "negative",
    },
    "ac64ce50b7df": {
        "importance": 60,
        "summary": {
            "el": "Το ΠΑΣΟΚ καταγγέλλει «εξόφθαλμη επιχείρηση χειραγώγησης» μέσω δημοσκοπήσεων που, όπως υποστηρίζει, δημοσιεύονται κατά παράβαση των κανόνων του συνδέσμου εταιρειών για να ευνοηθεί η ΝΔ. Η ανακοίνωση εντάσσεται στη σκληρή προεκλογική αντιπαράθεση.",
            "en": "PASOK accuses 'a blatant operation to manipulate public opinion' through polls released, it says, in breach of polling-industry rules and designed to favour New Democracy. The statement fits into the increasingly bitter pre-election clash."
        },
        "tags": {
            "el": ["ΠΑΣΟΚ", "δημοσκοπήσεις", "ΝΔ", "προεκλογική", "χειραγώγηση"],
            "en": ["PASOK", "polls", "New Democracy", "pre-election", "manipulation"]
        },
        "sentiment": "negative",
    },

    # ===== ECONOMY =====
    "a3828d211e6f": {
        "importance": 78,
        "summary": {
            "el": "Ανάλυση των New York Times για το πώς η Ευρώπη οδηγείται σε εμπορικό πόλεμο με την Κίνα. Η ευρωπαία διπλωμάτης Κάγια Κάλας μίλησε για «χημειοθεραπεία» που θα απαιτηθεί για να σπάσει η εξάρτηση από το Πεκίνο, καθώς οι εισαγωγές από την Κίνα αυξάνονται και η ευρωπαϊκή βιομηχανία πιέζεται.",
            "en": "NYT analysis on how Europe is sliding into a trade war with China. EU foreign-policy chief Kaja Kallas likened breaking dependence on Beijing to 'chemotherapy' — painful but necessary — as Chinese imports surge and European industry comes under growing pressure."
        },
        "tags": {
            "el": ["Κίνα", "Ε.Ε.", "εμπορικός πόλεμος", "Κάλας", "βιομηχανία"],
            "en": ["China", "EU", "trade war", "Kallas", "industry"]
        },
        "sentiment": "negative",
    },
    "d4c197640bc9": {
        "importance": 65,
        "summary": {
            "el": "Η Lidl Ελλάς εξαπολύει «πόλεμο» με τους ανταγωνιστές της στα προϊόντα ιδιωτικής ετικέτας, μέσω διαφημιστικών φυλλαδίων που δείχνουν 13,6% χαμηλότερες τιμές. Η κίνηση επαναλαμβάνεται σε περιόδους έντονης μείωσης της αγοραστικής δύναμης, όπως το 2016, το 2024 και τώρα λόγω πληθωρισμού.",
            "en": "Lidl Hellas is launching a price war on private-label groceries, with flyers showing baskets 13.6% cheaper than rivals. The tactic recurs in periods of squeezed purchasing power — 2016, 2024, and again now under inflation."
        },
        "tags": {
            "el": ["Lidl", "σούπερ μάρκετ", "ιδιωτική ετικέτα", "πληθωρισμός", "ακρίβεια"],
            "en": ["Lidl", "supermarkets", "private label", "inflation", "cost of living"]
        },
        "sentiment": "neutral",
    },
    "e4eb37a75aee": {
        "importance": 62,
        "summary": {
            "el": "Άλμα καθαρών κερδών στα 74,1 εκατ. ευρώ για τη Cenergy Holdings το πρώτο τρίμηνο του 2026, με πωλήσεις 511 εκατ. ευρώ και ανεκτέλεστο 3,3 δισ. Ο όμιλος επωφελείται από τη ζήτηση για ενεργειακές υποδομές παγκοσμίως.",
            "en": "Cenergy Holdings posted Q1 2026 net profit of €74.1m (up sharply year-on-year) on sales of €511m, with order backlog near €3.3bn. The group is benefiting from rising global demand for energy infrastructure."
        },
        "tags": {
            "el": ["Cenergy", "κέρδη", "ενέργεια", "Χρηματιστήριο", "Q1 2026"],
            "en": ["Cenergy", "earnings", "energy", "stock market", "Q1 2026"]
        },
        "sentiment": "positive",
    },
    "25b0554958f0": {
        "importance": 55,
        "summary": {
            "el": "Η Τεχνική Ολυμπιακή εντατικοποιεί εξαγορές χαρτοφυλακίων ακινήτων από τράπεζες και funds, αξιοποιώντας τη ρευστότητα 250 εκατ. ευρώ που εξασφάλισε με το Pollen Street Capital. Παράλληλα, ενισχύει την παρουσία της σε ναυτιλία και κατοικία.",
            "en": "Techniki Olympiaki is intensifying acquisitions of real-estate portfolios from banks and funds, leveraging €250m in liquidity secured with Pollen Street Capital. The group is also expanding in shipping and residential property."
        },
        "tags": {
            "el": ["Τεχνική Ολυμπιακή", "real estate", "Pollen Street", "ναυτιλία", "εξαγορές"],
            "en": ["Techniki Olympiaki", "real estate", "Pollen Street", "shipping", "acquisitions"]
        },
        "sentiment": "positive",
    },
    "edf2fcd403fd": {
        "importance": 58,
        "summary": {
            "el": "Η πορτογαλική TAP Air Portugal επιστρέφει τον Ιούλιο στην ελληνική αγορά μετά από 14 χρόνια, επαναφέροντας τη σύνδεση Αθήνας–Λισσαβώνας. Η κίνηση εντάσσεται σε ευρύτερη στρατηγική επανατοποθέτησης με προσανατολισμό προς τον Ατλαντικό.",
            "en": "TAP Air Portugal returns to Greece this July after 14 years' absence, restoring the Athens-Lisbon route. The move is part of a wider repositioning strategy aimed at transatlantic connectivity."
        },
        "tags": {
            "el": ["TAP", "Αθήνα-Λισσαβώνα", "αεροπορία", "τουρισμός", "Πορτογαλία"],
            "en": ["TAP", "Athens-Lisbon", "aviation", "tourism", "Portugal"]
        },
        "sentiment": "positive",
    },
    "7c9897917815": {
        "importance": 68,
        "summary": {
            "el": "Η Ελλάδα είναι πλέον η 11η μεγαλύτερη αγορά της Revolut διεθνώς, με πάνω από 2 εκατ. πελάτες. Η neobank βρίσκεται στην τελική ευθεία για ελληνικό IBAN, που θα της επιτρέψει είσοδο στους λογαριασμούς μισθοδοσίας.",
            "en": "Greece has become Revolut's 11th-largest market globally, with more than 2 million customers. The neobank is in the final stretch to issue Greek IBANs, opening the door to salary accounts and a broader product range locally."
        },
        "tags": {
            "el": ["Revolut", "neobank", "ελληνικό IBAN", "fintech", "τράπεζες"],
            "en": ["Revolut", "neobank", "Greek IBAN", "fintech", "banks"]
        },
        "sentiment": "positive",
    },
    "c79b2fa08cc7": {
        "importance": 72,
        "summary": {
            "el": "Ο Σύνδεσμος Ελληνικών Βιομηχανιών Τροφίμων (ΣΕΒΤ) αντιδρά στη «δαιμονοποίηση» του κλάδου για τον πληθωρισμό, υποστηρίζοντας ότι η άνοδος τιμών αφορά φρέσκα φρούτα, λαχανικά, κρέας και ψάρια — όχι τα επώνυμα τυποποιημένα προϊόντα. Χαρακτηρίζει την ακρίβεια «χειρότερο εχθρό».",
            "en": "Greece's Federation of Food Industries (SEVT) pushes back against being blamed for inflation, arguing the price hikes come from fresh produce, meat and fish — not branded packaged goods. It calls inflation the sector's 'worst enemy'."
        },
        "tags": {
            "el": ["ΣΕΒΤ", "πληθωρισμός", "ακρίβεια", "τρόφιμα", "βιομηχανία"],
            "en": ["SEVT", "inflation", "cost of living", "food", "industry"]
        },
        "sentiment": "negative",
    },
    "09cc2ac733eb": {
        "importance": 70,
        "summary": {
            "el": "Η ελληνόκτητη ποντοπόρος ναυτιλία ελέγχει τον μεγαλύτερο σε χωρητικότητα και αξία στόλο δεξαμενοπλοίων παγκοσμίως, σύμφωνα με αναλύσεις των Veson και Clarksons. Διαθέτει επίσης το μεγαλύτερο βιβλίο παραγγελιών για νεότευκτα tankers, καταγράφοντας την πιο ενεργή περίοδο ναυπηγήσεων από το 2008.",
            "en": "Greek-owned shipping leads the world both in tanker tonnage and in fleet value, per Veson and Clarksons. It also holds the largest newbuild order book for tankers, marking the most active shipbuilding period since 2008."
        },
        "tags": {
            "el": ["ναυτιλία", "tankers", "ελληνικός εφοπλισμός", "Clarksons", "ναυπηγήσεις"],
            "en": ["shipping", "tankers", "Greek shipowners", "Clarksons", "shipbuilding"]
        },
        "sentiment": "positive",
    },
    "4f424d924036": {
        "importance": 75,
        "summary": {
            "el": "Έκθεση του ΔΝΤ για τον ελληνικό χρηματοπιστωτικό τομέα: οι τράπεζες έχουν «καθαρίσει», όμως 2,9 εκατ. προβληματικά δάνεια έχουν περάσει στους servicers και συνεχίζουν να βαραίνουν την κοινωνία. Το ΔΝΤ προειδοποιεί και για την υπερσυγκέντρωση τραπεζικής χρηματοδότησης σε λίγους ομίλους.",
            "en": "An IMF financial-sector assessment finds Greek banks largely cleaned up, but 2.9 million distressed loans now sit with servicers and continue to weigh on households. The IMF also warns of over-concentrated bank lending to a handful of large corporate groups."
        },
        "tags": {
            "el": ["ΔΝΤ", "τράπεζες", "servicers", "κόκκινα δάνεια", "χρηματοπιστωτικό σύστημα"],
            "en": ["IMF", "banks", "servicers", "NPLs", "financial system"]
        },
        "sentiment": "negative",
    },
    "96a0df41ba0e": {
        "importance": 65,
        "summary": {
            "el": "Δέκα χρόνια μετά το Brexit, η Βρετανία προσπαθεί να ξανακτίσει δεσμούς με την Ε.Ε. καθώς η οικονομική ζημία (ΑΕΠ -4% τουλάχιστον) γίνεται όλο και πιο εμφανής και η κοινή γνώμη στρέφεται υπέρ της προσέγγισης. Τρία μεγάλα εμπόδια καθορίζουν τις διαπραγματεύσεις με τις Βρυξέλλες.",
            "en": "A decade after Brexit, Britain is trying to rebuild ties with the EU as the economic damage (GDP down at least 4%) becomes harder to ignore and public opinion shifts in favour of closer ties. Three major obstacles dominate the talks with Brussels."
        },
        "tags": {
            "el": ["Brexit", "Βρετανία", "Ε.Ε.", "διαπραγματεύσεις", "ΑΕΠ"],
            "en": ["Brexit", "Britain", "EU", "negotiations", "GDP"]
        },
        "sentiment": "neutral",
    },
    "bf37f05d7a7e": {
        "importance": 72,
        "summary": {
            "el": "Σε εποχή δασμών, οι κινεζικές επιχειρήσεις δεν εξάγουν πλέον μόνο προϊόντα αλλά και ολόκληρα εργοστάσια, μετακινώντας παραγωγή σε Βόρεια/Νότια Αμερική και Ανατολική Ευρώπη. Το φαινόμενο, που οι Κινέζοι ονομάζουν «chuhai», απειλεί δυτικές εταιρείες αλλά διατηρεί την κινεζική επιρροή στις διεθνείς εφοδιαστικές αλυσίδες.",
            "en": "In the tariff era, Chinese firms are exporting entire factories rather than just goods — relocating production to the Americas and Eastern Europe. Dubbed 'chuhai' ('going to sea'), the trend threatens Western incumbents while preserving China's grip on global supply chains."
        },
        "tags": {
            "el": ["Κίνα", "δασμοί", "εργοστάσια", "chuhai", "εφοδιαστική αλυσίδα"],
            "en": ["China", "tariffs", "factories", "chuhai", "supply chain"]
        },
        "sentiment": "negative",
    },

    # ===== SOCIETY =====
    "be18fea1bdcf": {
        "importance": 45,
        "summary": {
            "el": "Θλίψη στον Φενεό Κορινθίας από τον θάνατο 37χρονου διευθυντή Δημοτικού Σχολείου σε τροχαίο. Ο εκπαιδευτικός έχασε τη ζωή του στην Επαρχιακή Οδό Ορχομενού–Λίμνης, στην Αρκαδία, όταν το όχημά του ανετράπη σε ρέμα.",
            "en": "Mourning in Feneos, Corinthia after a 37-year-old primary-school headmaster died in a car crash on the Orchomenos–Limni road in Arcadia. His vehicle ran off the road and overturned into a stream."
        },
        "tags": {
            "el": ["τροχαίο", "Φενεός", "Αρκαδία", "εκπαιδευτικός", "δυστύχημα"],
            "en": ["road accident", "Feneos", "Arcadia", "teacher", "fatal crash"]
        },
        "sentiment": "negative",
    },
    "ae76e46f6772": {
        "importance": 68,
        "summary": {
            "el": "Συνέντευξη του ομότιμου καθηγητή Νομικής Απόστολου Γεωργιάδη στην «Κ» για το νέο Κληρονομικό Δίκαιο που εμπνεύστηκε. Ο εμβληματικός νομικός εξηγεί τις αλλαγές και τον λόγο της αναθεώρησης, υπογραμμίζοντας την προσαρμογή στις σύγχρονες κοινωνικές συνθήκες.",
            "en": "Interview with emeritus law professor Apostolos Georgiadis, architect of Greece's new Inheritance Law. He explains the rationale behind the overhaul and how it adapts to modern social realities."
        },
        "tags": {
            "el": ["Γεωργιάδης", "Κληρονομικό Δίκαιο", "νομική", "Ακαδημία Αθηνών", "συνέντευξη"],
            "en": ["Georgiadis", "Inheritance Law", "law", "Academy of Athens", "interview"]
        },
        "sentiment": "neutral",
    },
    "1b6416d0a1af": {
        "importance": 38,
        "summary": {
            "el": "Εργατικό ατύχημα στον Πύργο: εργάτης τραυματίστηκε κατά τη διάρκεια εργασιών ανακαίνισης κατοικίας στην οδό Εθνικής Αντιστάσεως, όταν καταπλακώθηκε από τμήμα τοίχου. Μεταφέρθηκε στο νοσοκομείο σε καλή κατάσταση.",
            "en": "Work-site accident in Pyrgos: a labourer was injured during a home renovation when part of a wall fell on him. He was taken to hospital in stable condition."
        },
        "tags": {
            "el": ["εργατικό ατύχημα", "Πύργος", "ασφάλεια εργασίας", "ΕΚΑΒ", "ανακαίνιση"],
            "en": ["workplace accident", "Pyrgos", "occupational safety", "EKAV", "renovation"]
        },
        "sentiment": "negative",
    },
    "f769655513b2": {
        "importance": 60,
        "summary": {
            "el": "Σε ύφεση η συρροή κρουσμάτων γαστρεντερίτιδας στο νοσοκομείο «Αττικόν», σύμφωνα με ανακοίνωση της διοίκησης και της Επιτροπής Νοσοκομειακών Λοιμώξεων. Πέντε νέα κρούσματα 25–28/5, ασθενείς σε απομόνωση και ασυμπτωματικοί. Τα μέτρα από 26/5 παραμένουν σε ισχύ.",
            "en": "Attikon hospital reports the gastroenteritis cluster is subsiding: five new cases between 25–28 May, all isolated and asymptomatic. Infection-control measures imposed on 26 May remain in force."
        },
        "tags": {
            "el": ["Αττικόν", "γαστρεντερίτιδα", "νοσοκομεία", "λοιμώξεις", "δημόσια υγεία"],
            "en": ["Attikon", "gastroenteritis", "hospitals", "infections", "public health"]
        },
        "sentiment": "neutral",
    },
    "a0500a12a1ff": {
        "importance": 78,
        "summary": {
            "el": "Σοβαρό περιστατικό ενδοσχολικής βίας στην Κέρκυρα: 12χρονος μεταφέρθηκε στο νοσοκομείο μετά από άγρια επίθεση συμμαθητών στο σχολικό περιβάλλον, καταγγέλλει ο πατέρας. Η διευθύντρια και ο υποδιευθυντής συνελήφθησαν στο πλαίσιο της αυτόφωρης διαδικασίας μετά τη μήνυση κατά εκπαιδευτικών και γονέων.",
            "en": "Serious case of school bullying in Corfu: a 12-year-old was hospitalised after being violently attacked by classmates at school, his father says. The headmistress and deputy were arrested in expedited proceedings following a complaint against teachers and parents."
        },
        "tags": {
            "el": ["ενδοσχολική βία", "Κέρκυρα", "bullying", "ανήλικοι", "σχολείο"],
            "en": ["school bullying", "Corfu", "bullying", "minors", "school"]
        },
        "sentiment": "negative",
    },
    "79afade6af8e": {
        "importance": 72,
        "summary": {
            "el": "Ξεκίνησαν την Παρασκευή 29 Μαΐου 2026 οι Πανελλαδικές Εξετάσεις με το μάθημα της Νεοελληνικής Γλώσσας και Λογοτεχνίας. Οι υποψήφιοι διεκδικούν 68.788 θέσεις της Τριτοβάθμιας Εκπαίδευσης. Τα κείμενα αφορούσαν τη σύγχρονη κρίση μοναξιάς, και τα νιάτα και τα γεράματα.",
            "en": "Greece's 2026 Panhellenic university entrance exams began on Friday 29 May with Modern Greek Language and Literature. Candidates are competing for 68,788 university places. The exam texts dealt with the contemporary loneliness crisis and on youth and old age."
        },
        "tags": {
            "el": ["Πανελλαδικές", "Νεοελληνική Γλώσσα", "εξετάσεις", "παιδεία", "υποψήφιοι"],
            "en": ["Panhellenic exams", "Modern Greek", "exams", "education", "candidates"]
        },
        "sentiment": "neutral",
    },
    "50a97f820d58": {
        "importance": 30,
        "summary": {
            "el": "Τροχαίο στο κέντρο της Θεσσαλονίκης, στη συμβολή Τσιμισκή και Βενιζέλου: ταξί συγκρούστηκε με Ι.Χ., με μόνο υλικές ζημιές. Οι δύο οδηγοί δεν τραυματίστηκαν.",
            "en": "Traffic accident in central Thessaloniki at Tsimiski/Venizelou junction: a taxi collided with a private car, causing only material damage. Both drivers were unharmed."
        },
        "tags": {
            "el": ["τροχαίο", "Θεσσαλονίκη", "Τσιμισκή", "ταξί", "ατύχημα"],
            "en": ["traffic accident", "Thessaloniki", "Tsimiski", "taxi", "crash"]
        },
        "sentiment": "neutral",
    },
    "6bb055abc614": {
        "importance": 70,
        "summary": {
            "el": "Άνοιξε η ηλεκτρονική πλατφόρμα Α21 για το Επίδομα Παιδιού 2026, με προθεσμία υποβολής αιτήσεων μέχρι 10 Ιουλίου στις 18.00. Οι δικαιούχοι υποβάλλουν αίτηση μέσω ΙΔΙΚΑ ή ΟΠΕΚΑ με τους κωδικούς Taxisnet, και το ποσό υπολογίζεται βάσει εξαρτώμενων τέκνων.",
            "en": "Greece's A21 child-benefit portal for 2026 is open, with applications due by 18:00 on 10 July. Beneficiaries apply via the IDIKA or OPEKA platform using Taxisnet credentials; the amount depends on dependent children."
        },
        "tags": {
            "el": ["Επίδομα Παιδιού", "Α21", "ΟΠΕΚΑ", "Taxisnet", "οικογένεια"],
            "en": ["child benefit", "A21", "OPEKA", "Taxisnet", "family"]
        },
        "sentiment": "positive",
    },
    "285a79868168": {
        "importance": 35,
        "summary": {
            "el": "Φωτιά τα ξημερώματα σε βιοτεχνία παραγωγής σφολιατοειδών στον Κρουσώνα Ηρακλείου Κρήτης. Στην επιχείρηση έσπευσαν τέσσερα πυροσβεστικά οχήματα με 12 πυροσβέστες, που έθεσαν τη φωτιά υπό έλεγχο. Δεν υπήρξαν τραυματισμοί.",
            "en": "Pre-dawn fire at a pastry factory in Krousonas, Heraklion, Crete. Four fire engines with 12 firefighters brought the blaze under control. No injuries reported."
        },
        "tags": {
            "el": ["φωτιά", "Κρήτη", "Ηράκλειο", "Πυροσβεστική", "βιοτεχνία"],
            "en": ["fire", "Crete", "Heraklion", "fire service", "factory"]
        },
        "sentiment": "negative",
    },
    "4473684a2ffe": {
        "importance": 72,
        "summary": {
            "el": "Σοβαρή καταγγελία στη Θεσσαλονίκη: εργαζόμενοι σε κέντρο φροντίδας ΑμεΑ φέρεται να ξέχασαν 17χρονη μέσα σε λεωφορείο για δύο ώρες. Η μητέρα της υπέβαλε έγκληση στο Τμήμα Δίωξης και Εξιχνίασης Εγκλημάτων Θερμαϊκού· διενεργείται έρευνα.",
            "en": "Disturbing complaint in Thessaloniki: staff at a day-care centre for people with disabilities allegedly left a 17-year-old girl on the bus for two hours. The mother filed criminal charges; police are investigating."
        },
        "tags": {
            "el": ["ΑμεΑ", "Θεσσαλονίκη", "καταγγελία", "παραμέληση", "ανήλικη"],
            "en": ["disability care", "Thessaloniki", "complaint", "neglect", "minor"]
        },
        "sentiment": "negative",
    },
    "4cdc26a5de85": {
        "importance": 80,
        "summary": {
            "el": "Νέα επιχείρηση διάσωσης μεταναστών νότια της Γαύδου: 36 άτομα εντοπίστηκαν σε λέμβο 10 ν.μ. νότια του νησιού και μεταφέρθηκαν στο λιμάνι. Μία ημέρα νωρίτερα είχαν περισυλλεγεί τουλάχιστον 610 άτομα νότια Κρήτης και Γαύδου, σημάδι αυξημένων μεταναστευτικών ροών στην περιοχή.",
            "en": "Fresh migrant-rescue operation south of Gavdos: 36 people were located in a boat 10 nautical miles south of the island and brought ashore. A day earlier at least 610 had been rescued south of Crete and Gavdos — a sign of intensifying migration flows in the area."
        },
        "tags": {
            "el": ["μεταναστευτικό", "Γαύδος", "Κρήτη", "Λιμενικό", "διάσωση"],
            "en": ["migration", "Gavdos", "Crete", "Coast Guard", "rescue"]
        },
        "sentiment": "negative",
    },
    "88a559ba553e": {
        "importance": 28,
        "summary": {
            "el": "Πυρκαγιά σε προαύλιο χώρο επιχείρησης στο Ωραιόκαστρο Θεσσαλονίκης κατασβέστηκε από 13 πυροσβέστες με 5 οχήματα. Έκαψε ξερά χόρτα και απορρίμματα.",
            "en": "A yard fire at a business in Oraiokastro, Thessaloniki was extinguished by 13 firefighters with 5 vehicles. It burned only dry grass and rubbish."
        },
        "tags": {
            "el": ["φωτιά", "Θεσσαλονίκη", "Ωραιόκαστρο", "Πυροσβεστική", "εμπρησμός"],
            "en": ["fire", "Thessaloniki", "Oraiokastro", "fire service", "blaze"]
        },
        "sentiment": "negative",
    },

    # ===== WORLD =====
    "ab5dbcf5d9a8": {
        "importance": 82,
        "summary": {
            "el": "Ο νέος ούγγρος πρωθυπουργός Πέτερ Μάγιαρ φτάνει στις Βρυξέλλες για κρίσιμες συνομιλίες με την Ούρσουλα φον ντερ Λάιεν, με στόχο την ξεκλείδωση δισεκατομμυρίων ευρωπαϊκών κονδυλίων μετά τα χρόνια του Ορμπάν. Το μάθημα της Πολωνίας λειτουργεί ως «πυξίδα» για την Ουγγαρία.",
            "en": "Hungary's new PM Péter Magyar arrives in Brussels for crucial talks with Commission President Ursula von der Leyen, aiming to unlock billions in EU funds frozen during the Orbán years. Poland's recent path serves as a roadmap."
        },
        "tags": {
            "el": ["Ουγγαρία", "Μάγιαρ", "Ε.Ε.", "Ορμπάν", "Πολωνία"],
            "en": ["Hungary", "Magyar", "EU", "Orbán", "Poland"]
        },
        "sentiment": "positive",
    },
    "ad8af45b292d": {
        "importance": 85,
        "summary": {
            "el": "Η Ρουμανία επισπεύδει υπογραφές για αντι-drone άμυνα στο πλαίσιο του προγράμματος SAFE της Ε.Ε., αφού ρωσικό drone έπληξε πολυκατοικία στη χώρα. Ο πρόεδρος Νικούσορ Νταν δηλώνει ότι «δεν θα δεχτούμε να μεταφερθεί ο πόλεμος της Ρωσίας στους πολίτες μας».",
            "en": "Romania is fast-tracking anti-drone procurement contracts under the EU's SAFE programme after a Russian drone struck a residential building in the country. President Nicușor Dan: 'We will not accept Russia's war being carried over to our citizens.'"
        },
        "tags": {
            "el": ["Ρουμανία", "drone", "Ρωσία", "SAFE", "ΝΑΤΟ"],
            "en": ["Romania", "drone", "Russia", "SAFE", "NATO"]
        },
        "sentiment": "negative",
    },
    "d3c78d8b1935": {
        "importance": 58,
        "summary": {
            "el": "Η Κίνα παραμένει «πατρίδα των θεριακλήδων»: παγκοσμίως το κάπνισμα μειώνεται, στην Κίνα όμως αυξήθηκε 39% μεταξύ 2003 και 2023, με 2,4 τρισ. τσιγάρα ετησίως — σχεδόν το μισό παγκόσμιο. Η Κρατική Διοίκηση Μονοπωλίου Καπνού φρενάρει τη μείωση.",
            "en": "China remains the world's smoking capital: global cigarette use is falling but China's rose 39% between 2003 and 2023, selling 2.4 trillion cigarettes a year — nearly half of the world's total. The State Tobacco Monopoly stymies anti-smoking efforts."
        },
        "tags": {
            "el": ["Κίνα", "κάπνισμα", "δημόσια υγεία", "μονοπώλιο", "τσιγάρα"],
            "en": ["China", "smoking", "public health", "monopoly", "cigarettes"]
        },
        "sentiment": "negative",
    },
    "2db1c0e7774b": {
        "importance": 35,
        "summary": {
            "el": "Πρωτοφανής απόφαση για τους οπαδούς της Νις πριν τον αγώνα μπαράζ Ligue 1 με τη Σεντ Ετιέν: ο νομάρχης Λοράν Χοτιό περιορίζει την παρουσία τους σε συγκεκριμένες ζώνες, αν και το παιχνίδι ήδη διεξάγεται κεκλεισμένων των θυρών στο «Allianz Riviera».",
            "en": "Unprecedented order against Nice fans before the Ligue 1 relegation play-off vs Saint-Étienne: prefect Laurent Hottiaux restricts their movement to specific zones, even though the match is already to be played behind closed doors at the Allianz Riviera."
        },
        "tags": {
            "el": ["Νις", "Σεντ Ετιέν", "Ligue 1", "οπαδοί", "ασφάλεια"],
            "en": ["Nice", "Saint-Étienne", "Ligue 1", "fans", "security"]
        },
        "sentiment": "neutral",
    },
    "49feaa67f0eb": {
        "importance": 80,
        "summary": {
            "el": "Ρωσικά drones χτύπησαν τρία πλοία ξένης σημαίας στη Μαύρη Θάλασσα τη νύχτα της Πέμπτης προς Παρασκευή. Από τα χτυπήματα ξέσπασε φωτιά στα πλοία· μεταξύ τους και φορτηγό σημαίας Βανουάτου που ταξίδευε από Οδησσό προς Τουρκία. Η Ουκρανία καταγγέλλει ευθεία επίθεση κατά διεθνούς ναυτιλίας.",
            "en": "Russian drones struck three foreign-flagged ships in the Black Sea overnight Thursday-Friday, setting fires aboard all three. Among them was a Vanuatu-flagged cargo ship sailing from Odesa to Turkey. Ukraine denounces a direct attack on international shipping."
        },
        "tags": {
            "el": ["Ουκρανία", "Ρωσία", "drones", "Μαύρη Θάλασσα", "ναυτιλία"],
            "en": ["Ukraine", "Russia", "drones", "Black Sea", "shipping"]
        },
        "sentiment": "negative",
    },
    "435ce7a9645a": {
        "importance": 78,
        "summary": {
            "el": "Σχέδιο επέκτασης της εκεχειρίας ΗΠΑ-Ιράν είναι έτοιμο και περιμένει την έγκριση του Ντόναλντ Τραμπ, αναφέρει το Axios. Ο αντιπρόεδρος Τζέι Ντι Βανς δήλωσε ότι ο πρόεδρος δεν είναι ακόμη «έτοιμος» να υπογράψει. Σήμερα Μάρκο Ρούμπιο θα συναντηθεί με τον Πακιστανό ΥΠΕΞ στην Ουάσινγκτον.",
            "en": "A plan to extend the US-Iran ceasefire is ready and awaits Donald Trump's sign-off, Axios reports. VP JD Vance said the president is not 'ready' to sign yet. Secretary of State Marco Rubio is meeting Pakistan's foreign minister in Washington today."
        },
        "tags": {
            "el": ["Μέση Ανατολή", "ΗΠΑ", "Ιράν", "Τραμπ", "εκεχειρία"],
            "en": ["Middle East", "USA", "Iran", "Trump", "ceasefire"]
        },
        "sentiment": "neutral",
    },
    "5e68335c4302": {
        "importance": 88,
        "summary": {
            "el": "Ρωσικό drone έπληξε πολυκατοικία στην πόλη Γκαλάτσι της Ρουμανίας, κοντά στα σύνορα με την Ουκρανία, προκαλώντας δύο ελαφρείς τραυματισμούς. Η Ρουμανία ζήτησε βοήθεια από το ΝΑΤΟ και κατήγγειλε τη Μόσχα· έντονη αντίδραση και από Βρυξέλλες/ΝΑΤΟ.",
            "en": "A Russian drone hit a residential building in Galați, Romania near the Ukrainian border, lightly injuring two people. Bucharest requested NATO assistance and denounced Moscow; sharp responses also from Brussels and NATO."
        },
        "tags": {
            "el": ["Ρουμανία", "drone", "Ρωσία", "Γκαλάτσι", "ΝΑΤΟ"],
            "en": ["Romania", "drone", "Russia", "Galați", "NATO"]
        },
        "sentiment": "negative",
    },
    "32cd459e060e": {
        "importance": 65,
        "summary": {
            "el": "Στους οκτώ αυξήθηκαν οι νεκροί από το βιομηχανικό δυστύχημα της Τρίτης στην Ουάσιγκτον, όταν έσπασε δεξαμενή χημικής ουσίας στη Nippon Dynawave Packaging στο Λόνγκβιου. Έξι ακόμη θάνατοι επιβεβαιώθηκαν την Πέμπτη.",
            "en": "The death toll from Tuesday's industrial accident in Washington state has risen to eight, after a chemical tank ruptured at Nippon Dynawave Packaging in Longview. Six more deaths were confirmed on Thursday."
        },
        "tags": {
            "el": ["ΗΠΑ", "Ουάσιγκτον", "βιομηχανικό", "Nippon Dynawave", "χημικά"],
            "en": ["USA", "Washington", "industrial", "Nippon Dynawave", "chemicals"]
        },
        "sentiment": "negative",
    },
    "4ef924b036b1": {
        "importance": 70,
        "summary": {
            "el": "Πύραυλος της Blue Origin εξερράγη κατά τη διάρκεια δοκιμής στη βάση εκτόξευσης του Ακρωτηρίου Κανάβεραλ στη Φλόριντα, περίπου στις 21:00 τοπική ώρα. Η εταιρεία του Τζεφ Μπέζος αναφέρει ότι το προσωπικό είναι ασφαλές και δεν υπήρξε απειλή για το κοινό.",
            "en": "A Blue Origin rocket exploded during a test on the launchpad at Cape Canaveral, Florida, around 21:00 local time. Jeff Bezos's company says all personnel are safe and there was no public threat."
        },
        "tags": {
            "el": ["Blue Origin", "Φλόριντα", "πύραυλος", "Μπέζος", "διαστημικά"],
            "en": ["Blue Origin", "Florida", "rocket", "Bezos", "space"]
        },
        "sentiment": "negative",
    },
    "ffac5dea1818": {
        "importance": 62,
        "summary": {
            "el": "Νέο ρεκόρ ζέστης για τον Μάιο στην Πορτογαλία: 40,3 βαθμοί Κελσίου στη Μόρα — ξεπερνώντας το προηγούμενο ρεκόρ 40 βαθμών του Μαΐου 2001. Η χώρα και μεγάλο τμήμα της Ευρώπης πλήττονται από πρώιμο κύμα ζέστης.",
            "en": "Portugal set a new May heat record of 40.3°C in Mora, beating the previous 40°C reached in May 2001. The country and much of Europe are gripped by an early heatwave."
        },
        "tags": {
            "el": ["Πορτογαλία", "ρεκόρ ζέστης", "κλιματική αλλαγή", "καύσωνας", "Μάιος"],
            "en": ["Portugal", "heat record", "climate change", "heatwave", "May"]
        },
        "sentiment": "negative",
    },
    "6c5573863981": {
        "importance": 75,
        "summary": {
            "el": "Ο πληθυσμός της Ιαπωνίας συρρικνώθηκε κατά 2,5% σε πέντε χρόνια, στα 123 εκατομμύρια το 2025 — αρνητικό ρεκόρ από το 1920. Η μείωση είναι τριπλάσια από την προηγούμενη πενταετία και αναδεικνύει την οξύτητα της δημογραφικής κρίσης για την τέταρτη οικονομία του κόσμου.",
            "en": "Japan's population shrank 2.5% in five years to 123 million in 2025 — the steepest decline since the census began in 1920, triple the prior five-year drop. The figures underscore the demographic crisis confronting the world's fourth-largest economy."
        },
        "tags": {
            "el": ["Ιαπωνία", "δημογραφικό", "πληθυσμός", "γήρανση", "απογραφή"],
            "en": ["Japan", "demographics", "population", "ageing", "census"]
        },
        "sentiment": "negative",
    },
}


def main():
    raw = json.loads(RAW.read_text(encoding="utf-8"))
    articles = raw["articles"]

    # Group by category, applying analysis
    by_cat: dict[str, list[dict]] = {
        "politics": [], "economy": [], "society": [],
        "world": [], "opinion": [], "culture": [],
    }
    for a in articles:
        cat = a.get("category_hint", "society")
        if cat not in by_cat:
            cat = "society"
        analysis = ANALYSIS.get(a["id"])
        if not analysis:
            # Default minimal analysis
            analysis = {
                "importance": 40,
                "summary": {"el": a.get("snippet", "")[:300], "en": ""},
                "tags": {"el": [], "en": []},
                "sentiment": "neutral",
            }
        item = {
            "id": a["id"],
            "title": a["title"],
            "url": a["url"],
            "author": a.get("author", ""),
            "published": a.get("published"),
            "source": a.get("source", "Kathimerini"),
            "source_type": a.get("source_type", "scrape"),
            "category": cat,
            "importance": analysis["importance"],
            "content": (a.get("content") or "")[:2000],
            "summary": analysis["summary"],
            "tags": analysis["tags"],
            "sentiment": analysis["sentiment"],
        }
        by_cat[cat].append(item)

    # Per-category themes (manually curated per the day's articles)
    themes_by_cat = {
        "politics": {
            "el": ["Ελληνοτουρκικά / drone Λευκάδας", "Πανελλαδικές 2026", "Νέο κόμμα Τσίπρα (ΕΛΑΣ)"],
            "en": ["Greece-Turkey / Lefkada drone affair", "Panhellenic exams 2026", "Tsipras's new ELAS party"],
        },
        "economy": {
            "el": ["Εμπορική ένταση Ε.Ε.-Κίνας", "Πληθωρισμός & ακρίβεια", "Επιστροφή της ναυτιλίας"],
            "en": ["EU-China trade tensions", "Inflation and cost of living", "Greek shipping leadership"],
        },
        "society": {
            "el": ["Πανελλαδικές 2026", "Ενδοσχολική βία και ΑμεΑ", "Μεταναστευτικές ροές νότια Κρήτης"],
            "en": ["Panhellenic exams 2026", "School violence and disability-care neglect", "Migration flows south of Crete"],
        },
        "world": {
            "el": ["Ρωσικά drones πλήττουν ΝΑΤΟ-Ρουμανία", "Διεθνής διπλωματία (Μ. Ανατολή, Ουγγαρία, Βρετανία)", "Δημογραφικό Ιαπωνίας / κλίμα Πορτογαλίας"],
            "en": ["Russian drones strike NATO Romania", "Diplomacy (Middle East, Hungary, UK)", "Japan demographics / Portugal heatwave"],
        },
        "opinion": {"el": [], "en": []},
        "culture": {"el": [], "en": []},
    }

    # Write per-category JSON files
    now_iso = datetime.now(timezone.utc).isoformat()
    for cat, items in by_cat.items():
        # Sort by importance desc
        items.sort(key=lambda x: x.get("importance", 0), reverse=True)
        cat_file = OUT_DIR / f"{cat}.json"
        payload = {
            "date": DATE,
            "generated_at": now_iso,
            "category": cat,
            "item_count": len(items),
            "themes": themes_by_cat.get(cat, {"el": [], "en": []}),
            "items": items,
        }
        cat_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {cat_file.name}: {len(items)} items", file=sys.stderr)

    # Build summary.json
    # categories shape: {cat: {item_count, top_items: [{id, title, importance}]}}
    categories_summary = {}
    for cat in ["politics", "economy", "society", "world", "opinion", "culture"]:
        items = sorted(by_cat[cat], key=lambda x: x.get("importance", 0), reverse=True)
        top_items = [
            {"id": it["id"], "title": it["title"], "importance": it["importance"]}
            for it in items[:5]
        ]
        categories_summary[cat] = {
            "item_count": len(by_cat[cat]),
            "top_items": top_items,
        }

    # Top topics for the day
    top_topics = [
        {
            "name": {
                "el": "Ρωσικά drones πλήττουν τη Ρουμανία — κλιμάκωση στη Μαύρη Θάλασσα",
                "en": "Russian drones hit Romania — Black Sea escalation",
            },
            "description": {
                "el": "Ρωσικό drone έπληξε πολυκατοικία στη Γκαλάτσι της Ρουμανίας τραυματίζοντας δύο πολίτες, ενώ άλλα drones χτύπησαν τρία πλοία ξένης σημαίας στη Μαύρη Θάλασσα. Το Βουκουρέστι ζητά βοήθεια από το ΝΑΤΟ και επισπεύδει αντι-drone συμβάσεις μέσω του ευρωπαϊκού προγράμματος SAFE, ενώ ο πρόεδρος Νταν προειδοποιεί ότι «δεν θα δεχτούμε να μεταφερθεί ο πόλεμος της Ρωσίας στους πολίτες μας».",
                "en": "A Russian drone struck a residential building in Galați, Romania, lightly injuring two civilians, while other drones hit three foreign-flagged ships in the Black Sea overnight. Bucharest is calling on NATO and accelerating anti-drone contracts via the EU's SAFE programme; President Dan warns Romania will not accept Russia's war 'being carried over to our citizens'.",
            },
            "related_items": ["5e68335c4302", "ad8af45b292d", "49feaa67f0eb"],
            "importance": 90,
        },
        {
            "name": {
                "el": "Ελληνοτουρκικά και διάβημα προς το Κίεβο για το drone της Λευκάδας",
                "en": "Greece-Turkey tensions and démarche to Kyiv over Lefkada drone",
            },
            "description": {
                "el": "Ο Γιώργος Γεραπετρίτης από το Gymnich της Κύπρου στέλνει σαφές μήνυμα στην Άγκυρα ότι η Αθήνα δεν θα ανεχθεί αναθεωρητισμό, ζητώντας «ενιαία, ισχυρή φωνή» από τους εταίρους. Ταυτόχρονα, ολοκληρώνεται διπλωματικό διάβημα προς το Κίεβο για το ναυτικό drone που εντοπίστηκε τον Μάιο στη Λευκάδα, με βάση πόρισμα ΓΕΕΘΑ που το συνδέει με ουκρανική επιχείρηση.",
                "en": "FM Gerapetritis at the EU Gymnich in Cyprus sent a stark message to Ankara that Athens will not accept revisionism, calling for a 'unified, strong voice' from EU partners. In parallel, Greece is finalising a démarche to Kyiv over the naval drone found in May off Lefkada, based on a General Staff report linking it to a Ukrainian operation.",
            },
            "related_items": ["d3430d6735bc", "b1817b22c9bd", "03d580dc6c9c"],
            "importance": 86,
        },
        {
            "name": {
                "el": "Πανελλαδικές Εξετάσεις 2026",
                "en": "Panhellenic university entrance exams 2026",
            },
            "description": {
                "el": "Ξεκίνησαν την Παρασκευή 29 Μαΐου οι Πανελλαδικές για τους υποψηφίους των Γενικών Λυκείων, με 68.788 θέσεις στην Τριτοβάθμια. Πρώτο μάθημα η Νεοελληνική Γλώσσα και Λογοτεχνία· τα κείμενα αφορούσαν την κρίση μοναξιάς και την αντίθεση νιάτων–γεραμάτων. Πολιτικοί αρχηγοί και η υπουργός Παιδείας Σοφία Ζαχαράκη απηύθυναν μηνύματα στους υποψηφίους.",
                "en": "Greece's 2026 Panhellenic exams opened on Friday 29 May, with 68,788 university places at stake. The first exam, Modern Greek Language and Literature, dealt with the contemporary loneliness crisis and the contrast between youth and old age. Political leaders and Education Minister Sofia Zacharaki sent messages of support.",
            },
            "related_items": ["79afade6af8e", "11fec5d3e328"],
            "importance": 75,
        },
        {
            "name": {
                "el": "Ευρωπαϊκή οικονομία υπό πίεση: Κίνα, πληθωρισμός, Brexit",
                "en": "European economy under strain: China, inflation, Brexit",
            },
            "description": {
                "el": "Η Ευρώπη οδηγείται σε εμπορικό πόλεμο με την Κίνα: η Κάγια Κάλας μίλησε για «χημειοθεραπεία» για να σπάσει η εξάρτηση, ενώ κινεζικές επιχειρήσεις «εξάγουν» τώρα ολόκληρα εργοστάσια («chuhai»). Στο εσωτερικό, ο ΣΕΒΤ χαρακτηρίζει την ακρίβεια «χειρότερο εχθρό» και η Lidl ανοίγει πόλεμο τιμών. Παράλληλα, η Βρετανία ξανακτίζει δεσμούς με την Ε.Ε. 10 χρόνια μετά το Brexit, με το ΑΕΠ μειωμένο κατά τουλάχιστον 4%.",
                "en": "Europe is sliding into a trade war with China: EU's Kaja Kallas likens breaking dependence to 'chemotherapy', while Chinese firms now relocate entire factories ('chuhai'). At home, Greece's food industry calls inflation its 'worst enemy' and Lidl launches a price war. Meanwhile, Britain is rebuilding ties with the EU a decade after Brexit, with GDP down at least 4%.",
            },
            "related_items": ["a3828d211e6f", "bf37f05d7a7e", "c79b2fa08cc7", "d4c197640bc9", "96a0df41ba0e"],
            "importance": 80,
        },
    ]

    article_count = sum(len(v) for v in by_cat.values())
    summary = {
        "date": DATE,
        "generated_at": now_iso,
        "source_note": f"Articles scraped from kathimerini.gr. {article_count} articles over 24h.",
        "executive_summary": {
            "el": (
                "Η ημέρα κυριαρχείται από την κλιμάκωση στη Μαύρη Θάλασσα: ρωσικά drones έπληξαν "
                "πολυκατοικία στη Γκαλάτσι της Ρουμανίας και τρία πλοία ξένης σημαίας στη θάλασσα, "
                "ωθώντας το Βουκουρέστι να ζητήσει βοήθεια από το ΝΑΤΟ και να επιταχύνει την αντι-drone "
                "προμήθεια μέσω του ευρωπαϊκού SAFE. Σε διπλωματικό επίπεδο, ο υπουργός Εξωτερικών "
                "Γιώργος Γεραπετρίτης από το Gymnich της Κύπρου έστειλε ισχυρό μήνυμα προς την Άγκυρα "
                "κατά του αναθεωρητισμού και επιταχύνει διάβημα προς το Κίεβο για το ναυτικό drone της "
                "Λευκάδας.\n\n"
                "Στο εσωτερικό, η σημαντικότερη είδηση κοινωνικού ενδιαφέροντος είναι η έναρξη των "
                "Πανελλαδικών Εξετάσεων 2026, με 68.788 θέσεις και πρώτο μάθημα τη Νεοελληνική Γλώσσα. "
                "Παράλληλα συγκλονίζουν περιστατικά ενδοσχολικής βίας στην Κέρκυρα και παραμέλησης σε "
                "δομή ΑμεΑ στη Θεσσαλονίκη, ενώ συνεχίζονται οι εντονότατες μεταναστευτικές ροές νότια "
                "Κρήτης και Γαύδου.\n\n"
                "Στην οικονομία, οι ευρωπαϊκές πιέσεις εντείνονται: η Ε.Ε. οδηγείται σε εμπορικό πόλεμο "
                "με την Κίνα, καθώς η Κάγια Κάλας μιλά για «χημειοθεραπεία» στην εξάρτηση και κινεζικές "
                "εταιρείες «εξάγουν» πλέον εργοστάσια. Ο ΣΕΒΤ χαρακτηρίζει την ακρίβεια «χειρότερο εχθρό», "
                "η Lidl ξεκινά πόλεμο τιμών στα προϊόντα ιδιωτικής ετικέτας, και το ΔΝΤ καμπανίζει για 2,9 "
                "εκατ. προβληματικά δάνεια στους servicers. Θετικά νέα από τη ναυτιλία (ελληνική "
                "πρωτοκαθεδρία στα tankers), τα Q1 της Cenergy και την επιστροφή της TAP στην Αθήνα.\n\n"
                "Στον κόσμο, η Πορτογαλία σπάει το ρεκόρ ζέστης Μαΐου με 40,3°C, η Ιαπωνία βλέπει "
                "δημογραφικό αρνητικό ρεκόρ και πύραυλος της Blue Origin εξερράγη στη Φλόριντα."
            ),
            "en": (
                "The day is dominated by escalation in the Black Sea: Russian drones struck a residential "
                "building in Galați, Romania and three foreign-flagged ships at sea, prompting Bucharest "
                "to call on NATO and accelerate anti-drone procurement via the EU's SAFE programme. "
                "Diplomatically, Greek FM Yiorgos Gerapetritis at the EU Gymnich in Cyprus sent a stark "
                "message to Ankara against revisionism, and is finalising a démarche to Kyiv over the "
                "naval drone found in May off Lefkada.\n\n"
                "Domestically, the headline social story is the start of the 2026 Panhellenic university "
                "entrance exams, with 68,788 places at stake and Modern Greek Language as the opening "
                "subject. Two disturbing cases dominate the social agenda: school violence in Corfu that "
                "hospitalised a 12-year-old, and neglect at a Thessaloniki disability-care centre where "
                "a 17-year-old was left on a bus. Migration flows south of Crete and Gavdos remain "
                "elevated.\n\n"
                "On the economy, European pressures intensify: the EU is sliding into a trade war with "
                "China — Kaja Kallas likens breaking dependence to 'chemotherapy' while Chinese firms "
                "now export entire factories ('chuhai'). Greece's food industry federation (SEVT) calls "
                "inflation its 'worst enemy', Lidl launches a private-label price war, and the IMF flags "
                "2.9 million distressed loans still sitting with servicers. Brighter spots: Greek shipping "
                "leads the world in tankers, Cenergy posts strong Q1 results, and TAP Portugal returns to "
                "Athens after 14 years.\n\n"
                "Internationally, Portugal sets a 40.3°C May heat record, Japan records its sharpest "
                "five-year demographic decline, and a Blue Origin rocket explodes during a Cape Canaveral test."
            ),
        },
        "top_topics": top_topics,
        "article_count": article_count,
        "categories": categories_summary,
    }

    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Wrote summary.json: {article_count} total articles", file=sys.stderr)


if __name__ == "__main__":
    main()
