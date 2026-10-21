# (versão 4.13 – Prof. Max / Portal SABIÁ)
# Correção: Restauração completa das funções de conversão HTML/Markdown.

import streamlit as st
import requests
import json
import re
import time
import html as html_lib
from datetime import datetime

def _get_secret(chave: str, padrao: str = "") -> str:
    try: return st.secrets[chave]
    except Exception: return padrao

WEBHOOK_URL = _get_secret("WEBHOOK_URL_MAX", "http://167.126.1.122.nip.io:5678/webhook/prof-max-fisica")
HISTORY_URL = _get_secret("HISTORY_URL_MAX", "http://167.126.1.122.nip.io:5678/webhook/prof-max-history")
CLEAR_URL   = _get_secret("CLEAR_URL_MAX",   "http://167.126.1.122.nip.io:5678/webhook/prof-max-clear")

session_id_fis = f"{st.session_state.session_id}_fis"

defaults = {
    "fis_messages": [], "fis_error_log": [], "fis_progress_log": [],
    "fis_last_response_html": "", "fis_formato_num": "1",
    "fis_last_simulacoes": [], "fis_history_loaded": False,
    "fis_confirmar_reset": False,
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

global_defaults = {
    "font_size": 16, "dark_mode": True,
    "fis_perfil_cor_dark": "Azul-noite", "fis_perfil_cor_light": "Papel",
}
for k, v in global_defaults.items():
    if k not in st.session_state: st.session_state[k] = v

if not st.session_state.fis_history_loaded:
    st.session_state.fis_history_loaded = True
    try:
        r = requests.post(HISTORY_URL, json={"sessionId": session_id_fis}, timeout=(5, 15), headers={"Content-Type": "application/json"})
        if r.status_code == 200:
            data = r.json()
            msgs = data.get("messages") or []
            if isinstance(msgs, list) and msgs: st.session_state.fis_messages = msgs
    except Exception: pass

def _detectar_tema(pergunta: str) -> str:
    p = (pergunta or "").lower()
    temas = [("eletromagnetismo", ["magnétic", "ímã", "indução"]), ("eletricidade", ["corrente", "resistor", "circuito"]), ("termodinâmica", ["calor", "temperatura", "gás"]), ("ondulatória", ["onda", "frequência", "som"]), ("óptica", ["luz", "refração", "lente"]), ("física moderna", ["quântic", "relativid"]), ("mecânica", ["velocidade", "newton", "força", "movimento"])]
    for nome, palavras in temas:
        if any(pal in p for pal in palavras): return nome
    return "física"

MDR_OPTIONS = {"📘 Teoria": "1", "✏️ Resolução": "2", "💡 Macetes": "3", "🎯 Simulado": "4", "📋 Resumão": "5", "🧭 Me Guie": "6"}
MDR_INFO = {"1": {"nome": "Teoria", "icone": "📘", "descricao": "Explicação."}, "2": {"nome": "Resolução", "icone": "✏️", "descricao": "Passo a passo."}, "3": {"nome": "Macetes", "icone": "💡", "descricao": "Bizus."}, "4": {"nome": "Simulado", "icone": "🎯", "descricao": "Exercício."}, "5": {"nome": "Resumão", "icone": "📋", "descricao": "Fórmulas."}, "6": {"nome": "Me Guie", "icone": "🧭", "descricao": "Diagnóstico."}}

PERFIS_DARK = {
    "Azul-noite": {"BG": "#0e1117", "CARD": "#1c2128", "INPUT_BG": "#21262d", "TXT": "#e6edf3", "TXT2": "#8b949e", "BORDER": "#30363d", "TABLE_HEADER_BG": "#21262d", "SIM_CARD": "#1a2d3d", "SIM_BORDER": "#2a5a7a", "TOOLTIP_BG": "#1e3a5f", "TOOLTIP_BORDER": "#4a7ab5", "ACCENT": "#0077ff", "ACCENT_DARK": "#005fcc"},
    "Neutro": {"BG": "#0d0d0d", "CARD": "#1a1a1a", "INPUT_BG": "#1f1f1f", "TXT": "#ededed", "TXT2": "#909090", "BORDER": "#2f2f2f", "TABLE_HEADER_BG": "#1f1f1f", "SIM_CARD": "#222222", "SIM_BORDER": "#444444", "TOOLTIP_BG": "#2e2e2e", "TOOLTIP_BORDER": "#5a5a5a", "ACCENT": "#888888", "ACCENT_DARK": "#555555"},
    "Ameixa": {"BG": "#140e1c", "CARD": "#211a2d", "INPUT_BG": "#2a2138", "TXT": "#ece4f3", "TXT2": "#9588a5", "BORDER": "#3a2e4a", "TABLE_HEADER_BG": "#2a2138", "SIM_CARD": "#2b1f3d", "SIM_BORDER": "#5a3f7a", "TOOLTIP_BG": "#5a1a6b", "TOOLTIP_BORDER": "#9a4ab5", "ACCENT": "#9a4ab5", "ACCENT_DARK": "#5a1a6b"},
}
PERFIS_LIGHT = {
    "Papel": {"BG": "#faf8f4", "CARD": "#f2ede4", "INPUT_BG": "#ffffff", "TXT": "#2b2621", "TXT2": "#6b6157", "BORDER": "#e0d8ca", "TABLE_HEADER_BG": "#ede6da", "SIM_CARD": "#f5efe4", "SIM_BORDER": "#c8b898", "TOOLTIP_BG": "#6b4a1e", "TOOLTIP_BORDER": "#9a7a3a", "ACCENT": "#9a7a3a", "ACCENT_DARK": "#6b4a1e"},
    "Gelo": {"BG": "#f6fafd", "CARD": "#eaf2f9", "INPUT_BG": "#ffffff", "TXT": "#182530", "TXT2": "#5a6c7a", "BORDER": "#d4e2ed", "TABLE_HEADER_BG": "#e3edf5", "SIM_CARD": "#eef6fc", "SIM_BORDER": "#a8c8e0", "TOOLTIP_BG": "#0f2a4a", "TOOLTIP_BORDER": "#3a6a9a", "ACCENT": "#3a6a9a", "ACCENT_DARK": "#0f2a4a"},
    "Areia": {"BG": "#fdfbf6", "CARD": "#f6efe2", "INPUT_BG": "#ffffff", "TXT": "#332b1c", "TXT2": "#736648", "BORDER": "#e5d9bf", "TABLE_HEADER_BG": "#f0e6d2", "SIM_CARD": "#f9f2e2", "SIM_BORDER": "#d4b980", "TOOLTIP_BG": "#8a6a10", "TOOLTIP_BORDER": "#c0a040", "ACCENT": "#c0a040", "ACCENT_DARK": "#8a6a10"},
}

def _hex_para_rgb(hex_cor: str) -> str:
    h = hex_cor.lstrip('#'); return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"

if st.session_state.dark_mode:
    _perfis_ativos = PERFIS_DARK
    _perfil_atual = st.session_state.fis_perfil_cor_dark
    if _perfil_atual not in _perfis_ativos:
        _perfil_atual = "Azul-noite"; st.session_state.fis_perfil_cor_dark = _perfil_atual
else:
    _perfis_ativos = PERFIS_LIGHT
    _perfil_atual = st.session_state.fis_perfil_cor_light
    if _perfil_atual not in _perfis_ativos:
        _perfil_atual = "Papel"; st.session_state.fis_perfil_cor_light = _perfil_atual

_paleta = _perfis_ativos[_perfil_atual]
BG, CARD, INPUT_BG, TXT, TXT2, BORDER = _paleta["BG"], _paleta["CARD"], _paleta["INPUT_BG"], _paleta["TXT"], _paleta["TXT2"], _paleta["BORDER"]
TABLE_HEADER_BG, SIM_CARD, SIM_BORDER = _paleta["TABLE_HEADER_BG"], _paleta["SIM_CARD"], _paleta["SIM_BORDER"]
TOOLTIP_BG, TOOLTIP_BORDER, ACCENT, ACCENT_DARK = _paleta["TOOLTIP_BG"], _paleta["TOOLTIP_BORDER"], _paleta["ACCENT"], _paleta["ACCENT_DARK"]
ACCENT_RGB = _hex_para_rgb(ACCENT); FS = st.session_state.font_size

st.markdown(f"""
<style>
    :root {{ --pm-tooltip-bg: {TOOLTIP_BG}; --pm-tooltip-border: {TOOLTIP_BORDER}; --pm-accent: {ACCENT}; --pm-accent-dark: {ACCENT_DARK}; --background-color: {BG}; --secondary-background-color: {CARD}; --text-color: {TXT}; --primary-color: {ACCENT}; }}
    .stApp {{ background-color: {BG} !important; color: {TXT} !important; }}
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{ background-color: {CARD} !important; border: 1px solid {BORDER} !important; border-radius: 18px !important; padding: 10px 16px !important; margin-left: auto !important; margin-right: 0 !important; max-width: 80% !important; width: fit-content !important; align-self: flex-end !important; }}
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{ background-color: transparent !important; border: none !important; }}
    .stApp p, .stApp span, .stApp div, .stApp li, .stApp h1, .stApp h2, .stApp h3, .stApp label, .stApp strong, .stApp td, .stApp th {{ color: {TXT} !important; font-size: {FS}px !important; }}
    .stButton > button[kind="primary"] {{ background: linear-gradient(135deg, {ACCENT_DARK} 0%, {ACCENT} 100%) !important; color: #ffffff !important; border: none !important; font-weight: 700 !important; }}
    [data-testid="stRadioGroup"] label {{ padding: 6px 12px !important; border-radius: 18px !important; font-size: 12px !important; border: 1px solid {BORDER} !important; color: {TXT2} !important; }}
    [data-testid="stRadioGroup"] label:has(input:checked) {{ background: {ACCENT} !important; border-color: {ACCENT} !important; color: #ffffff !important; }}
    .sim-card {{ background-color: {SIM_CARD}; border: 1px solid {SIM_BORDER}; border-radius: 10px; padding: 10px 12px; margin-bottom: 10px; }}
    .sim-card .sim-titulo {{ font-weight: 700; font-size: 13px; color: {TXT}; }}
    .sim-card .sim-desc {{ font-size: 12px; color: {TXT2}; }}
</style>
""", unsafe_allow_html=True)

st.title("⚛️ Prof. Max")
st.caption("Física para o ENEM")

def log_progress(msg): st.session_state.fis_progress_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
def log_error(msg): st.session_state.fis_error_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

_SUP = {'0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹','-':'⁻','+':'⁺','n':'ⁿ','i':'ⁱ'}
_SUB = {'0':'₀','1':'₁','2':'₂','3':'₃','4':'₄','5':'₅','6':'₆','7':'₇','8':'₈','9':'₉','-':'₋','+':'₊','a':'ₐ','e':'ₑ','o':'ₒ','x':'ₓ','i':'ᵢ','j':'ⱼ','n':'ₙ'}
_SIMBOLOS = {'\\pi': 'π', '\\alpha': 'α', '\\beta': 'β', '\\gamma': 'γ', '\\Delta': 'Δ', '\\theta': 'θ', '\\lambda': 'λ', '\\mu': 'μ', '\\rho': 'ρ', '\\sigma': 'σ', '\\phi': 'φ', '\\omega': 'ω', '\\cdot': '·', '\\times': '×', '\\div': '÷', '\\pm': '±', '\\rightarrow': '→', '\\Rightarrow': '⇒', '\\neq': '≠', '\\leq': '≤', '\\geq': '≥', '\\approx': '≈', '\\infty': '∞', '\\partial': '∂', '\\int': '∫', '\\sum': '∑', '\\sqrt': '√'}

def _sup_unicode(exp): return ''.join(_SUP.get(c, c) for c in exp)
def _sub_unicode(exp): return ''.join(_SUB.get(c, c) for c in exp)

def latex_to_unicode(text: str) -> str:
    if not text: return ""
    text = re.sub(r'\\\(|\\\)', '', text); text = re.sub(r'\\\[|\\\]', '', text)
    for k in sorted(_SIMBOLOS.keys(), key=len, reverse=True): text = text.replace(k, _SIMBOLOS[k])
    text = re.sub(r'\\text\{([^}]*)\}', r'\1', text); text = re.sub(r'\\frac\{([^{}]*)\}\{([^{}]*)\}', r'(\1)/(\2)', text)
    text = re.sub(r'\\sqrt\{([^}]*)\}', r'√(\1)', text); text = re.sub(r'\^\{([^}]+)\}', lambda m: _sup_unicode(m.group(1)), text)
    text = re.sub(r'_\{([^}]+)\}', lambda m: _sub_unicode(m.group(1)), text); return text

def _html_table_to_markdown(table_html: str) -> str:
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, flags=re.I | re.S); md_rows = []
    for row in rows:
        cells = re.findall(r'<(?:th|td)[^>]*>(.*?)</(?:th|td)>', row, flags=re.I | re.S); cleaned = []
        for c in cells:
            c = re.sub(r'<br\s*/?>', ' ', c, flags=re.I); c = re.sub(r'<[^>]+>', '', c); c = html_lib.unescape(c)
            c = re.sub(r'\\\((.*?)\\\)', r'$\1$', c, flags=re.DOTALL); c = c.replace('\n', ' ').replace('|', '\\|'); cleaned.append(c.strip())
        if all(re.match(r'^:?-{2,}:?$', x) for x in cleaned if x): continue
        if cleaned: md_rows.append(cleaned)
    if not md_rows: return ''
    n_cols = max(len(r) for r in md_rows)
    for r in md_rows:
        while len(r) < n_cols: r.append('')
    linhas = ['| ' + ' | '.join(md_rows[0]) + ' |', '| ' + ' | '.join(['---'] * n_cols) + ' |']
    for r in md_rows[1:]: linhas.append('| ' + ' | '.join(r) + ' |')
    return '\n\n' + '\n'.join(linhas) + '\n\n'

