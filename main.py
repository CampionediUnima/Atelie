import streamlit as st
from PIL import Image
import os
import json
import time

# Importazione della libreria ufficiale Google GenAI
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# Importazione opzionale per la ricerca immagini sul web
try:
    from duckduckgo_search import DDGS
    HAS_DDG = True
except ImportError:
    HAS_DDG = False

# ==========================================
# GESTIONE PERSISTENZA DATI SU DISCO (LOCAL STORAGE)
# ==========================================
DATA_FILE = "guardaroba.json"
CONFIG_FILE = "config.json"
UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def carica_guardaroba():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def salva_guardaroba(guardaroba_list):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(guardaroba_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Errore nel salvataggio del guardaroba: {e}")

def carica_config_api_key():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("api_key", "")
        except Exception:
            return ""
    return ""

def salva_config_api_key(key):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"api_key": key}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Errore nel salvataggio della configurazione: {e}")

# ==========================================
# 1. DIZIONARIO TRADUZIONI MULTILINGUA (IT, EN, DE, SQ)
# ==========================================
I18N = {
    "Italiano": {
        "lang_code": "Italiano",
        "menu": ["Diagnostica Fit", "Guardaroba", "Generatore Outfit", "Academy"],
        "config_title": "⚙️ Configurazione IA",
        "misure_title": "📐 Scheda Misure Sartoriali",
        "modifica_misure": "Modifica Parametri Fisici",
        "sesso": "Sesso / Genere",
        "sesso_opts": ["Uomo", "Donna"],
        "altezza": "Altezza (cm)",
        "peso": "Peso (kg)",
        "corporatura": "Conformazione / Corporeità",
        "postura": "Postura & Spalle",
        "corp_opts": ["Atletica / Regolare", "Slim / Sottile", "Robustezza / Torace Largo", "Addome Pronunciato", "Longilineo", "Clessidra / Curve Balanced"],
        "post_opts": ["Eretta / Standard", "Spalle Spioventi", "Spalle Dritte / Squadrate", "Postura Incurvata"],
        "misure_cm": "Misure in Centimetri (cm):",
        "torace": "Torace / Seno",
        "vita": "Punto Vita",
        "fianchi": "Fianchi",
        "spalle": "Spalle",
        "manica": "Manica",
        "cavallo": "Cavallo/Inseam",
        "collo": "Circonferenza Collo",
        "sec1_title": "DIAGNOSTICA FIT",
        "sec1_sub": "Analisi tecnica, scheda voti e abbinamenti cromatici avanzati",
        "sec1_step1": "1. Carica Immagine",
        "sec1_upload": "Seleziona scatto",
        "sec1_step2": "2. Parametri di Focus",
        "sec1_type": "Tipo di Scatto / Oggetto dell'analisi",
        "sec1_type_opts": ["Outfit Completo", "Capo Singolo (Giacca, Pantaloni, Abito, ecc.)", "Volto / Lineamenti / Armocromia", "Scarpe e Accessori"],
        "sec1_occ": "Occasione d'Uso prevista",
        "sec1_occ_opts": ["Casual / Everyday", "Business / Formale / Lavoro", "Serata / Evento Elegante", "Creativo / Avant-Garde / Runway", "Nessuna in particolare"],
        "sec1_notes": "Descrizione o dubbi specifici (opzionale)",
        "sec1_btn": "⚡ ANALIZZA CON IL MAESTRO",
        "sec1_report": "Report e Scheda Valutazione Sartoriale",
        "sec2_title": "GUARDAROBA DIGITALE",
        "sec2_sub": "Cataloga e gestisci i tuoi capi d'abbigliamento e accessori in modo permanente",
        "sec2_tab1": "➕ AGGIUNGI NUOVO CAPO O ACCESSORIO",
        "sec2_tab2": "👔 IL TUO ARMADIO",
        "sec2_mode": "Seleziona modalità di inserimento:",
        "sec2_modes": ["📸 Carica Foto dal Dispositivo (Riconoscimento IA)", "🔍 Ricerca Automatica sul Web (Marca + Modello)", "🔗 Inserisci Link URL Immagine"],
        "sec2_ai_title": "🤖 Assistente Visivo Sartoriale",
        "sec2_ai_desc": "Fai analizzare la foto a Gemini per identificare automaticamente tipo di vestito, accessorio, tessuto, colore e dettagli!",
        "sec2_ai_btn": "✨ RICONOSCI DETTAGLI CON IA",
        "sec2_cat_opts": ["Pantaloni", "Giacche / Capispalla", "Camicie / Bluse / Polo", "Maglieria", "Abiti Completi / Vestiti", "Gonne", "Scarpe", "Accessori"],
        "sec2_mat_opts": ["Cotone", "Lana / Cashmere", "Lino", "Seta", "Pelle / Camoscio", "Misto / Tecnico"],
        "sec2_sea_opts": ["Tutte le stagioni", "Autunno / Inverno", "Primavera / Estate"],
        "sec2_save": "💾 SALVA NEL GUARDAROBA",
        "sec2_empty": "👋 Il tuo guardaroba è attualmente vuoto. Utilizza la scheda 'Aggiungi nuovo capo o accessorio' per registrare i tuoi vestiti.",
        "sec2_filter": "Filtra per Categoria:",
        "sec2_all": "Tutti",
        "sec2_remove": "🗑️ Rimuovi",
        "sec3_title": "GENERATORE OUTFIT",
        "sec3_sub": "Crea abbinamenti perfetti attingendo dal tuo armadio ed integrando accessori ideali",
        "sec3_p1": "1. Parametri della Stylist Session",
        "sec3_occ_opts": ["Business / Meeting Formale", "Smart Casual / Ufficio informale", "Aperitivo / Serata Elegante", "Cerimonia / Matrimonio", "Weekend / Casual Tempo Libero", "Viaggio / Dynamic Style"],
        "sec3_meteo_opts": ["Primavera (Mite / Brezza)", "Estate (Caldo Intenso)", "Autunno (Fresco / Variabile)", "Inverno (Freddo / Capispalla Pesanti)", "Giornata di Pioggia"],
        "sec3_style_opts": ["Classico Sartoriale", "Quiet Luxury / Minimal Chic", "Modern Preppy / Ivy League", "Streetwear Elegante / Avant-Garde", "Sprezzatura Italiana"],
        "sec3_btn": "✨ GENERI OUTFIT CON L'IA",
        "sec3_report": "Proposta Stylist dell'Atelier",
        "sec4_title": "ATELIER ACADEMY",
        "sec4_sub": "Il tuo Mentore Sartoriale e Storico della Moda personale. Poni qualsiasi domanda per ampliare le tue conoscenze.",
        "sec4_quick_title": "💡 Spunti e Argomenti Rapidi",
        "sec4_quick_desc": "Clicca su un argomento o scrivi la tua domanda personalizzata a destra:",
        "sec4_quick_qs": [
            "Cos'è la Sprezzatura e come applicarla?",
            "Differenza tra lana Super 100s, 130s e 150s?",
            "Come scegliere il colletto della camicia o scollo in base al viso?",
            "Regole fondamentali del Dress Code Black Tie",
            "Come prendersi cura degli abiti in lana e cashmere?",
            "Come riconoscere un capo sartoriale rifinito a mano?"
        ],
        "sec4_chat_title": "💬 Consulta il Mentore dell'Atelier",
        "sec4_input_label": "Fai una domanda al Maestro:",
        "sec4_btn": "🎓 CHIEDI ALL'ACADEMY",
        "sec4_placeholder": "Scrivi qui la tua curiosità sartoriale...",
        "sec4_empty": "👋 Fai una domanda nel campo sopra o clicca su uno degli spunti rapidi a sinistra per iniziare la tua lezione con il Mentore!"
    },
    "English": {
        "lang_code": "English",
        "menu": ["Fit Diagnostics", "Wardrobe", "Outfit Generator", "Academy"],
        "config_title": "⚙️ AI Configuration",
        "misure_title": "📐 Tailoring Measurements",
        "modifica_misure": "Edit Physical Parameters",
        "sesso": "Gender / Sex",
        "sesso_opts": ["Man", "Woman"],
        "altezza": "Height (cm)",
        "peso": "Weight (kg)",
        "corporatura": "Body Type / Build",
        "postura": "Posture & Shoulders",
        "corp_opts": ["Athletic / Regular", "Slim / Lean", "Broad / Wide Chest", "Prominent Abdomen", "Tall / Longilineal", "Hourglass / Curved"],
        "post_opts": ["Erect / Standard", "Slanted Shoulders", "Straight / Square Shoulders", "Hunched Posture"],
        "misure_cm": "Measurements in Centimeters (cm):",
        "torace": "Chest / Bust",
        "vita": "Waist",
        "fianchi": "Hips",
        "spalle": "Shoulders",
        "manica": "Sleeve Length",
        "cavallo": "Inseam",
        "collo": "Neck Size",
        "sec1_title": "FIT DIAGNOSTICS",
        "sec1_sub": "Technical analysis, rating card, and advanced color matching",
        "sec1_step1": "1. Upload Image",
        "sec1_upload": "Select photo",
        "sec1_step2": "2. Focus Parameters",
        "sec1_type": "Photo Type / Subject of Analysis",
        "sec1_type_opts": ["Full Outfit", "Single Garment (Jacket, Trousers, Dress, etc.)", "Face / Features / Color Analysis", "Shoes and Accessories"],
        "sec1_occ": "Intended Occasion",
        "sec1_occ_opts": ["Casual / Everyday", "Business / Formal / Work", "Evening / Elegant Event", "Creative / Avant-Garde / Runway", "None in particular"],
        "sec1_notes": "Specific description or questions (optional)",
        "sec1_btn": "⚡ ANALYZE WITH MASTER TAILOR",
        "sec1_report": "Tailoring Evaluation Report & Scorecard",
        "sec2_title": "DIGITAL WARDROBE",
        "sec2_sub": "Catalog and manage your clothing items permanently with AI assistance",
        "sec2_tab1": "➕ ADD NEW ITEM OR ACCESSORY",
        "sec2_tab2": "👔 YOUR WARDROBE",
        "sec2_mode": "Select entry method:",
        "sec2_modes": ["📸 Upload Photo from Device (AI Recognition)", "🔍 Automatic Web Search (Brand + Model)", "🔗 Insert Image URL Link"],
        "sec2_ai_title": "🤖 Sartorial Visual Assistant",
        "sec2_ai_desc": "Have Gemini analyze the photo to automatically detect garment type, accessory, fabric, color, and details!",
        "sec2_ai_btn": "✨ RECOGNIZE DETAILS WITH AI",
        "sec2_cat_opts": ["Trousers", "Jackets / Outerwear", "Shirts / Blouses / Polos", "Knitwear", "Suits / Dresses", "Skirts", "Shoes", "Accessories"],
        "sec2_mat_opts": ["Cotton", "Wool / Cashmere", "Linen", "Silk", "Leather / Suede", "Blended / Technical"],
        "sec2_sea_opts": ["All Seasons", "Autumn / Winter", "Spring / Summer"],
        "sec2_save": "💾 SAVE TO WARDROBE",
        "sec2_empty": "👋 Your wardrobe is currently empty. Use the 'Add new item or accessory' tab to register your clothes.",
        "sec2_filter": "Filter by Category:",
        "sec2_all": "All",
        "sec2_remove": "🗑️ Remove",
        "sec3_title": "OUTFIT GENERATOR",
        "sec3_sub": "Create flawless combinations from your wardrobe and suggest ideal complementary accessories",
        "sec3_p1": "1. Stylist Session Parameters",
        "sec3_occ_opts": ["Business / Formal Meeting", "Smart Casual / Office", "Aperitif / Evening Event", "Ceremony / Wedding", "Weekend / Casual Leisure", "Travel / Dynamic Style"],
        "sec3_meteo_opts": ["Spring (Mild / Breeze)", "Summer (Intense Heat)", "Autumn (Cool / Variable)", "Winter (Cold / Heavy Outerwear)", "Rainy Day"],
        "sec3_style_opts": ["Classic Tailored", "Quiet Luxury / Minimal Chic", "Modern Preppy / Ivy League", "Elegant Streetwear / Avant-Garde", "Italian Sprezzatura"],
        "sec3_btn": "✨ GENERATE OUTFIT WITH AI",
        "sec3_report": "Atelier Stylist Proposal",
        "sec4_title": "ATELIER ACADEMY",
        "sec4_sub": "Your personal Sartorial Mentor and Fashion Historian. Ask any question to expand your knowledge.",
        "sec4_quick_title": "💡 Quick Topics & Prompts",
        "sec4_quick_desc": "Click on a topic or write your custom question on the right:",
        "sec4_quick_qs": [
            "What is Sprezzatura and how to apply it?",
            "Difference between Super 100s, 130s, and 150s wool?",
            "How to choose shirt collar or neckline based on face shape?",
            "Essential rules of Black Tie Dress Code",
            "How to care for wool and cashmere garments?",
            "How to identify a genuine handmade tailoring finish?"
        ],
        "sec4_chat_title": "💬 Consult the Atelier Mentor",
        "sec4_input_label": "Ask a question to the Master:",
        "sec4_btn": "🎓 ASK ACADEMY",
        "sec4_placeholder": "Type your sartorial query here...",
        "sec4_empty": "👋 Ask a question above or click one of the quick topics on the left to start your masterclass!"
    },
    "Deutsch": {
        "lang_code": "Deutsch",
        "menu": ["Passform-Diagnose", "Garderobe", "Outfit-Generator", "Academy"],
        "config_title": "⚙️ KI-Konfiguration",
        "misure_title": "📐 Schneider-Masse",
        "modifica_misure": "Körperparameter bearbeiten",
        "sesso": "Geschlecht",
        "sesso_opts": ["Mann", "Frau"],
        "altezza": "Grösse (cm)",
        "peso": "Gewicht (kg)",
        "corporatura": "Körperbau / Statur",
        "postura": "Haltung & Schultern",
        "corp_opts": ["Athletisch / Normal", "Schlank / Dünn", "Kräftig / Breiter Brustkorb", "Ausgeprägter Bauch", "Gross / Longiline", "Sanduhr / Kurvig"],
        "post_opts": ["Aufrecht / Standard", "Hängende Schultern", "Gerade / Quadratische Schultern", "Gebogene Haltung"],
        "misure_cm": "Massangaben in Zentimetern (cm):",
        "torace": "Brustumfang",
        "vita": "Taillenumfang",
        "fianchi": "Hüftumfang",
        "spalle": "Schulterbreite",
        "manica": "Ärmellänge",
        "cavallo": "Schrittlänge",
        "collo": "Halsweite",
        "sec1_title": "PASSFORM-DIAGNOSE",
        "sec1_sub": "Technische Analyse, Bewertung und erweiterte Farbkombinationen",
        "sec1_step1": "1. Bild hochladen",
        "sec1_upload": "Foto auswählen",
        "sec1_step2": "2. Fokus-Parameter",
        "sec1_type": "Foto-Typ / Analyseobjekt",
        "sec1_type_opts": ["Gesamtes Outfit", "Einzelkleidungsstück (Sakko, Hose, Kleid, etc.)", "Gesicht / Farbanalyse", "Schuhe und Accessoires"],
        "sec1_occ": "Geplanter Anlass",
        "sec1_occ_opts": ["Freizeit / Alltag", "Business / Formell", "Abendveranstaltung / Elegant", "Kreativ / Avantgarde", "Kein spezieller Anlass"],
        "sec1_notes": "Spezifische Fragen oder Anmerkungen (optional)",
        "sec1_btn": "⚡ MIT DEM SCHNEIDERMEISTER ANALYSIEREN",
        "sec1_report": "Schneider-Bewertungsbericht",
        "sec2_title": "DIGITALE GARDEROBE",
        "sec2_sub": "Katalogisieren und verwalten Sie Ihre Kleidung dauerhaft mit KI-Unterstützung",
        "sec2_tab1": "➕ NEUES TEIL ODER ACCESSOIRE HINZUFÜGEN",
        "sec2_tab2": "👔 IHR KLEIDERSCHRANK",
        "sec2_mode": "Eingabemethode wählen:",
        "sec2_modes": ["📸 Foto vom Gerät hochladen (KI-Erkennung)", "🔍 Automatische Web-Suche (Marke + Modell)", "🔗 Bild-URL eingeben"],
        "sec2_ai_title": "🤖 Visueller Schneider-Assistent",
        "sec2_ai_desc": "Lassen Sie Gemini das Foto analysieren, um Kleidungstyp, Stoff, Farbe und Details automatisch zu erkennen!",
        "sec2_ai_btn": "✨ DETAILS MIT KI ERKENNEN",
        "sec2_cat_opts": ["Hosen", "Jacken / Mäntel", "Hemden / Blusen / Polos", "Strickbekleidung", "Anzüge / Kleider", "Röcke", "Schuhe", "Accessoires"],
        "sec2_mat_opts": ["Baumwolle", "Wolle / Kaschmir", "Leinen", "Seide", "Leder / Wildleder", "Mischgewebe / Technische Fasern"],
        "sec2_sea_opts": ["Alle Jahreszeiten", "Herbst / Winter", "Frühling / Sommer"],
        "sec2_save": "💾 IN GARDEROBE SPEICHERN",
        "sec2_empty": "👋 Ihre Garderobe ist derzeit leer. Nutzen Sie das Tab 'Neues Teil hinzufügen', um Ihre Kleidung zu erfassen.",
        "sec2_filter": "Nach Kategorie filtern:",
        "sec2_all": "Alle",
        "sec2_remove": "🗑️ Entfernen",
        "sec3_title": "OUTFIT-GENERATOR",
        "sec3_sub": "Erstellen Sie perfekte Kombinationen aus Ihrem Kleiderschrank und passenden Accessoires",
        "sec3_p1": "1. Stylist-Sitzungsparameter",
        "sec3_occ_opts": ["Business / Formelles Meeting", "Smart Casual / Büro", "Aperitif / Eleganter Abend", "Zeremonie / Hochzeit", "Wochenende / Freizeit", "Reise / Dynamischer Stil"],
        "sec3_meteo_opts": ["Frühling (Mild / Brise)", "Sommer (Hitze)", "Herbst (Kühl / Variable)", "Winter (Kalt / Schwere Mäntel)", "Regentag"],
        "sec3_style_opts": ["Klassisch Schneiderei", "Quiet Luxury / Minimal Chic", "Modern Preppy / Ivy League", "Eleganter Streetwear / Avantgarde", "Italienische Sprezzatura"],
        "sec3_btn": "✨ OUTFIT MIT KI GENERIEREN",
        "sec3_report": "Atelier-Stylist-Vorschlag",
        "sec4_title": "ATELIER ACADEMY",
        "sec4_sub": "Ihr persönlicher Schneider-Mentor und Modehistoriker. Stellen Sie Fragen, um Ihr Wissen zu erweitern.",
        "sec4_quick_title": "💡 Schnelle Themen & Fragen",
        "sec4_quick_desc": "Klicken Sie auf ein Thema oder schreiben Sie Ihre Frage rechts:",
        "sec4_quick_qs": [
            "Was ist Sprezzatura und wie wendet man sie an?",
            "Unterschied zwischen Super 100s, 130s und 150s Wolle?",
            "Wie wählt man den Hemdkragen passend zur Gesichtsform?",
            "Grundregeln des Black Tie Dresscodes",
            "Wie pflegt man Kleidungsstücke aus Wolle und Kaschmir?",
            "Wie erkennt man ein echtes handgenähtes Knopfloch?"
        ],
        "sec4_chat_title": "💬 Fragen Sie den Atelier-Mentor",
        "sec4_input_label": "Stellen Sie eine Frage an den Meister:",
        "sec4_btn": "🎓 ACADEMY FRAGEN",
        "sec4_placeholder": "Geben Sie hier Ihre Fragen zur Schneiderei ein...",
        "sec4_empty": "👋 Stellen Sie oben eine Frage oder klicken Sie links auf ein Thema, um Ihre Lektion zu beginnen!"
    },
    "Albanese": {
        "lang_code": "Shqip",
        "menu": ["Diagnostikimi i Prerjes", "Garderoba", "Gjeneruesi i Outfit-eve", "Akademia"],
        "config_title": "⚙️ Konfigurimi i AI",
        "misure_title": "📐 Skeda e Masave Rrobaqepëse",
        "modifica_misure": "Ndrysho Parametrat Fizikë",
        "sesso": "Gjinija",
        "sesso_opts": ["Mashkull", "Femër"],
        "altezza": "Lartësia (cm)",
        "peso": "Pesha (kg)",
        "corporatura": "Trupformimi / Ndërtimi Fizik",
        "postura": "Qëndrimi & Supet",
        "corp_opts": ["Atletike / Rregullt", "E Hollë / Slim", "E Bëshme / Gjoks i Gjerë", "Me Bark të Dalë", "Shtatnaltë / Longilineo", "Orë Rëre / Formë me Kurva"],
        "post_opts": ["Ngrritur / Standarde", "Supe të Rëna", "Supe të Drejta / Katrore", "Qëndrim i Varur"],
        "misure_cm": "Masat në Centimetra (cm):",
        "torace": "Gjoksi / Sfondi",
        "vita": "Brezi / Belit",
        "fianchi": "Kofshët",
        "spalle": "Gjerësia e Supeve",
        "manica": "Gjatësia e Mëngës",
        "cavallo": "Mbrëndësia e Këmbës (Inseam)",
        "collo": "Qafa",
        "sec1_title": "DIAGNOSTIKIMI I PRERJES (FIT)",
        "sec1_sub": "Analizë teknike, skedë vlerësimi dhe kombinime ngjyrash të avancuara",
        "sec1_step1": "1. Ngarko Imazhin",
        "sec1_upload": "Zgjidh foton",
        "sec1_step2": "2. Parametrat e Fokusit",
        "sec1_type": "Lloji i Fotos / Objekti i Analizës",
        "sec1_type_opts": ["Outfit i Plotë", "Veshje Teke (Xhaketë, Pantallona, Fustan, etc.)", "Fytyra / Veçoritë / Kolorimetria", "Këpucë dhe Aksesorë"],
        "sec1_occ": "Rasti i Përdorimit",
        "sec1_occ_opts": ["Kauzale / Përditshmëri", "Biznes / Formale / Punë", "Mbrëmje / Ngjarje Elegante", "Krijuar / Avantgardë", "Asnjë e veçantë"],
        "sec1_notes": "Përshkrim ose pyetje specifike (opsionale)",
        "sec1_btn": "⚡ ANALIZO ME MESTRIN RROBAQEPËS",
        "sec1_report": "Raporti dhe Skeda e Vlerësimit",
        "sec2_title": "GARDEROBA DIGJITALE",
        "sec2_sub": "Katalogoni dhe menaxhoni veshjet tuaja në mënyrë permanente",
        "sec2_tab1": "➕ SHTO VESHJE OSE AKSESOR TË RI",
        "sec2_tab2": "👔 DOLLAPI YTI",
        "sec2_mode": "Zgjidh mënyrën e futjes:",
        "sec2_modes": ["📸 Ngarko Foto nga Pajisja (Njohje me AI)", "🔍 Kërkim Automatik në Ueb (Marka + Modeli)", "🔗 Vendos Linkun e Fotos"],
        "sec2_ai_title": "🤖 Ndihmësi Vizual i Rrobaqepësisë",
        "sec2_ai_desc": "Lëreni Gemini të analizojë foton për të identifikuar automatikisht llojin e veshjes, materialin, ngjyrën dhe detajet!",
        "sec2_ai_btn": "✨ NJOH DETAJET ME AI",
        "sec2_cat_opts": ["Pantallona", "Xhaketa / Pallto", "Këmisha / Bluza / Polo", "Triko / Trikotazh", "Kostume / Fustane", "Fuste", "Këpucë", "Aksesore"],
        "sec2_mat_opts": ["Pambuk", "Lesh / Kashmir", "In", "Mëndafsh", "Lëkurë / Kamosh", "Miks / Teknike"],
        "sec2_sea_opts": ["Të gjitha stinët", "Vjeshtë / Dimër", "Pranverë / Verë"],
        "sec2_save": "💾 RUAJ NË GARDEROBË",
        "sec2_empty": "👋 Garderoba juaj është aktualisht bosh. Përdorni skedën 'Shto veshje të re' për të regjistruar rrobat tuaja.",
        "sec2_filter": "Filtro sipas Kategorisë:",
        "sec2_all": "Të gjitha",
        "sec2_remove": "🗑️ Fshij",
        "sec3_title": "GJENERUESI I OUTFIT-EVE",
        "sec3_sub": "Krijoni kombinime perfekte nga dollapi juaj dhe sugjeroni aksesorët plotësues idealë",
        "sec3_p1": "1. Parametrat e Sesionit të Stilit",
        "sec3_occ_opts": ["Biznes / Takim Formal", "Smart Casual / Zyrë", "Aperitiv / Mbrëmje Elegante", "Cermoni / Martesë", "Fundjavë / Kohë e Lirë", "Udhëtim / Stil Dinamik"],
        "sec3_meteo_opts": ["Pranverë (E butë / Era)", "Verë (Nxehtësi e Madhe)", "Vjeshtë (E freskët)", "Dimër (Ftohtë / Pallto të Rënda)", "Ditë me Chiadër / Shi"],
        "sec3_style_opts": ["Klasike Rrobaqepësie", "Quiet Luxury / Minimal Chic", "Modern Preppy / Ivy League", "Streetwear Elegant / Avant-Garde", "Sprezzatura Italiane"],
        "sec3_btn": "✨ GJENERO OUTFIT ME AI",
        "sec3_report": "Propozimi i Stilistit të Atelierit",
        "sec4_title": "AKADEMIA E ATELIERIT",
        "sec4_sub": "Mentori juaj personal i Stilit dhe Historiani i Modës. Bëni çdo pyetje për të zgjeruar njohuritë tuaja.",
        "sec4_quick_title": "💡 Tema dhe Pyetje të Shpejta",
        "sec4_quick_desc": "Klikoni mbi një temë ose shkruani pyetjen tuaj në të djathtë:",
        "sec4_quick_qs": [
            "Çfarë është Sprezzatura dhe si aplikohet?",
            "Dallimi mes leshit Super 100s, 130s dhe 150s?",
            "Si të zgjedhim jakën e këmishës sipas formës së fytyrës?",
            "Rregullat kryesore të Kodeve të Veshjes Black Tie",
            "Si të kujdesemi për veshjet me lesh dhe kashmir?",
            "Si të njohim një vrimë kopshe të bërë me dorë?"
        ],
        "sec4_chat_title": "💬 Konsultohuni me Mentorin e Atelierit",
        "sec4_input_label": "Bëj një pyetje për Maestron:",
        "sec4_btn": "🎓 PYET AKADEMINË",
        "sec4_placeholder": "Shkruani pyetjen tuaj rreth rrobaqepësisë këtu...",
        "sec4_empty": "👋 Bëni një pyetje më sipër ose klikoni në një nga temat e shpejta në të majtë për të filluar mësimin tuaj!"
    }
}

