#!/usr/bin/env python3
"""Build per-category JSON, summary.json, and Atom feed from scraped articles.
This script is generated for a specific run - do not edit manually.
"""
import json
import os
import sys
from datetime import datetime, timezone

TARGET_DATE = "2026-05-11"
RAW_PATH = "/sessions/zen-trusting-ritchie/tmp/collected_raw.json"
OUT_ROOT = "/sessions/zen-trusting-ritchie/mnt/greek-news-aggregator/frontend/static/data"

# Per-article analyses keyed by URL hash id.
# fields: el (Greek summary), en (English summary), tel (Greek tags),
#         ten (English tags), s (sentiment), i (importance 1-100)
ANALYSES = {
    # politics
    "https://www.kathimerini.gr/politics/564220021/pothen-esches-ti-dilonei-o-proedros-tis-voylis-nikitas-kaklamanis-2/": {
        "el": "Δημοσιοποιήθηκε η δήλωση «πόθεν έσχες» του προέδρου της Βουλής Νικήτα Κακλαμάνη για τη χρήση 2024. Δηλώνει συνολικό καθαρό εισόδημα από μισθωτές υπηρεσίες 57.599 ευρώ, καταθέσεις 234.000 ευρώ και άλλα στοιχεία περιουσιακής κατάστασης.",
        "en": "Speaker of Parliament Nikitas Kaklamanis publishes his asset declaration ('pothen esches') for fiscal year 2024. He reports total net salaried income of €57,599 and bank deposits of €234,000 alongside other holdings.",
        "tel": ["πόθεν έσχες", "Κακλαμάνης", "Βουλή", "διαφάνεια"],
        "ten": ["asset declaration", "Kaklamanis", "parliament", "transparency"],
        "s": "neutral", "i": 55,
    },
    "https://www.kathimerini.gr/politics/564220012/pothen-esches-ti-dilonei-o-kyriakos-mitsotakis-kai-i-syzygos-toy-mareva-gkrampofski/": {
        "el": "Στη δημοσιότητα η δήλωση «πόθεν έσχες» του πρωθυπουργού Κυριάκου Μητσοτάκη και της συζύγου του Μαρέβας Γκραμπόφσκι, χωρίς ουσιαστικές μεταβολές σε σχέση με πέρυσι. Δηλώνει εισόδημα από μισθούς 35.916 ευρώ, ακίνητα 10.700 ευρώ και επενδυτικά προϊόντα.",
        "en": "Prime Minister Kyriakos Mitsotakis and wife Mareva Grabowski file their 2025 asset declaration, showing no major changes from last year. He reports €35,916 in salary, €10,700 in property income and various investment holdings.",
        "tel": ["Μητσοτάκης", "πόθεν έσχες", "διαφάνεια", "πρωθυπουργός"],
        "ten": ["Mitsotakis", "asset declaration", "transparency", "prime minister"],
        "s": "neutral", "i": 68,
    },
    "https://www.kathimerini.gr/politics/564219838/sti-dimosiotita-ta-pothen-esches-ton-politikon/": {
        "el": "Δημοσιοποιήθηκαν 1.854 δηλώσεις «πόθεν έσχες» βουλευτών, ευρωβουλευτών, δημάρχων και περιφερειαρχών για τη χρήση 2024. Οι δηλώσεις θα παραμείνουν αναρτημένες για τρία χρόνια στον διαδικτυακό τόπο της Βουλής των Ελλήνων.",
        "en": "Greek authorities publish 1,854 asset declarations from MPs, MEPs, mayors and regional governors for fiscal year 2024. The disclosures will remain online on the Parliament's website for three years.",
        "tel": ["πόθεν έσχες", "διαφάνεια", "Βουλή", "δημόσιο"],
        "ten": ["asset declarations", "transparency", "parliament", "public office"],
        "s": "neutral", "i": 60,
    },
    "https://www.kathimerini.gr/politics/parties/564217513/machi-metaxy-toys-kai-me-to-parelthon-toys/": {
        "el": "Ανάλυση για τον ανταγωνισμό μεταξύ ΠΑΣΟΚ και του υπό διαμόρφωση κόμματος Τσίπρα για τη δεύτερη θέση στην αντιπολίτευση. Ο ΣΥΡΙΖΑ παραμένει σε παράλυση, ενώ το νέο εγχείρημα θα λειτουργήσει ως καταλύτης για την ανασύνθεση της Κεντροαριστεράς-Αριστεράς.",
        "en": "Analysis of the contest between PASOK and Tsipras' new party for second place in the opposition. SYRIZA remains paralysed in the post-Tsipras era while the new venture is expected to reshape Greece's centre-left.",
        "tel": ["ΠΑΣΟΚ", "Τσίπρας", "ΣΥΡΙΖΑ", "αντιπολίτευση"],
        "ten": ["PASOK", "Tsipras", "SYRIZA", "opposition"],
        "s": "neutral", "i": 72,
    },
    "https://www.kathimerini.gr/politics/parties/564217423/anametrisi-se-dyo-faseis-gia-ti-2i-thesi/": {
        "el": "Ανάλυση για τις δύο φάσεις της μάχης ΠΑΣΟΚ-Τσίπρα για τη δεύτερη θέση εν όψει εκλογών. Δημοσκοπικά οι Ανδρουλάκης, Τσίπρας και Καρυστιανού καταγράφουν μικρές διαφορές, ενώ ο Σαμαράς εξετάζει επίσης την επιστροφή του.",
        "en": "Analysis of the two-phase battle between PASOK and Tsipras' party for second place ahead of elections. Polls show small gaps between Androulakis, Tsipras and Karystianou, with Samaras also weighing a return.",
        "tel": ["ΠΑΣΟΚ", "Τσίπρας", "δημοσκοπήσεις", "εκλογές"],
        "ten": ["PASOK", "Tsipras", "polls", "opposition"],
        "s": "neutral", "i": 70,
    },
    "https://www.kathimerini.gr/politics/564219718/pethane-o-proin-voyleytis-tis-nd-christos-fotopoylos/": {
        "el": "Απεβίωσε σε ηλικία 98 ετών ο πρώην βουλευτής Αιτωλοακαρνανίας της Νέας Δημοκρατίας Χρήστος Φωτόπουλος. Διετέλεσε βουλευτής 1977-1989 και ήταν απόφοιτος της Στρατιωτικής Σχολής Ευελπίδων, με τον βαθμό του αντιστράτηγου ε.α.",
        "en": "Former New Democracy MP for Aetolia-Acarnania Christos Fotopoulos has died at the age of 98. He served as MP from 1977 to 1989 and was a graduate of the Evelpidon Military Academy, retired with the rank of lieutenant-general.",
        "tel": ["νεκρολογία", "ΝΔ", "Φωτόπουλος"],
        "ten": ["obituary", "New Democracy", "Fotopoulos"],
        "s": "negative", "i": 30,
    },
    "https://www.kathimerini.gr/politics/564219544/anartisi-tsipra-to-taxidi-synechizetai-i-mipos-tora-molis-archizei/": {
        "el": "Ο Αλέξης Τσίπρας ανήρτησε βίντεο-απολογισμό από τις παρουσιάσεις της «Ιθάκης» σε εννέα πόλεις, προαναγγέλλοντας την έναρξη ενός «ταξιδιού» που σηματοδοτεί το νέο πολιτικό φορέα. Συμμετέχει σήμερα σε εκδήλωση στη Ρεματιά Χαλανδρίου.",
        "en": "Former PM Alexis Tsipras posts a video summary of his nine-city 'Ithaca' book tour, previewing the launch of his new political party. He appears today at an event in Chalandri's Rematia theatre.",
        "tel": ["Τσίπρας", "νέο κόμμα", "Ιθάκη"],
        "ten": ["Tsipras", "new party", "Ithaca", "opposition"],
        "s": "positive", "i": 72,
    },
    "https://www.kathimerini.gr/politics/564217579/theoreio-makria-kai-ochi-agapimenoi-2/": {
        "el": "Στήλη «Θεωρείο» για την αναγόρευση του Ευάγγελου Βενιζέλου σε επίτιμο διδάκτορα από το ΕΚΠΑ, όπου οι πρώην Πρόεδροι Σακελλαροπούλου και Παυλόπουλος παρευρέθηκαν σχεδόν δίπλα-δίπλα διατηρώντας ψυχρή στάση. Σχολιάζεται η παρουσία Σαμαρά, Δένδια και Ανδρουλάκη στην εκδήλωση.",
        "en": "The 'Theoreio' column on Evangelos Venizelos receiving an honorary doctorate from Athens University, with former Presidents Sakellaropoulou and Pavlopoulos seated coolly side by side. The column also notes the presence of Samaras, Dendias and PASOK leader Androulakis.",
        "tel": ["Θεωρείο", "Βενιζέλος", "πολιτικά παρασκήνια"],
        "ten": ["Theoreio", "Venizelos", "honorary doctorate", "political gossip"],
        "s": "neutral", "i": 45,
    },
    "https://www.kathimerini.gr/politics/564219463/ad-georgiadis-kanenas-apolytos-fovos-exaplosis-toy-chantaioy-stin-ellada/": {
        "el": "Ο υπουργός Υγείας Αδωνις Γεωργιάδης διαβεβαιώνει ότι δεν υπάρχει κίνδυνος εξάπλωσης του ιού χανταϊού στην Ελλάδα. Ο Έλληνας επιβάτης του κρουαζιερόπλοιου «MV Hondius» μεταφέρθηκε με ειδική πτήση στο νοσοκομείο «Αττικόν» όπου τέθηκε σε καραντίνα 45 ημερών.",
        "en": "Health Minister Adonis Georgiadis insists there is no risk of hantavirus spreading in Greece. The Greek passenger from the MV Hondius cruise ship was airlifted to Attikon Hospital for a 45-day precautionary quarantine.",
        "tel": ["χανταϊός", "υγεία", "καραντίνα", "Γεωργιάδης"],
        "ten": ["hantavirus", "public health", "quarantine", "Georgiadis"],
        "s": "neutral", "i": 78,
    },
    "https://www.kathimerini.gr/politics/564219406/i-synenteyxi-dimitriadi-kai-oi-antidraseis-tis-antipoliteysis/": {
        "el": "Ο πρώην γενικός γραμματέας του Μαξίμου Γρηγόρης Δημητριάδης μίλησε για τις υποκλοπές, στρεφόμενος κατά των Τσίπρα και Ανδρουλάκη. Δήλωσε ότι ανέλαβε την πολιτική ευθύνη για να προστατεύσει την κυβέρνηση και ξεκαθάρισε ότι δεν θα είναι υποψήφιος στις εκλογές.",
        "en": "Former PM aide Grigoris Dimitriadis spoke out on the wiretapping scandal, attacking both Tsipras and Androulakis. He said he assumed political responsibility to protect the government and ruled out running in any election.",
        "tel": ["υποκλοπές", "Δημητριάδης", "Μαξίμου"],
        "ten": ["wiretaps", "Dimitriadis", "Maximos", "scandal"],
        "s": "negative", "i": 70,
    },
    "https://www.kathimerini.gr/politics/564219271/v-kikilias-oi-eyropaikes-igesies-prepei-na-paremvainoyn-noritera-kai-pio-egkaira/": {
        "el": "Ο υπουργός Ναυτιλίας Βασίλης Κικίλιας ζήτησε ταχύτερη και ενεργότερη ευρωπαϊκή παρέμβαση, σημειώνοντας πως οι εθνικοί προϋπολογισμοί δεν έχουν συντονιστεί για συνθήκες πολέμου. Ανέφερε επιπτώσεις στον τουρισμό και τη ναυτιλία λόγω της κρίσης στη Μέση Ανατολή.",
        "en": "Shipping Minister Vassilis Kikilias called for faster, earlier European intervention, saying national budgets were not designed for wartime conditions. He cited fallout for tourism and shipping from the Middle East crisis.",
        "tel": ["Κικίλιας", "ΕΕ", "πόλεμος", "οικονομία"],
        "ten": ["Kikilias", "EU", "war", "economy"],
        "s": "neutral", "i": 62,
    },
    "https://www.kathimerini.gr/opinion/interviews/564217555/andreas-drakopoylos-stin-k-den-mas-zitoyn-roysfetia-xeroyn-oti-den-kanoyme/": {
        "el": "Ο Ανδρέας Δρακόπουλος, πρόεδρος του Ιδρύματος Σταύρος Νιάρχος, δηλώνει ότι το Ίδρυμα συμπληρώνει αντί να υποκαθιστά το κράτος και αρνείται τη λογική του «ρουσφετιού». Δέκα χρόνια μετά τη δημιουργία του ΚΠΙΣΝ μιλά για το κίνημα προσφοράς στην Ελλάδα.",
        "en": "Andreas Drakopoulos, president of the Stavros Niarchos Foundation, says the Foundation supplements rather than replaces the state and refuses to engage in clientelism. Ten years after the SNFCC opened, he discusses the rise of philanthropy in Greece.",
        "tel": ["ΙΣΝ", "φιλανθρωπία", "συνέντευξη"],
        "ten": ["SNF", "philanthropy", "Drakopoulos", "interview"],
        "s": "positive", "i": 55,
    },
    "https://www.kathimerini.gr/world/564219214/floisvos-entyposiako-airshow-gia-ta-95-chronia-tis-polemikis-aeroporias/": {
        "el": "Πραγματοποιήθηκε εντυπωσιακό airshow στον Φλοίσβο για τα 95 χρόνια της Πολεμικής Αεροπορίας. Η εκδήλωση περιελάμβανε σχηματισμούς ιστορικών και σύγχρονων αεροσκαφών (Spitfire, Phantom, F-16, Rafale) και τις ομάδες «Ζευς» και «Δαίδαλος».",
        "en": "An impressive airshow took place at Flisvos to mark 95 years of the Greek Air Force. Historic and modern aircraft including the Spitfire, Phantom, F-16 and Rafale joined display teams Zeus and Daedalus.",
        "tel": ["Πολεμική Αεροπορία", "Φλοίσβος", "επέτειος"],
        "ten": ["air force", "Flisvos", "anniversary", "military"],
        "s": "positive", "i": 50,
    },
    "https://www.kathimerini.gr/politics/foreign-policy/564219088/g-gerapetritis-metavainei-stis-vryxelles-gia-to-symvoylio-exoterikon-ypotheseon-tis-e-e/": {
        "el": "Ο υπουργός Εξωτερικών Γιώργος Γεραπετρίτης μεταβαίνει στις Βρυξέλλες για το Συμβούλιο Εξωτερικών Υποθέσεων της ΕΕ. Στην ατζέντα τα Δυτικά Βαλκάνια, η Μέση Ανατολή και ο πόλεμος στην Ουκρανία, με προσκεκλημένη την Καναδή υπουργό Εξωτερικών Ανίτα Ανάντ.",
        "en": "Foreign Minister Giorgos Gerapetritis travels to Brussels for the EU Foreign Affairs Council. Top agenda items include the Western Balkans, the Middle East and the war in Ukraine, with Canadian Foreign Minister Anita Anand as guest.",
        "tel": ["Γεραπετρίτης", "ΕΕ", "Βρυξέλλες", "διπλωματία"],
        "ten": ["foreign policy", "EU", "Gerapetritis", "Brussels"],
        "s": "neutral", "i": 62,
    },

    # economy
    "https://www.kathimerini.gr/economy/564218026/monoi-sto-spiti-moy-ii/": {
        "el": "Κριτικό σχόλιο για την κυβερνητική απόφαση να συντομευθεί η προθεσμία υπαγωγής στο «Σπίτι μου ΙΙ» από τέλη Αυγούστου σε 2 Ιουνίου. Η αλλαγή προκαλεί αναστάτωση σε όσους είχαν προγραμματίσει εκταμιεύσεις βάσει του αρχικού χρονοδιαγράμματος.",
        "en": "Critical column on the government's decision to shorten the deadline for the 'Spiti Mou II' housing scheme from end-August to June 2. The change disrupts prospective beneficiaries who had planned around the original timeline.",
        "tel": ["στέγαση", "Σπίτι μου", "κυβέρνηση"],
        "ten": ["housing", "Spiti Mou", "government", "criticism"],
        "s": "negative", "i": 65,
    },
    "https://www.kathimerini.gr/economy/international/564219817/aramco-ektoxeysi-kerdon-gia-ton-petrelaiko-kolosso-para-ti-sygkroysi-sti-mesi-anatoli/": {
        "el": "Η Saudi Aramco ανακοίνωσε εκτόξευση κερδών 25% στα 33,6 δισ. δολάρια το πρώτο τρίμηνο του 2026, παρά τη σύγκρουση στη Μέση Ανατολή. Ο αγωγός Ανατολής-Δύσης λειτούργησε στη μέγιστη χωρητικότητα των 7 εκατ. βαρελιών ημερησίως, αντισταθμίζοντας τους περιορισμούς στα Στενά του Ορμούζ.",
        "en": "Saudi Aramco reports a 25% profit jump to $33.6 billion in Q1 2026 despite the Middle East conflict. The East-West pipeline hit its 7 million barrel-a-day peak capacity, offsetting shipping disruptions in the Strait of Hormuz.",
        "tel": ["Aramco", "πετρέλαιο", "Σαουδική Αραβία"],
        "ten": ["Aramco", "oil", "Saudi Arabia", "energy"],
        "s": "positive", "i": 68,
    },
    "https://www.kathimerini.gr/economy/local/564219808/h-blackstone-exagorazei-ti-skroutz-apo-ti-cvc-sta-635-ekat-eyro-i-apotimisi/": {
        "el": "Η Blackstone εξαγοράζει πλειοψηφικό μερίδιο της Skroutz από τη CVC Capital Partners με αποτίμηση 635 εκατ. ευρώ, συμπεριλαμβανομένου του χρέους. Οι ιδρυτές παραμένουν στη διοίκηση και η συναλλαγή θα ολοκληρωθεί στο δεύτερο εξάμηνο του 2026.",
        "en": "Blackstone is acquiring a majority stake in Greek e-commerce platform Skroutz from CVC Capital Partners at a €635 million enterprise value. The founders remain on the board and the deal will close in H2 2026.",
        "tel": ["Blackstone", "Skroutz", "εξαγορά"],
        "ten": ["Blackstone", "Skroutz", "M&A", "ecommerce"],
        "s": "positive", "i": 80,
    },
    "https://www.kathimerini.gr/economy/564218044/mpiznes-1-tris-dolarion-sto-diastima/": {
        "el": "Η αποστολή Artemis II της NASA σηματοδότησε νέο κύκλο επενδύσεων ύψους ενός τρισ. δολαρίων στη διαστημική βιομηχανία την επόμενη δεκαετία. Εταιρείες όπως η Blue Origin σχεδιάζουν ανάπτυξη χιλιάδων δορυφόρων, ενώ νέοι τομείς όπως η εξόρυξη στο Διάστημα κερδίζουν έδαφος.",
        "en": "NASA's Artemis II mission signals a new investment cycle worth $1 trillion in the global space industry over the next decade. Companies like Blue Origin plan to deploy thousands of satellites, while frontiers such as space mining are gaining momentum.",
        "tel": ["Διάστημα", "NASA", "Artemis", "επενδύσεις"],
        "ten": ["space", "NASA", "Artemis", "investment"],
        "s": "positive", "i": 60,
    },
    "https://www.kathimerini.gr/economy/564217885/adilota-pos-aorates-synallages/": {
        "el": "Νέα μορφή φοροδιαφυγής εντοπίζει ο φοροελεγκτικός μηχανισμός με αδήλωτα POS που εκδίδουν αποδείξεις αλλά δεν διαβιβάζονται στην ΑΑΔΕ. Παρότι η διασύνδεση POS-ταμειακών έφερε άνω των 2,5 δισ. ευρώ έσοδα, νέο εξελιγμένο δίκτυο φοροαπάτης παρακάμπτει τα ηλεκτρονικά συστήματα ελέγχου.",
        "en": "Greek tax authorities are uncovering a new evasion scheme involving undeclared POS terminals that issue receipts but never transmit transactions to AADE. Despite the POS-cash register link generating €2.5+ billion in revenue, an evolved fraud network is sidestepping electronic controls.",
        "tel": ["φοροδιαφυγή", "POS", "ΑΑΔΕ"],
        "ten": ["tax evasion", "POS", "AADE", "fraud"],
        "s": "negative", "i": 72,
    },
    "https://www.kathimerini.gr/economy/564217927/poioi-idioktites-chanoyn-to-anakainizo-noikiazo/": {
        "el": "Από το πρόγραμμα «Ανακαινίζω-Νοικιάζω» αποκλείονται περιπτώσεις πολυϊδιοκτησίας και ακίνητα με αρρύθμιστα χρέη. Το υπουργείο Οικονομικών έχει εντοπίσει 400.000 κλειστά ακίνητα ως δυνητικά δικαιούχα, αλλά η επανένταξή τους στην αγορά παραμένει αβέβαιη.",
        "en": "Properties with multiple owners or unresolved debts are excluded from the 'Renovate-Rent' programme. The Finance Ministry has identified 400,000 closed homes as potential candidates, but their return to the rental market remains uncertain.",
        "tel": ["στέγαση", "ακίνητα", "ανακαίνιση"],
        "ten": ["housing", "real estate", "renovation", "policy"],
        "s": "neutral", "i": 60,
    },
    "https://www.kathimerini.gr/economy/564217966/arthro-tis-agapis-smpokoy-stin-k-o-neos-kyklos-toy-ellinikoy-toyrismoy/": {
        "el": "Άρθρο γνώμης της Αγάπης Σμπώκου για τον νέο κύκλο του ελληνικού τουρισμού. Προτείνει μετάβαση από τη μέτρηση επιτυχίας σε αριθμούς προς πιο ώριμη ανάπτυξη, με έμφαση στους ανθρώπους, την τεχνολογία και τη δίκαιη διάχυση της αξίας.",
        "en": "Op-ed by Agapi Sbokou on the next phase of Greek tourism. She urges a shift from measuring success in raw numbers to a more mature model focused on people, technology and equitable value distribution.",
        "tel": ["τουρισμός", "οικονομία", "ανάπτυξη"],
        "ten": ["tourism", "opinion", "Greece", "economy"],
        "s": "positive", "i": 55,
    },

    # society
    "https://www.kathimerini.gr/society/564220000/rodos-syllipsi-36chronoy-gia-viasmo-21chronis/": {
        "el": "Συνελήφθη 36χρονος Έλληνας στη Ρόδο με την κατηγορία βιασμού 21χρονης συναδέλφου του από την Αυστρία. Η πράξη φέρεται να τελέσθηκε στις 04:00 του Σαββάτου και ακολούθησε η σύλληψη του δράστη το βράδυ της Κυριακής.",
        "en": "A 36-year-old Greek man was arrested in Rhodes for the alleged rape of a 21-year-old Austrian colleague. The assault reportedly took place at 4 AM on Saturday and the suspect was arrested Sunday evening.",
        "tel": ["έγκλημα", "βιασμός", "Ρόδος", "σύλληψη"],
        "ten": ["crime", "rape", "Rhodes", "arrest"],
        "s": "negative", "i": 65,
    },
    "https://www.kathimerini.gr/life/health/564217693/tzeims-nestor-stin-k-giati-prepei-na-mathoyme-pos-na-anapneoyme/": {
        "el": "Συνέντευξη του Αμερικανού δημοσιογράφου Τζέιμς Νέστορ, συγγραφέα του best seller «ΑΝΑΣΑ». Εξηγεί πώς η σωστή αναπνοή μπορεί να μειώσει το άγχος, να βελτιώσει την ποιότητα ύπνου και τη συγκέντρωση. Θα δώσει Breathing Masterclass στην Αθήνα τον Οκτώβριο.",
        "en": "Interview with American journalist James Nestor, author of the NYT bestseller 'Breath.' He explains how proper breathing can reduce stress, improve sleep quality and boost focus. He will hold a Breathing Masterclass in Athens in October.",
        "tel": ["υγεία", "αναπνοή", "συνέντευξη"],
        "ten": ["health", "breathing", "interview", "wellness"],
        "s": "positive", "i": 40,
    },
    "https://www.kathimerini.gr/society/564219967/trochaio-dystychima-stin-ko-nekros-55chronos-stin-periochi-psalidi/": {
        "el": "Θανατηφόρο τροχαίο στην Κω: 55χρονος οδηγός σκοτώθηκε όταν το αυτοκίνητό του εκτράπηκε στην περιοχή Ψαλίδι και προσέκρουσε σε δέντρο. Τα ακριβή αίτια διερευνώνται από την Τροχαία.",
        "en": "Fatal road accident in Kos: a 55-year-old driver was killed when his car veered off the road in Psalidi and struck a tree. Traffic police are investigating the exact cause.",
        "tel": ["τροχαίο", "Κως", "θάνατος"],
        "ten": ["accident", "Kos", "fatal", "traffic"],
        "s": "negative", "i": 35,
    },
    "https://www.kathimerini.gr/society/564219916/irakleio-ayrio-apologeitai-o-30chronos-poy-paresyre-me-ich-ti-syzygo-toy-sovari-i-katastasi-tis-28chronis/": {
        "el": "Στις Αρχές Ηρακλείου απολογείται 30χρονος που παρέσυρε με Ι.Χ. τη 28χρονη σύζυγό του, μητέρα τεσσάρων παιδιών. Η γυναίκα νοσηλεύεται με κρανιοεγκεφαλικές κακώσεις σε σοβαρή αλλά όχι κρίσιμη κατάσταση. Ο δράστης αντιμετωπίζει κατηγορία απόπειρας ανθρωποκτονίας.",
        "en": "A 30-year-old man in Heraklion will appear before authorities for running over his 28-year-old wife, a mother of four, with their car. She is hospitalised with serious but stable head and neck injuries; he faces attempted murder charges.",
        "tel": ["ενδοοικογενειακή βία", "Ηράκλειο", "ανθρωποκτονία"],
        "ten": ["domestic violence", "Heraklion", "attempted murder", "crime"],
        "s": "negative", "i": 75,
    },
    "https://www.kathimerini.gr/society/564219844/chantaios-choris-symptomata-o-ellinas-epivatis-toy-hondius-i-anakoinosi-toy-attikon/": {
        "el": "Σε προληπτική καραντίνα 45 ημερών στο νοσοκομείο «Αττικόν» τέθηκε ο Έλληνας επιβάτης του κρουαζιερόπλοιου «MV Hondius», όπου εμφανίστηκαν κρούσματα χανταϊού. Σύμφωνα με ανακοίνωση του νοσοκομείου, δεν παρουσιάζει συμπτώματα και η απομόνωση είναι αμιγώς προληπτική.",
        "en": "The Greek passenger from the MV Hondius cruise ship has been placed in 45-day preventative quarantine at Attikon Hospital after hantavirus cases were detected on board. According to the hospital, he is asymptomatic and isolation is purely precautionary.",
        "tel": ["χανταϊός", "καραντίνα", "Αττικόν"],
        "ten": ["hantavirus", "quarantine", "public health", "Attikon"],
        "s": "neutral", "i": 75,
    },
    "https://www.kathimerini.gr/society/astynomiko/564219820/listeia-me-kalasnikof-stin-kato-tithorea/": {
        "el": "Ένοπλη ληστεία 200.000 ευρώ σε τράπεζα στην Κάτω Τιθορέα. Τρεις δράστες, εκ των οποίων δύο ένοπλοι με καλάσνικοφ και πιστόλι, παρέμειναν 30 λεπτά εντός του καταστήματος λόγω χρονοκαθυστέρησης του χρηματοκιβωτίου και διέφυγαν προς τον Παρνασσό.",
        "en": "An armed robbery in Kato Tithorea netted €200,000 from a bank branch. Three robbers, two armed with a Kalashnikov and a pistol, stayed 30 minutes inside due to the safe's time delay, then fled toward Parnassus. A manhunt is underway.",
        "tel": ["έγκλημα", "ληστεία", "τράπεζα"],
        "ten": ["crime", "robbery", "bank", "Tithorea"],
        "s": "negative", "i": 70,
    },
    "https://www.kathimerini.gr/society/564219775/chania-neo-atychima-me-ilektriko-patini-sto-nosokomeio-dyo-15chronoi/": {
        "el": "Δύο 15χρονοι τραυματίστηκαν στα Χανιά όταν το ηλεκτρικό πατίνι που οδηγούσαν μαζί έχασε τον έλεγχο σε κατηφορικό δρόμο. Μεταφέρθηκαν στο Γενικό Νοσοκομείο Χανίων χωρίς να κινδυνεύει η ζωή τους.",
        "en": "Two 15-year-olds were injured in Chania when the e-scooter they were sharing lost control on a downhill street. Both were taken to Chania General Hospital and are not in life-threatening condition.",
        "tel": ["ατύχημα", "πατίνι", "Χανιά"],
        "ten": ["accident", "e-scooter", "Chania", "teens"],
        "s": "negative", "i": 35,
    },
    "https://www.kathimerini.gr/society/564219772/kriti-kleisto-to-epal-moiron-logo-kroysmatos-vaktiriakis-miniggitidas/": {
        "el": "Κλειστό για προληπτικούς λόγους θα παραμείνει το ΕΠΑΛ Μοιρών στην Κρήτη μετά από κρούσμα βακτηριακής μηνιγγίτιδας σε μαθήτρια της Γ' Λυκείου. Η ασθενής έχει λάβει την αναγκαία φαρμακευτική αγωγή και η κατάστασή της κρίνεται καλή.",
        "en": "The vocational high school in Moires, Crete is closed as a precaution after a bacterial meningitis case in a third-year student. She is receiving medication and her condition is described as good.",
        "tel": ["υγεία", "μηνιγγίτιδα", "Κρήτη"],
        "ten": ["health", "meningitis", "Crete", "school"],
        "s": "negative", "i": 55,
    },
    "https://www.kathimerini.gr/society/564219757/metallica-sto-oaka-pos-scholiasan-oi-trypes-ti-diaskeyi-toy-den-choras-poythena/": {
        "el": "Τα μέλη του ροκ συγκροτήματος «Τρύπες» σχολίασαν θετικά τη διασκευή των Metallica στο «Δεν χωράς πουθενά» στο ΟΑΚΑ. Ο Μπάμπης Παπαδόπουλος και ο Γιώργος Καρράς εξέφρασαν συγκίνηση για την τιμή αυτή προς την ελληνική ροκ σκηνή.",
        "en": "Members of Greek rock band Trypes warmly received Metallica's cover of 'Den Choras Pouthena' at OAKA. Babis Papadopoulos and Giorgos Karras expressed deep emotion at the gesture honouring the Greek rock scene.",
        "tel": ["μουσική", "Metallica", "Τρύπες"],
        "ten": ["music", "Metallica", "Trypes", "OAKA"],
        "s": "positive", "i": 50,
    },
    "https://www.kathimerini.gr/society/564219724/xanthi-vrefos-entopistike-nekro-se-oikismo-synelifthi-i-mitera/": {
        "el": "Νεογέννητο βρέφος εντοπίστηκε νεκρό σε εγκαταλελειμμένο σπίτι σε οικισμό στην Ξάνθη. Η μητέρα συνελήφθη από το Τμήμα Δίωξης Εγκλημάτων και κατηγορείται για έκθεση ανηλίκου σε κίνδυνο, ενώ αναμένεται νεκροψία-νεκροτομή.",
        "en": "A newborn baby was found dead in an abandoned house in a Xanthi settlement. The mother has been arrested and charged with endangering a minor; an autopsy is pending to determine cause of death.",
        "tel": ["έγκλημα", "Ξάνθη", "βρέφος"],
        "ten": ["crime", "Xanthi", "infant death", "arrest"],
        "s": "negative", "i": 65,
    },
    "https://www.kathimerini.gr/society/564219658/kriti-nees-epicheiriseis-diasosis-metanaston/": {
        "el": "Δύο νέα περιστατικά διάσωσης μεταναστών στα νότια της Κρήτης. Σκάφος της Frontex εντόπισε 56 άτομα 23 ν.μ. ΝΑ των Καλών Λιμένων και ναυαγοσωστικό σκάφος διέσωσε άλλους 44. Την Κυριακή είχαν καταγραφεί τέσσερα ανάλογα περιστατικά.",
        "en": "Two more migrant rescues took place south of Crete. A Frontex vessel located 56 people in a boat 23 nautical miles SE of Kaloi Limenes, while a rescue boat saved 44 more. Four similar operations were recorded on Sunday.",
        "tel": ["μετανάστευση", "Κρήτη", "διάσωση"],
        "ten": ["migration", "Crete", "rescue", "Frontex"],
        "s": "neutral", "i": 70,
    },
    "https://www.kathimerini.gr/society/564219601/thessaloniki-cheiropedes-se-48chrono-gia-parenochlisi-dyo-nearon-se-parko/": {
        "el": "Συνελήφθη 48χρονος στη Θεσσαλονίκη για προσβολή γενετήσιας αξιοπρέπειας δύο νεαρών σε πάρκο της Τούμπας. Σχηματίσθηκε δικογραφία και ο κατηγορούμενος θα οδηγηθεί στην αρμόδια δικαστική αρχή.",
        "en": "A 48-year-old man was arrested in Thessaloniki for sexual harassment of two young men in a park in the Toumba district. A criminal case has been filed and he will be brought before the judicial authorities.",
        "tel": ["έγκλημα", "Θεσσαλονίκη", "παρενόχληση"],
        "ten": ["crime", "Thessaloniki", "harassment", "arrest"],
        "s": "negative", "i": 40,
    },
    "https://www.kathimerini.gr/society/564219595/thessaloniki-se-exelixi-oi-ereynes-ston-loydia-gia-ti-soro-toy-54chronoy-ston-eisaggelea-oi-dyo-syllifthentes/": {
        "el": "Συνεχίζονται οι έρευνες στον Λουδία για τη σορό 54χρονου θύματος δολοφονίας, στο πλαίσιο υπόθεσης με διαφορές για ναρκωτικά. Συνελήφθησαν δύο άνδρες (43 και 44 ετών) που φέρεται να ομολόγησαν την εμπλοκή τους και οδηγούνται στον εισαγγελέα.",
        "en": "Police continue searching the Loudias river for the body of a 54-year-old murder victim killed in a dispute over drugs. Two men aged 43 and 44 have reportedly confessed their involvement and are being sent to the prosecutor.",
        "tel": ["έγκλημα", "Θεσσαλονίκη", "δολοφονία"],
        "ten": ["crime", "murder", "Thessaloniki", "drugs"],
        "s": "negative", "i": 60,
    },
    "https://www.kathimerini.gr/society/564219520/chantaios-sto-attikon-proliptika-o-ellinas-epivatis-toy-hondius/": {
        "el": "Στο νοσοκομείο «Αττικόν» μεταφέρθηκε προληπτικά ο Έλληνας επιβάτης του «MV Hondius» όπου τέθηκε σε καραντίνα 45 ημερών σε θάλαμο αρνητικής πίεσης. Σύμφωνα με τον υπουργό Υγείας, ο επιβάτης είναι απύρετος και ασυμπτωματικός, χωρίς λόγο ανησυχίας.",
        "en": "The Greek passenger from the MV Hondius cruise ship was preventatively transferred to Attikon Hospital and placed in 45-day isolation in a negative-pressure room. According to the Health Minister, he is afebrile and asymptomatic; there is no cause for concern.",
        "tel": ["χανταϊός", "Αττικόν", "καραντίνα"],
        "ten": ["hantavirus", "Attikon", "quarantine", "health"],
        "s": "neutral", "i": 70,
    },

    # world
    "https://www.kathimerini.gr/world/564219994/starmer-tha-diapseyso-toys-epikrites-moy/": {
        "el": "Ο Βρετανός πρωθυπουργός Κιρ Στάρμερ προσπαθεί να ανακόψει την εσωκομματική δυσαρέσκεια μετά τη βαριά εκλογική ήττα των Εργατικών στις τοπικές εκλογές. Δηλώνει ότι θα διαψεύσει τους επικριτές του και πως «οι σταδιακές αλλαγές δεν επαρκούν» για τη Βρετανία.",
        "en": "British PM Keir Starmer is trying to stem internal Labour dissent after the party's heavy local-election defeat. He vows to defy critics and says 'incremental change is not enough' for a Britain in stagnation.",
        "tel": ["Βρετανία", "Στάρμερ", "Εργατικοί"],
        "ten": ["UK", "Starmer", "Labour", "politics"],
        "s": "negative", "i": 78,
    },
    "https://www.kathimerini.gr/world/564219988/bafta-tv-awards-2026-to-adolescence-kyriarchise-sta-vretanika-vraveia/": {
        "el": "Η σειρά «Adolescence» του Netflix αναδείχθηκε ο μεγάλος νικητής στα τηλεοπτικά Βραβεία BAFTA 2026, κερδίζοντας τέσσερα βραβεία στο Royal Festival Hall: καλύτερης μίνι σειράς, α΄ ανδρικού ρόλου (Στίβεν Γκράχαμ) και β΄ ρόλων (Όουεν Κούπερ, Κριστίν Τρεμάρκο).",
        "en": "Netflix's 'Adolescence' was the big winner at the 2026 BAFTA TV Awards, taking four prizes at the Royal Festival Hall, including Best Mini-Series, Lead Actor (Stephen Graham) and Supporting roles (Owen Cooper, Christine Tremarco).",
        "tel": ["BAFTA", "Adolescence", "Netflix"],
        "ten": ["BAFTA", "Adolescence", "Netflix", "awards"],
        "s": "positive", "i": 50,
    },
    "https://www.kathimerini.gr/world/564219961/vretania-nees-kyroseis-kata-roson-axiomatoychon-mme-kai-organismon/": {
        "el": "Η Βρετανία επέβαλε νέες κυρώσεις σε δεκάδες Ρώσους αξιωματούχους, στελέχη ΜΜΕ και οργανισμούς, στοχεύοντας προγράμματα νεολαίας του Κρεμλίνου και δίκτυα προπαγάνδας. Από το 2022 η Βρετανία έχει επιβάλει κυρώσεις σε άνω των 3.200 ατόμων και επιχειρήσεων.",
        "en": "Britain imposed fresh sanctions on dozens of Russian officials, media figures and organisations, targeting Kremlin-controlled youth programmes and propaganda networks. Since 2022 the UK has sanctioned over 3,200 entities.",
        "tel": ["κυρώσεις", "Βρετανία", "Ρωσία"],
        "ten": ["sanctions", "UK", "Russia", "Ukraine"],
        "s": "neutral", "i": 65,
    },
    "https://www.kathimerini.gr/world/564219934/oi-trampistes-tis-aystralias-katektisan-tin-proti-toys-edra-sto-koinovoylio/": {
        "el": "Το δεξιό λαϊκιστικό κόμμα «One Nation» στην Αυστραλία κατέκτησε την πρώτη του έδρα στην κάτω βουλή μετά τη νίκη του Ντέιβιντ Φάρλεϊ στις ενδιάμεσες εκλογές. Το κόμμα της Πολίν Χάνσον δηλώνει εμπνεόμενο από τη ρητορική Τραμπ για τις απελάσεις.",
        "en": "The right-wing populist 'One Nation' party in Australia won its first seat in the lower house after David Farley's by-election victory. Pauline Hanson's party openly emulates Trump's mass-deportation rhetoric.",
        "tel": ["Αυστραλία", "λαϊκισμός", "εκλογές"],
        "ten": ["Australia", "One Nation", "populism", "election"],
        "s": "negative", "i": 55,
    },
    "https://www.kathimerini.gr/world/564219928/toyrkia-xekina-i-diki-toy-ekrem-imamogloy-gia-politiki-kataskopeia/": {
        "el": "Ξεκίνησε στις φυλακές Μαρμαρά η δίκη του παυθέντος δημάρχου Κωνσταντινούπολης Εκρέμ Ιμάμογλου με κατηγορίες «πολιτικής κατασκοπείας». Η εισαγγελία ζητά κάθειρξη 15-20 ετών και πολιτική απαγόρευση για τον βασικό αντίπαλο του Ερντογάν.",
        "en": "The trial of suspended Istanbul mayor Ekrem Imamoglu opened at Marmara prison on 'political espionage' charges. Prosecutors seek 15-20 years' imprisonment and a political ban for Erdogan's main rival.",
        "tel": ["Τουρκία", "Ιμάμογλου", "δίκη"],
        "ten": ["Turkey", "Imamoglu", "trial", "espionage"],
        "s": "negative", "i": 80,
    },
    "https://www.kathimerini.gr/world/564219913/verolino-o-srenter-den-apotelei-entimo-mesolaviti-gia-synomilies-stin-oykrania/": {
        "el": "Το Βερολίνο απορρίπτει την πρόταση Πούτιν να μεσολαβήσει ο πρώην καγκελάριος Γκέρχαρντ Σρέντερ σε συνομιλίες για την Ουκρανία. Ο υπουργός για ευρωπαϊκά θέματα Γκίντερ Κρίχμπαουμ δηλώνει ότι ο Σρέντερ είναι πολύ επηρεασμένος από τον Πούτιν για ρόλο «έντιμου διαμεσολαβητή».",
        "en": "Berlin rejects Putin's proposal that former Chancellor Gerhard Schroeder mediate Ukraine talks. German EU Affairs Minister Guenter Krichbaum says Schroeder is too close to Putin to act as an 'honest broker.'",
        "tel": ["Γερμανία", "Σρέντερ", "Ουκρανία"],
        "ten": ["Germany", "Schroeder", "Putin", "Ukraine"],
        "s": "negative", "i": 65,
    },
    "https://www.kathimerini.gr/world/564219577/cnn-ti-mathainei-i-kina-apo-ton-polemo-ton-ipa-sto-iran/": {
        "el": "Ανάλυση του CNN για όσα μαθαίνει η Κίνα από τον πόλεμο ΗΠΑ-Ιράν, εν όψει πιθανού μέτωπου με την Ταϊβάν. Ειδικοί προειδοποιούν ότι το Πεκίνο κινδυνεύει να υπερεκτιμήσει τις δυνατότητές του και να υποτιμήσει την έλλειψη πολεμικής εμπειρίας.",
        "en": "CNN analysis on what China is learning from the US-Iran war, with an eye on a possible Taiwan scenario. Experts warn Beijing risks overestimating its own capabilities and underestimating its lack of combat experience.",
        "tel": ["Κίνα", "Ιράν", "ΗΠΑ", "Ταϊβάν"],
        "ten": ["China", "Iran", "US", "Taiwan"],
        "s": "neutral", "i": 75,
    },
    "https://www.kathimerini.gr/world/564219811/arthro-dimitri-avramopoyloy-stin-k-i-anagkaiotita-tis-synennoisis-ipa-kinas/": {
        "el": "Άρθρο γνώμης του πρώην Επιτρόπου Δημήτρη Αβραμόπουλου για τη συνάντηση Τραμπ-Σι ως δοκιμασία ευθύνης για το παγκόσμιο μέλλον. Επισημαίνει ότι η σχέση ΗΠΑ-Κίνας αποτελεί καθοριστικό άξονα παγκόσμιας σταθερότητας, πέρα από το εμπόριο και την τεχνολογία.",
        "en": "Op-ed by former EU Commissioner Dimitris Avramopoulos on the Trump-Xi meeting as a test of global responsibility. He argues the US-China relationship is now the decisive axis for global stability, beyond trade or technology.",
        "tel": ["ΗΠΑ", "Κίνα", "γεωπολιτική"],
        "ten": ["US", "China", "geopolitics", "opinion"],
        "s": "neutral", "i": 65,
    },
    "https://www.kathimerini.gr/world/564219799/iran-oi-protaseis-pros-tis-ipa-itan-gennaiodores-kai-ypeythynes/": {
        "el": "Το Ιράν χαρακτηρίζει «γενναιόδωρες και υπεύθυνες» τις προτάσεις του προς τις ΗΠΑ, ενώ ο Τραμπ τις απορρίπτει ως «εντελώς απαράδεκτες». Η Τεχεράνη ζητά τερματισμό του πολέμου, άρση αποκλεισμού και αποδέσμευση παγωμένων ιρανικών περιουσιακών στοιχείων.",
        "en": "Iran calls its proposals to the US 'generous and responsible' while Trump dismisses them as 'totally unacceptable.' Tehran demands an end to the war, lifting of the embargo and unfreezing of Iranian assets abroad.",
        "tel": ["Ιράν", "ΗΠΑ", "διπλωματία"],
        "ten": ["Iran", "US", "war", "diplomacy"],
        "s": "negative", "i": 82,
    },
    "https://www.kathimerini.gr/world/564219742/ypo-piesi-o-starmer-meta-tin-eklogiki-syntrivi-pos-schediazei-na-anastrepsei-to-klima/": {
        "el": "Υπό πίεση ο Βρετανός πρωθυπουργός Κιρ Στάρμερ μετά την εκλογική συντριβή των Εργατικών στις τοπικές εκλογές. Πολλοί βουλευτές ζητούν την αποχώρησή του, ενώ ο ίδιος επιχειρεί με ομιλία να ανατρέψει το κλίμα και να υπερασπιστεί τη θέση του.",
        "en": "British PM Keir Starmer faces mounting pressure after Labour's drubbing in local elections. Many MPs are calling for his exit while he uses a major speech to defend his record and try to turn the tide.",
        "tel": ["Βρετανία", "Στάρμερ", "κρίση"],
        "ten": ["UK", "Starmer", "Labour", "crisis"],
        "s": "negative", "i": 75,
    },
    "https://www.kathimerini.gr/world/564219631/kagia-kalas-ochi-sto-aitima-poytin-gia-ton-srenter-dichasmenoi-oi-germanoi/": {
        "el": "Επιφυλακτικές έως αρνητικές οι αντιδράσεις Ευρωπαίων και Γερμανών αξιωματούχων στην πρόταση Πούτιν να αναλάβει ρόλο διαμεσολαβητή ο Γκέρχαρντ Σρέντερ. Η Κάγια Κάλας δηλώνει ότι δεν μπορεί να επιτραπεί στη Ρωσία να ορίζει διαπραγματευτή για την ΕΕ.",
        "en": "European and German officials are reserved to hostile over Putin's suggestion that Gerhard Schroeder mediate. EU foreign-policy chief Kaja Kallas says Russia cannot be allowed to choose Europe's negotiator.",
        "tel": ["ΕΕ", "Ρωσία", "Σρέντερ"],
        "ten": ["EU", "Russia", "Schroeder", "Ukraine"],
        "s": "negative", "i": 68,
    },
    "https://www.kathimerini.gr/world/564219634/e-e-kyroseis-gia-epoikoys-sti-dytiki-ochthi-prota-senaria-dialogoy-me-ti-rosia-sto-symvoylio-ypex/": {
        "el": "Στο Συμβούλιο Εξωτερικών της ΕΕ στις Βρυξέλλες, οι «27» επιχειρούν πολιτική συμφωνία για κυρώσεις κατά βίαιων Ισραηλινών εποίκων στη Δυτική Όχθη — πακέτο που παρέμενε μπλοκαρισμένο από βέτο της Ουγγαρίας. Παράλληλα εξετάζονται πρώτα σενάρια διαλόγου με τη Μόσχα.",
        "en": "At the EU Foreign Affairs Council in Brussels, the 27 are seeking political agreement on sanctions against violent Israeli settlers in the West Bank, a package long blocked by Hungary's veto. The agenda also includes initial scenarios for renewed dialogue with Moscow.",
        "tel": ["ΕΕ", "κυρώσεις", "Δυτική Όχθη"],
        "ten": ["EU", "sanctions", "West Bank", "Israel"],
        "s": "neutral", "i": 75,
    },
    "https://www.kathimerini.gr/world/564219628/ellinoktito-tanker-exilthe-apo-ta-stena-toy-ormoyz/": {
        "el": "Το ελληνόκτητο τάνκερ «Agios Fanourios I» διέσχισε τα Στενά του Ορμούζ φορτωμένο με ιρακινό αργό πετρέλαιο προς το Βιετνάμ. Σύμφωνα με ιρανικές πηγές, ακολούθησε διαδρομή που έχει ορίσει η Τεχεράνη σε δεύτερη απόπειρα. Η κίνηση στα Στενά παραμένει σημαντικά περιορισμένη.",
        "en": "Greek-owned tanker 'Agios Fanourios I' transited the Strait of Hormuz carrying Iraqi crude bound for Vietnam. Iranian sources say it followed a route set by Tehran on its second attempt; overall traffic through the strait remains severely curtailed.",
        "tel": ["ναυτιλία", "Ορμούζ", "Ελλάδα"],
        "ten": ["shipping", "Hormuz", "Greece", "Iran"],
        "s": "neutral", "i": 70,
    },
    "https://www.kathimerini.gr/world/564219610/i-atzenta-tramp-stin-kina-emporio-taivan-kai-piesi-pros-si-gia-iran/": {
        "el": "Ο Ντόναλντ Τραμπ επιδιώκει να ασκήσει πίεση στον Σι Τζινπίνγκ για το Ιράν κατά την επίσκεψή του στο Πεκίνο. Η σύνοδος των δύο μεγαλύτερων οικονομιών στοχεύει κυρίως στην αποκλιμάκωση των εμπορικών εντάσεων, με ατζέντα δασμούς, Ταϊβάν, ΑΙ και σπάνιες γαίες.",
        "en": "Donald Trump aims to pressure Xi Jinping on Iran during his Beijing visit. The summit of the world's two largest economies is mainly intended to de-escalate trade tensions, with an agenda spanning tariffs, Taiwan, AI and rare earths.",
        "tel": ["ΗΠΑ", "Κίνα", "Τραμπ", "σύνοδος"],
        "ten": ["US", "China", "Trump", "summit"],
        "s": "neutral", "i": 80,
    },

    # opinion
    "https://www.kathimerini.gr/opinion/564217537/polythrona-gia-enan/": {
        "el": "Άρθρο γνώμης για τον ανταγωνισμό ΠΑΣΟΚ-Τσίπρα για τη δεύτερη θέση. Το κόμμα Καρυστιανού φαίνεται πτωτικό, ενώ οι δύο πρωταγωνιστές της Κεντροαριστεράς αποφεύγουν την κατά μέτωπο σύγκρουση, στρέφοντας τα βέλη τους κυρίως κατά της κυβέρνησης.",
        "en": "Op-ed on the PASOK-Tsipras contest for second place. The Karystianou party appears to be losing momentum while the two main centre-left players avoid frontal confrontation and focus attacks on the government instead.",
        "tel": ["άποψη", "ΠΑΣΟΚ", "Τσίπρας"],
        "ten": ["opinion", "PASOK", "Tsipras", "opposition"],
        "s": "neutral", "i": 65,
    },
    "https://www.kathimerini.gr/opinion/564217609/stratiotiki-yperochi-geopolitiki-apotychia/": {
        "el": "Άρθρο γνώμης για το τέλμα στις διαπραγματεύσεις ΗΠΑ-Ιράν, εβδομήντα ημέρες μετά την έναρξη των επιχειρήσεων. Κριτική στον Τραμπ που χειρίστηκε ερασιτεχνικά το ζήτημα, παραχωρώντας στην Τεχεράνη ουσιαστικό βέτο στον Ορμούζ και προκαλώντας ρήγματα στους περιφερειακούς συμμάχους.",
        "en": "Op-ed on the stalemate in US-Iran negotiations 70 days into operations. The piece is critical of Trump's amateurish handling, which effectively gave Tehran a veto over Hormuz and opened rifts among regional partners.",
        "tel": ["άποψη", "Ιράν", "ΗΠΑ", "Τραμπ"],
        "ten": ["opinion", "Iran", "US", "Trump"],
        "s": "negative", "i": 72,
    },
    "https://www.kathimerini.gr/opinion/564217351/koinoniko-elleimma/": {
        "el": "Σχόλιο για την έλλειψη προετοιμασίας της Ελλάδας στη φροντίδα τρίτης ηλικίας, παρά τη ραγδαία αύξηση της ζήτησης. Το κράτος υποεπενδύει σε δομές και προσωπικό, η νόμιμη αγορά χρεώνει υπέρογκα και αναπτύσσονται απάνθρωπες πρακτικές με αδήλωτες «αποθήκες» ανθρώπων.",
        "en": "Comment on Greece's failure to prepare for elderly care needs despite surging demand. The state under-invests in facilities and staff, the legal market over-charges and inhumane shadow practices including 'warehouses' for the elderly are spreading.",
        "tel": ["άποψη", "τρίτη ηλικία", "πρόνοια"],
        "ten": ["opinion", "elderly care", "welfare", "demographics"],
        "s": "negative", "i": 65,
    },
    "https://www.kathimerini.gr/opinion/564217711/o-elefantas-toy-amerikanikoy-chreoys/": {
        "el": "Άρθρο γνώμης για το διογκωμένο αμερικανικό χρέος που ξεπέρασε το 100% του ΑΕΠ. Για πρώτη φορά τα ποσά εξυπηρέτησης του χρέους ξεπερνούν τις αμυντικές δαπάνες, με τον Τραμπ να έχει ξοδέψει 25 δισ. δολάρια στον πόλεμο του Ιράν. Οι ανησυχίες για τη θέση του δολαρίου εντείνονται.",
        "en": "Op-ed on the spiralling US debt, which has crossed 100% of GDP. For the first time, debt servicing exceeds annual defence spending, with Trump having already spent $25 billion on the Iran war. Doubts about the dollar's primacy are growing.",
        "tel": ["άποψη", "ΗΠΑ", "χρέος", "δολάριο"],
        "ten": ["opinion", "US debt", "dollar", "economy"],
        "s": "negative", "i": 70,
    },
    "https://www.kathimerini.gr/opinion/564217717/poy-kryvontai-ta-ellinika/": {
        "el": "Άρθρο για τα 50 χρόνια από την κατάργηση της καθαρεύουσας τον Μάιο του 1976. Συζητείται η μεταρρύθμιση του Γεωργίου Ράλλη ως κατάκτηση της δημοκρατίας μετά τη χούντα και η πορεία της δημοτικής ως επίσημης γλώσσας του ελληνικού κράτους.",
        "en": "Reflection on 50 years since the abolition of katharevousa in May 1976. The piece discusses Georgios Rallis' reform as a post-junta democratic gain and the trajectory of demotic Greek as the state's official language.",
        "tel": ["άποψη", "ελληνική γλώσσα", "ιστορία"],
        "ten": ["opinion", "Greek language", "history", "education"],
        "s": "neutral", "i": 50,
    },
    "https://www.kathimerini.gr/opinion/564218143/tzeni-tzeni-eisai-edo/": {
        "el": "Άρθρο για την ταινία «Τζένη Τζένη» με αφορμή τα 100 χρόνια από τη γέννηση του Κώστα Πρετεντέρη. Στο Δημοτικό Θέατρο Πειραιά παρουσιάζεται η θεατρική μεταφορά, αναβιώνοντας τη μαγεία του ελληνικού κινηματογράφου της δεκαετίας του '60.",
        "en": "Op-ed on the classic film 'Jenny Jenny' marking 100 years since screenwriter Kostas Pretenteris' birth. The Piraeus Municipal Theatre's stage adaptation revives the magic of 1960s Greek cinema.",
        "tel": ["άποψη", "σινεμά", "Πρετεντέρης"],
        "ten": ["opinion", "cinema", "Pretenteris", "theatre"],
        "s": "positive", "i": 35,
    },
    "https://www.kathimerini.gr/opinion/564217714/give-peace-a-chance/": {
        "el": "Άρθρο γνώμης για το «απρόβλεπτο» της εξωτερικής πολιτικής Τραμπ, που πολλοί βλέπουν ως χάος και ανασφάλεια στους συμμάχους ΗΠΑ. Συγκρίνεται με τις αντιδράσεις Ευρωπαίων στον πόλεμο του Ιράκ το 2003 και αναδεικνύεται η ανάγκη ευρωπαϊκής στρατηγικής αυτονομίας.",
        "en": "Op-ed on the 'unpredictability' of Trump's foreign policy, which many see as chaos for US allies. The author compares it to European reactions to the 2003 Iraq war and argues for European strategic autonomy.",
        "tel": ["άποψη", "Τραμπ", "εξωτερική πολιτική"],
        "ten": ["opinion", "Trump", "foreign policy", "Europe"],
        "s": "negative", "i": 65,
    },
    "https://www.kathimerini.gr/opinion/564217747/ola-tis-omospondias-dyskola/": {
        "el": "Άρθρο για τη διαμάχη μεταξύ ομοσπονδιακής και πολιτειακής εξουσίας στις ΗΠΑ από την ψήφιση του Συντάγματος ως σήμερα. Αναλύονται οι σύγχρονες εντάσεις γύρω από τη χρήση της εθνοφρουράς και τα όρια της ομοσπονδιακής παρέμβασης στις πολιτείες.",
        "en": "Op-ed on the centuries-old struggle between federal and state authority in the United States, from the 1789 Constitution to today. The author analyses current tensions around National Guard deployments and federal overreach.",
        "tel": ["άποψη", "ΗΠΑ", "ομοσπονδία"],
        "ten": ["opinion", "US politics", "federalism", "history"],
        "s": "neutral", "i": 55,
    },
    "https://www.kathimerini.gr/opinion/564217573/i-alosi-toy-met-gala/": {
        "el": "Σχόλιο για τη μετατροπή του Met Gala από φιλανθρωπικό θεσμό για το Μητροπολιτικό Μουσείο σε κοσμική σύναξη πολυτελείας. Η εμπλοκή του Τζεφ Μπέζος και της Λόρεν Σάντσεζ ανοίγει πολιτικά ερωτήματα για τον ρόλο των δισεκατομμυριούχων στους πολιτιστικούς θεσμούς.",
        "en": "Op-ed on how the Met Gala has morphed from a charity event for the Met Museum's Costume Institute into a celebrity vanity fair. Jeff Bezos and Lauren Sanchez's involvement raises political questions about billionaires' grip on cultural institutions.",
        "tel": ["άποψη", "Met Gala", "Μπέζος"],
        "ten": ["opinion", "Met Gala", "Bezos", "culture"],
        "s": "negative", "i": 45,
    },
    "https://www.kathimerini.gr/opinion/564217708/to-epaggelma-toy-lompista-diamesolaviti/": {
        "el": "Άρθρο γνώμης για τον διορισμό του Πίτερ Μάντελσον στη θέση του Βρετανού πρέσβη στις ΗΠΑ και τις αμφισβητούμενες διασυνδέσεις του με τον Επστάιν, τη Ρωσία και την Κίνα. Αναδεικνύονται οι ελλείψεις του ελεγκτικού μηχανισμού στη Βρετανία.",
        "en": "Op-ed on the controversial appointment of Peter Mandelson as British ambassador to the US given his ties to Epstein, Russia and China. Highlights failures in the UK's vetting mechanism for sensitive diplomatic posts.",
        "tel": ["άποψη", "Βρετανία", "Μάντελσον"],
        "ten": ["opinion", "UK", "Mandelson", "ambassador"],
        "s": "negative", "i": 55,
    },
    "https://www.kathimerini.gr/opinion/564218149/ta-peiratika-toy-kapten-mpimpi/": {
        "el": "Κριτική στις διαφορετικές διατυπώσεις των ΜΜΕ για το ναυάγιο πλοίου του στολίσκου Sumud Flotilla προς τη Γάζα στη Γαύδο, μετά από επέμβαση Ισραηλινών. Η ανάλυση δείχνει πώς η αλλαγή σειράς των ίδιων λέξεων αλλάζει ριζικά το νόημα της είδησης.",
        "en": "Critique of how Greek media framed the wreck of a Sumud Flotilla vessel off Gavdos after Israeli interception. The piece shows how reshuffling the same words radically alters the meaning of a news story.",
        "tel": ["άποψη", "ΜΜΕ", "Γάζα"],
        "ten": ["opinion", "media", "Gaza", "journalism"],
        "s": "negative", "i": 55,
    },
    "https://www.kathimerini.gr/opinion/564217954/gyrnontas-56-chronia-piso/": {
        "el": "Νοσταλγικό άρθρο για τα πρώτα βήματα της ελληνικής πληροφορικής με αφορμή τα 25 χρόνια του περιοδικού Netweek. Ο συγγραφέας θυμάται την εγκατάσταση του UNIVAC 1107 στην Αθήνα τη δεκαετία του '70 από την εταιρεία Doxiadis Associates Computer Center.",
        "en": "Nostalgic essay on the early days of Greek computing, prompted by Netweek magazine's 25th anniversary. The author recalls installing the UNIVAC 1107 mainframe in 1970s Athens via Doxiadis Associates Computer Center.",
        "tel": ["άποψη", "πληροφορική", "ιστορία"],
        "ten": ["opinion", "computing", "history", "technology"],
        "s": "positive", "i": 35,
    },
    "https://www.kathimerini.gr/opinion/564217744/o-sarkasmos-toy-karoloy-kai-i-elliniki-arena/": {
        "el": "Άρθρο για τη σαρκαστική απάντηση του βασιλιά Καρόλου στον Τραμπ κατά τη συνάντηση στον Λευκό Οίκο, υπενθυμίζοντας ότι «αν δεν ήμασταν εμείς θα μιλούσατε γαλλικά». Παράλληλα κατακρίνεται η ντροπιαστική παντοδυναμία του πελατειακού κράτους στην Ελλάδα.",
        "en": "Op-ed praising King Charles' sarcastic riposte to Trump at the White House dinner, recalling that without Britain Americans would be speaking French. The piece also condemns the embarrassing grip of Greek clientelism.",
        "tel": ["άποψη", "Κάρολος", "Τραμπ"],
        "ten": ["opinion", "King Charles", "Trump", "diplomacy"],
        "s": "positive", "i": 55,
    },
    "https://www.kathimerini.gr/opinion/564217756/skepseis-sto-mpotiliarisma/": {
        "el": "Άρθρο γνώμης για τα διαρθρωτικά προβλήματα της Ελλάδας: φορολογικό βάρος σε μισθωτούς και συνταξιούχους, καχεξία θεσμών, δημογραφικό, στρεβλό παραγωγικό μοντέλο και κρίση της εκπαίδευσης. Όλα τα παραπάνω συνοψίζονται στην εικόνα του χρόνιου μποτιλιαρίσματος.",
        "en": "Op-ed surveying Greece's systemic problems: tax burden skewed to wage-earners and pensioners, weak institutions, demographic decline, a distorted productive model and the education crisis. All converge into the image of chronic gridlock.",
        "tel": ["άποψη", "Ελλάδα", "μεταρρυθμίσεις"],
        "ten": ["opinion", "Greece", "reform", "structural problems"],
        "s": "negative", "i": 65,
    },

    # culture
    "https://www.kathimerini.gr/culture/564218137/edo-as-statho-sto-pagkaki-me-ton-kavafi/": {
        "el": "Νέο τοπόσημο της Αθήνας: το γλυπτό-καθιστικό του Κ. Π. Καβάφη στη Διονυσίου Αρεοπαγίτου, δωρεά του Ιδρύματος Ωνάση στον Δήμο Αθηναίων, με τη δημιουργία του Πραξιτέλη Τζανουλίνου. Ποιητές, ηθοποιοί και μελετητές μιλούν για το νέο σημείο αναφοράς της πόλης.",
        "en": "A new Athens landmark: the K. P. Cavafy sculpture-seat on Dionysiou Areopagitou, gifted by the Onassis Foundation to the City of Athens and crafted by Praxitelis Tzanoulinos. Poets, actors and scholars reflect on this new tribute to the poet.",
        "tel": ["Καβάφης", "γλυπτό", "Αθήνα"],
        "ten": ["Cavafy", "Athens", "sculpture", "Onassis Foundation"],
        "s": "positive", "i": 60,
    },
    "https://www.kathimerini.gr/culture/564213814/stratos-dionysioy-o-diskos-poy-ichografise-mesa-sti-fylaki/": {
        "el": "Με αφορμή τη συμπλήρωση χρόνων από τον θάνατο του Στράτου Διονυσίου στις 11 Μαΐου 1990, αναβιώνει η ιστορία της ηχογράφησης δίσκου του μέσα στη φυλακή. Ο λαϊκός βάρδος πέρασε από τις φυλακές Γεντί Κουλέ, Κέρκυρας και Τίρυνθας.",
        "en": "On the anniversary of singer Stratos Dionysiou's death on 11 May 1990, the story of how he recorded an album while behind bars resurfaces. The popular bard spent time in Yedi Kule, Corfu and Tiryns prisons.",
        "tel": ["μουσική", "Διονυσίου", "ιστορία"],
        "ten": ["music", "Dionysiou", "history", "biography"],
        "s": "neutral", "i": 45,
    },
    "https://www.kathimerini.gr/culture/564218185/ayto-den-einai-ena-krevati/": {
        "el": "Η αναδρομική της Τρέισι Έμιν στην Tate Modern επαναφέρει το ερώτημα τι είναι η σύγχρονη τέχνη. Τέσσερις γυναίκες σχολιάζουν την έκθεση που πολώνει: για κάποιους ωμή και προκλητική, για άλλους πρόκληση και υπερβολική αυτοέκθεση της καλλιτέχνιδας.",
        "en": "Tracey Emin's retrospective at Tate Modern reopens the debate about what contemporary art is. Four women review the polarising show — raw and provocative for some, an exercise in over-exposure for others.",
        "tel": ["τέχνη", "Tate", "Έμιν"],
        "ten": ["art", "Tate Modern", "Emin", "review"],
        "s": "neutral", "i": 45,
    },
    "https://www.kathimerini.gr/culture/564218194/i-aristera-o-ntostogiefski-ta-endon-rimata/": {
        "el": "Άρθρο για τη νέα έκδοση των ποιητικών απάντων του Άρη Αλεξάνδρου. Το ποίημα «Υποσημείωση», παράφραση του επιγράμματος για τους Σπαρτιάτες των Θερμοπυλών, σκιαγραφεί την υπαρξιακή αγωνία και την επιλογή της εσωτερικής ζωής μετά από μια ιστορική ήττα.",
        "en": "Feature on the new collected poems of Aris Alexandrou. His 'Footnote', a rewrite of the Thermopylae epigram, captures the existential anxiety that drove the poet toward a life defined by inner imperatives.",
        "tel": ["λογοτεχνία", "Αλεξάνδρου", "ποίηση"],
        "ten": ["literature", "Alexandrou", "poetry", "Greek"],
        "s": "neutral", "i": 45,
    },
    "https://www.kathimerini.gr/culture/564218104/archaioellinikos-tromos/": {
        "el": "Κριτική για τις «αρχαιοελληνικές» αμφιέσεις διασήμων στο πρόσφατο Met Gala — Νίκη της Σαμοθράκης, Αφροδίτη της Μήλου, θεά Ειρήνη. Επίσης σχολιάζεται η ταινία «Ο διάβολος φοράει Prada 2» ως νωθρή επανάληψη γνωστών χαρακτήρων χωρίς ανανέωση.",
        "en": "Critique of celebrity 'ancient-Greek' looks at the recent Met Gala — Winged Victory of Samothrace, Venus de Milo, the goddess Eirene. The column also pans 'The Devil Wears Prada 2' as a lazy retread of familiar characters.",
        "tel": ["πολιτισμός", "Met Gala", "μόδα"],
        "ten": ["culture", "Met Gala", "fashion", "cinema"],
        "s": "negative", "i": 40,
    },
    "https://www.kathimerini.gr/culture/564218179/i-ameriki-ton-gkala-kai-toy-ompama/": {
        "el": "Σχόλιο για την εμπορευματοποίηση του Met Gala που από φιλανθρωπικός θεσμός για το Ινστιτούτο Κοστουμιών έχει γίνει πασαρέλα πολυτελείας με εισιτήρια χιλιάδων δολαρίων. Αμφισβητείται η συμβολή του στους πολιτιστικούς θεσμούς όταν αυτοί προσαρμόζονται στα μέτρα των δωρητών.",
        "en": "Reflection on how the Met Gala has shifted from a charity supporting the Costume Institute into a luxury runway with five-figure tickets. The column questions what cultural institutions lose when they bend to wealthy donors.",
        "tel": ["άποψη", "Met Gala", "πολιτισμός"],
        "ten": ["opinion", "Met Gala", "culture", "criticism"],
        "s": "negative", "i": 45,
    },
    "https://www.kathimerini.gr/culture/564218176/koykaki-i-monadikotita-tis-agioy-nikolaoy/": {
        "el": "Άρθρο για την ιδιαίτερη αρχιτεκτονική και κοινωνική ιστορία της οδού Αγίου Νικολάου στο Κουκάκι. Τρία χρόνια μετά την προηγούμενη επίσκεψη, ο αρθρογράφος καταγράφει τις αλλαγές και τις κατεδαφίσεις σε έναν δρόμο που διασώζει ακόμη ευγενή αστική κλίμακα.",
        "en": "Essay on the architectural and social history of Agiou Nikolaou Street in Athens' Koukaki. Three years on, the author records the demolitions and new builds eroding the street's distinctive urban scale.",
        "tel": ["αρχιτεκτονική", "Αθήνα", "Κουκάκι"],
        "ten": ["architecture", "Athens", "urbanism", "Koukaki"],
        "s": "negative", "i": 45,
    },
    "https://www.kathimerini.gr/culture/564218146/parafonies-enos-moysikoy-diagonismoy/": {
        "el": "Σχόλιο για τις πολιτικές παραφωνίες του διαγωνισμού Eurovision λόγω της συμμετοχής του Ισραήλ. Πέντε χώρες — Ιρλανδία, Ισπανία, Ολλανδία, Ισλανδία, Σλοβενία — έχουν δηλώσει αποχή, ενώ η EBU επιμένει στην προσχηματική απολιτικότητα του διαγωνισμού.",
        "en": "Comment on the political turbulence at Eurovision over Israel's participation. Five countries — Ireland, Spain, the Netherlands, Iceland and Slovenia — have pulled out, while the EBU clings to its pretence of apoliticism.",
        "tel": ["Eurovision", "Ισραήλ", "μουσική"],
        "ten": ["Eurovision", "Israel", "politics", "music"],
        "s": "negative", "i": 60,
    },
    "https://www.kathimerini.gr/culture/564218086/moysiki-san-astriko-nefeloma/": {
        "el": "Στήλη για τη Μεγάλη Λειτουργία σε ντο ελάσσονα Κ 427 και το Ρέκβιεμ Κ 626 του Μότσαρτ, δύο έργα που στέκουν στις κορυφές της ανθρώπινης μουσικής δημιουργίας. Η ανάλυση τα τοποθετεί δίπλα στα μεγάλα θρησκευτικά έργα του Μπαχ και του Μπετόβεν.",
        "en": "Column on Mozart's Great Mass in C minor (K 427) and Requiem (K 626), two of the pinnacles of human musical creation. The analysis places them alongside the great religious works of Bach and Beethoven.",
        "tel": ["μουσική", "Μότσαρτ", "κλασική"],
        "ten": ["music", "Mozart", "classical", "requiem"],
        "s": "positive", "i": 35,
    },
    "https://www.kathimerini.gr/culture/564219316/metallica-pos-stithike-sto-oaka-i-megalyteri-synayliaki-egkatastasi-poy-egine-pote-stin-ellada/": {
        "el": "Πώς στήθηκε στο ΟΑΚΑ η μεγαλύτερη συναυλιακή εγκατάσταση που έγινε ποτέ στην Ελλάδα για τη συναυλία των Metallica. Για περισσότερες από 12 μέρες χιλιάδες εργαζόμενοι δούλεψαν 24ωρα για την εγκατάσταση, με ενισχύσεις υποδομών και σύνθετα τεχνικά έργα.",
        "en": "How the biggest concert installation ever staged in Greece came together at OAKA for Metallica's show. Thousands of workers spent over 12 days, working 24/7, to assemble a production fit for the world's top venues.",
        "tel": ["Metallica", "ΟΑΚΑ", "συναυλία"],
        "ten": ["Metallica", "OAKA", "concert", "music"],
        "s": "positive", "i": 50,
    },
    "https://www.kathimerini.gr/culture/564219031/seismos-sto-oaka-gia-toys-metallica-to-asteroskopeio-athinon-kategrapse-tis-doniseis-toy-koinoy/": {
        "el": "Το Εθνικό Αστεροσκοπείο Αθηνών κατέγραψε σεισμογραφικά τις δονήσεις που προκάλεσε το πλήθος στη συναυλία των Metallica στο ΟΑΚΑ. Το πείραμα μελετά το φαινόμενο των «concert quakes», συνδέοντας την επιστήμη με τον πολιτισμό και τη μουσική εμπειρία.",
        "en": "The National Observatory of Athens used seismographic equipment to capture vibrations from the crowd at Metallica's OAKA concert. The experiment studies 'concert quakes' as a bridge between science, culture and music.",
        "tel": ["επιστήμη", "Metallica", "ΟΑΚΑ"],
        "ten": ["science", "Metallica", "OAKA", "seismograph"],
        "s": "positive", "i": 45,
    },
    "https://www.kathimerini.gr/culture/564219019/metallica-seistike-to-oaka-osa-eginan-sti-synaylia-tis-chronias/": {
        "el": "Οι Metallica επέστρεψαν στην Αθήνα μετά από 16 χρόνια με μια συναυλία στο ΟΑΚΑ που έμεινε στη μνήμη χιλιάδων θεατών. Στις κορυφαίες στιγμές: η ηλεκτρική εκδοχή του «Ζορμπά» του Μίκη Θεοδωράκη και η διασκευή του «Δεν χωράς πουθενά» των Τρυπών.",
        "en": "Metallica returned to Athens after 16 years for an OAKA concert that lived up to expectations. Highlights included an electric rendition of Mikis Theodorakis' 'Zorba' and a cover of Trypes' 'Den Choras Pouthena'.",
        "tel": ["Metallica", "ΟΑΚΑ", "μουσική"],
        "ten": ["Metallica", "OAKA", "music", "concert"],
        "s": "positive", "i": 55,
    },
}