def html_to_markdown(html_text: str) -> str:
    if not html_text: return ""
    t = html_text; t = re.sub(r'<table[^>]*>.*?</table>', lambda m: _html_table_to_markdown(m.group(0)), t, flags=re.I | re.S)
    t = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', t, flags=re.DOTALL); t = re.sub(r'\\\((.*?)\\\)', r'$\1$', t, flags=re.DOTALL)
    t = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n# \1\n', t, flags=re.I | re.S); t = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', t, flags=re.I | re.S); t = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', t, flags=re.I | re.S)
    t = re.sub(r'<(strong|b)[^>]*>(.*?)</\1>', r'**\2**', t, flags=re.I | re.S); t = re.sub(r'<(em|i)[^>]*>(.*?)</\1>', r'*\2*', t, flags=re.I | re.S)
    t = re.sub(r'<li[^>]*>(.*?)</li>', r'\n- \1', t, flags=re.I | re.S); t = re.sub(r'</?(ul|ol)[^>]*>', '', t, flags=re.I); t = re.sub(r'<br\s*/?>', '\n', t, flags=re.I); t = re.sub(r'</?p[^>]*>', '\n', t, flags=re.I)
    t = re.sub(r'<[^>]+>', '', t); t = html_lib.unescape(t); t = re.sub(r'\n{3,}', '\n\n', t); return t.strip()

