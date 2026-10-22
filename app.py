# Versão 1.7 - Portal SABIÁ com Química integrada
import streamlit as st
from st_supabase_connection import SupabaseConnection
from streamlit_cookies_manager import EncryptedCookieManager

st.set_page_config(
    page_title="SABIÁ - Portal do Aluno",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

COOKIES_PASSWORD = "sabia_tutores_secret_key_2026_muito_longa_e_segura"
cookies = EncryptedCookieManager(prefix="sabia/", password=COOKIES_PASSWORD)

if not cookies.ready():
    st.stop()

try:
    conn = st.connection("supabase", type=SupabaseConnection)
except Exception as e:
    st.error(f"Erro crítico ao conectar ao banco de dados: {e}")
    st.stop()

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

bg = "#1e1e24" if st.session_state.dark_mode else "#f5f5f7"
card = "#2b2b36" if st.session_state.dark_mode else "#ffffff"
txt = "#e0e0e0" if st.session_state.dark_mode else "#1a1a1a"
border = "#444455" if st.session_state.dark_mode else "#d1d1d6"
accent = "#7a5a9a" if st.session_state.dark_mode else "#5a3a7a"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg} !important; color: {txt} !important; }}
    [data-testid="stSidebar"] {{ background-color: {card} !important; border-right: 1px solid {border} !important; }}
    [data-testid="stSidebar"] * {{ color: {txt} !important; }}
    .stApp p, .stApp span, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp label {{ color: {txt} !important; }}
    [data-testid="stForm"] {{ background-color: {card} !important; border: 1px solid {border} !important; border-radius: 12px; padding: 30px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); }}
    .stButton > button {{ background-color: {accent} !important; color: #ffffff !important; border: none !important; font-weight: 600 !important; border-radius: 8px !important; }}
    [data-testid="stSidebarNav"] {{ padding-top: 20px; }}
    [data-testid="stSidebarNav"] span {{ font-size: 16px !important; font-weight: 600 !important; }}
</style>
""", unsafe_allow_html=True)

# RECUPERAÇÃO DE SESSÃO
if "user" not in st.session_state:
    access_token = cookies.get("sb_access_token")
    refresh_token = cookies.get("sb_refresh_token")

    if access_token and refresh_token:
        try:
            session = conn.session_client().auth.set_session(access_token, refresh_token)
            if session and session.user:
                st.session_state["user"] = session.user
                st.rerun()
        except Exception:
            cookies["sb_access_token"] = ""
            cookies["sb_refresh_token"] = ""
            cookies.save()

# TELA DE LOGIN
if "user" not in st.session_state:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🐦 SABIÁ")
        st.markdown("Bem-vindo ao seu ambiente de estudos personalizado.")
        st.divider()

        with st.form("auth_form"):
            st.markdown("### Acesse sua conta")
            email = st.text_input("Email")
            password = st.text_input("Senha", type="password")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                btn_login = st.form_submit_button("Entrar", use_container_width=True)
            with col_btn2:
                btn_signup = st.form_submit_button("Criar Conta", use_container_width=True)

            if btn_login:
                try:
                    res = conn.session_client().auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state["user"] = res.user

                    cookies["sb_access_token"] = res.session.access_token
                    cookies["sb_refresh_token"] = res.session.refresh_token
                    cookies.save()

                    st.rerun()
                except Exception as e:
                    st.error(f"Falha no login: {e}")

            if btn_signup:
                try:
                    conn.session_client().auth.sign_up({"email": email, "password": password})
                    st.success("Conta criada! Clique em Entrar para acessar.")
                except Exception as e:
                    st.error(f"Falha ao criar conta: {e}")

    st.stop()

# APÓS O LOGIN
st.session_state.session_id = st.session_state["user"].id

with st.sidebar:
    st.markdown(f"👤 **{st.session_state['user'].email}**")
    st.caption(f"ID: {st.session_state.session_id[:8]}...")

    if st.button("Sair (Logout)", use_container_width=True):
        try:
            conn.session_client().auth.sign_out()
        except Exception:
            pass

        cookies["sb_access_token"] = ""
        cookies["sb_refresh_token"] = ""
        cookies.save()

        for key in ["mat_loaded_for_user", "fis_loaded_for_user", "qui_loaded_for_user"]:
            if key in st.session_state:
                del st.session_state[key]

        del st.session_state["user"]
        st.rerun()

    st.divider()

# ==========================================
# MENU DE NAVEGAÇÃO (Adição da Química)
# ==========================================
pg = st.navigation([
    st.Page("views/home.py", title="Início", icon="🏠", default=True),
    st.Page("views/matematica.py", title="Matemática", icon="📐"),
    st.Page("views/fisica.py", title="Física", icon="⚛️"),
    st.Page("views/quimica.py", title="Química", icon="🧪")
])

pg.run()