#!/usr/bin/env python3
"""Daily build for 2026-05-25 — generates per-category JSON, summary.json,
Atom feed, and updates index.json from /tmp/collected_raw.json."""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

TARGET_DATE = "2026-05-25"
RAW_PATH = "/tmp/collected_raw.json"
ROOT = Path("/sessions/keen-eloquent-cori/mnt/greek-news-aggregator")
OUT_ROOT = ROOT / "frontend" / "static" / "data"
DAY_DIR = OUT_ROOT / TARGET_DATE
FEED_DIR = OUT_ROOT / "feeds"
INDEX_PATH = OUT_ROOT / "index.json"

CATEGORIES = ["politics", "economy", "society", "world", "opinion", "culture"]

# Per-article analyses keyed by URL.
# Fields: el (Greek summary), en (English summary), tel (Greek tags),
#         ten (English tags), s (sentiment), i (importance 1-100),
#         cat (final category - lets us reroute mis-categorised articles)
ANALYSES = {
    # ── WORLD ──────────────────────────────────────────────────────
    "https://www.kathimerini.gr/world/564246484/tramp-gia-symfonia-me-iran-eite-megali-kai-simantiki-eite-den-tha-yparxei/": {
        "el": "Ο Αμερικανός πρόεδρος Ντόναλντ Τραμπ τόνισε ότι η συμφωνία με το Ιράν είτε θα είναι «μεγάλη και σημαντική» είτε δεν θα υπάρξει καθόλου. Λίγο νωρίτερα Ιράν και ΗΠΑ υποβάθμισαν τις προσδοκίες για επικείμενη πρόοδο, με τον Μάρκο Ρούμπιο να προειδοποιεί ότι η Ουάσιγκτον θα αντιδράσει «με άλλο τρόπο» αν δεν υπάρξει συμφωνία.",
        "en": "US President Donald Trump said the Iran deal will either be 'big and important' or nonexistent. Hours earlier Iran and the US played down expectations of imminent progress, with Marco Rubio warning Washington will respond 'another way' if a deal fails.",
        "tel": ["Τραμπ", "Ιράν", "ΗΠΑ", "διπλωματία"],
        "ten": ["Trump", "Iran", "US", "diplomacy"],
        "s": "neutral", "i": 88, "cat": "world",
    },
    "https://www.kathimerini.gr/world/564246469/kina-ennea-nekroi-apo-tis-plimmyres-stin-tsongktsingk/": {
        "el": "Εννέα νεκροί και 11 αγνοούμενοι από καταρρακτώδεις βροχές και πλημμύρες στην πόλη Τσονγκτσίνγκ της νοτιοδυτικής Κίνας. Πάνω από 2.000 κάτοικοι μετεγκαταστάθηκαν μετά τις ξαφνικές πλημμύρες και τις κατολισθήσεις που έπληξαν τη γειτονιά Γιονγκτσουάν.",
        "en": "Floods in Chongqing, southwest China, have killed nine people with 11 still missing. More than 2,000 residents have been evacuated after torrential rains triggered flash floods and landslides in the Yongchuan district.",
        "tel": ["Κίνα", "πλημμύρες", "καταστροφή"],
        "ten": ["China", "floods", "disaster"],
        "s": "negative", "i": 55, "cat": "world",
    },
    "https://www.kathimerini.gr/world/564246400/kiniseis-gia-ton-schimatismo-neas-kyvernisis-sti-letonia/": {
        "el": "Ο Λετονός βουλευτής Αντρις Κούλμπεργκς δηλώνει ότι επιδιώκει τον σχηματισμό τετρακομματικής κυβέρνησης πλειοψηφίας, μετά την κατάρρευση του προηγούμενου συνασπισμού της Εβίκα Σιλίνια εν μέσω ανησυχιών για παραβιάσεις ρωσικών drones στα ΝΑΤΟϊκά σύνορα της Βαλτικής.",
        "en": "Latvian opposition MP Andris Kulbergs is trying to form a four-party majority government after PM Evika Silina's coalition collapsed amid criticism of how it handled repeated Russian drone incursions over NATO's Baltic borders.",
        "tel": ["Λετονία", "ΝΑΤΟ", "Ρωσία", "drones"],
        "ten": ["Latvia", "NATO", "Russia", "drones"],
        "s": "neutral", "i": 62, "cat": "world",
    },
    "https://www.kathimerini.gr/world/564246355/kalifornia-synagermos-meta-apo-diarroi-se-dexameni-chimikon-maziki-ekkenosi-ypo-ton-kindyno-ekrixis/": {
        "el": "Κατάσταση έκτακτης ανάγκης κήρυξε ο κυβερνήτης Καλιφόρνιας Γκάβιν Νιούσομ μετά από διαρροή 7.000 γαλονιών εξαιρετικά τοξικού μεθακρυλικού μεθυλίου στην αεροδιαστημική μονάδα GKN στο Γκάρντεν Γκρόουβ. Περίπου 50.000 κάτοικοι έχουν εκκενώσει υπό τον φόβο έκρηξης.",
        "en": "California Governor Gavin Newsom has declared a state of emergency after 7,000 gallons of highly toxic methyl methacrylate leaked at GKN Aerospace's Garden Grove plant. About 50,000 residents have been evacuated amid fears of an explosion.",
        "tel": ["Καλιφόρνια", "χημικά", "εκκένωση", "καταστροφή"],
        "ten": ["California", "chemicals", "evacuation", "emergency"],
        "s": "negative", "i": 75, "cat": "world",
    },
    "https://www.kathimerini.gr/world/564246307/pakistan-dystychima-me-leoforeio-skotose-17-anthropoys-kai-traymatise-alloys-10/": {
        "el": "Τουλάχιστον 17 νεκροί και 10 τραυματίες σε τροχαίο στο βόρειο Πακιστάν, όταν φορτηγάκι έπεσε πάνω σε επιβάτες λεωφορείου που είχαν αποβιβαστεί λόγω μηχανικής βλάβης. Πολλά θύματα επέστρεφαν στα σπίτια τους ενόψει του Ιντ.",
        "en": "At least 17 people were killed and 10 injured in a road accident in northern Pakistan when a van slammed into bus passengers who had disembarked due to a breakdown. Many were travelling home for the Eid holiday.",
        "tel": ["Πακιστάν", "τροχαίο", "θύματα"],
        "ten": ["Pakistan", "accident", "fatalities"],
        "s": "negative", "i": 50, "cat": "world",
    },
    "https://www.kathimerini.gr/visual/video/564242227/pos-tha-sosoyme-ta-moyseia-poy-pernane-krisi/": {
        "el": "Ντοκιμαντέρ της ARTE (συμπαραγωγή με την «Κ» στο πλαίσιο της πλατφόρμας BEAM) για την κρίση των ευρωπαϊκών μουσείων: λόγω μειωμένης κρατικής χρηματοδότησης γίνονται περικοπές σε ασφάλεια και συντήρηση, με αποτέλεσμα κλοπές υψηλού προφίλ και αμφισβητούμενες εταιρικές χορηγίες.",
        "en": "ARTE documentary co-produced with Kathimerini under the BEAM platform on the crisis facing European museums: cuts in security and maintenance amid falling state funding have led to high-profile thefts and controversial corporate sponsorships.",
        "tel": ["μουσεία", "πολιτισμός", "ARTE"],
        "ten": ["museums", "culture", "ARTE"],
        "s": "negative", "i": 40, "cat": "culture",
    },
    "https://www.kathimerini.gr/world/564246271/iran-proodos-alla-ochi-teliki-symfonia-me-ipa/": {
        "el": "Η Τεχεράνη ανακοίνωσε ότι το προτεινόμενο μνημόνιο συνεννόησης «14 σημείων» επικεντρώνεται στον τερματισμό του πολέμου και την άρση του ναυτικού αποκλεισμού, με αντάλλαγμα ασφαλή διέλευση στα Στενά του Ορμούζ. Η συμφωνία θα ακολουθηθεί από διαπραγμάτευση 60 ημερών για το πυρηνικό πρόγραμμα.",
        "en": "Tehran says the proposed 14-point memorandum of understanding centres on ending the war and the US naval blockade in exchange for guaranteed transit through the Strait of Hormuz. If signed, a 60-day window of further talks on the nuclear programme would follow.",
        "tel": ["Ιράν", "ΗΠΑ", "Ορμούζ", "διπλωματία"],
        "ten": ["Iran", "US", "Hormuz", "diplomacy"],
        "s": "neutral", "i": 90, "cat": "world",
    },
    "https://www.kathimerini.gr/world/564246250/vretania-radioparemvoles-sto-aeroplano-toy-ypoyrgoy-amynas-konta-sta-rosika-synora/": {
        "el": "Το αεροπλάνο του Βρετανού υπουργού Άμυνας Τζον Χίλι δέχθηκε ραδιοπαρεμβολές κοντά στα ρωσικά σύνορα κατά την επιστροφή του από επίσκεψη σε Βρετανούς στρατιώτες στην Εσθονία. Το GPS παρέμεινε εκτός λειτουργίας για τρεις ώρες, αναγκάζοντας τους πιλότους να χρησιμοποιήσουν αδρανειακή πλοήγηση.",
        "en": "British Defence Secretary John Healey's plane was hit by signal jamming near the Russian border on his return from visiting UK troops in Estonia. GPS was knocked out for three hours, forcing the pilots to fall back on inertial navigation.",
        "tel": ["Βρετανία", "Ρωσία", "GPS", "Εσθονία"],
        "ten": ["UK", "Russia", "GPS", "Estonia"],
        "s": "negative", "i": 70, "cat": "world",
    },
    "https://www.kathimerini.gr/world/564246205/maziko-skandalo-sexoyalikis-kakopoiisis-paidion-se-scholeia-tis-gallias/": {
        "el": "Η γαλλική αστυνομία διερευνά πάνω από 100 καταγγελίες για κακοποίηση, σωματική βία και βιασμό παιδιών —ακόμη και τριών ετών— από επιστάτες σε 84 νηπιαγωγεία, 20 δημοτικά και 10 παιδικούς σταθμούς του Παρισιού. Ομάδες γονέων καταγγέλλουν ότι παλεύουν επί χρόνια για να ληφθούν σοβαρά υπόψη οι καταγγελίες.",
        "en": "French police are investigating over 100 complaints of abuse, violence and rape of children — some as young as three — by janitors at 84 Paris nurseries, 20 primary schools and 10 daycare centres. Parent groups say they fought for years to be taken seriously.",
        "tel": ["Γαλλία", "παιδική κακοποίηση", "σκάνδαλο"],
        "ten": ["France", "child abuse", "scandal"],
        "s": "negative", "i": 82, "cat": "world",
    },
    "https://www.kathimerini.gr/world/564246202/o-vasikos-diamesolavitis-toy-pakistan-stis-synomilies-ipa-iran-vrisketai-sto-pekino-mazi-me-ton-sarif/": {
        "el": "Ο αρχηγός του πακιστανικού στρατού Ασίμ Μουνίρ, βασικός διαμεσολαβητής στις συνομιλίες ΗΠΑ-Ιράν, βρίσκεται στο Πεκίνο μαζί με τον πρωθυπουργό Σαρίφ για συνομιλίες με την κινεζική ηγεσία. Η Κίνα δηλώνει ότι θα συνεργαστεί με το Πακιστάν για την αποκατάσταση της ειρήνης στη Μέση Ανατολή.",
        "en": "Pakistani army chief Asim Munir, the central mediator in the US-Iran talks, is in Beijing alongside PM Sharif for discussions with the Chinese leadership. China says it will work with Pakistan to help restore peace in the Middle East.",
        "tel": ["Πακιστάν", "Κίνα", "ΗΠΑ", "Ιράν"],
        "ten": ["Pakistan", "China", "US", "Iran"],
        "s": "neutral", "i": 78, "cat": "world",
    },
    "https://www.kathimerini.gr/world/564246193/o-kalimpaf-epanexelegi-proedros-toy-iranikoy-koinovoylioy/": {
        "el": "Ο επικεφαλής διαπραγματευτής του Ιράν στις συνομιλίες με τις ΗΠΑ, Μοχαμάντ Μπαγέρ Γκαλιμπάφ, επανεξελέγη πρόεδρος του ιρανικού Κοινοβουλίου, σύμφωνα με το πρακτορείο Fars.",
        "en": "Iran's chief negotiator in talks with the US, Mohammad Bagher Ghalibaf, has been re-elected speaker of the Iranian parliament, according to the Fars news agency.",
        "tel": ["Ιράν", "Γκαλιμπάφ", "κοινοβούλιο"],
        "ten": ["Iran", "Ghalibaf", "parliament"],
        "s": "neutral", "i": 55, "cat": "world",
    },
    "https://www.kathimerini.gr/world/564246283/rosia-pente-nekroi-apo-pyrkagia-se-exochiki-katoikia-konta-sti-moscha/": {
        "el": "Πέντε νεκροί — τρεις ενήλικες και δύο παιδιά — από πυρκαγιά σε εξοχική κατοικία στο Παβλόφσκι Πόσαντ της περιφέρειας Μόσχας. Οι ρωσικές αρχές κίνησαν ποινική διαδικασία για πρόκληση θανάτου από αμέλεια· η πυρκαγιά εικάζεται ότι προκλήθηκε από ηλεκτρικό βραχυκύκλωμα.",
        "en": "Five people — three adults and two children — died in a house fire in Pavlovsky Posad, Moscow region. Russian authorities have opened a criminal case for death through negligence; the blaze is believed to have been caused by an electrical short circuit.",
        "tel": ["Ρωσία", "πυρκαγιά", "θύματα"],
        "ten": ["Russia", "fire", "fatalities"],
        "s": "negative", "i": 45, "cat": "world",
    },
    "https://www.kathimerini.gr/world/564246181/rosia-dyo-nekroi-apo-oykranika-pligmata-se-mpelgkoront-kai-mpriansk/": {
        "el": "Δύο άμαχοι σκοτώθηκαν από ουκρανικά πλήγματα στις ρωσικές περιφέρειες Μπέλγκοροντ και Μπριάνσκ. Drone χτύπησε όχημα στο Γκραϊβόρον και πύραυλοι προκάλεσαν διακοπές ρεύματος και νερού στην ευρύτερη περιοχή.",
        "en": "Two civilians were killed by Ukrainian strikes on Russia's Belgorod and Bryansk regions. A drone hit a vehicle in Graivoron and missiles knocked out power and water in surrounding areas.",
        "tel": ["Ουκρανία", "Ρωσία", "πόλεμος", "drones"],
        "ten": ["Ukraine", "Russia", "war", "drones"],
        "s": "negative", "i": 62, "cat": "world",
    },
    "https://www.kathimerini.gr/world/564246079/chanei-o-tramp-ton-polemo-sto-iran-piesi-palinodies-kai-i-diexodos-tis-koyvas/": {
        "el": "Ανάλυση του Reuters: παρά την αμερικανική στρατιωτική υπεροχή και τα σοβαρά πλήγματα στο Ιράν, το θεοκρατικό καθεστώς παραμένει ανέπαφο, ελέγχει τα Στενά του Ορμούζ και αντιστέκεται στις πυρηνικές παραχωρήσεις, βάζοντας ερωτηματικά αν ο Τραμπ χάνει τελικά τον πόλεμο που κερδίζει τακτικά.",
        "en": "Reuters analysis: despite US military superiority and severe blows to Iran, the theocratic regime remains intact, controls the Strait of Hormuz and refuses nuclear concessions — raising doubts that Trump can convert tactical wins into a geopolitical victory.",
        "tel": ["Τραμπ", "Ιράν", "ΗΠΑ", "Reuters"],
        "ten": ["Trump", "Iran", "US", "Reuters"],
        "s": "negative", "i": 80, "cat": "world",
    },

    # ── POLITICS ───────────────────────────────────────────────────
    "https://www.kathimerini.gr/politics/564243775/alexis-tsipras-mple-kai-kokkino-sto-thiseio/": {
        "el": "Ρεπορτάζ για τα εγκαίνια του νέου κόμματος του Αλέξη Τσίπρα στο Θησείο την Τρίτη, με μότο «Από την κοινωνία, με την κοινωνία, για την κοινωνία». Το σήμα συνδυάζει το μπλε (πατρίδα, θάλασσα) με το κόκκινο (Αριστερά, αγώνες), στοιχεία της «πατριωτικής Αριστεράς» που επιδιώκει να συγκροτήσει.",
        "en": "Report on the launch event of Alexis Tsipras' new party at Thiseio on Tuesday, under the slogan 'From society, with society, for society.' Its logo blends blue (homeland, sea) with red (left, struggle), reflecting the 'patriotic left' identity Tsipras is targeting.",
        "tel": ["Τσίπρας", "νέο κόμμα", "αντιπολίτευση", "Αριστερά"],
        "ten": ["Tsipras", "new party", "opposition", "left"],
        "s": "neutral", "i": 88, "cat": "politics",
    },
    "https://www.kathimerini.gr/politics/564246388/mitsotakis-gia-dimografiko-den-einai-mono-oikonomiko-zitima-synechizoyme-tis-paremvaseis/": {
        "el": "Ο πρωθυπουργός Κυριάκος Μητσοτάκης μιλώντας στο συνέδριο «Δημογραφικό 2026» χαρακτήρισε την υπογεννητικότητα παγκόσμιο πρόβλημα και ανακοίνωσε ότι εξετάζεται «Σπίτι μου 3». Συνεχίζονται οι παρεμβάσεις στήριξης οικογένειας, μέσω και του υπουργείου Κοινωνικής Συνοχής και Οικογένειας.",
        "en": "PM Kyriakos Mitsotakis told the 'Demographic 2026' conference that declining birth rates are a global problem and confirmed a 'Spiti Mou 3' housing scheme is on the table. The government will keep expanding family-support measures through the new Social Cohesion and Family Ministry.",
        "tel": ["Μητσοτάκης", "δημογραφικό", "Σπίτι μου", "οικογένεια"],
        "ten": ["Mitsotakis", "demographics", "Spiti Mou", "family"],
        "s": "neutral", "i": 72, "cat": "politics",
    },
    "https://www.kathimerini.gr/politics/564246358/v-kikilias-51-perissoteroi-ektaktoi-elegchoi-sta-ploia/": {
        "el": "Ο υπουργός Ναυτιλίας Βασίλης Κικίλιας ανακοίνωσε αύξηση 51% στους έκτακτους ελέγχους πλοίων το 2026 (515 έναντι 341 πέρυσι) και 12πλάσιες απαγορεύσεις απόπλου (50 έναντι 4). Στόχος η ασφάλεια εν όψει της θερινής τουριστικής περιόδου.",
        "en": "Shipping Minister Vassilis Kikilias announced a 51% rise in spot inspections of vessels in 2026 (515 vs 341 last year) and a twelvefold rise in sailing bans (50 vs 4). The drive aims to boost safety ahead of the summer tourism season.",
        "tel": ["Κικίλιας", "ναυτιλία", "έλεγχοι", "ασφάλεια"],
        "ten": ["Kikilias", "shipping", "inspections", "safety"],
        "s": "positive", "i": 60, "cat": "politics",
    },
    "https://www.kathimerini.gr/politics/564243757/o-chartis-sta-dyo-to-neo-eklogiko-topio-sti-voreia-ellada/": {
        "el": "Ανάλυση της Δώρας Αντωνίου για το πώς τα νέα κόμματα Καρυστιανού, Τσίπρα και Σαμαρά αναδιαμορφώνουν τον εκλογικό χάρτη της Βόρειας Ελλάδας. Δημοσκόπηση στη Θεσσαλονίκη δείχνει διαφορετική δυναμική των τριών σχημάτων έναντι του υπόλοιπου της χώρας.",
        "en": "Dora Antoniou analyses how the new Karystianou, Tsipras and Samaras parties are reshaping northern Greece's electoral map. A Thessaloniki poll shows the three projects perform very differently in Macedonia and Thrace than in the rest of the country.",
        "tel": ["εκλογές", "Βόρεια Ελλάδα", "δημοσκόπηση"],
        "ten": ["elections", "Northern Greece", "poll"],
        "s": "neutral", "i": 75, "cat": "politics",
    },
    "https://www.kathimerini.gr/politics/564244708/theoreio-apo-to-archeio-tis-kathimerinis/": {
        "el": "Στήλη «Θεωρείο» για το δώρο του Προέδρου της Δημοκρατίας Κωνσταντίνου Τασούλα στην Πριγκίπισσα Άννα: μια φωτογραφία του Πρίγκιπα Ανδρέα από το αρχείο της «Καθημερινής». Ο Τασούλας έθεσε διακριτικά το θέμα της επιστροφής των Γλυπτών του Παρθενώνα στη συνάντηση.",
        "en": "'Theoreio' column on President Konstantinos Tasoulas' gift to Princess Anne: an archival Kathimerini photograph of Prince Andrew. During the meeting Tasoulas discreetly raised the question of returning the Parthenon Marbles.",
        "tel": ["Θεωρείο", "Τασούλας", "Πριγκίπισσα Άννα", "Γλυπτά Παρθενώνα"],
        "ten": ["Theoreio", "Tasoulas", "Princess Anne", "Parthenon Marbles"],
        "s": "positive", "i": 55, "cat": "politics",
    },
    "https://www.kathimerini.gr/politics/564243736/i-n-d-kai-i-partida-ton-trion/": {
        "el": "Ο Σταύρος Παπαντωνίου αναλύει την «παρτίδα των τριών» που αντιμετωπίζει η Νέα Δημοκρατία: τα νέα κόμματα Καρυστιανού, Τσίπρα και Σαμαρά. Δημοσκοπικά ο Τσίπρας εμφανίζει δυναμική δεύτερου κόμματος, ακόμη πριν την επίσημη ίδρυση, αντλώντας από το 17% του 2023 και τμήμα ΠΑΣΟΚ.",
        "en": "Stavros Papantoniou analyses the 'three-front battle' New Democracy now faces against the new Karystianou, Tsipras and Samaras parties. Polls show Tsipras has the dynamic of a second-place party even before its formal launch, drawing from his 17% 2023 vote and part of PASOK's base.",
        "tel": ["ΝΔ", "Τσίπρας", "δημοσκοπήσεις", "εκλογές"],
        "ten": ["New Democracy", "Tsipras", "polls", "elections"],
        "s": "neutral", "i": 78, "cat": "politics",
    },
    "https://www.kathimerini.gr/politics/564245956/androylakis-to-tropaio-toy-final-four-tis-athinas-se-elliniki-omada/": {
        "el": "Ο πρόεδρος του ΠΑΣΟΚ Νίκος Ανδρουλάκης συνεχάρη τον Ολυμπιακό για την κατάκτηση της Ευρωλίγκας στο Final Four της Αθήνας. Αντίστοιχα μηνύματα έστειλαν ο πρωθυπουργός Μητσοτάκης και ο Πρόεδρος της Δημοκρατίας Τασούλας.",
        "en": "PASOK leader Nikos Androulakis congratulated Olympiacos on winning the EuroLeague at the Athens Final Four. PM Mitsotakis and President Tasoulas issued similar messages.",
        "tel": ["Ανδρουλάκης", "Ολυμπιακός", "Ευρωλίγκα"],
        "ten": ["Androulakis", "Olympiacos", "EuroLeague"],
        "s": "positive", "i": 35, "cat": "politics",
    },
    "https://www.kathimerini.gr/politics/564245947/tasoylas-gia-akoma-mia-fora-stin-koryfi-tis-eyropis-to-elliniko-mpasket/": {
        "el": "Ο Πρόεδρος της Δημοκρατίας Κωνσταντίνος Τασούλας συνεχάρη τον Ολυμπιακό και τον προπονητή Γιώργο Μπαρτζώκα για την κατάκτηση του Ευρωπαϊκού Κυπέλλου μπάσκετ, χαρακτηρίζοντας την επιτυχία λαμπρό παράδειγμα σκληρής δουλειάς και αυτοπεποίθησης.",
        "en": "President Konstantinos Tasoulas congratulated Olympiacos and coach Georgios Bartzokas on winning the EuroLeague basketball trophy, calling it a shining example of hard work and self-belief for Greek sport.",
        "tel": ["Τασούλας", "Ολυμπιακός", "μπάσκετ"],
        "ten": ["Tasoulas", "Olympiacos", "basketball"],
        "s": "positive", "i": 35, "cat": "politics",
    },
    "https://www.kathimerini.gr/politics/564245917/kyr-mitsotakis-therma-sygcharitiria-ston-olympiako-gia-ti-megali-epitychia/": {
        "el": "Ο πρωθυπουργός Κυριάκος Μητσοτάκης συνεχάρη τον Ολυμπιακό για την τέταρτη κατάκτηση της Ευρωλίγκας μετά τη νίκη 92-85 επί της Ρεάλ Μαδρίτης στο Final Four της Αθήνας, και αναγνώρισε την άρτια διοργάνωση.",
        "en": "PM Kyriakos Mitsotakis congratulated Olympiacos on their fourth EuroLeague title after defeating Real Madrid 92-85 in the Athens Final Four and praised the event's smooth organisation.",
        "tel": ["Μητσοτάκης", "Ολυμπιακός", "Ευρωλίγκα"],
        "ten": ["Mitsotakis", "Olympiacos", "EuroLeague"],
        "s": "positive", "i": 38, "cat": "politics",
    },
    "https://www.kathimerini.gr/politics/foreign-policy/564243799/to-nomoschedio-gia-to-aigaio-kai-o-fovos-toy-israil/": {
        "el": "Ανάλυση του Κωνσταντίνου Φίλη για το επικείμενο τουρκικό νομοσχέδιο που κωδικοποιεί το δόγμα της «Γαλάζιας Πατρίδας» και τη συνεπακόλουθη ένταση. Σε προεκλογική περίοδο και Ελλάδα και Τουρκία, οι δύο ηγέτες θα είναι λιγότερο διαλλακτικοί, ενώ ο Ερντογάν ανησυχεί για τη στρατηγική συνεργασία Ελλάδας-Ισραήλ.",
        "en": "Konstantinos Filis analyses the looming Turkish bill codifying the 'Blue Homeland' doctrine and the diplomatic strain it will create. With both Greece and Turkey near elections, neither leader can be conciliatory; Erdogan is especially uneasy about the Greece-Israel strategic axis.",
        "tel": ["Τουρκία", "Αιγαίο", "Γαλάζια Πατρίδα", "Ισραήλ"],
        "ten": ["Turkey", "Aegean", "Blue Homeland", "Israel"],
        "s": "negative", "i": 82, "cat": "politics",
    },
    "https://www.kathimerini.gr/politics/564245659/paraitithike-apo-ton-syriza-o-dionysis-temponeras/": {
        "el": "Ο Διονύσης Τεμπονέρας υπέβαλε την παραίτησή του από μέλος του ΣΥΡΙΖΑ και κάλεσε το κόμμα να στηρίξει το εγχείρημα Τσίπρα. Λίγες ημέρες νωρίτερα είχε παραιτηθεί και ο γραμματέας του ΣΥΡΙΖΑ Στέργιος Καλπάκης.",
        "en": "Dionysis Temboneras has resigned from SYRIZA and called on the party to back Alexis Tsipras' new political venture. Days earlier SYRIZA general secretary Stergios Kalpakis also resigned.",
        "tel": ["ΣΥΡΙΖΑ", "Τεμπονέρας", "Τσίπρας", "παραίτηση"],
        "ten": ["SYRIZA", "Temboneras", "Tsipras", "resignation"],
        "s": "neutral", "i": 65, "cat": "politics",
    },
    "https://www.kathimerini.gr/politics/564245446/mitsotakis-paratasi-sto-spiti-moy-ii-eos-to-telos-aygoystoy-ti-eipe-gia-chorotaxiko-kai-kysea/": {
        "el": "Ο πρωθυπουργός Κυριάκος Μητσοτάκης ανακοίνωσε παράταση του προγράμματος «Σπίτι μου ΙΙ» έως το τέλος Αυγούστου για τις ήδη εγκεκριμένες αιτήσεις, με χρηματοδότηση από εθνικούς πόρους μέσω της Ελληνικής Αναπτυξιακής Τράπεζας. Αναφέρθηκε επίσης σε χωροταξικό για τον τουρισμό και ΚΥΣΕΑ.",
        "en": "PM Kyriakos Mitsotakis announced an extension of the 'Spiti Mou II' housing scheme through end-August for already-approved applications, funded from national resources via the Hellenic Development Bank. He also discussed the tourism spatial-planning bill and KYSEA agenda.",
        "tel": ["Μητσοτάκης", "Σπίτι μου", "στέγαση", "χωροταξικό"],
        "ten": ["Mitsotakis", "Spiti Mou", "housing", "spatial planning"],
        "s": "positive", "i": 72, "cat": "politics",
    },

    # ── SOCIETY ───────────────────────────────────────────────────
    "https://www.kathimerini.gr/society/564246436/o-traianos-dellas-apochaireta-ti-gogo-mastrokosta-i-anartisi-toy/": {
        "el": "Ο Τραϊανός Δέλλας αποχαιρετά συγκινητικά τη σύζυγό του Γωγώ Μαστροκώστα, που έφυγε από τη ζωή σε ηλικία 56 ετών μετά από πολυετή μάχη με τον καρκίνο. Η κόρη τους Βικτώρια δημοσίευσε επίσης τρυφερό μήνυμα για τη μητέρα της.",
        "en": "Greek football coach Traianos Dellas posted an emotional farewell to his wife, gymnast Gogo Mastrokosta, who died at 56 after a long battle with cancer. Their daughter Victoria also shared a tribute to her mother.",
        "tel": ["Δέλλας", "Μαστροκώστα", "νεκρολογία"],
        "ten": ["Dellas", "Mastrokosta", "obituary"],
        "s": "negative", "i": 45, "cat": "society",
    },
    "https://www.kathimerini.gr/society/564246394/opekepe-enochoi-13-katigoroymenoi-stis-serres-gia-paranomes-epidotiseis-250-000-eyro/": {
        "el": "Με 13 ένοχους από τους 25 κατηγορουμένους ολοκληρώθηκε στο Τριμελές Εφετείο Κακουργημάτων η δίκη για παράνομες επιδοτήσεις ΟΠΕΚΕΠΕ ύψους 250.000 ευρώ στις Σέρρες. Επιβλήθηκαν ποινές φυλάκισης 5-26 μηνών με τριετή αναστολή. Αποκαλύφθηκε «μπάχαλο» στις διαδικασίες ελέγχου του οργανισμού.",
        "en": "13 of 25 defendants were convicted at the Athens Felonies Court of Appeal over €250,000 in illegal OPEKEPE subsidies in Serres. They received 5-26 month suspended sentences. The case exposed a 'mess' of missing controls within the agency.",
        "tel": ["ΟΠΕΚΕΠΕ", "δίκη", "Σέρρες", "επιδοτήσεις"],
        "ten": ["OPEKEPE", "trial", "Serres", "subsidies"],
        "s": "negative", "i": 70, "cat": "society",
    },
    "https://www.kathimerini.gr/society/564241474/alexandros-giotopoylos-anairesi-tis-apofylakisis-zitei-i-eisaggelia-toy-areioy-pagoy/": {
        "el": "Η εισαγγελία του Αρείου Πάγου άσκησε αναίρεση κατά της απόφασης αποφυλάκισης του αρχηγού της «17 Νοέμβρη» Αλέξανδρου Γιωτόπουλου, καταδικασμένου σε 17 φορές ισόβια. Η εισαγγελία υποστηρίζει ότι δεν συμπληρώθηκε ο απαιτούμενος χρόνος έκτισης ποινής. Το δικαστικό συμβούλιο θα αποφασίσει εντός του πρώτου δεκαημέρου του Ιουνίου.",
        "en": "Greece's Supreme Court prosecution has filed an appeal against the parole release of '17 November' terrorist leader Alexandros Giotopoulos, who was sentenced to 17 life terms. Prosecutors argue he has not served the legally required minimum. A court panel will decide in early June.",
        "tel": ["Γιωτόπουλος", "17 Νοέμβρη", "Άρειος Πάγος", "δικαιοσύνη"],
        "ten": ["Giotopoulos", "17 November", "Supreme Court", "justice"],
        "s": "negative", "i": 78, "cat": "society",
    },
    "https://www.kathimerini.gr/society/564246322/rethymno-sto-nosokomeio-15chroni-meta-apo-katanalosi-alkool/": {
        "el": "15χρονο κορίτσι στο Ρέθυμνο μεταφέρθηκε εσπευσμένα στο νοσοκομείο μετά από κατανάλωση μεγάλης ποσότητας βότκας που είχε αγοράσει με συνομήλικό της από μίνι μάρκετ. Η 70χρονη ιδιοκτήτρια του καταστήματος συνελήφθη για πώληση αλκοόλ σε ανήλικους.",
        "en": "A 15-year-old girl in Rethymno was rushed to hospital after drinking a large quantity of vodka she had bought with a peer at a mini-market. The 70-year-old shop owner was arrested for selling alcohol to minors.",
        "tel": ["Ρέθυμνο", "αλκοόλ", "ανήλικοι"],
        "ten": ["Rethymno", "alcohol", "minors"],
        "s": "negative", "i": 45, "cat": "society",
    },
    "https://www.kathimerini.gr/society/564246316/metro-thessalonikis-apo-mia-trochia-ta-dromologia/": {
        "el": "Πρόβλημα στο μετρό Θεσσαλονίκης την Δευτέρα το πρωί: τα δρομολόγια εκτελούνται μόνο μέσω της τροχιάς 1 από τον σταθμό Δημοκρατίας έως τον σταθμό Σιντριβάνι. Ο σταθμός Νέος Σιδηροδρομικός Σταθμός παραμένει προσωρινά κλειστός.",
        "en": "Disruption hit the Thessaloniki Metro on Monday morning, with trains running only on track 1 between Dimokratias and Syntrivani stations. New Railway Station is temporarily closed.",
        "tel": ["Θεσσαλονίκη", "μετρό", "μεταφορές"],
        "ten": ["Thessaloniki", "metro", "transport"],
        "s": "negative", "i": 40, "cat": "society",
    },
    "https://www.kathimerini.gr/society/564246292/kozani-soros-andra-entopistike-sti-limni-polyfytoy/": {
        "el": "Νεκρός άνδρας εντοπίστηκε στη λίμνη Πολυφύτου της Κοζάνης μετά από πληροφορία περαστικού που είδε αυτοκίνητο μέσα στη λίμνη. Ισχυρές αστυνομικές δυνάμεις έχουν αποκλείσει την περιοχή ενώ διερευνώνται οι συνθήκες.",
        "en": "A man's body was found in Lake Polyfytos in Kozani after a passer-by spotted a car in the water. Strong police forces have sealed off the area while investigators look into the cause.",
        "tel": ["Κοζάνη", "θάνατος", "έρευνες"],
        "ten": ["Kozani", "death", "investigation"],
        "s": "negative", "i": 42, "cat": "society",
    },
    "https://www.kathimerini.gr/society/564246289/archanes-synelifthisan-dyo-23chronoi-gia-toys-pyrovolismoys-meta-apo-diapliktismo/": {
        "el": "Δύο 23χρονοι συνελήφθησαν στις Αρχάνες Ηρακλείου για ρίψη πυροβολισμών μετά από διαπληκτισμό. Βρέθηκε πιστόλι κρότου και πέντε κάλυκες, και σχηματίστηκε δικογραφία για παραβάσεις της νομοθεσίας περί όπλων και απόπειρα σωματικής βλάβης.",
        "en": "Two 23-year-olds were arrested in Archanes, Heraklion, for firing shots after a quarrel. Police seized a blank-firing pistol and five shell casings; charges include weapons offences and attempted assault.",
        "tel": ["Ηράκλειο", "πυροβολισμοί", "σύλληψη"],
        "ten": ["Heraklion", "shooting", "arrest"],
        "s": "negative", "i": 45, "cat": "society",
    },
    "https://www.kathimerini.gr/society/564246187/opekepe-20-nees-syllipseis-stin-kriti-pano-apo-3-ekat-ta-paranoma-kerdi-tis-organosis/": {
        "el": "Σε εξέλιξη μεγάλη επιχείρηση της ΕΛ.ΑΣ. στην Κρήτη με 20 συλλήψεις για παράνομες επιδοτήσεις ΟΠΕΚΕΠΕ που ξεπερνούν τα 2,5 εκατ. ευρώ από το 2019. Στο επίκεντρο λογιστικό γραφείο στο Ρέθυμνο, με συνεργασία Κέντρων Υποβολής Δηλώσεων και ψευδείς μισθώσεις αγροτεμαχίων. Συνολικά εμπλέκονται περίπου 90 άτομα.",
        "en": "A major Cretan police operation has so far yielded 20 arrests over illegal OPEKEPE subsidy fraud topping €2.5 million since 2019. The probe centres on a Rethymno accounting firm collaborating with declaration centres on fake farmland leases. About 90 individuals are believed to be implicated.",
        "tel": ["ΟΠΕΚΕΠΕ", "Κρήτη", "συλλήψεις", "απάτη"],
        "ten": ["OPEKEPE", "Crete", "arrests", "fraud"],
        "s": "negative", "i": 80, "cat": "society",
    },
    "https://www.kathimerini.gr/society/564243904/i-zoi-piso-apo-ti-resepsion/": {
        "el": "Ρεπορτάζ για το νέο βιβλίο της Κωνσταντίνας Τσουκαλά-Σταθάκη «Η σεζόν» από τις εκδόσεις Αντίποδες, που χαρτογραφεί την εργασιακή εμπειρία στον ελληνικό τουρισμό. Καταγράφει επταήμερη εργασία επί έξι μήνες σε νησιωτικό ξενοδοχείο και τις σκληρές συνθήκες ζωής του εποχικού προσωπικού.",
        "en": "Profile of Konstantina Tsoukala-Stathaki's new book 'The Season' (Antipodes), mapping the labour reality of Greek tourism. It documents her seven-day-a-week six-month stints at island hotels and the harsh living conditions for seasonal staff.",
        "tel": ["τουρισμός", "εργασία", "βιβλίο"],
        "ten": ["tourism", "labour", "book"],
        "s": "neutral", "i": 55, "cat": "society",
    },
    "https://www.kathimerini.gr/society/564246133/thessaloniki-ston-eisaggelea-o-30chronos-poy-synelifthi-gia-to-fono-toy-patera-toy/": {
        "el": "Στον εισαγγελέα οδηγείται 30χρονος στη Θεσσαλονίκη που συνελήφθη για τη δολοφονία του 67χρονου πατέρα του στο Τριάδι Θέρμης. Από τον τόπο του εγκλήματος κατασχέθηκαν μαχαίρι, κατσαβίδι και δύο κουτιά ναρκωτικών δισκίων χωρίς συνταγή.",
        "en": "A 30-year-old man is being brought before prosecutors in Thessaloniki after being arrested for murdering his 67-year-old father in Triadi, Thermi. Police seized a knife, a screwdriver and two boxes of unprescribed narcotic pills.",
        "tel": ["Θεσσαλονίκη", "δολοφονία", "ενδοοικογενειακή βία"],
        "ten": ["Thessaloniki", "murder", "domestic violence"],
        "s": "negative", "i": 70, "cat": "society",
    },
    "https://www.kathimerini.gr/society/564246121/syllipsi-dyo-toyrkon-sti-thraki-meteferan-25-pistolia-sto-mikroskopio-i-toyrkiki-mafia/": {
        "el": "Δύο Τούρκοι υπήκοοι συνελήφθησαν στη Θράκη για διακίνηση 25 «όπλων-φαντασμάτων» (πιστολιών χωρίς σειριακό αριθμό) που βρέθηκαν στο πορτ μπαγκάζ αυτοκινήτου μεταξύ Ξάνθης και Κομοτηνής. Η ΕΛ.ΑΣ. εκτιμά ότι προορίζονταν για εγκληματικές οργανώσεις ομοεθνών τους στην Ελλάδα.",
        "en": "Greek police arrested two Turkish nationals in Thrace smuggling 25 'ghost guns' (serial-less pistols) hidden in a car trunk between Xanthi and Komotini. Authorities believe the weapons were destined for Turkish-led criminal networks operating in Greece.",
        "tel": ["Θράκη", "όπλα", "μαφία", "Τουρκία"],
        "ten": ["Thrace", "weapons", "mafia", "Turkey"],
        "s": "negative", "i": 70, "cat": "society",
    },
    "https://www.kathimerini.gr/society/564246001/kairos-nefoseis-kai-topikes-vroches-eos-27-vathmoys-i-thermokrasia/": {
        "el": "Νεφώσεις και τοπικές βροχές αναμένονται τη Δευτέρα στην κεντρική Μακεδονία, Θεσσαλία, Εύβοια, Στερεά και Κρήτη. Η θερμοκρασία θα φτάσει τους 27 βαθμούς. Βόρειοι άνεμοι 3-6 μποφόρ.",
        "en": "Cloudy skies and localised rain are forecast on Monday across central Macedonia, Thessaly, Evia, Sterea and Crete, with temperatures reaching 27°C and northerly winds of 3-6 Beaufort.",
        "tel": ["καιρός", "βροχές"],
        "ten": ["weather", "rain"],
        "s": "neutral", "i": 25, "cat": "society",
    },
    "https://www.kathimerini.gr/society/564245989/efyge-apo-ti-zoi-i-gogo-mastrokosta-i-anartisi-ti-koris-tis/": {
        "el": "Έφυγε από τη ζωή σε ηλικία 56 ετών η γνωστή γυμνάστρια Γωγώ Μαστροκώστα μετά από πολυετή μάχη με τον καρκίνο, νοσηλευόμενη στο νοσοκομείο «Ευαγγελισμός». Την είδηση γνωστοποίησε η κόρη της Βικτώρια Δέλλα με συγκινητική ανάρτηση.",
        "en": "Well-known Greek gymnast Gogo Mastrokosta died at 56 after a long battle with cancer at Evangelismos Hospital in Athens. Her daughter Victoria Della announced the news with a moving tribute.",
        "tel": ["Μαστροκώστα", "νεκρολογία", "καρκίνος"],
        "ten": ["Mastrokosta", "obituary", "cancer"],
        "s": "negative", "i": 45, "cat": "society",
    },

    # ── ECONOMY ───────────────────────────────────────────────────
    "https://www.kathimerini.gr/economy/564244174/psifiakes-anaskafes-kai-energeia-apo-fykia/": {
        "el": "Το παράρτημα του ερευνητικού κέντρου «Αθηνά» στην Ξάνθη αποκτά δεύτερη στέγη και επεκτείνει το πεδίο ερευνών σε ευφυή γεωργία, παραγωγή ενέργειας από φύκια και ψηφιακές αρχαιολογικές «ανασκαφές», συνδυάζοντας πολιτιστική τεχνολογία και ΑΠΕ.",
        "en": "The Athena research centre's Xanthi branch is opening a second site and broadening its work into smart agriculture, algae-based energy and digital archaeological 'excavations', blending cultural heritage tech with renewable-energy research.",
        "tel": ["έρευνα", "Ξάνθη", "ΑΠΕ", "τεχνολογία"],
        "ten": ["research", "Xanthi", "renewables", "technology"],
        "s": "positive", "i": 55, "cat": "economy",
    },
    "https://www.kathimerini.gr/economy/local/564244111/fthino-reyma-apo-ellinikes-ape-gia-toys-voylgaroys/": {
        "el": "Παράδοξο της ελληνικής ενεργειακής αγοράς: ενώ η Ελλάδα έχει γίνει η 4η μεγαλύτερη εξαγωγέας ηλεκτρισμού στην Ευρώπη, με 18.000 «πράσινα» μεγαβάτ, η λιανική τιμή παραμένει η ακριβότερη σε όρους αγοραστικής δύναμης. Φθηνό ρεύμα από ΑΠΕ εξάγεται και αποθηκεύεται σε βουλγάρικες μπαταρίες.",
        "en": "Greek energy paradox: although the country is now Europe's 4th largest electricity net exporter with 18 GW of green capacity, retail kWh prices remain the highest in purchasing-power terms. Cheap renewables flow out to Bulgaria, where they are stored in batteries for later use.",
        "tel": ["ενέργεια", "ΑΠΕ", "Βουλγαρία", "εξαγωγές"],
        "ten": ["energy", "renewables", "Bulgaria", "exports"],
        "s": "neutral", "i": 75, "cat": "economy",
    },
    "https://www.kathimerini.gr/economy/564244168/ta-ofeli-tis-entaxis-nosileyton-sta-varea/": {
        "el": "Η υπουργός Εργασίας Νίκη Κεραμέως προανήγγειλε ένταξη στα Βαρέα και Ανθυγιεινά Επαγγέλματα νοσηλευτών, βοηθών νοσηλευτών, οδηγών ασθενοφόρων και διασωστών του ΕΣΥ/ΕΚΑΒ που είχαν προσληφθεί πριν την 1η Ιανουαρίου 2011 — περισσότεροι από 23.000 εργαζόμενοι θα μπορούν να συνταξιοδοτηθούν έως 5 χρόνια νωρίτερα.",
        "en": "Labour Minister Niki Kerameus has previewed a regulation adding nurses, nursing assistants, ambulance drivers and EKAV rescuers hired before 1 January 2011 to Greece's 'heavy and hazardous' professions register — over 23,000 workers will be able to retire up to five years earlier.",
        "tel": ["Κεραμέως", "ΕΣΥ", "ΕΚΑΒ", "συνταξιοδότηση"],
        "ten": ["Kerameus", "ESY", "EKAV", "pensions"],
        "s": "positive", "i": 68, "cat": "economy",
    },
    "https://www.kathimerini.gr/economy/local/564244102/freno-se-chreoseis-choris-ti-synainesi-toy-pelati/": {
        "el": "Το οικονομικό επιτελείο εξετάζει νομοθετική παρέμβαση που θα απαιτεί ρητή συναίνεση (opt-in αντί opt-out) του πελάτη πριν επιβληθούν τραπεζικές χρεώσεις για «προνομιακούς» λογαριασμούς. Δεύτερη ρύθμιση εξετάζεται για τον τρόπο υπολογισμού τόκων σε στεγαστικά δάνεια.",
        "en": "The Finance Ministry is weighing a law requiring explicit customer consent (opt-in instead of opt-out) before banks can impose monthly fees on 'premium' accounts. A second amendment is being considered on how mortgage interest is calculated.",
        "tel": ["τράπεζες", "χρεώσεις", "νομοθεσία"],
        "ten": ["banks", "fees", "legislation"],
        "s": "positive", "i": 70, "cat": "economy",
    },
    "https://www.kathimerini.gr/economy/international/564245974/ypochorisi-5-stis-diethneis-times-toy-petrelaioy/": {
        "el": "Πτώση 5% στις διεθνείς τιμές πετρελαίου στις πρωινές ασιατικές αγορές της Δευτέρας, εν αναμονή συμφωνίας ΗΠΑ-Ιράν. Το Brent υποχώρησε στα 98,22 δολάρια το βαρέλι και το WTI στα 91,57 δολάρια, παρά τις δηλώσεις του Τραμπ που μετριάζουν προσδοκίες.",
        "en": "Oil prices dropped over 5% in early Asian trading Monday on hopes of a US-Iran deal. Brent fell to $98.22 per barrel and WTI to $91.57, even as Trump tempered expectations of an imminent breakthrough.",
        "tel": ["πετρέλαιο", "Brent", "Ιράν", "αγορές"],
        "ten": ["oil", "Brent", "Iran", "markets"],
        "s": "positive", "i": 82, "cat": "economy",
    },
    "https://www.kathimerini.gr/economy/564244210/mporoyme-na-vgoyme-alovitoi-apo-tin-krisi/": {
        "el": "Ανάλυση του Νίκου Φιλιππίδη για το αν η ελληνική και παγκόσμια οικονομία θα βγει αλώβητη από την ενεργειακή κρίση που προκαλεί ο πόλεμος στον Κόλπο. Όλοι αποφεύγουν μακροχρόνιες δαπάνες όπως στις προηγούμενες κρίσεις, με τη λογική «βλέποντας και κάνοντας».",
        "en": "Nikos Filippidis analyses whether Greek and global economies can emerge unscathed from the Gulf-war energy crisis. Governments are avoiding the long-term spending of previous crises, opting for a 'wait and see' stance.",
        "tel": ["οικονομία", "κρίση", "ενέργεια"],
        "ten": ["economy", "crisis", "energy"],
        "s": "negative", "i": 72, "cat": "economy",
    },
    "https://www.kathimerini.gr/economy/local/564244123/oxyteri-i-stegastiki-krisi-stin-ellada/": {
        "el": "Ένα στα τέσσερα ελληνικά νοικοκυριά αντιμετωπίζει υπέρογκες δαπάνες στέγης, με το ενοίκιο να απορροφά πάνω από το 60% του μισθού (στοιχεία Eurostat). Ο πρόεδρος του Eurogroup Κυριάκος Πιερρακάκης παρουσίασε στη Λευκωσία καλές πρακτικές Κροατίας-Ισπανίας-Ιρλανδίας για τη στεγαστική κρίση.",
        "en": "One in four Greek households face crushing housing costs, with rent absorbing over 60% of wages (Eurostat data). At the Nicosia Eurogroup, chair Kyriakos Pierrakakis presented Croatian, Spanish and Irish housing policies as best practices.",
        "tel": ["στέγαση", "Eurogroup", "Πιερρακάκης"],
        "ten": ["housing", "Eurogroup", "Pierrakakis"],
        "s": "negative", "i": 75, "cat": "economy",
    },
    "https://www.kathimerini.gr/economy/local/564244099/koinos-logariasmos-kai-foros-klironomias-se-akinita/": {
        "el": "Φορολογικές διευκρινίσεις: κοινός λογαριασμός σε τράπεζα αλλοδαπής ή ημεδαπής απαλλάσσεται φόρου κληρονομιάς για συνδικαιούχους, εκτός μη συνεργάσιμων κρατών. Επίσης κινητή περιουσία στο εξωτερικό απαλλάσσεται αν ο θανών ήταν εγκατεστημένος εκεί πάνω από 10 χρόνια.",
        "en": "Tax clarifications: joint accounts in domestic or foreign banks are exempt from inheritance tax for surviving co-holders, except for non-cooperative jurisdictions. Movable property abroad is also exempt if the deceased lived there for over 10 years.",
        "tel": ["φόρος", "κληρονομιά", "τράπεζες"],
        "ten": ["tax", "inheritance", "banks"],
        "s": "neutral", "i": 55, "cat": "economy",
    },
    "https://www.kathimerini.gr/economy/local/564244129/megalonei-o-logariasmos-tis-energeiakis-krisis/": {
        "el": "Η Ευρωπαϊκή Επιτροπή αναθεώρησε προς τα κάτω την πρόβλεψη ανάπτυξης για την Ελλάδα στο 1,8% και προς τα πάνω τον πληθωρισμό στο 3,7%. Ο Πιερρακάκης προειδοποιεί ότι «αν τα Στενά του Ορμούζ δεν ανοίξουν τον Ιούνιο, ο Ιούνιος θα είναι χειρότερος από τον Μάιο».",
        "en": "The European Commission has cut its Greek growth forecast to 1.8% and lifted its inflation projection to 3.7%. Eurogroup chair Pierrakakis warns that 'if the Strait of Hormuz isn't reopened in June, June will be worse than May'.",
        "tel": ["ανάπτυξη", "πληθωρισμός", "Πιερρακάκης", "ενέργεια"],
        "ten": ["growth", "inflation", "Pierrakakis", "energy"],
        "s": "negative", "i": 85, "cat": "economy",
    },
    "https://www.kathimerini.gr/opinion/interviews/564243577/tzianpiero-petrilieri-stin-k-atoy-gia-mia-etaireia-i-anaptyxi-talenton/": {
        "el": "Συνέντευξη του καθηγητή Οργανωσιακής Συμπεριφοράς στο INSEAD Τζιανπιέρο Πετριλιέρι: στην εποχή της ΑΙ, η ανάπτυξη ταλέντων είναι ανταγωνιστικό πλεονέκτημα. Οι εργαζόμενοι μένουν όχι για τις υποσχέσεις αλλά για τις απτές ευκαιρίες εξέλιξης.",
        "en": "Interview with INSEAD organisational-behaviour professor Gianpiero Petriglieri: in the AI era, talent development is a competitive edge. Employees stay not for promises but for tangible growth opportunities.",
        "tel": ["INSEAD", "ηγεσία", "συνέντευξη", "AI"],
        "ten": ["INSEAD", "leadership", "interview", "AI"],
        "s": "neutral", "i": 45, "cat": "economy",
    },

    # ── OPINION ───────────────────────────────────────────────────
    "https://www.kathimerini.gr/opinion/564243733/i-profanis-stratigiki/": {
        "el": "Άρθρο του Ευτύχη Βαρδουλάκη για τη στρατηγική Μητσοτάκη που παρουσιάστηκε στο συνέδριο της ΝΔ: η «Ελλάδα του 2030» μεταφέρει τη συζήτηση από τα πεπραγμένα στις προσδοκίες και επιδιώκει να οριοθετήσει τις επόμενες εκλογές ως αντιπαράθεση προσώπων (Μητσοτάκης–Τσίπρας ή Μητσοτάκης–Ανδρουλάκης).",
        "en": "Op-ed by Eftychis Vardoulakis on Mitsotakis' strategy unveiled at the ND congress: the 'Greece 2030' framing shifts debate from past record to future expectations and seeks to frame the next election as a head-to-head contest (Mitsotakis–Tsipras or Mitsotakis–Androulakis).",
        "tel": ["άποψη", "Μητσοτάκης", "στρατηγική", "εκλογές"],
        "ten": ["opinion", "Mitsotakis", "strategy", "elections"],
        "s": "neutral", "i": 65, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564243658/idiotes-san-dimosio/": {
        "el": "Κύριο άρθρο: οι μεγάλες ιδιωτικές επιχειρήσεις σε ολιγοπωλιακές αγορές αντιμετωπίζουν τους πελάτες με γραφειοκρατική αλαζονεία που θυμίζει παλιές ΔΕΚΟ. Η αδυναμία επίλυσης σοβαρών ζητημάτων δεν ταιριάζει σε ευρωπαϊκή χώρα.",
        "en": "Editorial: large private firms in oligopolistic markets are treating customers with bureaucratic arrogance reminiscent of the old state utilities. The inability to resolve basic issues is unworthy of a European country.",
        "tel": ["άποψη", "ιδιωτικές επιχειρήσεις", "καταναλωτές"],
        "ten": ["opinion", "private firms", "consumers"],
        "s": "negative", "i": 55, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564243928/ta-irema-nera-kai-oi-oroi-tis-ninemias/": {
        "el": "Άρθρο του Αλέξη Παπαχελά για την ένταση στις ελληνοτουρκικές σχέσεις: η Άγκυρα είναι ενοχλημένη από τη συνεργασία Ελλάδας-Ισραήλ και τη δήλωση Μακρόν για το Αιγαίο. Η ελληνική κυβέρνηση ενημερώθηκε από ξένο τηλεγράφημα για το τουρκικό νομοσχέδιο θαλασσίων ζωνών — το κανάλι Γεραπετρίτη-Φιντάν δεν λειτούργησε.",
        "en": "Op-ed by Alexis Papahelas on Greek-Turkish tensions: Ankara is irked by Greece-Israel cooperation and Macron's Aegean remarks. Athens learned of Turkey's pending maritime-zones bill via a foreign news wire — the Gerapetritis-Fidan channel failed to operate.",
        "tel": ["άποψη", "Ελλάδα", "Τουρκία", "Αιγαίο"],
        "ten": ["opinion", "Greece", "Turkey", "Aegean"],
        "s": "negative", "i": 78, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564243934/to-glossiko-einai-panta-zontano/": {
        "el": "Άρθρο του Τάκη Θεοδωρόπουλου για το «γλωσσικό» ζήτημα — πάνω από 200 σχόλια αναγνωστών δείχνουν ότι παραμένει ζωντανό, παρά τη νίκη της δημοτικής. Σε έναν κόσμο που χρησιμοποιεί υποτυπωδώς τα αγγλικά, η συζήτηση για τα ελληνικά πρέπει να γίνει με νέους όρους.",
        "en": "Op-ed by Takis Theodoropoulos on Greece's 'language question' — over 200 reader comments show it remains live despite demotic Greek's victory. In a world that uses English only rudimentarily, the conversation about Greek must be reframed.",
        "tel": ["άποψη", "γλώσσα", "ελληνικά"],
        "ten": ["opinion", "language", "Greek"],
        "s": "neutral", "i": 50, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564243724/apo-ta-tempi-sto-olympion/": {
        "el": "Άρθρο του Μιχάλη Τσιντσίνη για την πρόσφατη ίδρυση του κόμματος της Μαρίας Καρυστιανού στο «Ολύμπιον» Θεσσαλονίκης. Η συγγραφέας υποστηρίζει ότι το πολιτικό υπερθέαμα συσκότισε το καταστατικό τραύμα των Τεμπών και θεωρεί ότι η Ρωσία οπλοποιεί ανοιχτά τα δίκτυα επιρροής της.",
        "en": "Op-ed by Michalis Tsintsinis on the recent launch of Maria Karystianou's party at Thessaloniki's Olympion theatre. He argues the political spectacle eclipsed the founding Tempi trauma and that Russia is now openly weaponising its cultural influence networks in Greece.",
        "tel": ["άποψη", "Καρυστιανού", "Τέμπη", "Ρωσία"],
        "ten": ["opinion", "Karystianou", "Tempi", "Russia"],
        "s": "negative", "i": 75, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564244315/to-bangaranga-yparchei-ston-kathena-mas/": {
        "el": "Άρθρο της Μαρίας Κατσουνάκη για τη νίκη της Βουλγαρίας στη Eurovision με το «Bangaranga» και τη μεταφορά του μουσικού κέντρου βάρους ανατολικά. Τα Βαλκάνια εκλύουν ενέργεια και φρεσκάδα έναντι μιας «καθηλωμένης» Ευρώπης.",
        "en": "Op-ed by Maria Katsounaki on Bulgaria's Eurovision win with 'Bangaranga' and the shift of the contest's musical centre of gravity eastward. The Balkans pulse with energy and freshness in contrast to a 'frozen' Europe.",
        "tel": ["άποψη", "Βαλκάνια", "Eurovision"],
        "ten": ["opinion", "Balkans", "Eurovision"],
        "s": "positive", "i": 45, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564243931/pame-aplos-piso/": {
        "el": "Άρθρο του Κώστα Ιορδανίδη για τις ελληνοτουρκικές σχέσεις και τη δήλωση Δένδια ότι δεν πιστεύει στα «ήρεμα νερά». Παραλληλίζει με την ιστορική προσπάθεια του Κωνσταντίνου Ζωγράφου το 1834 και 1840 για σύναψη συμφωνιών με την Υψηλή Πύλη.",
        "en": "Op-ed by Kostas Iordanidis on Greek-Turkish relations and Defence Minister Dendias' rejection of the 'calm waters' narrative. He draws parallels with Konstantinos Zografos' 19th-century missions to the Sublime Porte.",
        "tel": ["άποψη", "Ελλάδα", "Τουρκία", "Δένδιας"],
        "ten": ["opinion", "Greece", "Turkey", "Dendias"],
        "s": "negative", "i": 65, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564243964/antisimitismos-kai-genoktonia/": {
        "el": "Άρθρο του Πάσχου Μανδραβέλη που διαφωνεί με τον ραββίνο Λάρισας ότι μόνο «ισλαμιστές και αριστερίστες» μιλούν για γενοκτονία στη Γάζα. Υποστηρίζει ότι οι σφαγές των IDF έχουν τεχνικά χαρακτηριστικά γενοκτονίας αλλά λείπει το βασικό στοιχείο: το σχέδιο εξόντωσης πληθυσμού.",
        "en": "Op-ed by Paschos Mandravelis disagreeing with the rabbi of Larissa's claim that only 'Islamists and leftists' speak of genocide in Gaza. He argues IDF mass killings show technical features of genocide but lack the defining element: a plan to exterminate a population.",
        "tel": ["άποψη", "Γάζα", "γενοκτονία", "Ισραήλ"],
        "ten": ["opinion", "Gaza", "genocide", "Israel"],
        "s": "negative", "i": 70, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564243925/o-pio-antidimofilis-prothypoyrgos/": {
        "el": "Άρθρο της Ελεάννας Βλαστού για τον Βρετανό πρωθυπουργό Κιρ Στάρμερ ως τον «πιο αντιδημοφιλή πρωθυπουργό» — πιο και από τη Λιζ Τρας. Οι κατηγορίες (δωρεάν κοστούμια, διορισμός Μάντελσον στις ΗΠΑ) θεωρούνται ασύμμετρες με την αντίδραση, που αποδίδεται στην έλλειψη ιδεολογίας.",
        "en": "Op-ed by Eleanna Vlastou on UK PM Keir Starmer as 'the most unpopular PM' — even more than Liz Truss. The trigger issues (free suits, the Mandelson US ambassador appointment) feel disproportionate to the backlash, which she traces to his absence of ideology.",
        "tel": ["άποψη", "Στάρμερ", "Βρετανία"],
        "ten": ["opinion", "Starmer", "UK"],
        "s": "negative", "i": 60, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564244321/o-ponos-ton-anthropon-kai-ton-skylon/": {
        "el": "Σχόλιο του Παντελή Μπουκάλα για περιστατικό όπου Ισραηλινός έποικος στη Δυτική Όχθη χτυπά άγρια το δεμένο σκυλί Παλαιστινίων. Η Haaretz δημοσιεύει την ιστορία, την οποία ο συγγραφέας θεωρεί αλληγορία της κατοχικής βαρβαρότητας.",
        "en": "Op-ed by Pantelis Boukalas on a West Bank incident in which an Israeli settler savagely beats the tethered dog of a Palestinian family. Haaretz's reporting becomes, for Boukalas, an allegory of the brutality of occupation.",
        "tel": ["άποψη", "Δυτική Όχθη", "Ισραήλ"],
        "ten": ["opinion", "West Bank", "Israel"],
        "s": "negative", "i": 60, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564244162/poios-den-thelei-tis-dimoskopiseis/": {
        "el": "Άρθρο του Ανδρέα Δρυμιώτη για το ΠΑΣΟΚ και τις δημοσκοπήσεις. Στέλεχος του κόμματος του επιτέθηκε δημόσια επειδή σχολιάζει δημοσκοπικά δεδομένα, αποδεικνύοντας ότι «επειδή δεν κουνιέται η βελόνα» κηρύσσεται πόλεμος στους δημοσκόπους.",
        "en": "Op-ed by Andreas Drymiotis on PASOK and polling. After a senior party figure publicly attacked him for commenting on polls, he argues PASOK's stagnant numbers are pushing the party into a war on pollsters themselves.",
        "tel": ["άποψη", "ΠΑΣΟΚ", "δημοσκοπήσεις"],
        "ten": ["opinion", "PASOK", "polls"],
        "s": "negative", "i": 55, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564243961/oi-neoi-zitoyn-prositi-stegi/": {
        "el": "Άρθρο του Νότη Παπαδόπουλου για την ακρίβεια και τη στέγη: το 62,8% των μισθωτών ζει με κάτω από 1.000-1.100 ευρώ καθαρά, ενώ το 46% «τα φέρνει βόλτα ίσα ίσα». Παρά τα θετικά μακροοικονομικά στοιχεία, οι πολίτες αισθάνονται απογοήτευση για την οικονομική τους κατάσταση.",
        "en": "Op-ed by Notis Papadopoulos on cost of living and housing: 62.8% of Greek wage-earners take home under €1,000-1,100/month, and 46% report 'just scraping by'. Despite positive macroeconomic data, citizens express deep frustration over their finances.",
        "tel": ["άποψη", "στέγαση", "ακρίβεια", "νέοι"],
        "ten": ["opinion", "housing", "cost of living", "youth"],
        "s": "negative", "i": 72, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564243973/toxiki-periergeia-kai-fthonos/": {
        "el": "Άρθρο της Αγγελικής Σπανού για τις μισθώσεις από το Δημόσιο σε ακίνητα συγγενών πολιτικών (Ανδρουλάκη στο Ηράκλειο, Σπανάκη στο Μοσχάτο). Δεν τίθεται ζήτημα νομιμότητας, αλλά είναι εύλογος ο σχολιασμός σε εποχή βαθιάς κοινωνικής καχυποψίας απέναντι στα κόμματα.",
        "en": "Op-ed by Angeliki Spanou on government leases of properties owned by relatives of politicians (Androulakis in Heraklion, Spanakis in Moschato). She finds no legal issue but says public scrutiny is fair in an era of deep mistrust toward parties.",
        "tel": ["άποψη", "Ανδρουλάκης", "Σπανάκης", "δημόσιο"],
        "ten": ["opinion", "Androulakis", "Spanakis", "public sector"],
        "s": "neutral", "i": 60, "cat": "opinion",
    },
    "https://www.kathimerini.gr/opinion/564243970/i-pagida-ton-deyteron-eklogon/": {
        "el": "Άρθρο του Σάκη Μουμτζή για το σενάριο διπλών εκλογών για τη ΝΔ. Αν στις πρώτες εκλογές η ΝΔ λάβει 27-29%, οι ελπίδες αυτοδυναμίας στις δεύτερες είναι περιορισμένες — μπορεί να βγει μπούμερανγκ. Μόνο με ξεκάθαρο στόχο αυτοδυναμίας θα έχει νόημα η διπλή κάλπη.",
        "en": "Op-ed by Sakis Moumtzis on the double-election scenario for New Democracy. If ND lands 27-29% in the first round, hopes of a majority in the second are slim — and could backfire. Only a clear single-party majority goal would justify going to the ballot twice.",
        "tel": ["άποψη", "ΝΔ", "εκλογές", "αυτοδυναμία"],
        "ten": ["opinion", "New Democracy", "elections", "majority"],
        "s": "neutral", "i": 65, "cat": "opinion",
    },

    # ── CULTURE ───────────────────────────────────────────────────
    "https://www.kathimerini.gr/culture/564242122/i-proti-agnosti-ektelesi-enos-gnostoy-tragoydioy-tis-vasos-alagianni/": {
        "el": "Αφιέρωμα του Κώστα Μπαλαχούτη για την πρώτη ηχογράφηση (1988) του τραγουδιού «Πού πάει η αγάπη όταν φεύγει» της Βάσως Αλαγιάννη από τη Γιούλη Τσίρου — έξι χρόνια πριν την κλασική ερμηνεία της Πίτσας Παπαδοπούλου. Παραγωγή Νταλάρα στην ΕΜΙ.",
        "en": "Kostas Balachoutis revisits the long-forgotten 1988 first recording of Vasso Alagianni's song 'Where Does Love Go When It Leaves' by Yiouli Tsirou — six years before Pitsa Papadopoulou's classic version. Produced by Dalaras on EMI.",
        "tel": ["μουσική", "Αλαγιάννη", "δισκογραφία"],
        "ten": ["music", "Alagianni", "discography"],
        "s": "positive", "i": 35, "cat": "culture",
    },
    "https://www.kathimerini.gr/culture/564244429/mia-ayli-tis-metemfyliakis-elladas/": {
        "el": "Κριτική της Ελισάβετ Κοτζιά για τη μετεμφυλιακή Ελλάδα στο μυθιστόρημα «Η καγκελόπορτα» (1962) του Αντρέα Φραγκιά. Το πολυπρόσωπο έργο, χαρακτηρισμένο από τον Δ. Ραυτόπουλο «κοινωνική ψυχογραφία της ήττας», αποτυπώνει τον ασθματικό ρυθμό της επιβίωσης σε μια γκρεμισμένη χώρα.",
        "en": "Elisavet Kotzia reviews 'I Kangeloporta' (1962) by Andreas Fragias, a multi-character novel that critic Dimitris Raftopoulos called 'a social psychography of defeat', set in the Athens of the brutal post-civil war years.",
        "tel": ["βιβλίο", "Φραγκιάς", "λογοτεχνία"],
        "ten": ["book", "Fragias", "literature"],
        "s": "neutral", "i": 35, "cat": "culture",
    },
    "https://www.kathimerini.gr/istoria/564244339/90-chronia-prin-24-5-1936/": {
        "el": "Στήλη «90 Χρόνια πριν» από το αρχείο της «Καθημερινής» (24-5-1936): σύγκρουση Ναζί-αστυνομίας σε πύργο της Αυστρίας, διαταγή του Γκρατσιάνι προς τον αρχιεπίσκοπο Χαράρ να εγκαταλείψει την Αιθιοπία, και χαλάρωση των ιταλο-βρετανικών εντάσεων.",
        "en": "'Ninety Years Ago' column from the Kathimerini archive of 24 May 1936: a Nazi-police clash at an Austrian castle, Marshal Graziani ordering the Catholic archbishop of Harar out of Ethiopia, and easing Italian-British tensions.",
        "tel": ["ιστορία", "αρχείο", "1936"],
        "ten": ["history", "archive", "1936"],
        "s": "neutral", "i": 30, "cat": "culture",
    },
    "https://www.kathimerini.gr/culture/564244438/mparok-aries-synodeia-archilaoytoy/": {
        "el": "Κριτική του Νίκου Α. Δοντά για το ρεσιτάλ της σοπράνο Μυρτώς Παπαθανασίου με τον Θεόδωρο Κίτσο στο αρχιλαούτο στην αίθουσα «Δημήτρης Μητρόπουλος», με άριες του 17ου αιώνα. Σπάνια ευκαιρία να ακουστεί η Παπαθανασίου εκτός Μότσαρτ και Πουτσίνι.",
        "en": "Nikos A. Dontas reviews soprano Myrto Papathanasiou's 17th-century aria recital with Theodore Kitsos on archlute at the Dimitris Mitropoulos Hall — a rare chance to hear her outside her usual Mozart and Puccini repertoire.",
        "tel": ["κλασική μουσική", "Παπαθανασίου", "ρεσιτάλ"],
        "ten": ["classical music", "Papathanasiou", "recital"],
        "s": "positive", "i": 35, "cat": "culture",
    },
    "https://www.kathimerini.gr/culture/tv/564245542/prime-time-i-leoforos-eiche-ti-diki-tis-istoria/": {
        "el": "Στον ΣΚΑΪ απόψε το Α' μέρος του αφιερώματος του Παύλου Τσίμα για τη «Λεωφόρο», το θρυλικό γήπεδο του Παναθηναϊκού. Σπάνιες μαρτυρίες των Αντωνιάδη, Καμάρα, Κωνσταντίνου και Φυλακούρη, με αναφορές στους θρύλους Μεσσάρη και Δομάζο.",
        "en": "SKAI airs tonight the first part of Pavlos Tsimas' tribute to 'Leoforos', Panathinaikos' legendary stadium. The programme features rare testimonies from Antoniadis, Kamaras, Konstantinou and Fylakouris, with nods to legends Messaris and Domazos.",
        "tel": ["Λεωφόρος", "Παναθηναϊκός", "ΣΚΑΪ"],
        "ten": ["Leoforos", "Panathinaikos", "SKAI"],
        "s": "positive", "i": 40, "cat": "culture",
    },
    "https://www.kathimerini.gr/culture/564245473/iremi-dynami-me-nompel/": {
        "el": "Άρθρο του Σάκη Ιωαννίδη για δύο νομπελίστες — Ορχάν Παμούκ και Λάζλο Κρασναχορκάι — που από τα Χανιά και την Αθήνα έστειλαν μηνύματα αισιοδοξίας και ελπίδας. Ο Παμούκ προβλέπει ότι «ο Τραμπ θα έχει εξαφανιστεί μέσα στα επόμενα δύο με τρία χρόνια».",
        "en": "Sakis Ioannidis profiles two Nobel laureates — Orhan Pamuk and László Krasznahorkai — who sent messages of optimism and hope from their visits to Chania and Athens. Pamuk predicted that 'Trump will have vanished within the next two to three years'.",
        "tel": ["Παμούκ", "Κρασναχορκάι", "Νομπέλ"],
        "ten": ["Pamuk", "Krasznahorkai", "Nobel"],
        "s": "positive", "i": 50, "cat": "culture",
    },
    "https://www.kathimerini.gr/culture/564244348/i-astiki-laografia-enos-gipedoy/": {
        "el": "Άρθρο του Νίκου Βατόπουλου για την αστική λαογραφία γύρω από το γήπεδο του Παναθηναϊκού στη Λεωφόρο Αλεξάνδρας, εν όψει της μετακόμισης του συλλόγου στο Βοτανικό. Καταγράφει συνθήματα, εικόνες και λαϊκά ιδεολογήματα ενός γηπέδου-σύμβολου του 20ού αιώνα.",
        "en": "Nikos Vatopoulos walks the streets around Panathinaikos' Leoforos stadium ahead of the club's move to Votanikos, cataloguing the slogans, images and folk iconography that have grown around this symbolic 20th-century arena.",
        "tel": ["Λεωφόρος", "Παναθηναϊκός", "αστική λαογραφία"],
        "ten": ["Leoforos", "Panathinaikos", "urban folklore"],
        "s": "neutral", "i": 40, "cat": "culture",
    },
    "https://www.kathimerini.gr/culture/564244318/ena-sanidi-eidika-gia-toys-neoys/": {
        "el": "Άρθρο του Απόστολου Λακασά για τα ετήσια θεατρικά βραβεία «Μελίνα Μερκούρη» και «Δημήτρης Χορν» για νέους ηθοποιούς — φέτος Εβελύν Ασουάντ και Βασίλης Μπούτσικος. Συζητείται η δυσκολία αξιολόγησης 2.000 παραστάσεων ετησίως στην Αθήνα.",
        "en": "Apostolos Lakasas covers the annual 'Melina Mercouri' and 'Dimitris Chorn' theatre awards for young actors, this year going to Evelyn Asouad and Vassilis Boutsikos. He explores the difficulty of judging the 2,000 productions staged in Athens each year.",
        "tel": ["θέατρο", "βραβεία", "νέοι ηθοποιοί"],
        "ten": ["theatre", "awards", "young actors"],
        "s": "positive", "i": 35, "cat": "culture",
    },
    "https://www.kathimerini.gr/culture/564244273/me-ton-tropo-ton-archaion-ellinon/": {
        "el": "Αφιέρωμα του Ηλία Μαγκλίνη στον πιανίστα Αντονι Ρομάνιουκ και στο νέο του άλμπουμ «On Modes» που εξερευνά τους αρχαιοελληνικούς μουσικούς τρόπους — Δώριο, Φρύγιο, Λύδιο κ.ά. — μέσα από έργα σύγχρονης πιανιστικής μουσικής.",
        "en": "Ilias Maglinis profiles pianist Anthony Romaniuk's new album 'On Modes', which explores the ancient Greek musical modes — Dorian, Phrygian, Lydian and others — through contemporary piano repertoire.",
        "tel": ["μουσική", "Ρομάνιουκ", "αρχαία Ελλάδα"],
        "ten": ["music", "Romaniuk", "ancient Greece"],
        "s": "positive", "i": 35, "cat": "culture",
    },
}