def html_to_clean_text(html_text: str) -> str:
    if not html_text: return ""
    t = html_lib.unescape(html_text); t = re.sub(r'\\\((.*?)\\\)', lambda m: latex_to_unicode(m.group(1)), t, flags=re.DOTALL)
    t = re.sub(r'\\\[(.*?)\\\]', lambda m: '\n' + latex_to_unicode(m.group(1)) + '\n', t, flags=re.DOTALL); t = re.sub(r'<br\s*/?>', '\n', t, flags=re.I)
    t = re.sub(r'<hr\s*/?>', '\n' + '─'*40 + '\n', t, flags=re.I); t = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n══════ \1 ══════\n', t, flags=re.I|re.S)
    t = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n──── \1 ────\n', t, flags=re.I|re.S); t = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n▸ \1\n', t, flags=re.I|re.S)
    t = re.sub(r'<li[^>]*>(.*?)</li>', r'\n  • \1', t, flags=re.I|re.S); t = re.sub(r'</?(ul|ol|strong|b|em|i)>', '', t, flags=re.I)
    def _clean_table(m):
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', m.group(0), flags=re.I | re.S); lines = []
        for row in rows:
            cells = re.findall(r'<(?:th|td)[^>]*>(.*?)</(?:th|td)>', row, flags=re.I | re.S); cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
            if all(re.match(r'^:?-{2,}:?$', c) for c in cells if c): continue
            if cells: lines.append(' | '.join(cells))
        return '\n' + '\n'.join(lines) + '\n'
    t = re.sub(r'<table[^>]*>.*?</table>', _clean_table, t, flags=re.I | re.S); t = re.sub(r'<[^>]+>', '', t); return re.sub(r'\n{3,}', '\n\n', t).strip()

