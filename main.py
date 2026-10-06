import streamlit as st
from PIL import Image
import json
import os
import base64
from io import BytesIO
import hashlib
import pandas as pd

# Importazione della libreria ufficiale Google GenAI
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# ==========================================
# DIZIONARIO TRADUZIONI MULTILINGUA (IT, EN, DE, SQ)
# ==========================================
I18N = {
    "Italiano": {
        "lang_code": "Italiano",
        "menu": ["Diagnostica Fit", "Guardaroba", "Generatore Outfit", "Academy"],
        "config_title": "⚙️ Configurazione IA",
        "misure_title": "📐 Scheda Profilo e Misure",
        "modifica_misure": "Modifica Parametri Fisici",
        "sesso": "Sesso",
        "sesso_opts": ["Uomo", "Donna"],
        "altezza": "Altezza (cm)",
        "peso": "Peso (kg)",
        "corporatura": "Corporatura",
        "postura": "Postura",
        "armocromia": "Armocromia (Stagione)",
        "corp_opts": ["Atletica / Regolare", "Slim / Sottile", "Robustezza / Torace Largo", "Addome Pronunciato", "Longilineo", "Clessidra / Curve Balanced"],
        "post_opts": ["Eretta / Standard", "Spalle Spioventi", "Spalle Dritte / Squadrate", "Postura Incurvata"],
        "armo_opts": ["Non lo so", "Inverno (Colori freddi e intensi)", "Primavera (Colori caldi e luminosi)", "Estate (Colori freddi e delicati)", "Autunno (Colori caldi e profondi)"],
        "misure_cm": "Misure in Centimetri (cm):",
        "torace": "Torace",
        "vita": "Vita",
        "fianchi": "Fianchi",
        "spalle": "Spalle",
        "manica": "Manica",
        "cavallo": "Cavallo",
        "collo": "Collo",
        "sec1_title": "🔍 DIAGNOSTICA FIT",
        "sec1_sub": "Analisi tecnica, scheda voti e consulenza sartoriale",
        "sec1_upload": "Carica una foto",
        "sec1_camera": "O scatta una foto",
        "sec1_type": "Tipo di Scatto",
        "sec1_type_opts": ["Outfit Completo", "Capo Singolo", "Valutazione Acquisto in Negozio", "Scarpe/Accessori"],
        "sec1_occ": "Occasione d'Uso",
        "sec1_occ_opts": ["Casual", "Business", "Elegante", "Avant-Garde", "Nessuna"],
        "sec1_notes": "Note/Dubbi (es. 'Vale la pena comprarlo?')",
        "sec1_btn": "⚡ ANALIZZA CON IL MAESTRO",
        "sec1_report": "Report Sartoriale",
        "sec2_title": "👔 GUARDAROBA DIGITALE PRIVATO",
        "sec2_sub": "Il tuo armadio salvato in modo permanente e sicuro",
        "sec2_tab1": "➕ AGGIUNGI CAPO",
        "sec2_tab2": "👔 IL TUO ARMADIO",
        "sec2_tab3": "📊 ANALYTICS & BACKUP",
        "sec2_ai_title": "🤖 Assistente Visivo IA",
        "sec2_ai_desc": "Usa la fotocamera o carica una foto: l'IA compilerà automaticamente i dettagli!",
        "sec2_ai_btn": "✨ RICONOSCI DETTAGLI CON IA",
        "sec2_cat_opts": ["Tutte", "Pantaloni", "Giacche / Capispalla", "Camicie / Bluse", "Maglieria", "Abiti Completi", "Gonne", "Scarpe", "Accessori"],
        "sec2_mat_opts": ["Cotone", "Lana / Cashmere", "Lino", "Seta", "Pelle", "Misto / Tecnico"],
        "sec2_sea_opts": ["Tutte le stagioni", "Autunno / Inverno", "Primavera / Estate"],
        "sec2_save": "💾 SALVA NEL GUARDAROBA",
        "sec2_empty": "👋 Il tuo guardaroba è vuoto.",
        "sec2_remove": "🗑️ Rimuovi",
        "sec3_title": "✨ GENERATORE OUTFIT",
        "sec3_sub": "Crea abbinamenti perfetti attingendo dal TUO armadio",
        "sec3_p1": "1. Parametri della Stylist Session",
        "sec3_occ_opts": ["Business", "Smart Casual", "Serata Elegante", "Cerimonia", "Tempo Libero", "Viaggio"],
        "sec3_meteo_opts": ["Primavera", "Estate", "Autunno", "Inverno", "Pioggia"],
        "sec3_style_opts": ["Classico Sartoriale", "Quiet Luxury", "Modern Preppy", "Streetwear", "Sprezzatura Italiana"],
        "sec3_btn": "✨ GENERA OUTFIT",
        "sec3_report": "Proposta Stylist",
        "sec4_title": "🎓 ATELIER ACADEMY",
        "sec4_sub": "Il tuo Mentore Sartoriale personale.",
        "sec4_quick_title": "💡 Spunti Rapidi",
        "sec4_quick_desc": "Clicca su un argomento:",
        "sec4_quick_qs": ["Cos'è la Sprezzatura?", "Lana Super 100s vs 150s?", "Regole Black Tie", "Cura del cashmere"],
        "sec4_chat_title": "💬 Consulta il Mentore",
        "sec4_input_label": "Fai una domanda:",
        "sec4_btn": "🎓 CHIEDI",
        "sec4_placeholder": "Scrivi la tua curiosità...",
        "sec4_empty": "Fai una domanda o clicca su uno spunto rapido!"
    },
    "English": {
        "lang_code": "English",
        "menu": ["Fit Diagnostics", "Wardrobe", "Outfit Generator", "Academy"],
        "config_title": "⚙️ AI Configuration",
        "misure_title": "📐 Profile & Body Measurements",
        "modifica_misure": "Edit Physical Parameters",
        "sesso": "Gender",
        "sesso_opts": ["Male", "Female"],
        "altezza": "Height (cm)",
        "peso": "Weight (kg)",
        "corporatura": "Body Type",
        "postura": "Posture",
        "armocromia": "Color Season",
        "corp_opts": ["Athletic / Regular", "Slim / Lean", "Broad / Wide Chest", "Pronounced Abdomen", "Tall / Slender", "Hourglass / Balanced Curves"],
        "post_opts": ["Erect / Standard", "Sloping Shoulders", "Square Shoulders", "Hunched Posture"],
        "armo_opts": ["Don't know", "Winter (Cool & Intense)", "Spring (Warm & Bright)", "Summer (Cool & Delicate)", "Autumn (Warm & Deep)"],
        "misure_cm": "Measurements in Centimeters (cm):",
        "torace": "Chest",
        "vita": "Waist",
        "fianchi": "Hips",
        "spalle": "Shoulders",
        "manica": "Sleeve",
        "cavallo": "Inseam",
        "collo": "Neck",
        "sec1_title": "🔍 FIT DIAGNOSTICS",
        "sec1_sub": "Technical analysis, score card, and tailoring advice",
        "sec1_upload": "Upload a photo",
        "sec1_camera": "Or take a photo",
        "sec1_type": "Shot Type",
        "sec1_type_opts": ["Full Outfit", "Single Garment", "In-Store Purchase Assessment", "Shoes/Accessories"],
        "sec1_occ": "Occasion",
        "sec1_occ_opts": ["Casual", "Business", "Formal", "Avant-Garde", "None"],
        "sec1_notes": "Notes/Questions (e.g., 'Is it worth buying?')",
        "sec1_btn": "⚡ ANALYZE WITH MASTER TAILOR",
        "sec1_report": "Tailoring Report",
        "sec2_title": "👔 PRIVATE DIGITAL WARDROBE",
        "sec2_sub": "Your wardrobe permanently and securely stored",
        "sec2_tab1": "➕ ADD ITEM",
        "sec2_tab2": "👔 YOUR CLOSET",
        "sec2_tab3": "📊 ANALYTICS & BACKUP",
        "sec2_ai_title": "🤖 AI Visual Assistant",
        "sec2_ai_desc": "Use your camera or upload a photo: AI will automatically fill in details!",
        "sec2_ai_btn": "✨ DETECT DETAILS WITH AI",
        "sec2_cat_opts": ["All", "Pants", "Jackets / Outerwear", "Shirts / Blouses", "Knitwear", "Suits", "Skirts", "Shoes", "Accessories"],
        "sec2_mat_opts": ["Cotton", "Wool / Cashmere", "Linen", "Silk", "Leather", "Blend / Technical"],
        "sec2_sea_opts": ["All Seasons", "Autumn / Winter", "Spring / Summer"],
        "sec2_save": "💾 SAVE TO WARDROBE",
        "sec2_empty": "👋 Your wardrobe is empty.",
        "sec2_remove": "🗑️ Remove",
        "sec3_title": "✨ OUTFIT GENERATOR",
        "sec3_sub": "Create perfect combinations from YOUR closet",
        "sec3_p1": "1. Stylist Session Parameters",
        "sec3_occ_opts": ["Business", "Smart Casual", "Formal Evening", "Black Tie / Ceremony", "Leisure", "Travel"],
        "sec3_meteo_opts": ["Spring", "Summer", "Autumn", "Winter", "Rain"],
        "sec3_style_opts": ["Classic Tailored", "Quiet Luxury", "Modern Preppy", "Streetwear", "Italian Sprezzatura"],
        "sec3_btn": "✨ GENERATE OUTFIT",
        "sec3_report": "Stylist Recommendation",
        "sec4_title": "🎓 ATELIER ACADEMY",
        "sec4_sub": "Your Personal Tailoring Mentor.",
        "sec4_quick_title": "💡 Quick Topics",
        "sec4_quick_desc": "Click on a topic:",
        "sec4_quick_qs": ["What is Sprezzatura?", "Super 100s vs 150s Wool?", "Black Tie Rules", "Cashmere Care"],
        "sec4_chat_title": "💬 Ask the Mentor",
        "sec4_input_label": "Ask a question:",
        "sec4_btn": "🎓 ASK",
        "sec4_placeholder": "Type your question...",
        "sec4_empty": "Ask a question or click on a quick topic!"
    }
}
I18N["Deutsch"] = I18N["English"]
I18N["Albanese"] = I18N["Italiano"]

