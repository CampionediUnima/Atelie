import streamlit as st
from PIL import Image
import json
import os
import base64
from io import BytesIO
import hashlib
import pandas as pd # Aggiunto per le analytics

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
        "modifica_misure": "Modifica Parametri",
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
        "sec1_title": "DIAGNOSTICA FIT",
        "sec1_sub": "Analisi tecnica, scheda voti e consulenza",
        "sec1_upload": "Carica una foto",
        "sec1_camera": "O scatta una foto",
        "sec1_type": "Tipo di Scatto",
        "sec1_type_opts": ["Outfit Completo", "Capo Singolo", "Valutazione Acquisto in Negozio", "Scarpe/Accessori"],
        "sec1_occ": "Occasione d'Uso",
        "sec1_occ_opts": ["Casual", "Business", "Elegante", "Avant-Garde", "Nessuna"],
        "sec1_notes": "Note/Dubbi (es. 'Vale la pena comprarlo?')",
        "sec1_btn": "⚡ ANALIZZA CON IL MAESTRO",
        "sec1_report": "Report Sartoriale",
        "sec2_title": "GUARDAROBA DIGITALE PRIVATO",
        "sec2_sub": "Il tuo armadio salvato in modo permanente e sicuro",
        "sec2_tab1": "➕ AGGIUNGI CAPO",
        "sec2_tab2": "👔 IL TUO ARMADIO",
        "sec2_tab3": "📊 ANALYTICS & BACKUP",
        "sec2_ai_title": "🤖 Assistente Visivo",
        "sec2_ai_desc": "Usa la fotocamera o carica una foto: l'IA compilerà automaticamente i dettagli!",
        "sec2_ai_btn": "✨ RICONOSCI DETTAGLI",
        "sec2_cat_opts": ["Tutte", "Pantaloni", "Giacche / Capispalla", "Camicie / Bluse", "Maglieria", "Abiti Completi", "Gonne", "Scarpe", "Accessori"],
        "sec2_mat_opts": ["Cotone", "Lana / Cashmere", "Lino", "Seta", "Pelle", "Misto / Tecnico"],
        "sec2_sea_opts": ["Tutte le stagioni", "Autunno / Inverno", "Primavera / Estate"],
        "sec2_save": "💾 SALVA NEL GUARDAROBA",
        "sec2_empty": "👋 Il tuo guardaroba è vuoto.",
        "sec2_remove": "🗑️ Rimuovi",
        "sec3_title": "GENERATORE OUTFIT",
        "sec3_sub": "Crea abbinamenti perfetti attingendo dal TUO armadio",
        "sec3_p1": "1. Parametri della Stylist Session",
        "sec3_occ_opts": ["Business", "Smart Casual", "Serata Elegante", "Cerimonia", "Tempo Libero", "Viaggio"],
        "sec3_meteo_opts": ["Primavera", "Estate", "Autunno", "Inverno", "Pioggia"],
        "sec3_style_opts": ["Classico Sartoriale", "Quiet Luxury", "Modern Preppy", "Streetwear", "Sprezzatura Italiana"],
        "sec3_btn": "✨ GENERA OUTFIT",
        "sec3_report": "Proposta Stylist",
        "sec4_title": "ATELIER ACADEMY",
        "sec4_sub": "Il tuo Mentore Sartoriale personale.",
        "sec4_quick_title": "💡 Spunti Rapidi",
        "sec4_quick_desc": "Clicca su un argomento:",
        "sec4_quick_qs": ["Cos'è la Sprezzatura?", "Lana Super 100s vs 150s?", "Regole Black Tie", "Cura del cashmere"],
        "sec4_chat_title": "💬 Consulta il Mentore",
        "sec4_input_label": "Fai una domanda:",
        "sec4_btn": "🎓 CHIEDI",
        "sec4_placeholder": "Scrivi la tua curiosità...",
        "sec4_empty": "Fai una domanda o clicca su uno spunto rapido!"
    }
}
# Fallback
for lang in ["English", "Deutsch", "Albanese"]: I18N[lang] = I18N["Italiano"]

