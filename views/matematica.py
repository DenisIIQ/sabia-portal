# (versão 3.0 – Prof.ª Pati / Portal SABIÁ)
# Novidade: Bloqueio da barra lateral durante o processamento da resposta.

import streamlit as st
import requests
import json
import re
import time
import html as html_lib
from datetime import datetime
from st_supabase_connection import SupabaseConnection

def _get_secret(chave: str, padrao: str = "") -> str:
    try: return st.secrets[chave]
    except Exception: return padrao

WEBHOOK_URL = _get_secret("WEBHOOK_URL", "http://167.126.1.122.nip.io:5678/webhook/prof-pati-mat")
db_aluno_id = st.session_state.session_id
n8n_session_id = f"{db_aluno_id}_mat"

defaults = {
    "mat_messages": [], "mat_error_log": [], "mat_progress_log": [],
    "mat_last_response_html": "", "mat_formato_num": "1",
    "mat_last_simulacoes": [], "mat_confirmar_reset": False,
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

global_defaults = {
    "font_size": 16, "dark_mode": True,
    "mat_perfil_cor_dark": "Vinho", "mat_perfil_cor_light": "Pergaminho",
}
for k, v in global_defaults.items():
    if k not in st.session_state: st.session_state[k] = v

if st.session_state.get("mat_loaded_for_user") != db_aluno_id:
    st.session_state["mat_loaded_for_user"] = db_aluno_id
    st.session_state.mat_messages = []
    try:
        conn = st.connection("supabase", type=SupabaseConnection)
        res = conn.session_client().table("interacoes").select("pergunta, resposta").eq("aluno_id", db_aluno_id).eq("disciplina", "matematica").order("timestamp", desc=False).limit(30).execute()
        if res.data:
            for row in res.data:
                st.session_state.mat_messages.append({"role": "user", "content": row["pergunta"]})
                if row.get("resposta"):
                    st.session_state.mat_messages.append({"role": "assistant", "content": row["resposta"]})
    except Exception as e:
        st.error(f"Erro ao carregar histórico: {e}")

def _detectar_tema(pergunta: str) -> str:
    p = (pergunta or "").lower()
    temas = [("trigonometria", ["seno", "cosseno", "tangente"]), ("geometria", ["prisma", "triângulo", "área", "pitágoras"]), ("probabilidade", ["probabilidade", "combinação"]), ("estatística", ["média", "mediana"]), ("matemática financeira", ["juros", "montante"]), ("funções", ["função", "quadrática"]), ("álgebra", ["equação", "polinômio"]), ("aritmética", ["soma", "fração"])]
    for nome, palavras in temas:
        if any(pal in p for pal in palavras): return nome
    return "matemática"

MDR_OPTIONS = {"📘 Teoria": "1", "✏️ Resolução": "2", "💡 Macetes": "3", "🎯 Simulado": "4", "📋 Resumão": "5", "🧭 Me Guie": "6"}
MDR_INFO = {"1": {"nome": "Teoria", "icone": "📘", "descricao": "Explicação."}, "2": {"nome": "Resolução", "icone": "✏️", "descricao": "Passo a passo."}, "3": {"nome": "Macetes", "icone": "💡", "descricao": "Bizus."}, "4": {"nome": "Simulado", "icone": "🎯", "descricao": "Exercício."}, "5": {"nome": "Resumão", "icone": "📋", "descricao": "Fórmulas."}, "6": {"nome": "Me Guie", "icone": "🧭", "descricao": "Diagnóstico."}}

PERFIS_DARK = {
    "Vinho": {"BG": "#1a0d10", "CARD": "#2a171c", "INPUT_BG": "#331e24", "TXT": "#f5eaec", "TXT2": "#a58990", "BORDER": "#4a2a33", "TABLE_HEADER_BG": "#331e24", "SIM_CARD": "#2a1a22", "SIM_BORDER": "#6a3a4a", "TOOLTIP_BG": "#6a1a3a", "TOOLTIP_BORDER": "#a84a6a", "ACCENT": "#a84a6a", "ACCENT_DARK": "#6a1a3a"},
    "Esmeralda": {"BG": "#0a1410", "CARD": "#142220", "INPUT_BG": "#1a2a25", "TXT": "#e8f5ef", "TXT2": "#86a89a", "BORDER": "#2a4a3d", "TABLE_HEADER_BG": "#1a2a25", "SIM_CARD": "#152420", "SIM_BORDER": "#3a6a55", "TOOLTIP_BG": "#1a5a3a", "TOOLTIP_BORDER": "#4a9a6a", "ACCENT": "#4a9a6a", "ACCENT_DARK": "#1a5a3a"},
    "Grafite": {"BG": "#141414", "CARD": "#1e1e1e", "INPUT_BG": "#252525", "TXT": "#f0f0f0", "TXT2": "#9a9a9a", "BORDER": "#333333", "TABLE_HEADER_BG": "#252525", "SIM_CARD": "#1f1f1f", "SIM_BORDER": "#4a4a4a", "TOOLTIP_BG": "#3a3a3a", "TOOLTIP_BORDER": "#6a6a6a", "ACCENT": "#8a8a8a", "ACCENT_DARK": "#4a4a4a"},
}
PERFIS_LIGHT = {
    "Pergaminho": {"BG": "#faf6ed", "CARD": "#f2e9d5", "INPUT_BG": "#ffffff", "TXT": "#2b2418", "TXT2": "#6b5f4a", "BORDER": "#d9cdb0", "TABLE_HEADER_BG": "#ede0c5", "SIM_CARD": "#f5ead0", "SIM_BORDER": "#c0a880", "TOOLTIP_BG": "#6b4a1e", "TOOLTIP_BORDER": "#9a7a3a", "ACCENT": "#9a7a3a", "ACCENT_DARK": "#6b4a1e"},
    "Menta": {"BG": "#f2faf6", "CARD": "#e3f2eb", "INPUT_BG": "#ffffff", "TXT": "#12281f", "TXT2": "#4e7263", "BORDER": "#c0d9cc", "TABLE_HEADER_BG": "#d5e9dd", "SIM_CARD": "#e8f5ef", "SIM_BORDER": "#90c8a8", "TOOLTIP_BG": "#1a4a35", "TOOLTIP_BORDER": "#3a7a5a", "ACCENT": "#3a7a5a", "ACCENT_DARK": "#1a4a35"},
    "Lavanda": {"BG": "#f8f4fb", "CARD": "#ede4f5", "INPUT_BG": "#ffffff", "TXT": "#2a1f38", "TXT2": "#6a5878", "BORDER": "#d5c4e5", "TABLE_HEADER_BG": "#e0d0ee", "SIM_CARD": "#f0e8f7", "SIM_BORDER": "#a88ac0", "TOOLTIP_BG": "#4a2a6a", "TOOLTIP_BORDER": "#7a5a9a", "ACCENT": "#7a5a9a", "ACCENT_DARK": "#4a2a6a"},
}

def _hex_para_rgb(hex_cor: str) -> str:
    h = hex_cor.lstrip('#'); return f"{int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)}"

if st.session_state.dark_mode:
    _perfis_ativos = PERFIS_DARK
    _perfil_atual = st.session_state.mat_perfil_cor_dark
    if _perfil_atual not in _perfis_ativos:
        _perfil_atual = "Vinho"; st.session_state.mat_perfil_cor_dark = _perfil_atual
else:
    _perfis_ativos = PERFIS_LIGHT
    _perfil_atual = st.session_state.mat_perfil_cor_light
    if _perfil_atual not in _perfis_ativos:
        _perfil_atual = "Pergaminho"; st.session_state.mat_perfil_cor_light = _perfil_atual

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

st.title("📐 Prof.ª Pati")
st.caption("Matemática para o ENEM")

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
    if not st.session_state.mat_messages: return ""
    blocos = [f'<h1 style="font-family:Arial,sans-serif;color:{ACCENT_DARK};">📐 Prof.ª Pati – Histórico da Conversa</h1>', f'<p style="font-family:Arial,sans-serif;color:#666;">Exportado em {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>', '<hr>']
    for m in st.session_state.mat_messages:
        role = "👤 Usuário" if m["role"] == "user" else "📐 Prof.ª Pati"
        conteudo = m["content"]
        if m["role"] == "assistant": conteudo = html_to_word_html(conteudo)
        else: conteudo = html_lib.escape(conteudo).replace("\n", "<br>")
        blocos.append(f'<h3 style="font-family:Arial,sans-serif;color:{ACCENT};border-bottom:1px solid #ddd;padding-bottom:4px;margin-top:20px;">{role}</h3><div style="font-family:Arial,sans-serif;line-height:1.6;">{conteudo}</div>')
    return "\n".join(blocos)

def exportar_chat_docs():
    if not st.session_state.mat_messages: return ""
    blocos = ["══════════════════════════════════════════", "📐 Prof.ª Pati – Histórico da Conversa", f"Exportado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", "══════════════════════════════════════════", ""]
    separador = "\n\n" + ("─" * 40) + "\n\n"
    for m in st.session_state.mat_messages:
        role = "👤 Usuário" if m["role"] == "user" else "📐 Prof.ª Pati"
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
    word_html = html_to_word_html(st.session_state.mat_last_response_html) if st.session_state.mat_last_response_html else ""
    plain_text = html_to_clean_text(st.session_state.mat_last_response_html) if st.session_state.mat_last_response_html else ""
    _render_two_copy_buttons(word_html, plain_text, "last_mat")

def render_copy_buttons_chat_full():
    if not st.session_state.mat_messages: st.caption("Nenhuma mensagem para exportar."); return
    _render_two_copy_buttons(exportar_chat_word(), exportar_chat_docs(), "chat_mat")

def renderizar_simulacoes_painel(simulacoes):
    if not simulacoes: st.markdown('<div class="sim-vazio" style="text-align:center;color:#888;">Nenhuma simulação sugerida.</div>', unsafe_allow_html=True); return
    for idx, s in enumerate(simulacoes, 1):
        st.markdown(f'<div class="sim-card"><div class="sim-titulo">{idx}. {s.get("titulo", "")}</div><div class="sim-desc">{s.get("descricao", "")}</div><div class="sim-link" style="font-size:11px;"><a href="{s.get("link", "#")}" target="_blank" style="color:{ACCENT};">🔗 Acessar</a></div></div>', unsafe_allow_html=True)

def _executar_reset():
    try:
        conn = st.connection("supabase", type=SupabaseConnection)
        conn.session_client().table("interacoes").delete().eq("aluno_id", db_aluno_id).eq("disciplina", "matematica").execute()
    except Exception: pass
    st.session_state.mat_messages = []; st.session_state.mat_error_log = []; st.session_state.mat_progress_log = []
    st.session_state.mat_last_response_html = ""; st.session_state.mat_last_simulacoes = []; st.session_state.mat_confirmar_reset = False

# ==========================================
# FUNÇÃO DE BLOQUEIO DA BARRA LATERAL
# ==========================================
def bloquear_barra_lateral(bloquear: bool):
    if bloquear:
        st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                pointer-events: none !important; /* Impede cliques */
                opacity: 0.6 !important;         /* Deixa transparente */
            }
        </style>
        """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🔬 Simulações")
    with st.container(height=200, border=True): renderizar_simulacoes_painel(st.session_state.mat_last_simulacoes)
    st.divider()
    
    st.markdown("### ⚙️ Aparência")
    new_dark = st.toggle("🌙 Modo Escuro", value=st.session_state.dark_mode, key="tgl_dark_mat")
    if new_dark != st.session_state.dark_mode: st.session_state.dark_mode = new_dark; st.rerun()

    st.markdown("**🎨 Perfil de cor**")
    if st.session_state.dark_mode: perfis = list(PERFIS_DARK.keys()); chave = "mat_perfil_cor_dark"
    else: perfis = list(PERFIS_LIGHT.keys()); chave = "mat_perfil_cor_light"

    perfil_atual = st.session_state[chave]
    perfil_sel = st.radio("Perfil", options=perfis, index=perfis.index(perfil_atual), horizontal=True, label_visibility="collapsed", key=f"radio_mat_{'dark' if st.session_state.dark_mode else 'light'}")
    if perfil_sel != perfil_atual: st.session_state[chave] = perfil_sel; st.rerun()

    st.markdown("**📖 Tamanho da fonte**")
    fc1, fc2, fc3 = st.columns([1,1,1])
    with fc1:
        if st.button("A-", key="f_dec_mat", use_container_width=True): st.session_state.font_size = max(12, st.session_state.font_size - 1); st.rerun()
    with fc2: st.markdown(f"<div style='text-align:center;padding-top:8px;'>{st.session_state.font_size}px</div>", unsafe_allow_html=True)
    with fc3:
        if st.button("A+", key="f_inc_mat", use_container_width=True): st.session_state.font_size = min(24, st.session_state.font_size + 1); st.rerun()
    st.divider()

    with st.expander("❓ O que é MDR?"):
        for k in ["1", "2", "3", "4", "5", "6"]: st.markdown(f"**{MDR_INFO[k]['icone']} {MDR_INFO[k]['nome']}**"); st.caption(MDR_INFO[k]['descricao'])
    st.divider()
    
    st.markdown("### 🗑️ Zona de perigo")
    if not st.session_state.get("mat_confirmar_reset", False):
        if st.button("🔄 Resetar Conversa", use_container_width=True): st.session_state.mat_confirmar_reset = True; st.rerun()
    else:
        st.warning("Tem certeza?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sim", type="primary", use_container_width=True): _executar_reset(); st.rerun()
        with c2:
            if st.button("Não", use_container_width=True): st.session_state.mat_confirmar_reset = False; st.rerun()

for msg in st.session_state.mat_messages:
    with st.chat_message(msg["role"]): st.markdown(html_to_markdown(msg["content"]) if msg["role"] == "assistant" else msg["content"])

if st.session_state.mat_last_response_html:
    with st.expander("📋 Copiar última resposta", expanded=True): render_copy_buttons_response()
if st.session_state.mat_messages:
    with st.expander("📚 Exportar conversa completa", expanded=False): render_copy_buttons_chat_full()

st.markdown("##### 📋 Modalidade de Resposta")
formato_label = st.radio("Formato", options=list(MDR_OPTIONS.keys()), index=int(st.session_state.mat_formato_num) - 1, horizontal=True, label_visibility="collapsed", key="mat_mdr_radio")
if formato_label:
    try: st.session_state.mat_formato_num = MDR_OPTIONS[formato_label]
    except (KeyError, TypeError): pass

prompt = st.chat_input("Digite sua pergunta de Matemática...")

if prompt and prompt.strip():
    pergunta = prompt.strip()
    st.session_state.mat_messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"): st.markdown(pergunta)

    # 1. CONGELA A BARRA LATERAL
    bloquear_barra_lateral(True)

    with st.chat_message("assistant"):
        tema_detectado = _detectar_tema(pergunta)
        placeholder = st.empty()
        placeholder.markdown(f'<div style="color:{TXT2};"><i>Prof.ª Pati está analisando…</i></div>', unsafe_allow_html=True)
        try:
            payload = {"message": pergunta, "formato": st.session_state.mat_formato_num, "sessionId": n8n_session_id}
            response = requests.post(WEBHOOK_URL, json=payload, timeout=(10, 120), headers={"Content-Type": "application/json"})
            placeholder.empty()
            
            if response.status_code == 200:
                data = response.json()
                resposta = data.get("formattedResponse") or data.get("message") or "Desculpe."
                st.session_state.mat_last_response_html = resposta
                st.markdown(html_to_markdown(resposta))
                st.session_state.mat_messages.append({"role": "assistant", "content": resposta})
                
                try:
                    conn = st.connection("supabase", type=SupabaseConnection)
                    conn.session_client().table("interacoes").insert({
                        "aluno_id": db_aluno_id,
                        "disciplina": "matematica",
                        "topico": tema_detectado,
                        "mdr": int(st.session_state.mat_formato_num),
                        "pergunta": pergunta,
                        "resposta": resposta
                    }).execute()
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")
                
                simulacoes = data.get("simulacoes")
                if simulacoes:
                    if isinstance(simulacoes, str):
                        try: simulacoes = json.loads(simulacoes)
                        except Exception: simulacoes = []
                    st.session_state.mat_last_simulacoes = simulacoes if isinstance(simulacoes, list) else []
                else: st.session_state.mat_last_simulacoes = []
            else: st.error(f"Erro HTTP {response.status_code}")
        except Exception as e: 
            placeholder.empty(); 
            st.error(f"❌ {str(e)}")

    # 2. DESCONGELA A BARRA LATERAL ANTES DE RECARREGAR
    bloquear_barra_lateral(False)
    st.rerun()