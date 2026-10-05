import streamlit as st
from PIL import Image
import os
import json

# Importazione della libreria ufficiale Google GenAI
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# Importazione per la ricerca immagini sul web
try:
    from duckduckgo_search import DDGS
    HAS_DDG = True
except ImportError:
    HAS_DDG = False

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
        "sec2_title": "GUARDAROBA DIGITALE INDIPENDENTE",
        "sec2_sub": "Cataloga i tuoi capi personali in totale riservatezza",
        "sec2_tab1": "➕ AGGIUNGI NUOVO CAPO O ACCESSORIO",
        "sec2_tab2": "👔 IL TUO ARMADIO",
        "sec2_tab3": "💾 BACKUP & IMPORTAZIONE",
        "sec2_mode": "Seleziona modalità di inserimento:",
        "sec2_modes": ["📸 Carica Foto dal Dispositivo (Riconoscimento IA)", "🔍 Ricerca Automatica sul Web (Marca + Modello)", "🔗 Inserisci Link URL Immagine"],
        "sec2_ai_title": "🤖 Assistente Visivo Sartoriale",
        "sec2_ai_desc": "Fai analizzare la foto a Gemini per identificare automaticamente tipo di vestito, accessorio, tessuto, colore e dettagli!",
        "sec2_ai_btn": "✨ RICONOSCI DETTAGLI CON IA",
        "sec2_cat_opts": ["Pantaloni", "Giacche / Capispalla", "Camicie / Bluse / Polo", "Maglieria", "Abiti Completi / Vestiti", "Gonne", "Scarpe", "Accessori"],
        "sec2_mat_opts": ["Cotone", "Lana / Cashmere", "Lino", "Seta", "Pelle / Camoscio", "Misto / Tecnico"],
        "sec2_sea_opts": ["Tutte le stagioni", "Autunno / Inverno", "Primavera / Estate"],
        "sec2_save": "💾 SALVA NEL GUARDAROBA",
        "sec2_empty": "👋 Il tuo guardaroba è attualmente vuoto per questa sessione.",
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
        "sec2_title": "INDEPENDENT DIGITAL WARDROBE",
        "sec2_sub": "Catalog your items privately",
        "sec2_tab1": "➕ ADD ITEM OR ACCESSORY",
        "sec2_tab2": "👔 YOUR WARDROBE",
        "sec2_tab3": "💾 BACKUP & IMPORT",
        "sec2_mode": "Select entry method:",
        "sec2_modes": ["📸 Upload Photo (AI Recognition)", "🔍 Web Search", "🔗 Image URL Link"],
        "sec2_ai_title": "🤖 Visual Assistant",
        "sec2_ai_desc": "Have Gemini analyze the photo to detect details!",
        "sec2_ai_btn": "✨ RECOGNIZE WITH AI",
        "sec2_cat_opts": ["Trousers", "Jackets / Outerwear", "Shirts / Blouses", "Knitwear", "Suits / Dresses", "Skirts", "Shoes", "Accessories"],
        "sec2_mat_opts": ["Cotton", "Wool / Cashmere", "Linen", "Silk", "Leather / Suede", "Blended / Technical"],
        "sec2_sea_opts": ["All Seasons", "Autumn / Winter", "Spring / Summer"],
        "sec2_save": "💾 SAVE TO WARDROBE",
        "sec2_empty": "👋 Your wardrobe is empty for this session.",
        "sec2_filter": "Filter by Category:",
        "sec2_all": "All",
        "sec2_remove": "🗑️ Remove",
        "sec3_title": "OUTFIT GENERATOR",
        "sec3_sub": "Create flawless combinations",
        "sec3_p1": "1. Stylist Session Parameters",
        "sec3_occ_opts": ["Business Meeting", "Smart Casual / Office", "Evening Event", "Ceremony / Wedding", "Weekend Leisure", "Travel Style"],
        "sec3_meteo_opts": ["Spring", "Summer", "Autumn", "Winter", "Rainy Day"],
        "sec3_style_opts": ["Classic Tailored", "Quiet Luxury", "Modern Preppy", "Elegant Streetwear", "Italian Sprezzatura"],
        "sec3_btn": "✨ GENERATE OUTFIT WITH AI",
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

DEFAULT_PROFILO = {
    "sesso": "Uomo", "altezza": 178, "peso": 75, "corporatura": "Atletica / Regolare",
    "torace": 102, "vita": 84, "fianchi": 98, "spalle": 46, "manica": 64, "cavallo": 81, "collo": 40, "postura": "Eretta / Standard"
}

if "profilo" not in st.session_state:
    st.session_state.profilo = DEFAULT_PROFILO.copy()

if "guardaroba" not in st.session_state:
    st.session_state.guardaroba = []

if "academy_chat" not in st.session_state:
    st.session_state.academy_chat = []

if "auto_data" not in st.session_state:
    st.session_state.auto_data = {
        "nome": "", "categoria": "Pantaloni", "marca": "", "modello": "",
        "taglia": "", "colore": "", "materiale": "Cotone", "stagione": "Tutte le stagioni", "note": ""
    }

# Selettore lingua
col_spazio, col_lang = st.columns([4, 2])
with col_lang:
    scelta_lingua = st.selectbox("🌐 Lingua / Language", ["Italiano", "English"], index=0 if st.session_state.lingua == "Italiano" else 1, label_visibility="collapsed")
    st.session_state.lingua = scelta_lingua

t = I18N[st.session_state.lingua]