# ==========================================
# CONFIGURAZIONE E STILE
# ==========================================
st.set_page_config(page_title="ATELIER | Analisi Moda", layout="wide", initial_sidebar_state="expanded")
st.markdown("<style>.stApp { background-color: #ffffff !important; color: #111111 !important; } section[data-testid='stSidebar'] { background-color: #f7f7f9 !important; border-right: 1px solid #e2e8f0; } .atelier-card { background-color: #ffffff; border: 1px solid #e2e8f0; padding: 22px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }</style>", unsafe_allow_html=True)

DEFAULT_PROFILO = {
    "sesso": "Uomo", "altezza": 178, "peso": 75, "corporatura": "Atletica / Regolare", "armocromia": "Non lo so",
    "torace": 102, "vita": 84, "fianchi": 98, "spalle": 46, "manica": 64, "cavallo": 81, "collo": 40, "postura": "Eretta / Standard"
}

if "lingua" not in st.session_state: st.session_state.lingua = "Italiano"
t = I18N[st.session_state.lingua]

# ==========================================
# 🔐 SISTEMA DI LOGIN SICURO E LOGOUT
# ==========================================
st.sidebar.title("ATELIER")
st.sidebar.markdown("---")

if st.session_state.get("current_user") and st.session_state.current_user != "ospite_pubblico":
    nome_visualizzato = st.session_state.get("display_name", "Utente")
    st.sidebar.success(f"Bentornato, {nome_visualizzato}!")
    if st.sidebar.button("🚪 Esci / Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    user_safe = st.session_state.current_user
else:
    st.sidebar.subheader("👤 Accesso Privato")
    st.sidebar.caption("Inserisci Username e PIN.")
    col_u, col_p = st.sidebar.columns(2)
    with col_u: username_input = st.text_input("Username", placeholder="es. mario88")
    with col_p: pin_input = st.text_input("PIN", type="password", placeholder="****")

    if username_input and pin_input:
        stringa_da_criptare = f"{username_input}_{pin_input}".encode()
        hash_sicuro = hashlib.sha256(stringa_da_criptare).hexdigest()[:15]
        user_safe = f"{username_input}_{hash_sicuro}"
        st.session_state.display_name = username_input
        if st.sidebar.button("Accedi"):
            st.session_state.current_user = user_safe
            st.rerun()
    else:
        user_safe = "ospite_pubblico"

if "current_user" not in st.session_state: st.session_state.current_user = None

def salva_dati_su_file():
    if st.session_state.current_user == "ospite_pubblico": return
    filename = f"atelier_data_{st.session_state.current_user}.json"
    dati = {"guardaroba": st.session_state.guardaroba, "profilo": st.session_state.profilo}
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(dati, f, ensure_ascii=False, indent=2)

if st.session_state.current_user != user_safe:
    st.session_state.current_user = user_safe
    if user_safe != "ospite_pubblico":
        filename = f"atelier_data_{user_safe}.json"
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    dati = json.load(f)
                    st.session_state.guardaroba = dati.get("guardaroba", [])
                    st.session_state.profilo = dati.get("profilo", DEFAULT_PROFILO.copy())
            except:
                st.session_state.guardaroba = []
                st.session_state.profilo = DEFAULT_PROFILO.copy()
        else:
            st.session_state.guardaroba = []
            st.session_state.profilo = DEFAULT_PROFILO.copy()
    else:
        st.session_state.guardaroba = []
        st.session_state.profilo = DEFAULT_PROFILO.copy()

if "ai_draft" not in st.session_state:
    st.session_state.ai_draft = {"nome": "", "categoria": t["sec2_cat_opts"][1], "marca": "", "colore": "", "materiale": t["sec2_mat_opts"][0], "stagione": t["sec2_sea_opts"][0]}
if "chat" not in st.session_state: st.session_state.chat = []

def image_to_base64(uploaded_file):
    if not uploaded_file: return ""
    try:
        img = Image.open(uploaded_file)
        img.thumbnail((500, 500))
        img = img.convert("RGB")
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=80)
        return f"data:image/jpeg;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
    except: return ""

# ==========================================
# MENU E PROFILO FISICO
# ==========================================
sezione_idx = st.sidebar.radio("MENU", range(len(t["menu"])), format_func=lambda x: t["menu"][x])
st.sidebar.markdown("---")
api_key_input = st.sidebar.text_input("🔑 Gemini API Key", type="password")
st.sidebar.markdown("---")