# ───────────────────────────────────────────────────────────────────

def slug_id(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:12]


def build():
    with open(RAW_PATH) as f:
        data = json.load(f)

    articles = data["articles"]

    # Build items per category, redirecting articles whose final category
    # differs from the URL-derived hint via ANALYSES[url]["cat"].
    cat_items = {c: [] for c in CATEGORIES}
    all_items_by_id = {}
    missing = []

    for art in articles:
        url = art["url"]
        an = ANALYSES.get(url)
        if an is None:
            missing.append(url)
            continue
        final_cat = an["cat"]
        item = {
            "id": art.get("id") or slug_id(url),
            "title": art["title"],
            "url": url,
            "author": art.get("author", "Καθημερινή"),
            "published": art.get("published"),
            "source": "Kathimerini",
            "source_type": "scrape",
            "category": final_cat,
            "importance": an["i"],
            "content": (art.get("content") or "")[:2000],
            "summary": {"el": an["el"], "en": an["en"]},
            "tags": {"el": an["tel"], "en": an["ten"]},
            "sentiment": an["s"],
        }
        cat_items[final_cat].append(item)
        all_items_by_id[item["id"]] = item

    if missing:
        print(f"WARN: {len(missing)} articles missing analyses:", file=sys.stderr)
        for u in missing:
            print(f"  {u}", file=sys.stderr)

    # Sort each category by importance desc
    for c in CATEGORIES:
        cat_items[c].sort(key=lambda x: x["importance"], reverse=True)

    # Write per-category JSONs
    DAY_DIR.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(timezone.utc).isoformat()

    category_themes = {
        "politics": {
            "el": ["Εγκαίνια νέου κόμματος Τσίπρα", "Δημογραφικό & Σπίτι μου ΙΙ",
                   "Ελληνοτουρκικά - Αιγαίο", "Final Four Ολυμπιακού"],
            "en": ["Tsipras new party launch", "Demographics & Spiti Mou II",
                   "Greek-Turkish relations / Aegean", "Olympiacos EuroLeague win"],
        },
        "economy": {
            "el": ["Ενεργειακή κρίση & πετρέλαιο", "Στεγαστική κρίση",
                   "Τραπεζικές χρεώσεις", "ΑΠΕ & εξαγωγές ρεύματος"],
            "en": ["Energy crisis & oil prices", "Housing crisis",
                   "Bank fees reform", "Renewables & power exports"],
        },
        "society": {
            "el": ["Σκάνδαλο ΟΠΕΚΕΠΕ", "Έγκλημα & κοινωνικά περιστατικά",
                   "Γιωτόπουλος αποφυλάκιση", "Νεκρολογία Μαστροκώστα"],
            "en": ["OPEKEPE subsidy fraud", "Crime & social incidents",
                   "Giotopoulos parole case", "Gogo Mastrokosta obituary"],
        },
        "world": {
            "el": ["Διαπραγματεύσεις ΗΠΑ-Ιράν / Ορμούζ", "Σκάνδαλο κακοποίησης Γαλλίας",
                   "Διαρροή χημικών Καλιφόρνια", "Πόλεμος Ουκρανίας-Ρωσίας"],
            "en": ["US-Iran negotiations / Hormuz", "France child-abuse scandal",
                   "California chemical leak", "Ukraine-Russia war"],
        },
        "opinion": {
            "el": ["Στρατηγική Μητσοτάκη & εκλογές", "Ελληνοτουρκική ένταση",
                   "Στεγαστική / οικονομική κρίση", "Ίδρυση κόμματος Καρυστιανού"],
            "en": ["Mitsotakis strategy & elections", "Greek-Turkish tensions",
                   "Housing / cost-of-living crisis", "Karystianou party launch"],
        },
        "culture": {
            "el": ["Παναθηναϊκός Λεωφόρος αφιερώματα", "Παμούκ & Κρασναχορκάι",
                   "Κρίση ευρωπαϊκών μουσείων", "Μουσική & δισκογραφία"],
            "en": ["Panathinaikos Leoforos tributes", "Pamuk & Krasznahorkai",
                   "European museums in crisis", "Music & discography"],
        },
    }

    for cat in CATEGORIES:
        items = cat_items[cat]
        payload = {
            "date": TARGET_DATE,
            "generated_at": now_iso,
            "category": cat,
            "item_count": len(items),
            "themes": category_themes[cat],
            "items": items,
        }
        (DAY_DIR / f"{cat}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2)
        )

    # ── summary.json ──────────────────────────────────────────────
    # categories per FEEDBACK MEMORY must be {cat: {item_count, top_items}}
    cats_for_summary = {}
    for cat in CATEGORIES:
        items = cat_items[cat]
        cats_for_summary[cat] = {
            "item_count": len(items),
            "top_items": [it["id"] for it in items[:5]],
        }

    total = sum(len(cat_items[c]) for c in CATEGORIES)

    executive_summary_el = (
        "Η Δευτέρα 25 Μαΐου 2026 κυριαρχείται από τις διαπραγματεύσεις ΗΠΑ-Ιράν "
        "για τον τερματισμό του πολέμου στη Μέση Ανατολή. Το Ιράν παρουσίασε μνημόνιο 14 σημείων "
        "που επικεντρώνεται στον τερματισμό του αμερικανικού ναυτικού αποκλεισμού και την ασφαλή "
        "διέλευση στα Στενά του Ορμούζ, με αντάλλαγμα διαπραγμάτευση 60 ημερών για το πυρηνικό "
        "πρόγραμμα· οι τιμές πετρελαίου έπεσαν 5% στις πρώτες ασιατικές συναλλαγές. Παράλληλα, "
        "Πακιστανός αρχηγός στρατού και πρωθυπουργός Σαρίφ βρίσκονται στο Πεκίνο για διαμεσολάβηση."
        "\n\n"
        "Στο εσωτερικό μέτωπο, ξεχωρίζει η αυριανή ίδρυση του νέου κόμματος του Αλέξη Τσίπρα στο "
        "Θησείο με μότο «πατριωτικής Αριστεράς» — γεγονός που συγκλονίζει το πολιτικό σκηνικό όπου "
        "η ΝΔ αντιμετωπίζει «παρτίδα τριών» με τα κόμματα Καρυστιανού-Τσίπρα-Σαμαρά. Ο πρωθυπουργός "
        "Μητσοτάκης ανακοίνωσε «Σπίτι μου 3» για το δημογραφικό, ενώ παρατάθηκε το «Σπίτι μου ΙΙ» "
        "έως τέλος Αυγούστου. Παραιτήσεις από τον ΣΥΡΙΖΑ (Τεμπονέρας) τροφοδοτούν το ρεύμα προς "
        "Τσίπρα. Ο Παπαχελάς και άλλοι αναλυτές καταγράφουν ένταση στις ελληνοτουρκικές σχέσεις "
        "λόγω επικείμενου τουρκικού νομοσχεδίου για τις θαλάσσιες ζώνες."
        "\n\n"
        "Ο ΟΠΕΚΕΠΕ επανέρχεται στο επίκεντρο: 20 συλλήψεις στην Κρήτη για παράνομες επιδοτήσεις "
        "πάνω από 2,5 εκατ. ευρώ, ενώ στις Σέρρες καταδικάστηκαν 13 από 25 κατηγορούμενοι. Η "
        "εισαγγελία του Αρείου Πάγου ζητά αναίρεση της αποφυλάκισης του Αλέξανδρου Γιωτόπουλου. "
        "Η ενεργειακή κρίση πιέζει την οικονομία — η Κομισιόν αναθεώρησε προς τα κάτω την ανάπτυξη "
        "στο 1,8% και προς τα πάνω τον πληθωρισμό στο 3,7%. Στον αθλητισμό, ο Ολυμπιακός κατέκτησε "
        "για 4η φορά την Ευρωλίγκα νικώντας 92-85 τη Ρεάλ Μαδρίτης στο Final Four της Αθήνας."
    )

    executive_summary_en = (
        "Monday 25 May 2026 is dominated by US-Iran negotiations to end the Middle East war. "
        "Tehran has presented a 14-point memorandum focused on ending the US naval blockade and "
        "ensuring safe passage through the Strait of Hormuz in exchange for a 60-day window of "
        "further nuclear talks; oil prices fell 5% in early Asian trading. Pakistan's army chief "
        "and PM Sharif are in Beijing for mediation talks with the Chinese leadership."
        "\n\n"
        "Domestically, the standout story is Tuesday's launch of Alexis Tsipras' new party at Thiseio, "
        "framed as a 'patriotic left' project — shaking up a political landscape where New Democracy "
        "now faces a 'three-front contest' with the Karystianou, Tsipras and Samaras parties. PM "
        "Mitsotakis announced a 'Spiti Mou 3' housing scheme as part of his demographics push and "
        "extended the existing 'Spiti Mou II' programme through end-August. Resignations from SYRIZA "
        "(Temboneras) signal momentum toward the new Tsipras venture. Papahelas and other commentators "
        "flag rising tensions with Turkey over an imminent maritime-zones bill."
        "\n\n"
        "The OPEKEPE subsidy scandal returns to the spotlight: 20 arrests in Crete for over €2.5 "
        "million in illegal subsidies, and a Serres trial saw 13 of 25 defendants convicted. The "
        "Supreme Court prosecution wants to overturn the parole release of '17 November' terrorist "
        "leader Alexandros Giotopoulos. The energy crisis is squeezing the economy — the European "
        "Commission cut Greek growth to 1.8% and lifted inflation to 3.7%. In sport, Olympiacos won "
        "their fourth EuroLeague title beating Real Madrid 92-85 at the Athens Final Four."
    )

    top_topics = [
        {
            "name": {"el": "Διαπραγματεύσεις ΗΠΑ-Ιράν & Στενά Ορμούζ",
                     "en": "US-Iran negotiations & Strait of Hormuz"},
            "description": {
                "el": "Το Ιράν κατέθεσε μνημόνιο 14 σημείων για τερματισμό του πολέμου με αντάλλαγμα ασφαλή διέλευση στον Ορμούζ. Ο Τραμπ απαιτεί «μεγάλη συμφωνία», οι τιμές πετρελαίου υποχωρούν 5%. Πακιστανική διαμεσολάβηση μέσω Πεκίνου.",
                "en": "Iran tabled a 14-point MoU to end the war in exchange for safe Hormuz passage. Trump insists on a 'big deal'; oil prices dropped 5%. Pakistani mediation continues via Beijing."
            },
            "related_items": [it["id"] for url, it in all_items_by_id.items() if False] +
                             [all_items_by_id[slug_id(u)]["id"] for u in [
                                 "https://www.kathimerini.gr/world/564246484/tramp-gia-symfonia-me-iran-eite-megali-kai-simantiki-eite-den-tha-yparxei/",
                                 "https://www.kathimerini.gr/world/564246271/iran-proodos-alla-ochi-teliki-symfonia-me-ipa/",
                                 "https://www.kathimerini.gr/world/564246202/o-vasikos-diamesolavitis-toy-pakistan-stis-synomilies-ipa-iran-vrisketai-sto-pekino-mazi-me-ton-sarif/",
                                 "https://www.kathimerini.gr/world/564246079/chanei-o-tramp-ton-polemo-sto-iran-piesi-palinodies-kai-i-diexodos-tis-koyvas/",
                                 "https://www.kathimerini.gr/economy/international/564245974/ypochorisi-5-stis-diethneis-times-toy-petrelaioy/",
                             ] if slug_id(u) in all_items_by_id],
            "importance": 92,
        },
        {
            "name": {"el": "Νέο κόμμα Τσίπρα & αναδιάταξη αντιπολίτευσης",
                     "en": "Tsipras' new party & opposition realignment"},
            "description": {
                "el": "Εγκαίνια του νέου κόμματος Τσίπρα στο Θησείο την Τρίτη με χρώματα μπλε-κόκκινο. Παραιτήσεις από τον ΣΥΡΙΖΑ τροφοδοτούν το νέο φορέα. Η ΝΔ αντιμετωπίζει «παρτίδα τριών» με Καρυστιανού-Τσίπρα-Σαμαρά.",
                "en": "Tsipras' new party launches Tuesday at Thiseio under blue-red banners. SYRIZA defections feed the new vehicle; New Democracy faces a 'three-front' opposition (Karystianou, Tsipras, Samaras)."
            },
            "related_items": [all_items_by_id[slug_id(u)]["id"] for u in [
                "https://www.kathimerini.gr/politics/564243775/alexis-tsipras-mple-kai-kokkino-sto-thiseio/",
                "https://www.kathimerini.gr/politics/564245659/paraitithike-apo-ton-syriza-o-dionysis-temponeras/",
                "https://www.kathimerini.gr/politics/564243736/i-n-d-kai-i-partida-ton-trion/",
                "https://www.kathimerini.gr/politics/564243757/o-chartis-sta-dyo-to-neo-eklogiko-topio-sti-voreia-ellada/",
            ] if slug_id(u) in all_items_by_id],
            "importance": 88,
        },
        {
            "name": {"el": "Σκάνδαλο ΟΠΕΚΕΠΕ — συλλήψεις & καταδίκες",
                     "en": "OPEKEPE subsidy fraud — arrests & convictions"},
            "description": {
                "el": "20 συλλήψεις στην Κρήτη για παράνομες επιδοτήσεις άνω των 2,5 εκατ. ευρώ. Καταδίκη 13 από 25 κατηγορούμενους στις Σέρρες. Αποκαλύπτεται «μπάχαλο» ελέγχων στον οργανισμό.",
                "en": "20 arrests in Crete over €2.5M+ in illegal subsidies. 13 of 25 Serres defendants convicted. Investigations reveal systemic control failures inside the agency."
            },
            "related_items": [all_items_by_id[slug_id(u)]["id"] for u in [
                "https://www.kathimerini.gr/society/564246187/opekepe-20-nees-syllipseis-stin-kriti-pano-apo-3-ekat-ta-paranoma-kerdi-tis-organosis/",
                "https://www.kathimerini.gr/society/564246394/opekepe-enochoi-13-katigoroymenoi-stis-serres-gia-paranomes-epidotiseis-250-000-eyro/",
            ] if slug_id(u) in all_items_by_id],
            "importance": 80,
        },
        {
            "name": {"el": "Ενεργειακή κρίση & ελληνική οικονομία",
                     "en": "Energy crisis & Greek economy"},
            "description": {
                "el": "Η Κομισιόν αναθεώρησε ανάπτυξη στο 1,8% (από 2,1% πέρυσι) και πληθωρισμό στο 3,7%. Παράδοξο της ελληνικής αγοράς ΑΠΕ: εξάγει φθηνό ρεύμα αλλά η λιανική τιμή είναι η ακριβότερη της ΕΕ. Πιερρακάκης: «αν τα Στενά δεν ανοίξουν, ο Ιούνιος θα είναι χειρότερος».",
                "en": "European Commission cut Greek growth to 1.8% (from 2.1% last year) and lifted inflation to 3.7%. Renewables paradox: Greece exports cheap power but retail prices are EU's highest. Pierrakakis warns June will be worse than May if Hormuz stays closed."
            },
            "related_items": [all_items_by_id[slug_id(u)]["id"] for u in [
                "https://www.kathimerini.gr/economy/local/564244129/megalonei-o-logariasmos-tis-energeiakis-krisis/",
                "https://www.kathimerini.gr/economy/local/564244111/fthino-reyma-apo-ellinikes-ape-gia-toys-voylgaroys/",
                "https://www.kathimerini.gr/economy/local/564244123/oxyteri-i-stegastiki-krisi-stin-ellada/",
                "https://www.kathimerini.gr/economy/564244210/mporoyme-na-vgoyme-alovitoi-apo-tin-krisi/",
            ] if slug_id(u) in all_items_by_id],
            "importance": 85,
        },
    ]

    summary = {
        "date": TARGET_DATE,
        "generated_at": now_iso,
        "source_note": f"Articles scraped from kathimerini.gr. {total} articles over 24h.",
        "executive_summary": {"el": executive_summary_el, "en": executive_summary_en},
        "top_topics": top_topics,
        "article_count": total,
        "categories": cats_for_summary,
    }
    (DAY_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2))

    # ── Atom feed (top 20 by importance) ────────────────────────────
    FEED_DIR.mkdir(parents=True, exist_ok=True)
    all_items = list(all_items_by_id.values())
    all_items.sort(key=lambda x: x["importance"], reverse=True)
    top20 = all_items[:20]

    entries_xml = []
    for it in top20:
        title = xml_escape(it["title"])
        url = xml_escape(it["url"])
        author = xml_escape(it.get("author") or "Καθημερινή")
        summary_el = xml_escape(it["summary"]["el"])
        pub = it.get("published") or f"{TARGET_DATE}T00:00:00+00:00"
        entries_xml.append(
            f"""  <entry>
    <id>{url}</id>
    <title>{title}</title>
    <link href="{url}"/>
    <updated>{pub}</updated>
    <author><name>{author}</name></author>
    <category term="{it['category']}"/>
    <summary type="text">{summary_el}</summary>
  </entry>"""
        )

    feed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <id>https://greek-news-aggregator/feeds/main</id>
  <title>Greek News Aggregator — Top stories</title>
  <subtitle>Daily top stories from Kathimerini, generated {now_iso}</subtitle>
  <updated>{now_iso}</updated>
  <author><name>Greek News Aggregator</name></author>
  <link rel="self" href="https://greek-news-aggregator/feeds/main.xml"/>
{chr(10).join(entries_xml)}
</feed>
"""
    (FEED_DIR / "main.xml").write_text(feed_xml)

    # ── index.json ─────────────────────────────────────────────────
    if INDEX_PATH.exists():
        index = json.loads(INDEX_PATH.read_text())
    else:
        index = {"dates": [], "last_updated": ""}
    if TARGET_DATE not in index["dates"]:
        index["dates"].append(TARGET_DATE)
    # sort newest-first
    index["dates"].sort(reverse=True)
    index["last_updated"] = now_iso
    INDEX_PATH.write_text(json.dumps(index, ensure_ascii=False, indent=2))

    print(f"Built {total} articles into {DAY_DIR}")
    print(f"Categories: {dict((c, len(cat_items[c])) for c in CATEGORIES)}")
    print(f"Top 20 atom feed written to {FEED_DIR}/main.xml")
    print(f"Index dates: {index['dates'][:5]}...")
    print(f"Missing analyses: {len(missing)}")


if __name__ == "__main__":
    build()
