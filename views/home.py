import streamlit as st

st.title("🐦 Bem-vindo ao SABIÁ")
st.markdown("""
Este é o seu portal de estudos unificado. 
Escolha uma disciplina no menu lateral para começar.
""")

st.divider()

st.markdown("### 📚 Minhas Disciplinas")

# Alterado para 3 colunas para acomodar a nova disciplina
col1, col2, col3 = st.columns(3)

with col1:
    st.info("📐 **Matemática**\nProf.ª Pati (Hipátia de Alexandria)")
    
with col2:
    st.info("⚛️ **Física**\nProf. Max (James Clerk Maxwell)")

with col3:
    st.info("🧪 **Química**\nProf.ª Maria (Maria Salomea Skłodowska)")

st.caption("Novas disciplinas (como Biologia) estarão disponíveis em breve.")