
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Sistema de Precificação CONTFLOW", layout="centered")

st.title("💰 Sistema Interativo de Precificação para Pequenos Negócios")
st.markdown("""
Este sistema ajuda a calcular o **preço ideal de venda** de produtos e serviços com base em custos fixos, variáveis, impostos e margem de lucro desejada.
Preencha os campos abaixo para obter recomendações personalizadas.
""")

st.header("1. Informações Gerais")
faturamento_previsto = st.number_input("Faturamento mensal previsto (R$)", min_value=0.0, format="%.2f")
despesa_fixa_total = st.number_input("Total de despesas fixas mensais (R$)", min_value=0.0, format="%.2f")

st.subheader("Percentuais incidentes sobre a venda")
percentual_impostos = st.slider("% de impostos (Simples, ISS, etc)", 0.0, 50.0, 6.0, step=0.5) / 100
percentual_taxas = st.slider("% de taxas (cartão, marketplaces, etc)", 0.0, 30.0, 5.0, step=0.5) / 100
percentual_comissao = st.slider("% de comissão sobre vendas", 0.0, 50.0, 0.0, step=0.5) / 100
percentual_lucro = st.slider("% de lucro líquido desejado", 0.0, 100.0, 20.0, step=1.0) / 100
percentual_reserva = st.slider("% de reserva/reinvestimento", 0.0, 50.0, 5.0, step=1.0) / 100

st.header("2. Produtos ou Serviços")
st.markdown("Preencha abaixo o custo de produção/prestação e o nome do item.")
data = []
num_itens = st.number_input("Quantos itens deseja cadastrar?", min_value=1, max_value=50, value=3, step=1)

for i in range(num_itens):
    st.subheader(f"Item {i+1}")
    nome = st.text_input(f"Nome do item {i+1}", key=f"nome_{i}")
    custo_unitario = st.number_input(f"Custo variável unitário (R$) do item {i+1}", min_value=0.0, format="%.2f", key=f"custo_{i}")
    data.append({"Item": nome, "Custo Unitário (R$)": custo_unitario})

df_itens = pd.DataFrame(data)

if faturamento_previsto > 0:
    # Cálculo do percentual de despesas fixas sobre o faturamento
    percentual_despesas = despesa_fixa_total / faturamento_previsto
    markup = 1 / (1 - (percentual_despesas + percentual_impostos + percentual_taxas + percentual_comissao + percentual_lucro + percentual_reserva))
    
    df_itens["Preço Ideal (R$)"] = df_itens["Custo Unitário (R$)"] * markup
    df_itens["Markup aplicado"] = markup

    st.success("Preços calculados com sucesso!")
    st.dataframe(df_itens)

    st.markdown("""
    **Atenção:** Os preços calculados cobrem:
    - Todos os custos fixos e variáveis
    - Impostos, taxas e comissões
    - Lucro líquido desejado
    - Reserva para reinvestimento
    """)
else:
    st.warning("Insira o faturamento previsto para calcular os preços sugeridos.")
