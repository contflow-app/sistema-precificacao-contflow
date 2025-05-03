
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Sistema de Precificação ContFlow", layout="wide")
st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        h1 { color: #2c3e50; }
    </style>
""", unsafe_allow_html=True)

st.title("🧮 Sistema de Precificação ContFlow")
st.markdown("""
Bem-vindo ao sistema de precificação da ContFlow. Cadastre os itens com seus custos e preços desejados, defina sua margem de contribuição, e veja se sua precificação está ideal.
""")

# Inputs gerais
st.sidebar.header("Configurações Gerais")
percentual_despesas = st.sidebar.slider("Despesas Fixas e Administrativas (%)", 0.0, 100.0, 10.0, step=0.5) / 100
percentual_impostos = st.sidebar.slider("Tributação Total (%)", 0.0, 100.0, 6.0, step=0.5) / 100
percentual_taxas = st.sidebar.slider("Taxas sobre Vendas (Cartão, Marketplaces etc) (%)", 0.0, 100.0, 5.0, step=0.5) / 100
mc_desejada = st.sidebar.slider("Margem de Contribuição Desejada (%)", 0.0, 100.0, 30.0, step=0.5)
percentual_desconto = st.sidebar.slider("Desconto Promocional (%)", 0.0, 50.0, 0.0, step=0.5) / 100

# Entrada de dados dos itens
st.markdown("---")
st.subheader("📋 Cadastro de Itens")
num_itens = st.number_input("Quantos itens deseja cadastrar?", min_value=1, max_value=20, value=1, step=1)

itens = []
for i in range(num_itens):
    st.markdown(f"**Item {i+1}**")
    nome = st.text_input(f"Nome do Produto {i+1}", key=f"nome_{i}")
    custo = st.number_input(f"Custo Total (R$) do Produto {i+1}", min_value=0.0, step=0.01, key=f"custo_{i}")
    preco_desejado = st.number_input(f"Preço de Venda Desejado (R$) para o Produto {i+1}", min_value=0.0, step=0.01, key=f"preco_{i}")

    custos_var_p = custo + (preco_desejado * percentual_impostos) + (preco_desejado * percentual_taxas)
    mc_real = ((preco_desejado - custos_var_p) / preco_desejado) * 100 if preco_desejado else 0
    preco_ideal = custo / (1 - percentual_impostos - percentual_taxas - mc_desejada / 100) if (1 - percentual_impostos - percentual_taxas - mc_desejada / 100) > 0 else 0
    preco_com_desconto = preco_desejado * (1 - percentual_desconto)
    lucro_com_desconto = preco_com_desconto - custos_var_p
    mc_com_desconto = (lucro_com_desconto / preco_com_desconto) * 100 if preco_com_desconto else 0

    itens.append({
        "Nome": nome,
        "Custo": custo,
        "Preço Desejado": preco_desejado,
        "Preço Ideal": preco_ideal,
        "MC Real (%)": mc_real,
        "Preço com Desconto": preco_com_desconto,
        "MC com Desconto (%)": mc_com_desconto,
        "Situação": "✅ Adequado" if mc_real >= mc_desejada else "⚠️ Abaixo do Ideal"
    })

st.markdown("---")
st.subheader("📊 Resultados Consolidados")

if itens:
    df = pd.DataFrame(itens)
    st.dataframe(df.style.applymap(lambda val: 'background-color: #f8d7da' if val == "⚠️ Abaixo do Ideal" else '', subset=['Situação']))

    st.download_button("📥 Baixar Análise em Excel", data=df.to_excel(index=False, engine='openpyxl'), file_name="precificacao_contflow.xlsx")

    st.markdown("---")
    st.subheader("📈 Gráficos Interativos")

    col1, col2 = st.columns(2)

    with col1:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(x=df["Nome"], y=df["Preço Desejado"], name="Preço Desejado", marker_color='#2ecc71'))
        fig1.add_trace(go.Bar(x=df["Nome"], y=df["Preço Ideal"], name="Preço Ideal", marker_color='#e74c3c'))
        fig1.update_layout(barmode='group', title='Comparativo de Preço Desejado vs. Preço Ideal', yaxis_title='Preço (R$)')
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df["Nome"], y=df["MC Real (%)"], name="MC Real", marker_color='#3498db'))
        fig2.add_trace(go.Scatter(x=df["Nome"], y=[mc_desejada]*len(df), name="MC Desejada", mode='lines', line=dict(color='orange', dash='dash')))
        fig2.update_layout(title='Margem de Contribuição Real vs. Desejada', yaxis_title='MC (%)')
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name='Sem Desconto', x=df["Nome"], y=df["MC Real (%)"], marker_color='#4CAF50'))
    fig3.add_trace(go.Bar(name='Com Desconto', x=df["Nome"], y=df["MC com Desconto (%)"], marker_color='#FF7043'))
    fig3.update_layout(barmode='group', title='Margem com e sem Desconto', yaxis_title='MC (%)')
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("Cadastre pelo menos um item para visualizar os resultados.")
