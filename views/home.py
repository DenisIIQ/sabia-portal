import streamlit as st

st.title("🐦 Bem-vindo ao SABIÁ")
st.markdown("""
Este é o seu portal de estudos unificado. 
Escolha uma disciplina no menu lateral para começar.
""")

st.divider()

st.markdown("### 📚 Minhas Disciplinas")
col1, col2 = st.columns(2)

with col1:
    st.info("📐 **Matemática**\nProf.ª Pati (Hipátia de Alexandria)")
    
with col2:
    st.info("⚛️ **Física**\nProf. Max (James Clerk Maxwell)")

st.caption("Novas disciplinas (Química e Biologia) estarão disponíveis em breve.")