with st.sidebar.expander(t["modifica_misure"], expanded=False):
    p = st.session_state.profilo
    n_sesso = st.selectbox(t["sesso"], t["sesso_opts"], index=t["sesso_opts"].index(p.get("sesso", "Uomo")) if p.get("sesso", "Uomo") in t["sesso_opts"] else 0)
    n_altezza = st.number_input(t["altezza"], value=int(p.get("altezza", 178)), step=1)
    n_peso = st.number_input(t["peso"], value=int(p.get("peso", 75)), step=1)
    n_corp = st.selectbox(t["corporatura"], t["corp_opts"], index=t["corp_opts"].index(p.get("corporatura", t["corp_opts"][0])) if p.get("corporatura") in t["corp_opts"] else 0)
    n_post = st.selectbox(t["postura"], t["post_opts"], index=t["post_opts"].index(p.get("postura", t["post_opts"][0])) if p.get("postura") in t["post_opts"] else 0)
    # ARMOCROMIA Aggiunta
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

    if any([n_sesso != p.get("sesso"), n_altezza != p.get("altezza"), n_peso != p.get("peso"), n_corp != p.get("corporatura"), n_post != p.get("postura"), n_armo != p.get("armocromia"), n_torace != p.get("torace"), n_vita != p.get("vita"), n_fianchi != p.get("fianchi"), n_spalle != p.get("spalle"), n_manica != p.get("manica"), n_cavallo != p.get("cavallo"), n_collo != p.get("collo")]):
        st.session_state.profilo.update({"sesso": n_sesso, "altezza": n_altezza, "peso": n_peso, "corporatura": n_corp, "postura": n_post, "armocromia": n_armo, "torace": n_torace, "vita": n_vita, "fianchi": n_fianchi, "spalle": n_spalle, "manica": n_manica, "cavallo": n_cavallo, "collo": n_collo})
        salva_dati_su_file()

def get_scheda_fisica_prompt():
    p = st.session_state.profilo
    return f"Gender: {p.get('sesso')}, Height: {p.get('altezza')}cm, Weight: {p.get('peso')}kg, Build: {p.get('corporatura')}, Season/Color Palette: {p.get('armocromia')}. Measurements: Chest {p.get('torace')}cm, Waist {p.get('vita')}cm, Hips {p.get('fianchi')}cm, Shoulders {p.get('spalle')}cm."

# ==========================================
# 1. DIAGNOSTICA FIT
# ==========================================
if sezione_idx == 0:
    st.title(t["sec1_title"])
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        # SUPPORTO FOTOCAMERA E UPLOAD
        tab_up, tab_cam = st.tabs(["📁 Carica Foto", "📸 Scatta Foto"])
        uploaded_file = None
        with tab_up:
            up_file = st.file_uploader(t["sec1_upload"], type=["jpg", "jpeg", "png"])
            if up_file: uploaded_file = up_file
        with tab_cam:
            cam_file = st.camera_input(t["sec1_camera"])
            if cam_file: uploaded_file = cam_file

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Foto da analizzare", use_container_width=True)
            tipo_scatto = st.selectbox(t["sec1_type"], t["sec1_type_opts"])
            occasione = st.selectbox(t["sec1_occ"], t["sec1_occ_opts"])
            dettagli_extra = st.text_area(t["sec1_notes"], height=90)
            analizza_btn = st.button(t["sec1_btn"])
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c2:
        st.markdown("<div class='atelier-card' style='min-height: 400px;'>", unsafe_allow_html=True)
        st.subheader(t["sec1_report"])
        if uploaded_file is not None and 'analizza_btn' in locals() and analizza_btn:
            if not api_key_input: st.error("⚠️ Inserisci la tua API Key.")
            else:
                with st.spinner("Analisi in corso..."):
                    client = genai.Client(api_key=api_key_input)
                    prompt = f"Maestro Sartoriale. Lingua: {t['lang_code']}. Profilo: {get_scheda_fisica_prompt()}. Focus: {tipo_scatto}, Occasione: {occasione}, Note: {dettagli_extra}"
                    try:
                        res = client.models.generate_content(model='gemini-2.5-flash', contents=[image, prompt])
                        st.markdown(res.text)
                    except Exception as e: st.error(str(e))
        else: st.write("👋 Inserisci un'immagine a sinistra per iniziare.")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 2. GUARDAROBA DIGITALE