# Themes per category
THEMES = {
    "politics": {
        "el": ["Πόθεν έσχες πολιτικών", "Νέο κόμμα Τσίπρα & ΠΑΣΟΚ", "Υπόθεση χανταϊού", "Υποκλοπές & Δημητριάδης", "Εξωτερική πολιτική"],
        "en": ["Asset declarations", "Tsipras' new party vs PASOK", "Hantavirus case", "Wiretaps & Dimitriadis", "Foreign policy"],
    },
    "economy": {
        "el": ["Εξαγορά Skroutz από Blackstone", "Φορολογική απάτη με αδήλωτα POS", "Πρόγραμμα 'Σπίτι μου ΙΙ'", "Aramco κέρδη", "Νέος κύκλος ελληνικού τουρισμού"],
        "en": ["Blackstone-Skroutz deal", "Undeclared POS tax fraud", "'Spiti Mou II' housing scheme", "Aramco earnings", "Future of Greek tourism"],
    },
    "society": {
        "el": ["Καραντίνα χανταϊού στο 'Αττικόν'", "Ενδοοικογενειακή βία στο Ηράκλειο", "Ένοπλη ληστεία τράπεζας", "Διασώσεις μεταναστών στην Κρήτη", "Εγκληματικότητα"],
        "en": ["Hantavirus quarantine at Attikon", "Heraklion domestic violence", "Armed bank robbery", "Migrant rescues off Crete", "Crime news"],
    },
    "world": {
        "el": ["Κρίση Στάρμερ στη Βρετανία", "Πόλεμος ΗΠΑ-Ιράν", "Σύνοδος Τραμπ-Σι", "Συμβούλιο Εξωτερικών ΕΕ", "Δίκη Ιμάμογλου"],
        "en": ["Starmer's crisis in Britain", "US-Iran war stalemate", "Trump-Xi Beijing summit", "EU Foreign Affairs Council", "Imamoglu trial"],
    },
    "opinion": {
        "el": ["Μάχη ΠΑΣΟΚ-Τσίπρα", "Διεθνείς εντάσεις ΗΠΑ-Ιράν", "Δομικά προβλήματα Ελλάδας", "Αμερικανικό χρέος", "Πολιτισμός & εξουσία (Met Gala)"],
        "en": ["PASOK vs Tsipras contest", "US-Iran tensions", "Greek structural problems", "US debt and the dollar", "Culture & power (Met Gala)"],
    },
    "culture": {
        "el": ["Συναυλία Metallica στο ΟΑΚΑ", "Νέο γλυπτό Καβάφη στην Αθήνα", "Eurovision και πολιτική", "Met Gala και αρχαία Ελλάδα", "Tracey Emin στην Tate"],
        "en": ["Metallica at OAKA", "New Cavafy sculpture in Athens", "Eurovision and politics", "Met Gala and ancient Greece", "Tracey Emin at Tate"],
    },
}