# ==========================================
# 2. CONFIGURAZIONE PAGINA
# ==========================================
st.set_page_config(
    page_title="ATELIER | Analisi Moda & Sartoria",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS per Sfondo Bianco Permanente
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff !important;
        color: #111111 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #f7f7f9 !important;
        border-right: 1px solid #e2e8f0;
    }
    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: #111111 !important;
    }
    .atelier-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 22px;
        margin-bottom: 20px;
        border-radius: 8px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. INIZIALIZZAZIONE SESSION STATE E PERSISTENZA
# ==========================================
if "lingua" not in st.session_state:
    st.session_state.lingua = "Italiano"

if "api_key_salvata" not in st.session_state:
    st.session_state.api_key_salvata = carica_config_api_key()

DEFAULT_PROFILO = {
    "sesso": "Uomo",
    "altezza": 178,
    "peso": 75,
    "corporatura": "Atletica / Regolare",
    "torace": 102,
    "vita": 84,
    "fianchi": 98,
    "spalle": 46,
    "manica": 64,
    "cavallo": 81,
    "collo": 40,
    "postura": "Eretta / Standard"
}

if "profilo" not in st.session_state:
    st.session_state.profilo = DEFAULT_PROFILO.copy()
else:
    for k, v in DEFAULT_PROFILO.items():
        st.session_state.profilo.setdefault(k, v)

