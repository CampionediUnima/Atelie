import streamlit as st
from PIL import Image
import json
import uuid

# Importazione della libreria ufficiale Google GenAI
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

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
        "sec1_sub": "Analisi tecnica, scheda voti e consulenza sull'acquisto",
        "sec1_step1": "1. Carica Immagine dello Scatto o del Capo",
        "sec1_upload": "Seleziona foto o scatto in negozio",
        "sec1_step2": "2. Parametri di Focus",
        "sec1_type": "Tipo di Scatto / Oggetto dell'analisi",
        "sec1_type_opts": ["Outfit Completo", "Capo Singolo (Giacca, Pantaloni, Abito, ecc.)", "Valutazione Acquisto in Negozio", "Scarpe e Accessori"],
        "sec1_occ": "Occasione d'Uso prevista",
        "sec1_occ_opts": ["Casual / Everyday", "Business / Formale / Lavoro", "Serata / Evento Elegante", "Creativo / Avant-Garde / Runway", "Nessuna in particolare"],
        "sec1_notes": "Descrizione o dubbi specifici (es. 'Vale la pena comprarlo?')",
        "sec1_btn": "⚡ ANALIZZA CON IL MAESTRO",
        "sec1_report": "Report e Scheda Valutazione Sartoriale",
        "sec2_title": "GUARDAROBA DIGITALE ISOLATO",
        "sec2_sub": "Cataloga i tuoi capi personali in totale riservatezza",
        "sec2_tab1": "➕ AGGIUNGI NUOVO CAPO O ACCESSORIO",
        "sec2_tab2": "👔 IL TUO ARMADIO",
        "sec2_tab3": "💾 BACKUP & IMPORTAZIONE",
        "sec2_ai_title": "🤖 Assistente Visivo Sartoriale con IA",
        "sec2_ai_desc": "Carica la foto di un capo: Gemini analizzerà l'immagine e compilerà automaticamente i campi al posto tuo!",
        "sec2_ai_btn": "✨ RICONOSCI DETTAGLI CON IA",
        "sec2_cat_opts": ["Pantaloni", "Giacche / Capispalla", "Camicie / Bluse / Polo", "Maglieria", "Abiti Completi / Vestiti", "Gonne", "Scarpe", "Accessori"],
        "sec2_mat_opts": ["Cotone", "Lana / Cashmere", "Lino", "Seta", "Pelle / Camoscio", "Misto / Tecnico"],
        "sec2_sea_opts": ["Tutte le stagioni", "Autunno / Inverno", "Primavera / Estate"],
        "sec2_save": "💾 SALVA NEL MIO GUARDAROBA",
        "sec2_empty": "👋 Il tuo guardaroba personale è attualmente vuoto.",
        "sec2_remove": "🗑️ Rimuovi Capo",
        "sec3_title": "GENERATORE OUTFIT",
        "sec3_sub": "Crea abbinamenti perfetti attingendo dal tuo armadio personale",
        "sec3_p1": "1. Parametri della Stylist Session",
        "sec3_occ_opts": ["Business / Meeting Formale", "Smart Casual / Ufficio informale", "Aperitivo / Serata Elegante", "Cerimonia / Matrimonio", "Weekend / Casual Tempo Libero", "Viaggio / Dynamic Style"],
        "sec3_meteo_opts": ["Primavera (Mite / Brezza)", "Estate (Caldo Intenso)", "Autunno (Fresco / Variabile)", "Inverno (Freddo / Capispalla Pesanti)", "Giornata di Pioggia"],
        "sec3_style_opts": ["Classico Sartoriale", "Quiet Luxury / Minimal Chic", "Modern Preppy / Ivy League", "Streetwear Elegante / Avant-Garde", "Sprezzatura Italiana"],
        "sec3_btn": "✨ GENERA OUTFIT PERSONALIZZATO",
        "sec3_report": "Proposta Stylist dell'Atelier",
        "sec4_title": "ATELIER ACADEMY",
        "sec4_sub": "Il tuo Mentore Sartoriale e Storico della Moda personale.",
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
        "sec4_empty": "👋 Fai una domanda nel campo sopra o clicca su uno degli spunti rapidi!"
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
        "sec1_sub": "Technical analysis, scorecard, and shopping advice",
        "sec1_step1": "1. Upload Photo or Store Item",
        "sec1_upload": "Select photo",
        "sec1_step2": "2. Focus Parameters",
        "sec1_type": "Photo Type / Subject",
        "sec1_type_opts": ["Full Outfit", "Single Garment", "Store Purchase Evaluation", "Shoes and Accessories"],
        "sec1_occ": "Intended Occasion",
        "sec1_occ_opts": ["Casual / Everyday", "Business / Formal", "Evening / Elegant", "Creative / Avant-Garde", "None"],
        "sec1_notes": "Questions or notes (e.g. 'Is it worth buying?')",
        "sec1_btn": "⚡ ANALYZE WITH MASTER TAILOR",
        "sec1_report": "Tailoring Evaluation Report & Scorecard",
        "sec2_title": "ISOLATED DIGITAL WARDROBE",
        "sec2_sub": "Catalog your items privately",
        "sec2_tab1": "➕ ADD ITEM OR ACCESSORY",
        "sec2_tab2": "👔 YOUR WARDROBE",
        "sec2_tab3": "💾 BACKUP & IMPORT",
        "sec2_ai_title": "🤖 AI Visual Assistant",
        "sec2_ai_desc": "Upload a photo: Gemini will analyze it and auto-fill the form!",
        "sec2_ai_btn": "✨ RECOGNIZE WITH AI",
        "sec2_cat_opts": ["Trousers", "Jackets / Outerwear", "Shirts / Blouses", "Knitwear", "Suits / Dresses", "Skirts", "Shoes", "Accessories"],
        "sec2_mat_opts": ["Cotton", "Wool / Cashmere", "Linen", "Silk", "Leather / Suede", "Blended / Technical"],
        "sec2_sea_opts": ["All Seasons", "Autumn / Winter", "Spring / Summer"],
        "sec2_save": "💾 SAVE TO MY WARDROBE",
        "sec2_empty": "👋 Your personal wardrobe is currently empty.",
        "sec2_remove": "🗑️ Remove Item",
        "sec3_title": "OUTFIT GENERATOR",
        "sec3_sub": "Create flawless combinations from your private wardrobe",
        "sec3_p1": "1. Stylist Session Parameters",
        "sec3_occ_opts": ["Business Meeting", "Smart Casual / Office", "Evening Event", "Ceremony / Wedding", "Weekend Leisure", "Travel Style"],
        "sec3_meteo_opts": ["Spring", "Summer", "Autumn", "Winter", "Rainy Day"],
        "sec3_style_opts": ["Classic Tailored", "Quiet Luxury", "Modern Preppy", "Elegant Streetwear", "Italian Sprezzatura"],
        "sec3_btn": "✨ GENERATE PERSONALIZED OUTFIT",
        "sec3_report": "Atelier Stylist Proposal",
        "sec4_title": "ATELIER ACADEMY",
        "sec4_sub": "Your personal Sartorial Mentor.",
        "sec4_quick_title": "💡 Quick Topics & Prompts",
        "sec4_quick_desc": "Click a topic or type a question:",
        "sec4_quick_qs": ["What is Sprezzatura?", "Super 100s vs 150s wool?", "Shirt collar choice", "Black Tie rules", "Garment care", "Handmade buttonholes"],
        "sec4_chat_title": "💬 Consult the Atelier Mentor",
        "sec4_input_label": "Ask a question:",
        "sec4_btn": "🎓 ASK ACADEMY",
        "sec4_placeholder": "Type your query here...",
        "sec4_empty": "👋 Ask a question or click a prompt above!"
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
        "sec1_sub": "Technische Analyse, Bewertung und Kaufberatung",
        "sec1_step1": "1. Bild hochladen",
        "sec1_upload": "Foto auswählen",
        "sec1_step2": "2. Fokus-Parameter",
        "sec1_type": "Foto-Typ / Analyseobjekt",
        "sec1_type_opts": ["Gesamtes Outfit", "Einzelkleidungsstück", "Kaufbewertung im Geschäft", "Schuhe und Accessoires"],
        "sec1_occ": "Geplanter Anlass",
        "sec1_occ_opts": ["Freizeit / Alltag", "Business / Formell", "Abendveranstaltung / Elegant", "Kreativ / Avantgarde", "Kein spezieller Anlass"],
        "sec1_notes": "Spezifische Fragen (z.B. 'Lohnt sich der Kauf?')",
        "sec1_btn": "⚡ MIT DEM SCHNEIDERMEISTER ANALYSIEREN",
        "sec1_report": "Schneider-Bewertungsbericht",
        "sec2_title": "ISOLIERTE DIGITALE GARDEROBE",
        "sec2_sub": "Katalogisieren Sie Ihre Kleidung vertraulich",
        "sec2_tab1": "➕ NEUES TEIL HINZUFÜGEN",
        "sec2_tab2": "👔 IHR KLEIDERSCHRANK",
        "sec2_tab3": "💾 BACKUP & IMPORT",
        "sec2_ai_title": "🤖 KI-Visueller Assistent",
        "sec2_ai_desc": "Foto hochladen: Die KI erkennt automatisch alle Details!",
        "sec2_ai_btn": "✨ DETAILS MIT KI ERKENNEN",
        "sec2_cat_opts": ["Hosen", "Jacken / Mäntel", "Hemden / Blusen", "Strickbekleidung", "Anzüge / Kleider", "Röcke", "Schuhe", "Accessoires"],
        "sec2_mat_opts": ["Baumwolle", "Wolle / Kaschmir", "Leinen", "Seide", "Leder / Wildleder", "Mischgewebe"],
        "sec2_sea_opts": ["Alle Jahreszeiten", "Herbst / Winter", "Frühling / Sommer"],
        "sec2_save": "💾 IN MEINER GARDEROBE SPEICHERN",
        "sec2_empty": "👋 Ihre persönliche Garderobe ist leer.",
        "sec2_remove": "🗑️ Artikel entfernen",
        "sec3_title": "OUTFIT-GENERATOR",
        "sec3_sub": "Erstellen Sie perfekte Kombinationen aus Ihrem privaten Schrank",
        "sec3_p1": "1. Stylist-Sitzungsparameter",
        "sec3_occ_opts": ["Business Meeting", "Smart Casual", "Aperitif / Abend", "Zeremonie", "Wochenende", "Reise Stil"],
        "sec3_meteo_opts": ["Frühling", "Sommer", "Herbst", "Winter", "Regentag"],
        "sec3_style_opts": ["Klassisch Schneiderei", "Quiet Luxury", "Modern Preppy", "Eleganter Streetwear", "Italienische Sprezzatura"],
        "sec3_btn": "✨ PERSONALISIERTES OUTFIT GENERIEREN",
        "sec3_report": "Atelier-Stylist-Vorschlag",
        "sec4_title": "ATELIER ACADEMY",
        "sec4_sub": "Ihr persönlicher Schneider-Mentor.",
        "sec4_quick_title": "💡 Schnelle Themen & Fragen",
        "sec4_quick_desc": "Klicken Sie auf ein Thema:",
        "sec4_quick_qs": ["Was ist Sprezzatura?", "Super 100s vs 150s Wolle?", "Hemdkragen nach Gesichtsform", "Black Tie Regeln", "Kleidungspflege", "Echte Knopflöcher"],
        "sec4_chat_title": "💬 Fragen Sie den Atelier-Mentor",
        "sec4_input_label": "Stellen Sie eine Frage:",
        "sec4_btn": "🎓 ACADEMY FRAGEN",
        "sec4_placeholder": "Geben Sie Ihre Frage ein...",
        "sec4_empty": "👋 Stellen Sie eine Frage oben!"
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
        "sec1_sub": "Analizë teknike, skedë vlerësimi dhe konsulencë për blerjen",
        "sec1_step1": "1. Ngarko Imazhin",
        "sec1_upload": "Zgjidh foton ose foton në dyqan",
        "sec1_step2": "2. Parametrat e Fokusit",
        "sec1_type": "Lloji i Fotos / Objekti i Analizës",
        "sec1_type_opts": ["Outfit i Plotë", "Veshje Teke", "Vlerësim i Blerjes në Dyqan", "Këpucë dhe Aksesorë"],
        "sec1_occ": "Rasti i Përdorimit",
        "sec1_occ_opts": ["Kauzale / Përditshmëri", "Biznes / Formale", "Mbrëmje / Elegante", "Krijuar / Avantgardë", "Asnjë e veçantë"],
        "sec1_notes": "Pyetje ose shënime (psh. 'A ia vlen ta blej?')",
        "sec1_btn": "⚡ ANALIZO ME MESTRIN RROBAQEPËS",
        "sec1_report": "Raporti dhe Skeda e Vlerësimit",
        "sec2_title": "GARDEROBA DIGJITALE E IZOLUAR",
        "sec2_sub": "Katalogoni veshjet tuaja në privatësi të plotë",
        "sec2_tab1": "➕ SHTO VESHJE OSE AKSESOR TË RI",
        "sec2_tab2": "👔 DOLLAPI YTI",
        "sec2_tab3": "💾 BACKUP & IMPORT",
        "sec2_ai_title": "🤖 Ndihmësi Vizual me IA",
        "sec2_ai_desc": "Ngarko foton: Gemini do të analizojë dhe plotësojë fushat automatikisht!",
        "sec2_ai_btn": "✨ NJOH DETAJET ME AI",
        "sec2_cat_opts": ["Pantallona", "Xhaketa / Pallto", "Këmisha / Bluza", "Triko", "Kostume / Fustane", "Fuste", "Këpucë", "Aksesore"],
        "sec2_mat_opts": ["Pambuk", "Lesh / Kashmir", "In", "Mëndafsh", "Lëkurë / Kamosh", "Miks / Teknike"],
        "sec2_sea_opts": ["Të gjitha stinët", "Vjeshtë / Dimër", "Pranverë / Verë"],
        "sec2_save": "💾 RUAJ NË GARDEROBËN TIME",
        "sec2_empty": "👋 Garderoba juaj personale është bosh.",
        "sec2_remove": "🗑️ Fshij Veshjen",
        "sec3_title": "GJENERUESI I OUTFIT-EVE",
        "sec3_sub": "Krijoni kombinime perfekte nga dollapi juaj privat",
        "sec3_p1": "1. Parametrat e Sesionit të Stilit",
        "sec3_occ_opts": ["Biznes / Takim Formal", "Smart Casual", "Aperitiv / Mbrëmje", "Cermoni / Martesë", "Fundjavë", "Udhëtim / Stil Dinamik"],
        "sec3_meteo_opts": ["Pranverë", "Verë", "Vjeshtë", "Dimër", "Ditë me Shi"],
        "sec3_style_opts": ["Klasike Rrobaqepësie", "Quiet Luxury", "Modern Preppy", "Streetwear Elegant", "Sprezzatura Italiane"],
        "sec3_btn": "✨ GJENERO OUTFIT TË PERSONALIZUAR",
        "sec3_report": "Propozimi i Stilistit të Atelierit",
        "sec4_title": "AKADEMIA E ATELIERIT",
        "sec4_sub": "Mentori juaj personal i Stilit.",
        "sec4_quick_title": "💡 Tema dhe Pyetje të Shpejta",
        "sec4_quick_desc": "Klikoni mbi një temë:",
        "sec4_quick_qs": ["Çfarë është Sprezzatura?", "Dallimi leshit Super 100s vs 150s?", "Jakë këmishe sipas fytyrës", "Rregullat Black Tie", "Kujdesi për veshjet", "Vrima kopshe me dorë"],
        "sec4_chat_title": "💬 Konsultohuni me Mentorin",
        "sec4_input_label": "Bëj një pyetje:",
        "sec4_btn": "🎓 PYET AKADEMINË",
        "sec4_placeholder": "Shkruani pyetjen tuaj këtu...",
        "sec4_empty": "👋 Bëni një pyetje më sipër!"
    }
}

