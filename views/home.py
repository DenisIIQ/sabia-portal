import streamlit as st

st.title("🐦 Bem-vindo ao SABIÁ")
st.markdown("""
Este é o seu portal de estudos unificado. 
Escolha uma disciplina no menu lateral para começar.
""")

st.divider()

st.markdown("### 📚 Minhas Disciplinas")

# 4 colunas para as 4 disciplinas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("📐 **Matemática**\nProf.ª Pati (Hipátia de Alexandria)")

with col2:
    st.info("⚛️ **Física**\nProf. Max (James Clerk Maxwell)")

with col3:
    st.info("🧪 **Química**\nProf.ª Maria (Maria Salomea Skłodowska)")

with col4:
    st.info("🧬 **Biologia**\nProf.ª Rosa (Rosalind Elsie Franklin)")

st.caption("Novas disciplinas estarão disponíveis em breve.")