# ==========================================
elif sezione_idx == 1:
    st.title(t["sec2_title"])
    tab1, tab2, tab3 = st.tabs([t["sec2_tab1"], t["sec2_tab2"], t["sec2_tab3"]])
    
    with tab1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        st.subheader(t["sec2_ai_title"])
        # SUPPORTO FOTOCAMERA E UPLOAD PER GUARDAROBA
        t_up, t_cam = st.tabs(["📁 Carica Foto", "📸 Scatta Foto"])
        capo_image = None
        with t_up:
            cu_file = st.file_uploader("Carica immagine capo", type=["jpg", "jpeg", "png"])
            if cu_file: capo_image = cu_file
        with t_cam:
            cc_file = st.camera_input("Fotografa il capo", key="cam_guardaroba")
            if cc_file: capo_image = cc_file
        
        if capo_image is not None:
            st.image(Image.open(capo_image), width=250)
            if st.button(t["sec2_ai_btn"]):
                if not api_key_input: st.error("⚠️ Manca la API Key.")
                else:
                    with st.spinner("Riconoscimento in corso..."):
                        client = genai.Client(api_key=api_key_input)
                        prompt_vision = f"Analizza il capo. Ritorna JSON puro con: nome, categoria ({t['sec2_cat_opts'][1:]}), marca, colore, materiale ({t['sec2_mat_opts']}), stagione ({t['sec2_sea_opts']})."
                        try:
                            resp = client.models.generate_content(model='gemini-2.5-flash', contents=[Image.open(capo_image), prompt_vision])
                            txt = resp.text.strip().replace("```json", "").replace("```", "").strip()
                            st.session_state.ai_draft.update(json.loads(txt))
                            st.success("Dettagli riconosciuti!")
                        except: st.error("Errore nel riconoscimento")
        
        draft = st.session_state.ai_draft
        with st.form("form_aggiunta"):
            c1, c2 = st.columns(2)
            with c1:
                nome_capo = st.text_input("Nome*", value=draft.get("nome", ""))
                cat_opts_no_tutte = t["sec2_cat_opts"][1:]
                cat_idx = cat_opts_no_tutte.index(draft.get("categoria")) if draft.get("categoria") in cat_opts_no_tutte else 0
                categoria = st.selectbox("Categoria*", cat_opts_no_tutte, index=cat_idx)
                colore = st.text_input("Colore*", value=draft.get("colore", ""))
            with c2:
                marca = st.text_input("Marca", value=draft.get("marca", ""))
                mat_idx = t["sec2_mat_opts"].index(draft.get("materiale")) if draft.get("materiale") in t["sec2_mat_opts"] else 0
                materiale = st.selectbox("Tessuto", t["sec2_mat_opts"], index=mat_idx)
                sea_idx = t["sec2_sea_opts"].index(draft.get("stagione")) if draft.get("stagione") in t["sec2_sea_opts"] else 0
                stagione = st.selectbox("Stagione", t["sec2_sea_opts"], index=sea_idx)
                
            if st.form_submit_button(t["sec2_save"]) and nome_capo and colore:
                if st.session_state.current_user == "ospite_pubblico":
                    st.error("Devi fare il login per salvare i capi.")
                else:
                    b64_img = image_to_base64(capo_image)
                    nuovo_capo = {"id": len(st.session_state.guardaroba) + 1, "nome": nome_capo, "categoria": categoria, "marca": marca, "colore": colore, "materiale": materiale, "stagione": stagione, "immagine": b64_img}
                    st.session_state.guardaroba.append(nuovo_capo)
                    salva_dati_su_file()
                    st.success("✅ Salvato nel guardaroba!")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        if not st.session_state.guardaroba:
            st.info(t["sec2_empty"])
        else:
            # FILTRI DI RICERCA
            st.markdown("#### 🔍 Filtra il tuo Armadio")
            col_f1, col_f2 = st.columns(2)
            with col_f1: filtro_cat = st.selectbox("Categoria", t["sec2_cat_opts"])
            with col_f2: cerca_testo = st.text_input("Cerca (nome, colore, marca)")
            
            capi_filtrati = st.session_state.guardaroba
            if filtro_cat != "Tutte": capi_filtrati = [c for c in capi_filtrati if c.get("categoria") == filtro_cat]
            if cerca_testo: capi_filtrati = [c for c in capi_filtrati if cerca_testo.lower() in str(c.values()).lower()]

            st.markdown(f"Trovati: **{len(capi_filtrati)} capi**")
            cols = st.columns(3)
            for idx, capo in enumerate(capi_filtrati):
                with cols[idx % 3]:
                    st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
                    if capo.get("immagine"): st.image(capo["immagine"], use_container_width=True)
                    st.markdown(f"**{capo['nome']}**\n\n🏷 {capo['categoria']} | 🎨 {capo['colore']}\n\n🧵 {capo.get('materiale','')}")
                    if st.button(t["sec2_remove"], key=f"del_{capo['id']}"):
                        st.session_state.guardaroba = [c for c in st.session_state.guardaroba if c["id"] != capo["id"]]
                        salva_dati_su_file()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        # DASHBOARD ANALYTICS
        st.subheader("📊 Statistiche Guardaroba")
        if not st.session_state.guardaroba:
            st.info("Aggiungi capi per vedere le statistiche.")
        else:
            df = pd.DataFrame(st.session_state.guardaroba)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Composizione per Categoria**")
                st.bar_chart(df['categoria'].value_counts())
            with c2:
                st.markdown("**Composizione per Stagione**")
                st.bar_chart(df['stagione'].value_counts())
                
        st.markdown("---")
        st.subheader("💾 Esporta Dati")
        export_data = {"guardaroba": st.session_state.guardaroba, "profilo": st.session_state.profilo}
        st.download_button("📥 Scarica File JSON di Backup", data=json.dumps(export_data, indent=2), file_name=f"backup_atelier.json")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 3. GENERATORE OUTFIT & 4. ACADEMY
