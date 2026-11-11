import streamlit as st

st.title("🐦 Bem-vindo ao SABIÁ")
st.markdown("""
Este é o seu portal de estudos unificado. 
Escolha uma disciplina no menu lateral para começar a sua jornada rumo ao ENEM.
""")

st.divider()

st.markdown("### 📚 Minhas Disciplinas")

# 4 colunas para as disciplinas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("📐 **Matemática**\nProf.ª Pati (Hipátia de Alexandria)")
    
with col2:
    st.info("⚛️ **Física**\nProf. Max (James Clerk Maxwell)")

with col3:
    st.info("🧪 **Química**\nProf.ª Maria (Maria Salomea Skłodowska)")

with col4:
    st.info("🧬 **Biologia**\nProf.ª Rosa (Rosalind Elsie Franklin)")

st.divider()

# ==========================================
# MANUAIS EXPANSÍVEIS (Aluno e Professor)
# ==========================================

st.markdown("### 📖 Manuais e Orientações")

with st.expander("🎓 Desvende o SABIÁ: O seu quartel-general de estudos", expanded=False):
    st.markdown("""
Bem-vindo ao seu novo ecossistema de aprendizado! O SABIÁ não é apenas mais um site de perguntas e respostas. É o seu **quartel-general de estudos**, desenhado para ser o seu parceiro rumo à aprovação no ENEM. 

Aqui, você tem acesso a **quatro mentores de Inteligência Artificial**, cada um com uma persona única e especialista em uma área do conhecimento: 📐 Matemática, ⚛️ Física, 🧪 Química e 🧬 Biologia.

**Como funciona a mágica?**
Você não precisa aprender a usar um sistema complexo. Basta digitar sua dúvida e, antes de enviar, **escolher a sua estratégia de aprendizado** (as 6 MDRs). Você quer a explicação do zero? Um bizu para a prova? Ou prefere um exercício inédito que te desafie a resolver antes de ver a resposta? Você está no comando!

**Sua jornada é contínua:**
Pode fechar o navegador, trocar de computador ou continuar pelo celular na escola. O SABIÁ guarda o seu histórico em segurança total. Seu progresso nunca é perdido. Sinta-se livre para personalizar o ambiente (modo escuro, cores, tamanho da letra) e estude do seu jeito, no seu ritmo.

*Lembre-se: a IA é sua parceira de treino, não a sua muleta. Use os recursos de "Me Guie" e "Simulado" para forçar o seu cérebro a crescer, não apenas para copiar respostas.*
    """)

with st.expander("👩‍🏫 Sala dos Professores: O SABIÁ como seu assistente pedagógico", expanded=False):
    st.markdown("""
Prezado(a) educador(a), o SABIÁ foi arquitetado com um propósito claro: **devolver o seu tempo para o que realmente importa na sala de aula**. 

Sabemos que a maior parte da sua energia é consumida respondendo às mesmas dúvidas repetitivas. O SABIÁ atua como um **estagiário pedagógico incansável**, assumindo o atendimento individualizado e socrático de cada aluno, 24 horas por dia, 7 dias por semana. Enquanto a IA diagnostica a dificuldade do aluno e o guia passo a passo, você foca na intervenção humana, no acolhimento e nas discussões profundas.

**Como o SABIÁ ensina (e não apenas responde):**
O sistema não entrega respostas prontas. Ele opera no modelo socrático. No modo "Simulado", por exemplo, a IA apresenta o problema e espera a tentativa do aluno. Se ele errar, ela classifica a falha (conceitual, procedimental ou de desatenção) e corrige o ponto específico, ensinando a estratégia de resolução.

**O Futuro na palma da sua mão:**
Atualmente, cada interação do aluno já é registrada com segurança em nosso banco de dados (respeitando rigorosamente a LGPD). Em breve, o SABIÁ entregará a você um **Painel de Controle de Turma**. Imagine chegar na segunda-feira e saber que 70% da sua turma teve dificuldade específica em "Leis de Newton" durante o fim de semana. O SABIÁ municiará você com dados reais para planejar aulas cirúrgicas e focadas no gargalo verdadeiro da turma.

*Oriente seus alunos a explorarem as diferentes modalidades de resposta. O sucesso do SABIÁ depende de como o aluno o utiliza: como um treino, e não como uma cola.*
    """)