def html_to_word_html(html_text: str) -> str:
    if not html_text: return ""
    t = html_lib.unescape(html_text); t = re.sub(r'\\\((.*?)\\\)', lambda m: latex_to_unicode(m.group(1)), t, flags=re.DOTALL)
    t = re.sub(r'\\\[(.*?)\\\]', lambda m: '<div style="margin:8px 0;font-style:italic;">' + latex_to_unicode(m.group(1)) + '</div>', t, flags=re.DOTALL); t = re.sub(r'<br\s*/?>', '<br>', t, flags=re.I)
    return t

def exportar_chat_word():
    if not st.session_state.fis_messages: return ""
    blocos = [f'<h1 style="font-family:Arial,sans-serif;color:{ACCENT_DARK};">⚛️ Prof. Max – Histórico da Conversa</h1>', f'<p style="font-family:Arial,sans-serif;color:#666;">Exportado em {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>', '<hr>']
    for m in st.session_state.fis_messages:
        role = "👤 Usuário" if m["role"] == "user" else "⚛️ Prof. Max"
        conteudo = m["content"]
        if m["role"] == "assistant": conteudo = html_to_word_html(conteudo)
        else: conteudo = html_lib.escape(conteudo).replace("\n", "<br>")
        blocos.append(f'<h3 style="font-family:Arial,sans-serif;color:{ACCENT};border-bottom:1px solid #ddd;padding-bottom:4px;margin-top:20px;">{role}</h3><div style="font-family:Arial,sans-serif;line-height:1.6;">{conteudo}</div>')
    return "\n".join(blocos)