def main():
    with open(RAW_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    by_cat = {}
    for art in raw["articles"]:
        cat = art["category_hint"]
        by_cat.setdefault(cat, []).append(art)

    out_dir = os.path.join(OUT_ROOT, TARGET_DATE)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(os.path.join(OUT_ROOT, "feeds"), exist_ok=True)

    all_items_with_meta = []
    cat_counts = {}
    now_iso = datetime.now(timezone.utc).isoformat()

    for cat in ["politics", "economy", "society", "world", "opinion", "culture"]:
        arts = by_cat.get(cat, [])
        items = []
        for art in arts:
            url = art["url"]
            ana = ANALYSES.get(url)
            if ana is None:
                print(f"WARNING: no analysis for {url}", file=sys.stderr)
                ana = {
                    "el": art["snippet"][:300],
                    "en": art["snippet"][:300],
                    "tel": [cat], "ten": [cat],
                    "s": "neutral", "i": 50,
                }
            items.append({
                "id": art["id"],
                "title": art["title"],
                "url": url,
                "author": art["author"],
                "published": art["published"],
                "source": art["source"],
                "source_type": art["source_type"],
                "category": cat,
                "importance": ana["i"],
                "content": (art["content"] or "")[:2000],
                "summary": {"el": ana["el"], "en": ana["en"]},
                "tags": {"el": ana["tel"], "en": ana["ten"]},
                "sentiment": ana["s"],
            })
        # Sort items within category by importance descending then published descending
        items.sort(key=lambda x: (-x["importance"], x.get("published") or ""), reverse=False)
        # The above sorts by importance ascending. Reverse to descending:
        items.sort(key=lambda x: x["importance"], reverse=True)

        cat_doc = {
            "date": TARGET_DATE,
            "generated_at": now_iso,
            "category": cat,
            "item_count": len(items),
            "themes": THEMES.get(cat, {"el": [], "en": []}),
            "items": items,
        }
        with open(os.path.join(out_dir, f"{cat}.json"), "w", encoding="utf-8") as f:
            json.dump(cat_doc, f, ensure_ascii=False, indent=2)
        cat_counts[cat] = len(items)
        all_items_with_meta.extend(items)
        print(f"wrote {cat}.json ({len(items)} items)")

    # summary.json
    n = len(all_items_with_meta)
    exec_el = (
        "Η ειδησεογραφία της Δευτέρας 11 Μαΐου 2026 κυριαρχείται από τη δημοσιοποίηση των δηλώσεων «πόθεν έσχες» των πολιτικών για τη χρήση 2024. "
        "Στο πολιτικό προσκήνιο, ο Αλέξης Τσίπρας προαναγγέλλει την επίσημη ανακοίνωση του νέου του κόμματος μετά τις εννέα παρουσιάσεις της «Ιθάκης», "
        "ενώ συνεχίζεται η ανάλυση για τη μάχη ΠΑΣΟΚ-Τσίπρα-Καρυστιανού για τη δεύτερη θέση. Παράλληλα, ο Έλληνας επιβάτης του κρουαζιερόπλοιου «MV Hondius» "
        "τέθηκε σε προληπτική καραντίνα 45 ημερών στο νοσοκομείο «Αττικόν» λόγω κρουσμάτων χανταϊού επί του πλοίου.\n\n"
        "Στο διεθνές πεδίο, ο Βρετανός πρωθυπουργός Κιρ Στάρμερ βρίσκεται υπό έντονη εσωκομματική πίεση μετά τη βαριά εκλογική ήττα των Εργατικών "
        "στις τοπικές εκλογές, ενώ ο Ντόναλντ Τραμπ ταξιδεύει στο Πεκίνο για κρίσιμη σύνοδο με τον Σι Τζινπίνγκ, με αντικείμενα το εμπόριο, την Ταϊβάν "
        "και την πίεση για το Ιράν. Το Συμβούλιο Εξωτερικών της ΕΕ συζητά κυρώσεις κατά βίαιων Ισραηλινών εποίκων στη Δυτική Όχθη και σενάρια διαλόγου "
        "με τη Μόσχα, ενώ ξεκινά στις φυλακές Μαρμαρά η δίκη του Εκρέμ Ιμάμογλου με κατηγορίες «πολιτικής κατασκοπείας».\n\n"
        "Στην οικονομία ξεχωρίζει η εξαγορά της Skroutz από τη Blackstone με αποτίμηση 635 εκατ. ευρώ και η εκτόξευση κερδών της Saudi Aramco στα 33,6 δισ. "
        "δολάρια, παρά τη σύγκρουση στη Μέση Ανατολή. Παράλληλα, ο φορολογικός μηχανισμός εντοπίζει νέο εξελιγμένο δίκτυο φοροδιαφυγής μέσω αδήλωτων POS. "
        "Στον πολιτισμό, η συναυλία των Metallica στο ΟΑΚΑ μετά από 16 χρόνια κυριάρχησε με τις διασκευές του «Ζορμπά» και του «Δεν χωράς πουθενά», ενώ "
        "αποκαλύφθηκε νέο τοπόσημο της Αθήνας: το γλυπτό-καθιστικό του Κ. Π. Καβάφη στη Διονυσίου Αρεοπαγίτου, δωρεά του Ιδρύματος Ωνάση."
    )
    exec_en = (
        "Monday 11 May 2026 is dominated in Greece by the publication of politicians' annual asset declarations ('pothen esches') for fiscal year 2024, "
        "with 1,854 disclosures from MPs, MEPs, mayors and regional governors. On the political front, former PM Alexis Tsipras is preparing to launch his "
        "new party after a nine-city book tour, while the PASOK-Tsipras-Karystianou contest for second place in the opposition continues to dominate analysis. "
        "In public health, the Greek passenger from the MV Hondius cruise ship has been placed in a 45-day preventative quarantine at Attikon Hospital after "
        "hantavirus cases were detected on board.\n\n"
        "Internationally, British PM Keir Starmer faces mounting Labour dissent after a heavy local-election defeat, while Donald Trump travels to Beijing for "
        "a high-stakes summit with Xi Jinping covering trade, Taiwan and pressure over Iran. The EU Foreign Affairs Council is meeting in Brussels to consider "
        "sanctions on violent Israeli settlers in the West Bank and initial scenarios for dialogue with Moscow, while the trial of suspended Istanbul mayor "
        "Ekrem Imamoglu opens at Marmara prison on 'political espionage' charges that could carry 15-20 years' imprisonment.\n\n"
        "On the economy, Blackstone has agreed to acquire Greek e-commerce platform Skroutz at a €635 million valuation, Saudi Aramco's Q1 profits jumped 25% "
        "to $33.6 billion despite the Middle East war, and Greek tax authorities are uncovering a sophisticated fraud network using undeclared POS terminals. "
        "In culture, Metallica's return to Athens after 16 years dominated the weekend with covers of Theodorakis' 'Zorba' and Trypes' 'Den Choras Pouthena', "
        "while a new Cavafy sculpture-seat — gifted by the Onassis Foundation — was unveiled on Dionysiou Areopagitou as the city's newest landmark."
    )

    top_topics = [
        {
            "name": {"el": "Δημοσιοποίηση «πόθεν έσχες»", "en": "Politicians' asset declarations published"},
            "description": {
                "el": "Δημοσιοποιήθηκαν 1.854 δηλώσεις «πόθεν έσχες» πολιτικών για τη χρήση 2024, με αναλυτικά στοιχεία για τον πρωθυπουργό Μητσοτάκη, τον πρόεδρο της Βουλής Κακλαμάνη και ολόκληρο το πολιτικό προσωπικό. Οι δηλώσεις θα παραμείνουν αναρτημένες για τρία χρόνια.",
                "en": "Greek authorities published 1,854 asset declarations covering MPs, MEPs, mayors and regional governors for fiscal year 2024, including detailed reports for PM Mitsotakis and Speaker Kaklamanis. The disclosures will remain online for three years."
            },
            "related_items": ["bef0b94ef39c", "5816f3a40c92", "8a26eccf5f72"],
            "importance": 78,
        },
        {
            "name": {"el": "Νέο κόμμα Τσίπρα - μάχη με ΠΑΣΟΚ", "en": "Tsipras' new party and the PASOK rivalry"},
            "description": {
                "el": "Ο Αλέξης Τσίπρας προαναγγέλλει το νέο πολιτικό φορέα μετά τις εννέα παρουσιάσεις της «Ιθάκης», ενώ διαμορφώνεται η μάχη με το ΠΑΣΟΚ για τη δεύτερη θέση. Δημοσκοπικά οι Ανδρουλάκης, Τσίπρας και Καρυστιανού κινούνται με μικρές διαφορές, με το ΣΥΡΙΖΑ σε παράλυση.",
                "en": "Alexis Tsipras is preparing to launch his new party after a nine-city tour for his book 'Ithaca'. The contest with PASOK for second place is heating up, with Androulakis, Tsipras and Karystianou polling close together while SYRIZA remains paralysed."
            },
            "related_items": [],
            "importance": 75,
        },
        {
            "name": {"el": "Υπόθεση χανταϊού στην Ελλάδα", "en": "Hantavirus case in Greece"},
            "description": {
                "el": "Έλληνας επιβάτης του κρουαζιερόπλοιου «MV Hondius», όπου εμφανίστηκαν κρούσματα χανταϊού, μεταφέρθηκε με ειδική πτήση της Πολεμικής Αεροπορίας στο νοσοκομείο «Αττικόν». Τέθηκε σε προληπτική απομόνωση 45 ημερών, χωρίς συμπτώματα. Ο υπουργός Υγείας διαβεβαιώνει ότι δεν υπάρχει κίνδυνος εξάπλωσης.",
                "en": "A Greek passenger from the MV Hondius cruise ship, where hantavirus cases were detected, was airlifted to Attikon Hospital and placed in 45-day preventative isolation. He is asymptomatic. The Health Minister assures there is no risk of the virus spreading in Greece."
            },
            "related_items": [],
            "importance": 80,
        },
        {
            "name": {"el": "Κρίσεις στην παγκόσμια σκηνή", "en": "Global crises and diplomacy"},
            "description": {
                "el": "Ο Βρετανός πρωθυπουργός Κιρ Στάρμερ προσπαθεί να σώσει την ηγεσία του μετά την εκλογική συντριβή των Εργατικών. Παράλληλα, ο Τραμπ μεταβαίνει στο Πεκίνο για κρίσιμη σύνοδο με τον Σι Τζινπίνγκ ενώ συνεχίζεται το τέλμα στις διαπραγματεύσεις ΗΠΑ-Ιράν. Η ΕΕ στις Βρυξέλλες επιχειρεί πολιτική συμφωνία για κυρώσεις κατά βίαιων Ισραηλινών εποίκων.",
                "en": "British PM Keir Starmer fights for his leadership after Labour's heavy defeat. Donald Trump travels to Beijing for a high-stakes summit with Xi Jinping while US-Iran talks remain in stalemate. In Brussels, EU foreign ministers are pushing for political agreement on sanctioning violent Israeli settlers in the West Bank."
            },
            "related_items": [],
            "importance": 82,
        },
    ]

    # Fill related_items by walking through all_items_with_meta
    def collect_related(keyword_set, limit=5):
        ids = []
        for it in all_items_with_meta:
            text = (it["title"] + " " + " ".join(it["tags"]["el"]) + " " + " ".join(it["tags"]["en"])).lower()
            if any(k in text for k in keyword_set):
                ids.append(it["id"])
                if len(ids) >= limit:
                    break
        return ids

    top_topics[0]["related_items"] = collect_related({"πόθεν", "asset", "kaklamanis", "mitsotakis"}, 5)
    top_topics[1]["related_items"] = collect_related({"τσίπρα", "tsipras", "πασοκ", "pasok", "syriza"}, 5)
    top_topics[2]["related_items"] = collect_related({"χανταϊ", "hantavirus", "hondius"}, 5)
    top_topics[3]["related_items"] = collect_related({"starmer", "trump", "iran", "xi", "ukraine", "imamoglu", "eu"}, 6)

    summary_doc = {
        "date": TARGET_DATE,
        "generated_at": now_iso,
        "source_note": f"Articles scraped from kathimerini.gr. {n} articles over 24h.",
        "executive_summary": {"el": exec_el, "en": exec_en},
        "top_topics": top_topics,
        "article_count": n,
        "categories": cat_counts,
    }
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary_doc, f, ensure_ascii=False, indent=2)
    print(f"wrote summary.json (n={n})")

    # Atom feed: top 20 by importance
    all_items_with_meta.sort(key=lambda x: x["importance"], reverse=True)
    top20 = all_items_with_meta[:20]

    def xml_escape(s):
        return (
            (s or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
        )

    entries_xml = []
    for it in top20:
        entries_xml.append(
            f"""  <entry>
    <id>{xml_escape(it['url'])}</id>
    <title>{xml_escape(it['title'])}</title>
    <link href="{xml_escape(it['url'])}"/>
    <updated>{xml_escape(it.get('published') or now_iso)}</updated>
    <author><name>{xml_escape(it['author'])}</name></author>
    <category term="{xml_escape(it['category'])}"/>
    <summary type="text">{xml_escape(it['summary']['en'])}</summary>
    <content type="html">&lt;p&gt;&lt;strong&gt;EN:&lt;/strong&gt; {xml_escape(it['summary']['en'])}&lt;/p&gt;&lt;p&gt;&lt;strong&gt;EL:&lt;/strong&gt; {xml_escape(it['summary']['el'])}&lt;/p&gt;</content>
  </entry>"""
        )
    feed_xml = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
<feed xmlns=\"http://www.w3.org/2005/Atom\" xml:lang=\"el\">
  <title>Greek News Aggregator — Top 20 ({TARGET_DATE})</title>
  <subtitle>Daily curated Kathimerini stories with bilingual summaries.</subtitle>
  <link href=\"https://www.kathimerini.gr/\" rel=\"alternate\"/>
  <link href=\"https://zoetzikra.github.io/greek-news-aggregator/data/feeds/main.xml\" rel=\"self\"/>
  <id>tag:greek-news-aggregator,{TARGET_DATE}:/feeds/main</id>
  <updated>{now_iso}</updated>
  <author><name>Greek News Aggregator</name></author>
{chr(10).join(entries_xml)}
</feed>
"""
    feed_path = os.path.join(OUT_ROOT, "feeds", "main.xml")
    with open(feed_path, "w", encoding="utf-8") as f:
        f.write(feed_xml)
    print(f"wrote feed: {feed_path}")

    # index.json
    index_path = os.path.join(OUT_ROOT, "index.json")
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            idx = json.load(f)
    else:
        idx = {"dates": [], "last_updated": None}
    dates = set(idx.get("dates", []))
    dates.add(TARGET_DATE)
    idx["dates"] = sorted(dates, reverse=True)
    idx["last_updated"] = now_iso
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)
    print(f"updated index.json (dates: {idx['dates'][:5]})")


if __name__ == "__main__":
    main()