# ==========================================
# CONFIGURAZIONE E STILE
# ==========================================
st.set_page_config(page_title="ATELIER | Analisi Moda & Guardaroba", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    .stApp { background-color: #ffffff !important; color: #111111 !important; } 
    section[data-testid='stSidebar'] { background-color: #f7f7f9 !important; border-right: 1px solid #e2e8f0; } 
    .atelier-card { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 22px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
</style>
""", unsafe_allow_html=True)

DEFAULT_PROFILO = {
    "sesso": "Uomo", "altezza": 178, "peso": 75, "corporatura": "Atletica / Regolare", "armocromia": "Non lo so",
    "torace": 102, "vita": 84, "fianchi": 98, "spalle": 46, "manica": 64, "cavallo": 81, "collo": 40, "postura": "Eretta / Standard"
}

# Inizializzazione session state
if "lingua" not in st.session_state: 
    st.session_state.lingua = "Italiano"
if "logged_in" not in st.session_state: 
    st.session_state.logged_in = False
if "current_user" not in st.session_state: 
    st.session_state.current_user = "ospite_pubblico"
if "display_name" not in st.session_state: 
    st.session_state.display_name = "Ospite"
if "guardaroba" not in st.session_state: 
    st.session_state.guardaroba = []
if "profilo" not in st.session_state: 
    st.session_state.profilo = DEFAULT_PROFILO.copy()
if "chat" not in st.session_state: 
    st.session_state.chat = []
if "ai_draft" not in st.session_state:
    st.session_state.ai_draft = {"nome": "", "categoria": "", "marca": "", "colore": "", "materiale": "", "stagione": ""}

# ==========================================
# FUNZIONI PER SALVATAGGIO E UTILITY
# ==========================================
def salva_dati_su_file():
    if not st.session_state.logged_in or st.session_state.current_user == "ospite_pubblico": 
        return
    filename = f"atelier_data_{st.session_state.current_user}.json"
    dati = {
        "guardaroba": st.session_state.guardaroba, 
        "profilo": st.session_state.profilo
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=2)

def carica_dati_utente(username_safe):
    filename = f"atelier_data_{username_safe}.json"
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                dati = json.load(f)
                st.session_state.guardaroba = dati.get("guardaroba", [])
                st.session_state.profilo = dati.get("profilo", DEFAULT_PROFILO.copy())
        except Exception:
            st.session_state.guardaroba = []
            st.session_state.profilo = DEFAULT_PROFILO.copy()
    else:
        st.session_state.guardaroba = []
        st.session_state.profilo = DEFAULT_PROFILO.copy()

def image_to_base64(uploaded_file):
    if not uploaded_file: return ""
    try:
        img = Image.open(uploaded_file)
        img.thumbnail((500, 500))
        img = img.convert("RGB")
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=80)
        return f"data:image/jpeg;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
    except Exception:
        return ""

def get_scheda_fisica_prompt():
    p = st.session_state.profilo
    return (f"Gender: {p.get('sesso')}, Height: {p.get('altezza')}cm, Weight: {p.get('peso')}kg, "
            f"Build: {p.get('corporatura')}, Posture: {p.get('postura')}, Color Season: {p.get('armocromia')}. "
            f"Measurements: Chest {p.get('torace')}cm, Waist {p.get('vita')}cm, Hips {p.get('fianchi')}cm, "
            f"Shoulders {p.get('spalle')}cm, Sleeve {p.get('manica')}cm, Inseam {p.get('cavallo')}cm, Neck {p.get('collo')}cm.")

# ==========================================
# SIDEBAR: LOGIN, LINGUA E CONFIGURAZIONE
# ==========================================
st.sidebar.title("🏛️ ATELIER")

# Selettore Lingua
lingua_selezionata = st.sidebar.selectbox("🌐 Lingua / Language", list(I18N.keys()), index=list(I18N.keys()).index(st.session_state.lingua))
if lingua_selezionata != st.session_state.lingua:
    st.session_state.lingua = lingua_selezionata
    st.rerun()

t = I18N[st.session_state.lingua]
st.sidebar.markdown("---")

# Gestione Login Sicuro
if st.session_state.logged_in:
    st.sidebar.success(f"Bentornato, **{st.session_state.display_name}**!")
    if st.sidebar.button("🚪 Esci / Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = "ospite_pubblico"
        st.session_state.display_name = "Ospite"
        st.session_state.guardaroba = []
        st.session_state.profilo = DEFAULT_PROFILO.copy()
        st.rerun()
else:
    st.sidebar.subheader("👤 Accesso Privato")
    username_input = st.sidebar.text_input("Username", placeholder="es. mario88", key="login_user")
    pin_input = st.sidebar.text_input("PIN", type="password", placeholder="****", key="login_pin")
    
    if st.sidebar.button("Accedi", use_container_width=True):
        if username_input and pin_input:
            stringa_da_criptare = f"{username_input}_{pin_input}".encode()
            hash_sicuro = hashlib.sha256(stringa_da_criptare).hexdigest()[:15]
            user_safe = f"{username_input}_{hash_sicuro}"
            st.session_state.current_user = user_safe
            st.session_state.display_name = username_input
            st.session_state.logged_in = True
            carica_dati_utente(user_safe)
            st.rerun()
        else:
            st.sidebar.error("Inserisci sia Username che PIN.")

st.sidebar.markdown("---")

# Menu Navigazione
sezione_idx = st.sidebar.radio("MENU", range(len(t["menu"])), format_func=lambda x: t["menu"][x])
st.sidebar.markdown("---")

# Key Gemini API e Selezione Modello
st.sidebar.subheader("⚙️ Configurazione IA")
default_api_key = os.getenv("GEMINI_API_KEY", "")
api_key_input = st.sidebar.text_input("🔑 Gemini API Key", value=default_api_key, type="password")

model_choice = st.sidebar.selectbox(
    "🤖 Modello Gemini", 
    ["gemini-2.0-flash", "gemini-2.0-flash-lite", "Personalizzato..."],
    index=0
)

if model_choice == "Personalizzato...":
    MODEL_NAME = st.sidebar.text_input("Inserisci ID Modello Custom", "gemini-2.0-flash")
else:
    MODEL_NAME = model_choice

st.sidebar.markdown("---")

# Modifica Misure e Profilo
with st.sidebar.expander(t["modifica_misure"], expanded=False):
    p = st.session_state.profilo
    n_sesso = st.selectbox(t["sesso"], t["sesso_opts"], index=t["sesso_opts"].index(p.get("sesso", "Uomo")) if p.get("sesso") in t["sesso_opts"] else 0)
    n_altezza = st.number_input(t["altezza"], value=int(p.get("altezza", 178)), step=1)
    n_peso = st.number_input(t["peso"], value=int(p.get("peso", 75)), step=1)
    n_corp = st.selectbox(t["corporatura"], t["corp_opts"], index=t["corp_opts"].index(p.get("corporatura", t["corp_opts"][0])) if p.get("corporatura") in t["corp_opts"] else 0)
    n_post = st.selectbox(t["postura"], t["post_opts"], index=t["post_opts"].index(p.get("postura", t["post_opts"][0])) if p.get("postura") in t["post_opts"] else 0)
    n_armo = st.selectbox(t["armocromia"], t["armo_opts"], index=t["armo_opts"].index(p.get("armocromia", t["armo_opts"][0])) if p.get("armocromia") in t["armo_opts"] else 0)
    
    st.markdown(f"**{t['misure_cm']}**")
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        n_torace = st.number_input(t["torace"], value=int(p.get("torace", 102)), step=1)
        n_vita = st.number_input(t["vita"], value=int(p.get("vita", 84)), step=1)
        n_fianchi = st.number_input(t["fianchi"], value=int(p.get("fianchi", 98)), step=1)
    with c_s2:
        n_spalle = st.number_input(t["spalle"], value=int(p.get("spalle", 46)), step=1)
        n_manica = st.number_input(t["manica"], value=int(p.get("manica", 64)), step=1)
        n_cavallo = st.number_input(t["cavallo"], value=int(p.get("cavallo", 81)), step=1)
    n_collo = st.number_input(t["collo"], value=int(p.get("collo", 40)), step=1)

    if (n_sesso != p.get("sesso") or n_altezza != p.get("altezza") or n_peso != p.get("peso") or 
        n_corp != p.get("corporatura") or n_post != p.get("postura") or n_armo != p.get("armocromia") or
        n_torace != p.get("torace") or n_vita != p.get("vita") or n_fianchi != p.get("fianchi") or 
        n_spalle != p.get("spalle") or n_manica != p.get("manica") or n_cavallo != p.get("cavallo") or n_collo != p.get("collo")):
        
        st.session_state.profilo.update({
            "sesso": n_sesso, "altezza": n_altezza, "peso": n_peso, "corporatura": n_corp, 
            "postura": n_post, "armocromia": n_armo, "torace": n_torace, "vita": n_vita, 
            "fianchi": n_fianchi, "spalle": n_spalle, "manica": n_manica, "cavallo": n_cavallo, "collo": n_collo
        })
        salva_dati_su_file()

# ==========================================
# 1. DIAGNOSTICA FIT
# ==========================================
if sezione_idx == 0:
    st.title(t["sec1_title"])
    st.caption(t["sec1_sub"])
    
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        tab_up, tab_cam = st.tabs(["📁 " + t["sec1_upload"], "📸 " + t["sec1_camera"]])
        uploaded_file = None
        with tab_up:
            up_file = st.file_uploader("Carica immagine", type=["jpg", "jpeg", "png"], key="up_fit")
            if up_file: uploaded_file = up_file
        with tab_cam:
            cam_file = st.camera_input("Scatta foto", key="cam_fit")
            if cam_file: uploaded_file = cam_file

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Foto selezionata", use_container_width=True)
            tipo_scatto = st.selectbox(t["sec1_type"], t["sec1_type_opts"])
            occasione = st.selectbox(t["sec1_occ"], t["sec1_occ_opts"])
            dettagli_extra = st.text_area(t["sec1_notes"], height=90)
            analizza_btn = st.button(t["sec1_btn"], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='atelier-card' style='min-height: 400px;'>", unsafe_allow_html=True)
        st.subheader(t["sec1_report"])
        if uploaded_file is not None and 'analizza_btn' in locals() and analizza_btn:
            if not api_key_input: 
                st.error("⚠️ Inserisci la tua Gemini API Key nella barra laterale.")
            elif not HAS_GENAI:
                st.error("⚠️ Libreria 'google-genai' non installata.")
            else:
                with st.spinner("Il Maestro Sartoriale sta analizzando la vestibilità..."):
                    client = genai.Client(api_key=api_key_input)
                    prompt = (f"Sei un Maestro Sartoriale d'alta moda. Rispondi in lingua: {t['lang_code']}.\n"
                              f"Profilo dell'utente: {get_scheda_fisica_prompt()}\n"
                              f"Focus dello scatto: {tipo_scatto}, Occasione: {occasione}.\n"
                              f"Note utente: {dettagli_extra}\n"
                              f"Fornisci un'analisi dettagliata di: vestibilità (fit), proporzioni corporee, "
                              f"abbinamento cromatico ed eventuali modifiche sartoriali consigliate.")
                    try:
                        res = client.models.generate_content(
                            model=MODEL_NAME, 
                            contents=[image, prompt]
                        )
                        st.markdown(res.text)
                    except Exception as e:
                        if "404" in str(e):
                            st.error(f"⚠️ Il modello '{MODEL_NAME}' non è disponibile per la tua API Key. Assicurati di aver selezionato 'gemini-2.0-flash' nella barra laterale.")
                        else:
                            st.error(f"Errore durante l'analisi: {str(e)}")
        else: 
            st.info("👋 Carica o scatta una foto a sinistra e clicca su Analizza per ricevere la consulenza.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 2. GUARDAROBA DIGITALE PRIVATO
# ==========================================
elif sezione_idx == 1:
    st.title(t["sec2_title"])
    st.caption(t["sec2_sub"])
    
    tab1, tab2, tab3 = st.tabs([t["sec2_tab1"], t["sec2_tab2"], t["sec2_tab3"]])
    
    # AGGIUNGI CAPO
    with tab1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader(t["sec2_ai_title"])
        st.caption(t["sec2_ai_desc"])
        
        t_up, t_cam = st.tabs(["📁 Carica Foto Capo", "📸 Scatta Foto Capo"])
        capo_image = None
        with t_up:
            cu_file = st.file_uploader("Scegli immagine", type=["jpg", "jpeg", "png"], key="up_guardaroba")
            if cu_file: capo_image = cu_file
        with t_cam:
            cc_file = st.camera_input("Fotografa il capo", key="cam_guardaroba")
            if cc_file: capo_image = cc_file
        
        if capo_image is not None:
            st.image(Image.open(capo_image), width=200)
            if st.button(t["sec2_ai_btn"]):
                if not api_key_input: 
                    st.error("⚠️ Manca la Gemini API Key.")
                elif not HAS_GENAI:
                    st.error("⚠️ Libreria 'google-genai' non installata.")
                else:
                    with st.spinner("Analisi visiva in corso con IA..."):
                        client = genai.Client(api_key=api_key_input)
                        prompt_vision = (f"Analizza l'immagine di questo capo d'abbigliamento. "
                                         f"Restituisci un oggetto JSON con queste chiavi esatte:\n"
                                         f"- nome: breve titolo del capo\n"
                                         f"- categoria: uno tra {t['sec2_cat_opts'][1:]}\n"
                                         f"- marca: marca visibile o 'Sconosciuta'\n"
                                         f"- colore: colore principale\n"
                                         f"- materiale: uno tra {t['sec2_mat_opts']}\n"
                                         f"- stagione: uno tra {t['sec2_sea_opts']}")
                        try:
                            resp = client.models.generate_content(
                                model=MODEL_NAME, 
                                contents=[Image.open(capo_image), prompt_vision],
                                config=types.GenerateContentConfig(response_mime_type="application/json")
                            )
                            dati_estratta = json.loads(resp.text)
                            st.session_state.ai_draft.update(dati_estratta)
                            st.success("✨ Dettagli riconosciuti con successo! Verifica e salva qui sotto.")
                        except Exception as e:
                            if "404" in str(e):
                                st.error(f"⚠️ Errore 404: Il modello '{MODEL_NAME}' non è stato trovato. Assicurati che nella barra laterale sia selezionato 'gemini-2.0-flash'.")
                            else:
                                st.error(f"Impossibile riconoscere i dettagli automaticamente: {e}")
        
        st.markdown("---")
        st.markdown("### 📝 Dettagli Capo")
        
        draft = st.session_state.ai_draft
        cat_opts_no_tutte = t["sec2_cat_opts"][1:]
        
        with st.form("form_aggiunta_capo"):
            c1, c2 = st.columns(2)
            with c1:
                nome_capo = st.text_input("Nome Capo*", value=draft.get("nome", ""))
                cat_idx = cat_opts_no_tutte.index(draft.get("categoria")) if draft.get("categoria") in cat_opts_no_tutte else 0
                categoria = st.selectbox("Categoria*", cat_opts_no_tutte, index=cat_idx)
                colore = st.text_input("Colore*", value=draft.get("colore", ""))
            with c2:
                marca = st.text_input("Marca", value=draft.get("marca", ""))
                mat_idx = t["sec2_mat_opts"].index(draft.get("materiale")) if draft.get("materiale") in t["sec2_mat_opts"] else 0
                materiale = st.selectbox("Tessuto / Materiale", t["sec2_mat_opts"], index=mat_idx)
                sea_idx = t["sec2_sea_opts"].index(draft.get("stagione")) if draft.get("stagione") in t["sec2_sea_opts"] else 0
                stagione = st.selectbox("Stagione", t["sec2_sea_opts"], index=sea_idx)
                
            submitted = st.form_submit_button(t["sec2_save"], use_container_width=True)
            if submitted:
                if not nome_capo or not colore:
                    st.error("Inserisci almeno Nome e Colore per salvare.")
                elif not st.session_state.logged_in:
                    st.error("⚠️ Devi effettuare l'accesso per salvare i capi nel tuo guardaroba privato.")
                else:
                    b64_img = image_to_base64(capo_image)
                    nuovo_capo = {
                        "id": len(st.session_state.guardaroba) + 1, 
                        "nome": nome_capo, 
                        "categoria": categoria, 
                        "marca": marca, 
                        "colore": colore, 
                        "materiale": materiale, 
                        "stagione": stagione, 
                        "immagine": b64_img
                    }
                    st.session_state.guardaroba.append(nuovo_capo)
                    salva_dati_su_file()
                    # Resetta draft
                    st.session_state.ai_draft = {"nome": "", "categoria": "", "marca": "", "colore": "", "materiale": "", "stagione": ""}
                    st.success("✅ Salvato nel guardaroba!")
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # IL TUO ARMADIO
    with tab2:
        if not st.session_state.guardaroba:
            st.info(t["sec2_empty"])
        else:
            st.markdown("#### 🔍 Filtra il tuo Armadio")
            col_f1, col_f2 = st.columns(2)
            with col_f1: 
                filtro_cat = st.selectbox("Categoria", t["sec2_cat_opts"], key="filter_cat")
            with col_f2: 
                cerca_testo = st.text_input("Cerca (nome, colore, marca)", key="filter_text")
            
            capi_filtrati = st.session_state.guardaroba
            if filtro_cat != "Tutte": 
                capi_filtrati = [c for c in capi_filtrati if c.get("categoria") == filtro_cat]
            if cerca_testo: 
                capi_filtrati = [c for c in capi_filtrati if cerca_testo.lower() in str(c.values()).lower()]

            st.markdown(f"Trovati: **{len(capi_filtrati)} capi**")
            cols = st.columns(3)
            for idx, capo in enumerate(capi_filtrati):
                with cols[idx % 3]:
                    st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
                    if capo.get("immagine"): 
                        st.image(capo["immagine"], use_container_width=True)
                    st.markdown(f"### {capo['nome']}\n\n🏷 **{capo['categoria']}** | 🎨 {capo['colore']}\n\n🧵 {capo.get('materiale','')} | 🏷️ {capo.get('marca','')}")
                    if st.button(t["sec2_remove"], key=f"del_{capo['id']}_{idx}"):
                        st.session_state.guardaroba = [c for c in st.session_state.guardaroba if c["id"] != capo["id"]]
                        salva_dati_su_file()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    # ANALYTICS & BACKUP
    with tab3:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader("📊 Statistiche Guardaroba")
        if not st.session_state.guardaroba:
            st.info("Aggiungi capi per visualizzare le statistiche.")
        else:
            df = pd.DataFrame(st.session_state.guardaroba)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Composizione per Categoria**")
                if "categoria" in df.columns:
                    st.bar_chart(df['categoria'].value_counts())
            with c2:
                st.markdown("**Composizione per Stagione**")
                if "stagione" in df.columns:
                    st.bar_chart(df['stagione'].value_counts())
                
        st.markdown("---")
        st.subheader("💾 Backup e Export Dati")
        export_data = {"guardaroba": st.session_state.guardaroba, "profilo": st.session_state.profilo}
        st.download_button(
            "📥 Scarica File JSON di Backup", 
            data=json.dumps(export_data, indent=2, ensure_ascii=False), 
            file_name=f"backup_atelier_{st.session_state.current_user}.json",
            mime="application/json"
        )
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 3. GENERATORE OUTFIT
# ==========================================
elif sezione_idx == 2:
    st.title(t["sec3_title"])
    st.caption(t["sec3_sub"])
    
    c_out1, c_out2 = st.columns([1, 1], gap="large")
    with c_out1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader("⚙️ Parametri della Sessione")
        occ = st.selectbox("Occasione d'Uso", t["sec3_occ_opts"])
        meteo = st.selectbox("Stagione / Meteo", t["sec3_meteo_opts"])
        stile = st.selectbox("Stile Desiderato", t["sec3_style_opts"])
        genera_btn = st.button(t["sec3_btn"], use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_out2:
        st.markdown("<div class='atelier-card' style='min-height: 400px;'>", unsafe_allow_html=True)
        st.subheader(t["sec3_report"])
        if genera_btn:
            if not api_key_input: 
                st.error("⚠️ Manca la Gemini API Key.")
            elif not HAS_GENAI:
                st.error("⚠️ Libreria 'google-genai' non installata.")
            else:
                with st.spinner("La tua Stylist sta creando la combinazione ideale..."):
                    if st.session_state.guardaroba:
                        armadio_str = "\n".join([f"- {c['nome']} (Categoria: {c['categoria']}, Colore: {c['colore']}, Materiale: {c.get('materiale','')})" for c in st.session_state.guardaroba])
                    else:
                        armadio_str = "L'armadio dell'utente è attualmente vuoto. Suggerisci un outfit ideale dal catalogo ideale sartoriale."
                    
                    prompt = (f"Sei una Personal Stylist d'Alta Moda. Lingua risposta: {t['lang_code']}.\n"
                              f"Profilo utente: {get_scheda_fisica_prompt()}\n"
                              f"Richiesta: Occasione {occ}, Meteo {meteo}, Stile {stile}.\n"
                              f"Capi attualmente presenti nel guardaroba privato utente:\n{armadio_str}\n\n"
                              f"Crea un outfit completo coordinato attingendo prioritariamente dai capi salvati nell'armadio. "
                              f"Spiega le ragioni degli abbinamenti cromatici e delle proporzioni.")
                    
                    client = genai.Client(api_key=api_key_input)
                    try:
                        res = client.models.generate_content(model=MODEL_NAME, contents=prompt)
                        st.markdown(res.text)
                    except Exception as e:
                        if "404" in str(e):
                            st.error(f"⚠️ Il modello '{MODEL_NAME}' non è stato trovato per la tua API Key. Seleziona 'gemini-2.0-flash' nella barra laterale.")
                        else:
                            st.error(f"Errore nella generazione dell'outfit: {str(e)}")
        else:
            st.info("👋 Seleziona i parametri e clicca 'Genera Outfit' per ricevere il consiglio di stile.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 4. ACADEMY
# ==========================================
elif sezione_idx == 3:
    st.title(t["sec4_title"])
    st.caption(t["sec4_sub"])
    
    c_ac1, c_ac2 = st.columns([1, 2], gap="large")
    
    domanda_da_inviare = None
    
    with c_ac1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader(t["sec4_quick_title"])
        st.caption(t["sec4_quick_desc"])
        for q in t["sec4_quick_qs"]:
            if st.button(f"📌 {q}", use_container_width=True, key=f"btn_q_{q}"):
                domanda_da_inviare = q
        st.markdown("</div>", unsafe_allow_html=True)

    with c_ac2:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader(t["sec4_chat_title"])
        
        domanda_input = st.text_input(t["sec4_input_label"], placeholder=t["sec4_placeholder"], key="input_chat_academy")
        asked = st.button(t["sec4_btn"], use_container_width=True)
        
        if asked and domanda_input:
            domanda_da_inviare = domanda_input

        if domanda_da_inviare:
            if not api_key_input: 
                st.error("⚠️ Manca la Gemini API Key.")
            elif not HAS_GENAI:
                st.error("⚠️ Libreria 'google-genai' non installata.")
            else:
                with st.spinner("Il Mentore sta rispondendo..."):
                    client = genai.Client(api_key=api_key_input)
                    prompt_academy = (f"Sei un Mentore ed Esperto di Storia della Moda e Sartoria Tradizionale. "
                                      f"Rispondi in lingua: {t['lang_code']}.\n"
                                      f"Profilo utente: {get_scheda_fisica_prompt()}\n"
                                      f"Domanda dell'utente: {domanda_da_inviare}")
                    try:
                        res = client.models.generate_content(model=MODEL_NAME, contents=prompt_academy)
                        st.session_state.chat.append({"q": domanda_da_inviare, "a": res.text})
                    except Exception as e:
                        if "404" in str(e):
                            st.error(f"⚠️ Il modello '{MODEL_NAME}' non è stato trovato. Assicurati che nella barra laterale sia selezionato 'gemini-2.0-flash'.")
                        else:
                            st.error(f"Errore di connessione al mentore: {str(e)}")

        st.markdown("---")
        if not st.session_state.chat:
            st.info(t["sec4_empty"])
        else:
            for chat in reversed(st.session_state.chat): 
                st.markdown(f"**❓ {chat['q']}**\n\n{chat['a']}\n")
                st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)