# Configurazione pagina Streamlit
st.set_page_config(
    page_title="ATELIER | Analisi Moda & Sartoria",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sfondo bianco ed estetica pulita
st.markdown("""
    <style>
    .stApp { background-color: #ffffff !important; color: #111111 !important; }
    section[data-testid="stSidebar"] { background-color: #f7f7f9 !important; border-right: 1px solid #e2e8f0; }
    h1, h2, h3, h4, h5, h6, p, label, span, div { color: #111111 !important; }
    .atelier-card { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 22px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
    </style>
""", unsafe_allow_html=True)

# Inizializzazione Session State
if "lingua" not in st.session_state:
    st.session_state.lingua = "Italiano"

# GENERAZIONE AUTOMATICA DI UN ID UNIVOCO E INVISIBILE PER OGNI DISPOSITIVO/BROWSER
if "device_uuid" not in st.session_state:
    st.session_state.device_uuid = str(uuid.uuid4())

UID = st.session_state.device_uuid

DEFAULT_PROFILO = {
    "sesso": "Uomo", "altezza": 178, "peso": 75, "corporatura": "Atletica / Regolare",
    "torace": 102, "vita": 84, "fianchi": 98, "spalle": 46, "manica": 64, "cavallo": 81, "collo": 40, "postura": "Eretta / Standard"
}

# SELETTORE LINGUA IN ALTO
col_spazio, col_lang = st.columns([4, 2])
with col_lang:
    opzioni_lingue = ["Italiano", "English", "Deutsch", "Albanese"]
    idx_lingua = opzioni_lingue.index(st.session_state.lingua) if st.session_state.lingua in opzioni_lingue else 0
    scelta_lingua = st.selectbox("🌐 Lingua / Language", opzioni_lingue, index=idx_lingua, label_visibility="collapsed")
    st.session_state.lingua = scelta_lingua

t = I18N[st.session_state.lingua]

# ==========================================
# 🔐 ISOLAMENTO CRITTOGRAFICO AUTOMATICO
# ==========================================
st.sidebar.title("ATELIER")
st.sidebar.markdown("---")
st.sidebar.subheader("👤 Il Tuo Profilo Privato")
nome_utente = st.sidebar.text_input("Il tuo Nome", value="Ospite", help="Inserisci il tuo nome per personalizzare l'esperienza.")

key_guardaroba = f"guardaroba_{UID}"
key_profilo = f"profilo_{UID}"
key_chat = f"academy_chat_{UID}"
key_ai_draft = f"ai_draft_{UID}"

if key_guardaroba not in st.session_state:
    st.session_state[key_guardaroba] = []

if key_profilo not in st.session_state:
    st.session_state[key_profilo] = DEFAULT_PROFILO.copy()

if key_chat not in st.session_state:
    st.session_state[key_chat] = []

if key_ai_draft not in st.session_state:
    st.session_state[key_ai_draft] = {
        "nome": "", "categoria": t["sec2_cat_opts"][0], "marca": "", 
        "colore": "", "materiale": t["sec2_mat_opts"][0], "stagione": t["sec2_sea_opts"][0], "immagine": None
    }

# MENU PRINCIPALE
sezione_idx = st.sidebar.radio("MENU", range(len(t["menu"])), format_func=lambda x: t["menu"][x])

st.sidebar.markdown("---")
st.sidebar.subheader(t["config_title"])
api_key_input = st.sidebar.text_input("Gemini API Key", type="password", help="Inserisci la tua API Key Gemini personale.")

st.sidebar.markdown("---")
st.sidebar.subheader(t["misure_title"])

with st.sidebar.expander(t["modifica_misure"], expanded=False):
    p_corrente = st.session_state[key_profilo]
    sesso_idx = 0 if p_corrente.get("sesso", "Uomo") in ["Uomo", "Man", "Mann", "Mashkull"] else 1
    p_corrente["sesso"] = st.selectbox(t["sesso"], t["sesso_opts"], index=sesso_idx)
    p_corrente["altezza"] = st.number_input(t["altezza"], value=p_corrente["altezza"], step=1)
    p_corrente["peso"] = st.number_input(t["peso"], value=p_corrente["peso"], step=1)
    p_corrente["corporatura"] = st.selectbox(t["corporatura"], t["corp_opts"])
    p_corrente["postura"] = st.selectbox(t["postura"], t["post_opts"])
    
    st.markdown(f"**{t['misure_cm']}**")
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        p_corrente["torace"] = st.number_input(t["torace"], value=p_corrente["torace"], step=1)
        p_corrente["vita"] = st.number_input(t["vita"], value=p_corrente["vita"], step=1)
        p_corrente["fianchi"] = st.number_input(t["fianchi"], value=p_corrente["fianchi"], step=1)
    with c_s2:
        p_corrente["spalle"] = st.number_input(t["spalle"], value=p_corrente["spalle"], step=1)
        p_corrente["manica"] = st.number_input(t["manica"], value=p_corrente["manica"], step=1)
        p_corrente["cavallo"] = st.number_input(t["cavallo"], value=p_corrente["cavallo"], step=1)
    p_corrente["collo"] = st.number_input(t["collo"], value=p_corrente["collo"], step=1)

def get_scheda_fisica_prompt():
    p = st.session_state[key_profilo]
    return f"Gender: {p['sesso']}, Height: {p['altezza']}cm, Weight: {p['peso']}kg, Build: {p['corporatura']}, Measurements: Chest {p['torace']}cm, Waist {p['vita']}cm, Hips {p['fianchi']}cm, Shoulders {p['spalle']}cm, Sleeve {p['manica']}cm, Inseam {p['cavallo']}cm."

# ==========================================
# 1. DIAGNOSTICA FIT
# ==========================================
if sezione_idx == 0:
    st.title(t["sec1_title"])
    st.markdown(f"<p style='color: #666; font-size: 0.85rem;'>{t['sec1_sub']} (Benvenuto, <b>{nome_utente}</b>)</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(t["sec1_upload"], type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Foto Acquisita", use_container_width=True)
            tipo_scatto = st.selectbox(t["sec1_type"], t["sec1_type_opts"])
            occasione = st.selectbox(t["sec1_occ"], t["sec1_occ_opts"])
            dettagli_extra = st.text_area(t["sec1_notes"], height=90)
            analizza_btn = st.button(t["sec1_btn"])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='atelier-card' style='min-height: 400px;'>", unsafe_allow_html=True)
        st.subheader(t["sec1_report"])
        if uploaded_file is not None and 'analizza_btn' in locals() and analizza_btn:
            if not api_key_input:
                st.error("⚠️ Inserisci la tua Gemini API Key nella barra laterale.")
            else:
                with st.spinner("Analisi in corso con il Maestro..."):
                    client = genai.Client(api_key=api_key_input)
                    prompt_atelier = f"""
                    Sei un Maestro Sartoriale. Rispondi interamente in lingua {t['lang_code']}.
                    Profilo Utente ({nome_utente}): {get_scheda_fisica_prompt()}
                    Focus: {tipo_scatto}, Occasione: {occasione}, Note Utente: "{dettagli_extra}"
                    Se il focus è 'Valutazione Acquisto in Negozio', fornisci un verdetto chiaro se COMPRARE o NO in base alle misure del cliente e ai difetti visibili del capo.
                    """
                    for mod in ['gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-2.5-flash']:
                        try:
                            res = client.models.generate_content(model=mod, contents=[image, prompt_atelier])
                            if res and res.text:
                                st.markdown(res.text)
                                break
                        except Exception: continue
        else:
            st.write("👋 Carica una foto a sinistra per iniziare l'analisi.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 2. GUARDAROBA DIGITALE CON IA E ISOLAMENTO
# ==========================================
elif sezione_idx == 1:
    st.title(t["sec2_title"])
    st.markdown(f"<p style='color: #666;'>Guardaroba privato di: <b>{nome_utente}</b></p>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs([t["sec2_tab1"], t["sec2_tab2"], t["sec2_tab3"]])
    
    with tab1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader(t["sec2_ai_title"])
        st.caption(t["sec2_ai_desc"])
        
        capo_image = st.file_uploader("Fotografa o carica il capo", type=["jpg", "jpeg", "png"], key=f"ai_img_{UID}")
        if capo_image is not None:
            pil_img_preview = Image.open(capo_image)
            st.image(pil_img_preview, width=250, caption="Capo da catalogare")
            if st.button(t["sec2_ai_btn"], key=f"btn_ai_rec_{UID}"):
                if not api_key_input:
                    st.error("⚠️ Inserisci la tua API Key di Gemini nella barra laterale.")
                else:
                    with st.spinner("Analisi visiva e riconoscimento dettagli in corso..."):
                        client = genai.Client(api_key=api_key_input)
                        prompt_vision = f"""
                        Analizza questa foto di un capo d'abbigliamento o accessorio.
                        Restituisci ESATTAMENTE un oggetto JSON valido (senza blocchi di codice markdown attorno se possibile, o puro testo JSON) con queste chiavi:
                        - "nome": una breve descrizione commerciale (es. "Blazer monopetto blu")
                        - "categoria": deve essere una tra: {t["sec2_cat_opts"]}
                        - "marca": marca visibile o stringa vuota ""
                        - "colore": colore principale
                        - "materiale": uno tra {t["sec2_mat_opts"]}
                        - "stagione": uno tra {t["sec2_sea_opts"]}
                        """
                        for mod in ['gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-2.5-flash']:
                            try:
                                resp = client.models.generate_content(model=mod, contents=[pil_img_preview, prompt_vision])
                                txt = resp.text.strip()
                                if txt.startswith("```json"):
                                    txt = txt[7:-3].strip()
                                elif txt.startswith("```"):
                                    txt = txt[3:-3].strip()
                                data_parsed = json.loads(txt)
                                st.session_state[key_ai_draft].update(data_parsed)
                                st.success("✅ Dettagli riconosciuti con successo dall'IA! Controlla il modulo sotto.")
                                break
                            except Exception:
                                continue
        st.markdown("</div>", unsafe_allow_html=True)

        # Modulo di salvataggio precompilato o manuale
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        draft = st.session_state[key_ai_draft]
        
        with st.form(f"form_guardaroba_{UID}"):
            c1, c2 = st.columns(2)
            with c1:
                nome_capo = st.text_input("Titolo Capo*", value=draft.get("nome", ""))
                
                cat_list = t["sec2_cat_opts"]
                cat_val = draft.get("categoria", cat_list[0])
                cat_idx = cat_list.index(cat_val) if cat_val in cat_list else 0
                categoria = st.selectbox("Categoria*", cat_list, index=cat_idx)
                
                colore = st.text_input("Colore Principale*", value=draft.get("colore", ""))
            with c2:
                marca = st.text_input("Marca", value=draft.get("marca", ""))
                
                mat_list = t["sec2_mat_opts"]
                mat_val = draft.get("materiale", mat_list[0])
                mat_idx = mat_list.index(mat_val) if mat_val in mat_list else 0
                materiale = st.selectbox("Tessuto", mat_list, index=mat_idx)
                
                sea_list = t["sec2_sea_opts"]
                sea_val = draft.get("stagione", sea_list[0])
                sea_idx = sea_list.index(sea_val) if sea_val in sea_list else 0
                stagione = st.selectbox("Stagione", sea_list, index=sea_idx)
                
            salva_btn = st.form_submit_button(t["sec2_save"])
            
            if salva_btn and nome_capo and colore:
                # Se è stata caricata una foto nell'uploader sopra, la salviamo come oggetto Immagine o Bytes, altrimenti usiamo placeholder
                img_data_to_save = capo_image if capo_image is not None else "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?q=80&w=500&auto=format&fit=crop"
                nuovo_capo = {
                    "id": len(st.session_state[key_guardaroba]) + 1,
                    "nome": nome_capo, "categoria": categoria, "marca": marca,
                    "colore": colore, "materiale": materiale, "stagione": stagione, "immagine": img_data_to_save
                }
                st.session_state[key_guardaroba].append(nuovo_capo)
                st.success("✅ Salvato nel tuo guardaroba privato!")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        if not st.session_state[key_guardaroba]:
            st.info(t["sec2_empty"])
        else:
            cols = st.columns(3)
            for idx, capo in enumerate(st.session_state[key_guardaroba]):
                with cols[idx % 3]:
                    st.markdown("<div class='atelier-card' style='height: 100%;'>", unsafe_allow_html=True)
                    
                    # Mostra foto reale caricata o link di fallback
                    if capo["immagine"]:
                        st.image(capo["immagine"], use_container_width=True)
                    else:
                        st.image("https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?q=80&w=500&auto=format&fit=crop", use_container_width=True)
                    
                    st.markdown(f"### {capo['nome']}")
                    st.markdown(f"🏷️ **Categoria:** {capo['categoria']}")
                    if capo.get('marca'):
                        st.markdown(f"🔖 **Marca:** {capo['marca']}")
                    st.markdown(f"🎨 **Colore:** {capo['colore']}")
                    st.markdown(f"🧵 **Tessuto:** {capo['materiale']}")
                    st.markdown(f"🌤️ **Stagione:** {capo['stagione']}")
                    
                    st.markdown("---")
                    if st.button(t["sec2_remove"], key=f"del_{UID}_{capo['id']}"):
                        st.session_state[key_guardaroba] = [c for c in st.session_state[key_guardaroba] if c["id"] != capo["id"]]
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader("📥 Esporta o 📤 Importa il tuo Armadio")
        st.caption("Scarica il file JSON del tuo armadio sul telefono per averlo sempre con te.")
        
        # Per consentire il dump JSON senza errori dovuti agli oggetti binari delle immagini caricate, salviamo le info testuali
        export_data = [{k: v for k, v in c.items() if k != 'immagine'} for c in st.session_state[key_guardaroba]]
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
        st.download_button("📥 Scarica il mio Guardaroba (.json)", data=json_str, file_name=f"guardaroba_{nome_utente}.json", mime="application/json")
        
        st.markdown("---")
        uploaded_json = st.file_uploader("📤 Ricarica il tuo Guardaroba salvato", type=["json"], key=f"up_{UID}")
        if uploaded_json is not None:
            try:
                dados = json.load(uploaded_json)
                st.session_state[key_guardaroba] = dados
                st.success("✅ Guardaroba privato ripristinato con successo!")
            except Exception as e:
                st.error(f"Errore nel file caricato: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 3. GENERATORE OUTFIT
# ==========================================
elif sezione_idx == 2:
    st.title(t["sec3_title"])
    st.markdown(f"<p style='color: #666;'>Stylist session per: <b>{nome_utente}</b></p>", unsafe_allow_html=True)
    
    col_out_left, col_out_right = st.columns([1, 1], gap="large")
    
    with col_out_left:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader(t["sec3_p1"])
        
        occasione_outfit = st.selectbox("Occasione", t["sec3_occ_opts"])
        meteo_outfit = st.selectbox("Stagione & Meteo", t["sec3_meteo_opts"])
        stile_outfit = st.selectbox("Stile Desiderato", t["sec3_style_opts"])
        note_outfit = st.text_area("Richieste specifiche / capi da includere", height=90)
        
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
                with st.spinner("Creazione outfit in corso..."):
                    client = genai.Client(api_key=api_key_input)
                    scheda_fisica = get_scheda_fisica_prompt()
                    
                    armadio_utente = st.session_state[key_guardaroba]
                    armadio_str = "\n".join([
                        f"- [ID {c['id']}] {c['nome']} | Cat: {c['categoria']} | Colore: {c['colore']} | Tessuto: {c['materiale']}"
                        for c in armadio_utente
                    ]) if armadio_utente else "Il tuo armadio personale è vuoto. Proponi un outfit ideale completo da acquistare."

                    prompt_generatore = f"""
                    Sei uno Stylist e Maestro Sartoriale d'élite.
                    RISPONDI INTERAMENTE IN LINGUA: {t['lang_code']}.
                    
                    UTENTE: {nome_utente}
                    PARAMETRI FISICI: {scheda_fisica}
                    
                    PARAMETRI DELLA SESSIONE:
                    - Occasione: {occasione_outfit}
                    - Meteo: {meteo_outfit}
                    - Stile: {stile_outfit}
                    - Note: "{note_outfit.strip() if note_outfit else 'Nessuna'}"
                    
                    GUARDAROBA PERSONALE DI {nome_utente}:
                    {armadio_str}
                    
                    Struttura la risposta in Markdown chiaro:
                    1. 🧥 Outfit Selezionato dal tuo Armadio
                    2. 👓 Accessori Consigliati
                    3. 🎨 Armonia Cromatica e Fit per la tua Struttura Fisica
                    4. 💡 Tocco del Maestro (Sprezzatura)
                    """

                    risposta_ottenuta = None
                    for mod in ['gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-2.5-flash']:
                        try:
                            response = client.models.generate_content(model=mod, contents=prompt_generatore)
                            if response and response.text:
                                risposta_ottenuta = response.text
                                break 
                        except Exception: continue 
                    
                    if risposta_ottenuta:
                        st.markdown(risposta_ottenuta)
                    else:
                        st.warning("⚠️ Servizio temporaneamente non disponibile.")
        else:
            st.write("👋 Imposta i parametri a sinistra e clicca sul pulsante per generare il tuo outfit.")
            
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 4. ACADEMY
# ==========================================
elif sezione_idx == 3:
    st.title(t["sec4_title"])
    st.markdown(f"<p style='color: #666;'>Sessione Academy di: <b>{nome_utente}</b></p>", unsafe_allow_html=True)
    
    col_ac1, col_ac2 = st.columns([1, 2], gap="large")
    
    with col_ac1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader(t["sec4_quick_title"])
        st.caption(t["sec4_quick_desc"])
        
        scelta_rapida = None
        for q in t["sec4_quick_qs"]:
            if st.button(f"📌 {q}", use_container_width=True, key=f"btn_{UID}_{q[:10]}"):
                scelta_rapida = q
                
        st.markdown("</div>", unsafe_allow_html=True)

    with col_ac2:
        st.markdown("<div class='atelier-card' style='min-height: 500px;'>", unsafe_allow_html=True)
        st.subheader(t["sec4_chat_title"])
        
        domanda_utente = st.text_input(
            t["sec4_input_label"],
            value=scelta_rapida if scelta_rapida else "",
            placeholder=t["sec4_placeholder"],
            key=f"input_chat_{UID}"
        )
        
        invia_domanda = st.button(t["sec4_btn"], key=f"send_chat_{UID}")
        
        if invia_domanda and domanda_utente:
            if not api_key_input:
                st.error("⚠️ Inserisci la tua API Key di Google Gemini nella barra laterale.")
            elif not HAS_GENAI:
                st.error("⚠️ Libreria `google-genai` mancante.")
            else:
                with st.spinner("Consultazione archivi sartoriali in corso..."):
                    client = genai.Client(api_key=api_key_input)
                    scheda_fisica = get_scheda_fisica_prompt()
                    
                    prompt_academy = f"""
                    Sei un Professore di Storia della Moda, Maestro Sartoriale ed Esperto Tessile.
                    RISPONDI INTERAMENTE IN LINGUA: {t['lang_code']}.
                    
                    UTENTE: {nome_utente}
                    DOMANDA: "{domanda_utente}"
                    MISURE SARTORIALI UTENTE: {scheda_fisica}
                    
                    Fornisci una risposta formativa, eloquente, ben strutturata in sezioni con titoli chiari.
                    """
                    
                    risposta_academy = None
                    for mod in ['gemini-3.8-flash', 'gemini-3.5-flash', 'gemini-2.5-flash']:
                        try:
                            response = client.models.generate_content(model=mod, contents=prompt_academy)
                            if response and response.text:
                                risposta_academy = response.text
                                break
                        except Exception: continue
                    
                    if risposta_academy:
                        st.session_state[key_chat].append({"q": domanda_utente, "a": risposta_academy})
                    else:
                        st.error("⚠ Servizio momentaneamente occupato. Riprova tra qualche secondo.")

        chat_storico = st.session_state[key_chat]
        if chat_storico:
            st.markdown("---")
            for chat in reversed(chat_storico):
                st.markdown(f"#### ❓ {chat['q']}")
                st.markdown(chat['a'])
                st.markdown("---")
        else:
            st.info(t["sec4_empty"])
            
        st.markdown("</div>", unsafe_allow_html=True)