# Caricamento permanente del guardaroba da file JSON
if "guardaroba" not in st.session_state:
    st.session_state.guardaroba = carica_guardaroba()

if "academy_chat" not in st.session_state:
    st.session_state.academy_chat = []

if "auto_data" not in st.session_state:
    st.session_state.auto_data = {
        "nome": "", "categoria": "Pantaloni", "marca": "", "modello": "",
        "taglia": "", "colore": "", "materiale": "Cotone", "stagione": "Tutte le stagioni", "note": ""
    }

# ==========================================
# 4. SELETTORE LINGUA IN ALTO
# ==========================================
col_spazio, col_lang = st.columns([4, 2])
with col_lang:
    scelta_lingua = st.selectbox(
        "🌐 Lingua / Language",
        ["Italiano", "English", "Deutsch", "Albanese"],
        index=["Italiano", "English", "Deutsch", "Albanese"].index(st.session_state.lingua),
        label_visibility="collapsed"
    )
    st.session_state.lingua = scelta_lingua

t = I18N[st.session_state.lingua]

# ==========================================
# 5. BARRA LATERALE (CONFIG & MISURE)
# ==========================================
st.sidebar.title("ATELIER")
sezione_idx = st.sidebar.radio(
    "MENU",
    range(len(t["menu"])),
    format_func=lambda x: t["menu"][x]
)

