import streamlit as st
from st_supabase_connection import SupabaseConnection

# 1. Configuração da página principal
st.set_page_config(
    page_title="SABIÁ - Portal do Aluno",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inicializa a conexão com o Supabase
try:
    conn = st.connection("supabase", type=SupabaseConnection)
except Exception as e:
    st.error(f"Erro crítico ao conectar ao banco de dados: {e}")
    st.stop()

# 3. Define o tema base do Portal (Neutro)
# O Portal usa um tema neutro; as cores específicas são aplicadas por cada view (Pati/Max)
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

bg = "#1e1e24" if st.session_state.dark_mode else "#f5f5f7"
card = "#2b2b36" if st.session_state.dark_mode else "#ffffff"
txt = "#e0e0e0" if st.session_state.dark_mode else "#1a1a1a"
border = "#444455" if st.session_state.dark_mode else "#d1d1d6"
accent = "#7a5a9a" if st.session_state.dark_mode else "#5a3a7a"

st.markdown(f"""
<style>
    /* Tema neutro do Portal */
    .stApp {{ background-color: {bg} !important; color: {txt} !important; }}
    [data-testid="stSidebar"] {{ background-color: {card} !important; border-right: 1px solid {border} !important; }}
    [data-testid="stSidebar"] * {{ color: {txt} !important; }}
    .stApp p, .stApp span, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp label {{ color: {txt} !important; }}
    
    /* Estilo do Formulário de Login */
    [data-testid="stForm"] {{
        background-color: {card} !important;
        border: 1px solid {border} !important;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    }}
    .stButton > button {{
        background-color: {accent} !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }}
    
    /* Ajuste do menu de navegação lateral (st.navigation) */
    [data-testid="stSidebarNav"] {{ padding-top: 20px; }}
    [data-testid="stSidebarNav"] span {{ font-size: 16px !important; font-weight: 600 !important; }}
</style>
""", unsafe_allow_html=True)

# 4. Lógica de Autenticação
if "user" not in st.session_state:
    # Centraliza o formulário de login
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

# 5. Define o ID global do aluno
st.session_state.session_id = st.session_state["user"].id

# 6. Sidebar Global (Logout)
with st.sidebar:
    st.markdown(f"👤 **{st.session_state['user'].email}**")
    st.caption(f"ID: {st.session_state.session_id[:8]}...")
    
    if st.button("Sair (Logout)", use_container_width=True):
        conn.session_client().auth.sign_out()
        del st.session_state["user"]
        st.rerun()
        
    st.divider()

# 7. Configuração da Navegação Multipáginas
pg = st.navigation([
    st.Page("views/home.py", title="Início", icon="🏠", default=True),
    st.Page("views/matematica.py", title="Matemática", icon="📐"),
    st.Page("views/fisica.py", title="Física", icon="⚛️")
])

# Executa a página selecionada
pg.run()