# ==========================================
elif sezione_idx == 2:
    st.title(t["sec3_title"])
    c_out1, c_out2 = st.columns(2)
    with c_out1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        occ = st.selectbox("Occasione", t["sec3_occ_opts"])
        meteo = st.selectbox("Meteo", t["sec3_meteo_opts"])
        stile = st.selectbox("Stile", t["sec3_style_opts"])
        genera_btn = st.button(t["sec3_btn"])
        st.markdown("</div>", unsafe_allow_html=True)

    with c_out2:
        st.markdown("<div class='atelier-card' style='min-height: 400px;'>", unsafe_allow_html=True)
        if genera_btn:
            if not api_key_input: st.error("Manca API Key")
            else:
                with st.spinner("Creazione..."):
                    armadio_str = "\n".join([f"- {c['nome']} | {c['categoria']} | {c['colore']}" for c in st.session_state.guardaroba]) if st.session_state.guardaroba else "Armadio vuoto."
                    prompt = f"Stylist. Lingua: {t['lang_code']}. Profilo: {get_scheda_fisica_prompt()}. Occasione: {occ}. Meteo: {meteo}. Stile: {stile}. Guardaroba disponibile: {armadio_str}"
                    client = genai.Client(api_key=api_key_input)
                    try: st.markdown(client.models.generate_content(model='gemini-2.5-flash', contents=prompt).text)
                    except Exception as e: st.error(str(e))
        st.markdown("</div>", unsafe_allow_html=True)

elif sezione_idx == 3:
    st.title(t["sec4_title"])
    c_ac1, c_ac2 = st.columns([1, 2])
    with c_ac1:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        scelta_rapida = None
        for q in t["sec4_quick_qs"]:
            if st.button(f"📌 {q}", use_container_width=True): scelta_rapida = q
        st.markdown("</div>", unsafe_allow_html=True)

    with c_ac2:
        st.markdown("<div class='atelier-card'>", unsafe_allow_html=True)
        domanda = st.text_input("Domanda:", value=scelta_rapida if scelta_rapida else "")
        if st.button(t["sec4_btn"]) and domanda:
            if not api_key_input: st.error("Manca API Key")
            else:
                with st.spinner("Pensando..."):
                    client = genai.Client(api_key=api_key_input)
                    try:
                        res = client.models.generate_content(model='gemini-2.5-flash', contents=f"Esperto moda. Lingua: {t['lang_code']}. Profilo: {get_scheda_fisica_prompt()}. Domanda: {domanda}")
                        st.session_state.chat.append({"q": domanda, "a": res.text})
                    except Exception as e: st.error(str(e))
        for chat in reversed(st.session_state.chat): st.markdown(f"**❓ {chat['q']}**\n\n{chat['a']}\n---")
        st.markdown("</div>", unsafe_allow_html=True)