st.sidebar.markdown("---")
st.sidebar.subheader(t["config_title"])

# API Key memorizzata permanentemente
api_key_input = st.sidebar.text_input(
    "Gemini API Key", 
    value=st.session_state.api_key_salvata, 
    type="password", 
    help="Inserisci la tua chiave API. Verrà salvata automaticamente in locale."
)

if api_key_input != st.session_state.api_key_salvata:
    st.session_state.api_key_salvata = api_key_input
    salva_config_api_key(api_key_input)
    st.sidebar.success("🔑 API Key salvata permanentemente!")

st.sidebar.markdown("---")
st.sidebar.subheader(t["misure_title"])

with st.sidebar.expander(t["modifica_misure"], expanded=False):
    # Opzione Genere Uomo / Donna
    sesso_idx = 0 if st.session_state.profilo.get("sesso", "Uomo") in ["Uomo", "Man", "Mann", "Mashkull"] else 1
    sesso_scelto = st.selectbox(t["sesso"], t["sesso_opts"], index=sesso_idx)
    st.session_state.profilo["sesso"] = sesso_scelto

    st.session_state.profilo["altezza"] = st.number_input(t["altezza"], value=st.session_state.profilo["altezza"], step=1)
    st.session_state.profilo["peso"] = st.number_input(t["peso"], value=st.session_state.profilo["peso"], step=1)
    
    st.session_state.profilo["corporatura"] = st.selectbox(
        t["corporatura"],
        t["corp_opts"],
        index=0
    )
    st.session_state.profilo["postura"] = st.selectbox(
        t["postura"],
        t["post_opts"],
        index=0
    )
    
    st.markdown(f"**{t['misure_cm']}**")
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        st.session_state.profilo["torace"] = st.number_input(t["torace"], value=st.session_state.profilo["torace"], step=1)
        st.session_state.profilo["vita"] = st.number_input(t["vita"], value=st.session_state.profilo["vita"], step=1)
        st.session_state.profilo["fianchi"] = st.number_input(t["fianchi"], value=st.session_state.profilo["fianchi"], step=1)
    with c_s2:
        st.session_state.profilo["spalle"] = st.number_input(t["spalle"], value=st.session_state.profilo["spalle"], step=1)
        st.session_state.profilo["manica"] = st.number_input(t["manica"], value=st.session_state.profilo["manica"], step=1)
        st.session_state.profilo["cavallo"] = st.number_input(t["cavallo"], value=st.session_state.profilo["cavallo"], step=1)
        
    st.session_state.profilo["collo"] = st.number_input(t["collo"], value=st.session_state.profilo["collo"], step=1)