def exportar_chat_docs():
    if not st.session_state.fis_messages: return ""
    blocos = ["══════════════════════════════════════════", "⚛️ Prof. Max – Histórico da Conversa", f"Exportado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", "══════════════════════════════════════════", ""]
    separador = "\n\n" + ("─" * 40) + "\n\n"
    for m in st.session_state.fis_messages:
        role = "👤 Usuário" if m["role"] == "user" else "⚛️ Prof. Max"
        conteudo = m["content"]
        if m["role"] == "assistant": conteudo = html_to_clean_text(conteudo)
        blocos.extend([f"▸ {role}", "", conteudo.strip(), separador])
    return "\n".join(blocos)

def _render_iframe(html: str, height: int = 55):
    try: st.iframe(html, height=height); return
    except Exception: pass
    import streamlit.components.v1 as components
    components.html(html, height=height)

def _render_two_copy_buttons(word_html, plain_text, key_prefix):
    j_word_html = json.dumps(word_html or "", ensure_ascii=False); j_plain = json.dumps(plain_text or "", ensure_ascii=False)
    html = f"""
    <div style="display:flex; gap:8px; font-family:Arial,sans-serif;">
        <button id="{key_prefix}_bw" style="flex:1; padding:8px 12px; background:#2ecc71; color:#fff; border:none; border-radius:6px; font-size:13px; font-weight:600; cursor:pointer;">📋 Word</button>
        <button id="{key_prefix}_bd" style="flex:1; padding:8px 12px; background:#4285f4; color:#fff; border:none; border-radius:6px; font-size:13px; font-weight:600; cursor:pointer;">📋 Google Docs</button>
    </div>
    <script>
        (function() {{
            const data = {{ bw: {{ html: {j_word_html}, text: {j_plain} }}, bd: {{ html: {j_word_html}, text: {j_plain} }} }};
            const labels = {{ bw: '📋 Word', bd: '📋 Google Docs' }};
            function setClipboardRich(htmlText, plainText) {{
                if (navigator.clipboard && window.ClipboardItem) {{
                    try {{ return navigator.clipboard.write([new ClipboardItem({{'text/html': new Blob([htmlText || plainText], {{type: 'text/html'}}), 'text/plain': new Blob([plainText || htmlText], {{type: 'text/plain'}})}})]); }} catch(e) {{}}
                }}
                return navigator.clipboard.writeText(plainText || htmlText);
            }}
            ['bw','bd'].forEach(id => {{
                const btn = document.getElementById('{key_prefix}_' + id);
                if (!btn) return;
                btn.addEventListener('click', function() {{
                    const d = data[id];
                    if (!d.text && !d.html) {{ btn.textContent='⚠️ Vazio'; setTimeout(()=>btn.textContent=labels[id],2000); return; }}
                    setClipboardRich(d.html, d.text).then(() => {{ btn.textContent='✅ Copiado!'; setTimeout(()=>btn.textContent=labels[id],2000); }}).catch(err => {{
                        const ta = document.createElement('textarea'); ta.value = d.text || d.html; ta.style.position='fixed'; ta.style.opacity='0'; document.body.appendChild(ta); ta.select(); try {{ document.execCommand('copy'); }} catch(e) {{}} document.body.removeChild(ta); btn.textContent='✅ Copiado!'; setTimeout(()=>btn.textContent=labels[id],2000);
                    }});
                }});
            }});
        }})();
    </script>
    """
    _render_iframe(html, height=55)