# Sidebar
st.sidebar.title("ATELIER")
sezione_idx = st.sidebar.radio("MENU", range(len(t["menu"])), format_func=lambda x: t["menu"][x])

st.sidebar.markdown("---")
st.sidebar.subheader(t["config_title"])
api_key_input = st.sidebar.text_input("Gemini API Key", type="password", help="Inserisci la tua API Key Gemini personale.")

st.sidebar.markdown("---")
st.sidebar.subheader(t["misure_title"])

with st.sidebar.expander(t["modifica_misure"], expanded=False):
    st.session_state.profilo["sesso"] = st.selectbox(t["sesso"], t["sesso_opts"])
    st.session_state.profilo["altezza"] = st.number_input(t["altezza"], value=st.session_state.profilo["altezza"], step=1)
    st.session_state.profilo["peso"] = st.number_input(t["peso"], value=st.session_state.profilo["peso"], step=1)
    st.session_state.profilo["corporatura"] = st.selectbox(t["corporatura"], t["corp_opts"])
    st.session_state.profilo["postura"] = st.selectbox(t["postura"], t["post_opts"])
    
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
    return f"Gender: {p['sesso']}, Height: {p['altezza']}cm, Weight: {p['peso']}kg, Build: {p['corporatura']}, Measurements: Chest {p['torace']}cm, Waist {p['vita']}cm, Hips {p['fianchi']}cm, Shoulders {p['spalle']}cm, Sleeve {p['manica']}cm, Inseam {p['cavallo']}cm."

# 1. DIAGNOSTICA FIT (PERFETTO PER I NEGOZI)
if sezione_idx == 0:
    st.title(t["sec1_title"])
    st.markdown(f"<p style='color: #666; font-size: 0.85rem;'>{t['sec1_sub']}</p>", unsafe_allow_html=True)
    
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
                    Sei un Maestro Sartoriale. Rispondi in lingua {t['lang_code']}.
                    Profilo Utente: {get_scheda_fisica_prompt()}
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
        st.markdown("</div>", unsafe_allow_html=True)

# 2. GUARDAROBA DIGITALE CON BACKUP & IMPORT
elif sezione_idx == 1:
    st.title(t["sec2_title"])
    tab1, tab2, tab3 = st.tabs([t["sec2_tab1"], t["sec2_tab2"], t["sec2_tab3"]])
    
    with tab1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        modalita_foto = st.radio(t["sec2_mode"], t["sec2_modes"], horizontal=True)
        uploaded_img = st.file_uploader(t["sec1_upload"], type=["jpg", "jpeg", "png"]) if "📸" in modalita_foto else None
        
        with st.form("form_guardaroba"):
            c1, c2 = st.columns(2)
            with c1:
                nome_capo = st.text_input("Titolo Capo*", value=st.session_state.auto_data["nome"])
                categoria = st.selectbox("Categoria*", t["sec2_cat_opts"])
                colore = st.text_input("Colore Principale*", value=st.session_state.auto_data["colore"])
            with c2:
                marca = st.text_input("Marca", value=st.session_state.auto_data["marca"])
                materiale = st.selectbox("Tessuto", t["sec2_mat_opts"])
                stagione = st.selectbox("Stagione", t["sec2_sea_opts"])
            salva_btn = st.form_submit_button(t["sec2_save"])
            
            if salva_btn and nome_capo and colore:
                img_url = "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?q=80&w=500&auto=format&fit=crop"
                nuovo_capo = {"id": len(st.session_state.guardaroba)+1, "nome": nome_capo, "categoria": categoria, "marca": marca, "colore": colore, "materiale": materiale, "stagione": stagione, "immagine": img_url}
                st.session_state.guardaroba.append(nuovo_capo)
                st.success("✅ Salvato nella sessione!")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        if not st.session_state.guardaroba:
            st.info(t["sec2_empty"])
        else:
            cols = st.columns(3)
            for idx, capo in enumerate(st.session_state.guardaroba):
                with cols[idx % 3]:
                    st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
                    st.image(capo["immagine"], use_container_width=True)
                    st.markdown(f"### {capo['nome']}")
                    st.markdown(f"**{capo['categoria']}** | {capo['colore']}")
                    if st.button("🗑️ Rimuovi", key=f"del_{capo['id']}"):
                        st.session_state.guardaroba = [c for c in st.session_state.guardaroba if c["id"] != capo["id"]]
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader("📥 Esporta o 📤 Importa il tuo Armadio")
        st.caption("Scarica il file del tuo armadio sul telefono per averlo sempre salvato, oppure ricaricalo se riapri l'app.")
        
        # Download file JSON
        json_str = json.dumps(st.session_state.guardaroba, ensure_ascii=False, indent=2)
        st.download_button("📥 Scarica il mio Guardaroba (.json)", data=json_str, file_name="mio_guardaroba.json", mime="application/json")
        
        st.markdown("---")
        # Upload file JSON
        uploaded_json = st.file_uploader("📤 Ricarica il tuo Guardaroba salvato", type=["json"])
        if uploaded_json is not None:
            try:
                dados = json.load(uploaded_json)
                st.session_state.guardaroba = dados
                st.success("✅ Guardaroba ripristinato con successo!")
            except Exception as e:
                st.error(f"Errore nel file caricato: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

# 3. GENERATORE OUTFIT & ACADEMY
elif sezione_idx == 2:
    st.title(t["sec3_title"])
    # Generatore Outfit...
elif sezione_idx == 3:
    st.title(t["sec4_title"])
    # Academy...