def get_scheda_fisica_prompt():
    p = st.session_state.profilo
    return f"""
    - Gender/Sex: {p['sesso']}
    - Height: {p['altezza']} cm | Weight: {p['peso']} kg
    - Build: {p['corporatura']} | Posture/Shoulders: {p['postura']}
    - Tailoring Technical Measurements: Chest/Bust {p['torace']} cm, Waist {p['vita']} cm, Hips {p['fianchi']} cm, Shoulder Width {p['spalle']} cm, Sleeve Length {p['manica']} cm, Inseam {p['cavallo']} cm, Neck {p['collo']} cm
    """

# ==========================================
# SEZIONE 1: DIAGNOSTICA FIT
# ==========================================
if sezione_idx == 0:
    st.title(t["sec1_title"])
    st.markdown(f"<p style='color: #666; letter-spacing: 1px; text-transform: uppercase; font-size: 0.85rem;'>{t['sec1_sub']}</p>", unsafe_allow_html=True)
    
    col_1, col_2 = st.columns(2, gap="large")
    
    with col_1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader(t["sec1_step1"])
        
        uploaded_file = st.file_uploader(t["sec1_upload"], type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Photo acquired", use_container_width=True)
            
            st.markdown("---")
            st.subheader(t["sec1_step2"])
            
            tipo_scatto = st.selectbox(t["sec1_type"], t["sec1_type_opts"])
            occasione = st.selectbox(t["sec1_occ"], t["sec1_occ_opts"])
            dettagli_extra = st.text_area(t["sec1_notes"], height=90)
            
            analizza_btn = st.button(t["sec1_btn"])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_2:
        st.markdown("<div class='atelier-card' style='min-height: 400px;'>", unsafe_allow_html=True)
        st.subheader(t["sec1_report"])
        
        if uploaded_file is not None:
            if 'analizza_btn' in locals() and analizza_btn:
                if not api_key_input:
                    st.error("⚠️ Inserisci la tua API Key di Google Gemini nella barra laterale.")
                elif not HAS_GENAI:
                    st.error("⚠️ La libreria `google-genai` non è installata.")
                else:
                    with st.spinner("Analyzing with Master Tailor..."):
                        client = genai.Client(api_key=api_key_input)
                        scheda_fisica = get_scheda_fisica_prompt()
                        note_testo = dettagli_extra.strip() if dettagli_extra else "None"
                        
                        prompt_atelier = f"""
                        You are an esteemed Master Tailor and Fashion Stylist.
                        IMPORTANT: Respond ENTIRELY in {t['lang_code']} language.
                        
                        USER TAILORING MEASUREMENTS & PROFILE:
                        {scheda_fisica}
                        
                        ANALYSIS PARAMETERS:
                        - Photo Subject: {tipo_scatto}
                        - Occasion: {occasione}
                        - User Notes: "{note_testo}"
                        
                        Analyze the photo with precision and present the report with formatted sections:
                        1. Evaluation Scorecard (Proportions, Harmony, Fit, Occasion match with scores /10)
                        2. Color Palette & Complementary Shades
                        3. Technical Fit Analysis (shoulders, waist, sleeves based on gender and measurements)
                        4. Response to User's Question/Notes
                        5. Recommended Tailoring Alterations
                        6. Master's Verdict
                        """
                        
                        modelli_da_provare = ['gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-2.5-flash', 'gemini-2.0-flash']
                        risposta_ottenuta = None
                        
                        for mod in modelli_da_provare:
                            try:
                                response = client.models.generate_content(model=mod, contents=[image, prompt_atelier])
                                if response and response.text:
                                    risposta_ottenuta = response.text
                                    break 
                            except Exception:
                                continue 
                        
                        if risposta_ottenuta:
                            st.markdown(risposta_ottenuta)
                        else:
                            st.warning("⚠️ Service temporarily unavailable.")
        else:
            st.write("👋 Upload a photo on the left to start the analysis.")
            
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# SEZIONE 2: GUARDAROBA DIGITALE (PERMANENTE)
# ==========================================
elif sezione_idx == 1:
    st.title(t["sec2_title"])
    st.markdown(f"<p style='color: #666; letter-spacing: 1px; text-transform: uppercase; font-size: 0.85rem;'>{t['sec2_sub']}</p>", unsafe_allow_html=True)
    
    tab_registra, tab_catalogo = st.tabs([t["sec2_tab1"], t["sec2_tab2"]])
    
    with tab_registra:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader("1. Image Acquisition")
        
        modalita_foto = st.radio(t["sec2_mode"], t["sec2_modes"], horizontal=True)
        
        uploaded_img = None
        url_manuale = ""
        img_preview = None
        
        if 0 in [t["sec2_modes"].index(m) for m in [modalita_foto] if m in t["sec2_modes"]]:
            uploaded_img = st.file_uploader(t["sec1_upload"], type=["jpg", "jpeg", "png"])
            if uploaded_img is not None:
                img_preview = Image.open(uploaded_img)
                c_preview, c_ai_btn = st.columns([1, 2])
                with c_preview:
                    st.image(img_preview, caption="Photo", width=180)
                with c_ai_btn:
                    st.write(f"**{t['sec2_ai_title']}**")
                    st.caption(t["sec2_ai_desc"])
                    
                    if st.button(t["sec2_ai_btn"]):
                        if not api_key_input:
                            st.error("⚠️ Inserisci la tua API Key di Google Gemini.")
                        elif not HAS_GENAI:
                            st.error("⚠️ Libreria `google-genai` mancante.")
                        else:
                            with st.spinner("Analyzing..."):
                                client = genai.Client(api_key=api_key_input)
                                prompt_vision = """
                                Analyze this clothing item or accessory.
                                Return EXACTLY a JSON object without markdown formatting:
                                {
                                  "nome": "Short descriptive title",
                                  "categoria": "One of: Pantaloni, Giacche / Capispalla, Camicie / Bluse / Polo, Maglieria, Abiti Completi / Vestiti, Gonne, Scarpe, Accessori",
                                  "colore": "Primary color",
                                  "materiale": "One of: Cotone, Lana / Cashmere, Lino, Seta, Pelle / Camoscio, Misto / Tecnico",
                                  "stagione": "One of: Tutte le stagioni, Autunno / Inverno, Primavera / Estate",
                                  "note": "Short note on details."
                                }
                                """
                                res = None
                                for mod in ['gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-2.5-flash', 'gemini-2.0-flash']:
                                    try:
                                        res = client.models.generate_content(model=mod, contents=[img_preview, prompt_vision])
                                        if res and res.text: break
                                    except Exception: continue
                                
                                if res and res.text:
                                    try:
                                        text_resp = res.text.strip().replace("```json", "").replace("```", "").strip()
                                        dados_json = json.loads(text_resp)
                                        st.session_state.auto_data.update(dados_json)
                                        st.success("✅ Auto-filled with AI!")
                                    except Exception as err:
                                        st.error(f"Error parsing AI JSON: {err}")

        elif 2 in [t["sec2_modes"].index(m) for m in [modalita_foto] if m in t["sec2_modes"]]:
            url_manuale = st.text_input("URL Image", placeholder="https://example.com/item.jpg")

        st.markdown("---")
        st.subheader("2. Registration Card")
        
        with st.form("form_guardaroba"):
            c1, c2, c3 = st.columns(3)
            with c1:
                nome_capo = st.text_input("Title / Item Name*", value=st.session_state.auto_data["nome"])
                categoria = st.selectbox("Category*", t["sec2_cat_opts"])
            with c2:
                marca = st.text_input("Brand", value=st.session_state.auto_data["marca"])
                modello = st.text_input("Model / Fit", value=st.session_state.auto_data["modello"])
            with c3:
                taglia = st.text_input("Size", value=st.session_state.auto_data["taglia"])
                colore = st.text_input("Primary Color*", value=st.session_state.auto_data["colore"])

            c4, c5 = st.columns(2)
            with c4:
                materiale = st.selectbox("Fabric / Material", t["sec2_mat_opts"])
                stagione = st.selectbox("Season", t["sec2_sea_opts"])
            with c5:
                note_capo = st.text_area("Tailoring Notes", value=st.session_state.auto_data["note"], height=88)

            salva_btn = st.form_submit_button(t["sec2_save"])
            
            if salva_btn:
                if not nome_capo or not colore:
                    st.error("⚠️ Fill Name and Color.")
                else:
                    img_path_str = ""
                    new_id = len(st.session_state.guardaroba) + 1
                    
                    if uploaded_img is not None:
                        # Salvataggio fisico dell'immagine nella cartella uploads/
                        img_filename = f"{UPLOAD_DIR}/capo_{new_id}_{int(time.time())}.png"
                        Image.open(uploaded_img).save(img_filename)
                        img_path_str = img_filename
                    elif url_manuale:
                        img_path_str = url_manuale
                    else:
                        img_path_str = "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?q=80&w=500&auto=format&fit=crop"

                    nuovo_capo = {
                        "id": new_id,
                        "nome": nome_capo, "categoria": categoria, "marca": marca or "Tailored",
                        "modello": modello or "Standard", "taglia": taglia or "N.D.",
                        "colore": colore, "materiale": materiale, "stagione": stagione,
                        "note": note_capo, "immagine": img_path_str
                    }
                    st.session_state.guardaroba.append(nuovo_capo)
                    salva_guardaroba(st.session_state.guardaroba)
                    st.success(f"✅ '{nome_capo}' saved permanently to wardrobe!")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_catalogo:
        if not st.session_state.guardaroba:
            st.info(t["sec2_empty"])
        else:
            cat_scelta = st.selectbox(t["sec2_filter"], [t["sec2_all"]] + list(set([item["categoria"] for item in st.session_state.guardaroba])))
            capi_filtrati = st.session_state.guardaroba if cat_scelta == t["sec2_all"] else [c for c in st.session_state.guardaroba if c["categoria"] == cat_scelta]
            
            cols = st.columns(3)
            for idx, capo in enumerate(capi_filtrati):
                with cols[idx % 3]:
                    st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
                    st.image(capo["immagine"], use_container_width=True)
                    st.markdown(f"### {capo['nome']}")
                    st.markdown(f"**Cat:** {capo['categoria']} | **Brand:** {capo['marca']}")
                    st.markdown(f"**Color:** {capo['colore']} | **Fabric:** {capo['materiale']}")
                    
                    if st.button(t["sec2_remove"], key=f"del_{capo['id']}"):
                        # Rimuovi file locale se presente
                        if capo["immagine"].startswith(UPLOAD_DIR) and os.path.exists(capo["immagine"]):
                            try: os.remove(capo["immagine"])
                            except Exception: pass
                            
                        st.session_state.guardaroba = [c for c in st.session_state.guardaroba if c["id"] != capo["id"]]
                        salva_guardaroba(st.session_state.guardaroba)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# SEZIONE 3: GENERATORE OUTFIT
# ==========================================
elif sezione_idx == 2:
    st.title(t["sec3_title"])
    st.markdown(f"<p style='color: #666; letter-spacing: 1px; text-transform: uppercase; font-size: 0.85rem;'>{t['sec3_sub']}</p>", unsafe_allow_html=True)
    
    col_out_left, col_out_right = st.columns([1, 1], gap="large")
    
    with col_out_left:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader(t["sec3_p1"])
        
        occasione_outfit = st.selectbox("Occasion", t["sec3_occ_opts"])
        meteo_outfit = st.selectbox("Season & Weather", t["sec3_meteo_opts"])
        stile_outfit = st.selectbox("Desired Style", t["sec3_style_opts"])
        note_outfit = st.text_area("Specific requests / garments to include", height=90)
        
        genera_btn = st.button(t["sec3_btn"])
        st.markdown("</div>", unsafe_allow_html=True)

    with col_out_right:
        st.markdown("<div class='atelier-card' style='min-height: 400px;'>", unsafe_allow_html=True)
        st.subheader(t["sec3_report"])
        
        if 'genera_btn' in locals() and genera_btn:
            if not api_key_input:
                st.error("⚠️ Inserisci la tua API Key di Google Gemini.")
            elif not HAS_GENAI:
                st.error("⚠️ Libreria `google-genai` mancante.")
            else:
                with st.spinner("Styling outfit..."):
                    client = genai.Client(api_key=api_key_input)
                    scheda_fisica = get_scheda_fisica_prompt()
                    
                    armadio_str = "\n".join([
                        f"- [ID {c['id']}] {c['nome']} | Cat: {c['categoria']} | Color: {c['colore']} | Fabric: {c['materiale']}"
                        for c in st.session_state.guardaroba
                    ]) if st.session_state.guardaroba else "Wardrobe is empty. Suggest an ideal full outfit."

                    prompt_generatore = f"""
                    You are an Elite Fashion Stylist and Master Tailor.
                    IMPORTANT: Answer ENTIRELY in {t['lang_code']} language.
                    
                    USER TAILORING MEASUREMENTS:
                    {scheda_fisica}
                    
                    REQUEST PARAMETERS:
                    - Occasion: {occasione_outfit}
                    - Weather: {meteo_outfit}
                    - Style: {stile_outfit}
                    - Notes: "{note_outfit.strip() if note_outfit else 'None'}"
                    
                    AVAILABLE WARDROBE:
                    {armadio_str}
                    
                    Format your response in structured Markdown:
                    1. 🧥 Selected Outfit from Wardrobe (citing IDs)
                    2. 👓 Missing / Recommended Complementary Accessories & Items to purchase
                    3. 🎨 Color Harmony & Anatomical Fit (tailored to user's gender and measurements)
                    4. 💡 Master's Touch (Styling advice)
                    """

                    risposta_ottenuta = None
                    for mod in ['gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-2.5-flash', 'gemini-2.0-flash']:
                        try:
                            response = client.models.generate_content(model=mod, contents=prompt_generatore)
                            if response and response.text:
                                risposta_ottenuta = response.text
                                break 
                        except Exception: continue 
                    
                    if risposta_ottenuta:
                        st.markdown(risposta_ottenuta)
                    else:
                        st.warning("⚠️️ Service unavailable.")
        else:
            st.write("👋 Set parameters on the left and click generate.")
            
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# SEZIONE 4: ACADEMY
# ==========================================
elif sezione_idx == 3:
    st.title(t["sec4_title"])
    st.markdown(f"<p style='color: #666; letter-spacing: 1px; text-transform: uppercase; font-size: 0.85rem;'>{t['sec4_sub']}</p>", unsafe_allow_html=True)
    
    col_ac1, col_ac2 = st.columns([1, 2], gap="large")
    
    with col_ac1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader(t["sec4_quick_title"])
        st.caption(t["sec4_quick_desc"])
        
        scelta_rapida = None
        for q in t["sec4_quick_qs"]:
            if st.button(f"📌 {q}", use_container_width=True):
                scelta_rapida = q
                
        st.markdown("</div>", unsafe_allow_html=True)

    with col_ac2:
        st.markdown("<div class='atelier-card' style='min-height: 500px;'>", unsafe_allow_html=True)
        st.subheader(t["sec4_chat_title"])
        
        domanda_utente = st.text_input(
            t["sec4_input_label"],
            value=scelta_rapida if scelta_rapida else "",
            placeholder=t["sec4_placeholder"]
        )
        
        invia_domanda = st.button(t["sec4_btn"])
        
        if invia_domanda and domanda_utente:
            if not api_key_input:
                st.error("⚠️ Inserisci la tua API Key di Google Gemini.")
            elif not HAS_GENAI:
                st.error("⚠️ Libreria `google-genai` mancante.")
            else:
                with st.spinner("Consulting archives..."):
                    client = genai.Client(api_key=api_key_input)
                    scheda_fisica = get_scheda_fisica_prompt()
                    
                    prompt_academy = f"""
                    You are a distinguished Professor of Fashion History, Master Tailor, and Textile Expert.
                    IMPORTANT: Answer ENTIRELY in {t['lang_code']} language.
                    
                    USER QUESTION:
                    "{domanda_utente}"
                    
                    USER TAILORING MEASUREMENTS (Use if relevant):
                    {scheda_fisica}
                    
                    Provide an educational, eloquent, structured, and practical masterclass answer with clear headings.
                    """
                    
                    risposta_academy = None
                    for mod in ['gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-2.5-flash', 'gemini-2.0-flash']:
                        try:
                            response = client.models.generate_content(model=mod, contents=prompt_academy)
                            if response and response.text:
                                risposta_academy = response.text
                                break
                        except Exception: continue
                    
                    if risposta_academy:
                        st.session_state.academy_chat.append({"q": domanda_utente, "a": risposta_academy})
                    else:
                        st.error("⚠️ Service busy. Retry in a few seconds.")

        if st.session_state.academy_chat:
            st.markdown("---")
            for chat in reversed(st.session_state.academy_chat):
                st.markdown(f"#### ❓ {chat['q']}")
                st.markdown(chat['a'])
                st.markdown("---")
        else:
            st.info(t["sec4_empty"])
            
        st.markdown("</div>", unsafe_allow_html=True)