def render_copy_buttons_response():
    word_html = html_to_word_html(st.session_state.fis_last_response_html) if st.session_state.fis_last_response_html else ""
    plain_text = html_to_clean_text(st.session_state.fis_last_response_html) if st.session_state.fis_last_response_html else ""
    _render_two_copy_buttons(word_html, plain_text, "last_fis")

def render_copy_buttons_chat_full():
    if not st.session_state.fis_messages: st.caption("Nenhuma mensagem para exportar."); return
    _render_two_copy_buttons(exportar_chat_word(), exportar_chat_docs(), "chat_fis")

def renderizar_simulacoes_painel(simulacoes):
    if not simulacoes: st.markdown('<div class="sim-vazio" style="text-align:center;color:#888;">Nenhuma simulação sugerida.</div>', unsafe_allow_html=True); return
    for idx, s in enumerate(simulacoes, 1):
        st.markdown(f'<div class="sim-card"><div class="sim-titulo">{idx}. {s.get("titulo", "")}</div><div class="sim-desc">{s.get("descricao", "")}</div><div class="sim-link" style="font-size:11px;"><a href="{s.get("link", "#")}" target="_blank" style="color:{ACCENT};">🔗 Acessar</a></div></div>', unsafe_allow_html=True)

def _executar_reset():
    try: requests.post(CLEAR_URL, json={"sessionId": session_id_fis}, timeout=(5, 15), headers={"Content-Type": "application/json"})
    except Exception: pass
    st.session_state.fis_messages = []; st.session_state.fis_error_log = []; st.session_state.fis_progress_log = []
    st.session_state.fis_last_response_html = ""; st.session_state.fis_last_simulacoes = []; st.session_state.fis_confirmar_reset = False

with st.sidebar:
    st.markdown("### 🔬 Simulações")
    with st.container(height=200, border=True): renderizar_simulacoes_painel(st.session_state.fis_last_simulacoes)
    st.divider()
    
    st.markdown("### ⚙️ Aparência")
    new_dark = st.toggle("🌙 Modo Escuro", value=st.session_state.dark_mode, key="tgl_dark_fis")
    if new_dark != st.session_state.dark_mode: st.session_state.dark_mode = new_dark; st.rerun()

    st.markdown("**🎨 Perfil de cor**")
    if st.session_state.dark_mode: perfis = list(PERFIS_DARK.keys()); chave = "fis_perfil_cor_dark"
    else: perfis = list(PERFIS_LIGHT.keys()); chave = "fis_perfil_cor_light"

    perfil_atual = st.session_state[chave]
    perfil_sel = st.radio("Perfil", options=perfis, index=perfis.index(perfil_atual), horizontal=True, label_visibility="collapsed", key=f"radio_fis_{'dark' if st.session_state.dark_mode else 'light'}")
    if perfil_sel != perfil_atual: st.session_state[chave] = perfil_sel; st.rerun()

    st.markdown("**📖 Tamanho da fonte**")
    fc1, fc2, fc3 = st.columns([1,1,1])
    with fc1:
        if st.button("A-", key="f_dec_fis", use_container_width=True): st.session_state.font_size = max(12, st.session_state.font_size - 1); st.rerun()
    with fc2: st.markdown(f"<div style='text-align:center;padding-top:8px;'>{st.session_state.font_size}px</div>", unsafe_allow_html=True)
    with fc3:
        if st.button("A+", key="f_inc_fis", use_container_width=True): st.session_state.font_size = min(24, st.session_state.font_size + 1); st.rerun()
    st.divider()

    with st.expander("❓ O que é MDR?"):
        for k in ["1", "2", "3", "4", "5", "6"]: st.markdown(f"**{MDR_INFO[k]['icone']} {MDR_INFO[k]['nome']}**"); st.caption(MDR_INFO[k]['descricao'])
    st.divider()
    
    st.markdown("### 🗑️ Zona de perigo")
    if not st.session_state.get("fis_confirmar_reset", False):
        if st.button("🔄 Resetar Conversa", use_container_width=True): st.session_state.fis_confirmar_reset = True; st.rerun()
    else:
        st.warning("Tem certeza?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sim", type="primary", use_container_width=True): _executar_reset(); st.rerun()
        with c2:
            if st.button("Não", use_container_width=True): st.session_state.fis_confirmar_reset = False; st.rerun()

for msg in st.session_state.fis_messages:
    with st.chat_message(msg["role"]): st.markdown(html_to_markdown(msg["content"]) if msg["role"] == "assistant" else msg["content"])

if st.session_state.fis_last_response_html:
    with st.expander("📋 Copiar última resposta", expanded=True): render_copy_buttons_response()
if st.session_state.fis_messages:
    with st.expander("📚 Exportar conversa completa", expanded=False): render_copy_buttons_chat_full()

st.markdown("##### 📋 Modalidade de Resposta")
formato_label = st.radio("Formato", options=list(MDR_OPTIONS.keys()), index=int(st.session_state.fis_formato_num) - 1, horizontal=True, label_visibility="collapsed", key="fis_mdr_radio")
if formato_label:
    try: st.session_state.fis_formato_num = MDR_OPTIONS[formato_label]
    except (KeyError, TypeError): pass

prompt = st.chat_input("Digite sua pergunta de Física...")

if prompt and prompt.strip():
    pergunta = prompt.strip()
    st.session_state.fis_messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"): st.markdown(pergunta)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown(f'<div style="color:{TXT2};"><i>Prof. Max está analisando…</i></div>', unsafe_allow_html=True)
        try:
            payload = {"message": pergunta, "formato": st.session_state.fis_formato_num, "sessionId": session_id_fis}
            response = requests.post(WEBHOOK_URL, json=payload, timeout=(10, 120), headers={"Content-Type": "application/json"})
            placeholder.empty()
            if response.status_code == 200:
                data = response.json()
                resposta = data.get("formattedResponse") or data.get("message") or "Desculpe."
                st.session_state.fis_last_response_html = resposta
                st.markdown(html_to_markdown(resposta))
                st.session_state.fis_messages.append({"role": "assistant", "content": resposta})
                simulacoes = data.get("simulacoes")
                if simulacoes:
                    if isinstance(simulacoes, str):
                        try: simulacoes = json.loads(simulacoes)
                        except Exception: simulacoes = []
                    st.session_state.fis_last_simulacoes = simulacoes if isinstance(simulacoes, list) else []
                else: st.session_state.fis_last_simulacoes = []
            else: st.error(f"Erro HTTP {response.status_code}")
        except Exception as e: placeholder.empty(); st.error(f"❌ {str(e)}")
    st.rerun()