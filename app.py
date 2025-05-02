import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Sistema de Precificação CONTFLOW", layout="centered")

st.title("💰 Sistema Interativo de Precificação")
st.markdown(""" 
Calcule preços ideais com base em custos, impostos e margem desejada.
""")

# Seção 1: Informações Gerais (mantida igual)
st.header("1. Informações Gerais")
faturamento_previsto = st.number_input("Faturamento mensal previsto (R$)", min_value=0.0, format="%.2f")
despesa_fixa_total = st.number_input("Total de despesas fixas mensais (R$)", min_value=0.0, format="%.2f")

st.subheader("Percentuais incidentes sobre a venda")
percentual_impostos = st.slider("% de impostos", 0.0, 50.0, 6.0, step=0.5) / 100
percentual_taxas = st.slider("% de taxas", 0.0, 30.0, 5.0, step=0.5) / 100
percentual_comissao = st.slider("% de comissão", 0.0, 50.0, 0.0, step=0.5) / 100
percentual_lucro = st.slider("% de lucro líquido", 0.0, 100.0, 20.0, step=1.0) / 100
percentual_reserva = st.slider("% de reserva", 0.0, 50.0, 5.0, step=1.0) / 100

# Seção 2: Produtos/Serviços (mantida igual)
st.header("2. Produtos ou Serviços")
data = []
num_itens = st.number_input("Quantos itens deseja cadastrar?", min_value=1, max_value=50, value=3)

for i in range(num_itens):
    st.subheader(f"Item {i+1}")
    nome = st.text_input(f"Nome do item {i+1}", key=f"nome_{i}")
    custo_unitario = st.number_input(f"Custo unitário (R$)", min_value=0.0, format="%.2f", key=f"custo_{i}")
    data.append({"Item": nome, "Custo Unitário (R$)": custo_unitario})

df_itens = pd.DataFrame(data)

# Cálculos (atualizados com novas funcionalidades)
if faturamento_previsto > 0 and not df_itens.empty:
    percentual_despesas = despesa_fixa_total / faturamento_previsto
    percentual_total = percentual_despesas + percentual_impostos + percentual_taxas + percentual_comissao + percentual_lucro + percentual_reserva
    markup_ideal = 1 / (1 - percentual_total)
    margem_contrib_ideal = (1 - (percentual_impostos + percentual_taxas + percentual_comissao)) * 100

    # Novos campos
    preco_desejavel_list = []
    margem_liquida_ideal_list = []
    margem_liquida_desejada_list = []

    for index, row in df_itens.iterrows():
        preco_ideal = row["Custo Unitário (R$)"] * markup_ideal
        
        # Input para preço desejável (novo)
        preco_desejavel = st.number_input(
            f"Preço desejável para '{row['Item']}' (R$)", 
            min_value=0.0, 
            value=round(preco_ideal, 2),
            key=f"preco_desejavel_{index}"
        )
        preco_desejavel_list.append(preco_desejavel)

        # Cálculo margens líquidas (novo)
        margem_liquida_ideal = ((preco_ideal * (1 - (percentual_impostos + percentual_taxas + percentual_comissao)) - row["Custo Unitário (R$)"] - (despesa_fixa_total/num_itens)) / preco_ideal) * 100
        margem_liquida_desejada = ((preco_desejavel * (1 - (percentual_impostos + percentual_taxas + percentual_comissao)) - row["Custo Unitário (R$)"] - (despesa_fixa_total/num_itens)) / preco_desejavel) * 100 if preco_desejavel > 0 else 0
        
        margem_liquida_ideal_list.append(margem_liquida_ideal)
        margem_liquida_desejada_list.append(margem_liquida_desejada)

    # Dataframe de resultados (atualizado)
    df_itens["Preço Ideal (R$)"] = df_itens["Custo Unitário (R$)"] * markup_ideal
    df_itens["Preço Desejável (R$)"] = preco_desejavel_list
    df_itens["Margem Contrib. Ideal (%)"] = margem_contrib_ideal
    df_itens["Margem Líq. Ideal (%)"] = margem_liquida_ideal_list
    df_itens["Margem Líq. Desejada (%)"] = margem_liquida_desejada_list
    df_itens["Dif. Margem Líq. (pp)"] = df_itens["Margem Líq. Desejada (%)"] - df_itens["Margem Líq. Ideal (%)"]

    st.success("Cálculos concluídos!")
    st.dataframe(df_itens.style.format({
        "Preço Ideal (R$)": "R$ {:.2f}",
        "Preço Desejável (R$)": "R$ {:.2f}",
        "Margem Contrib. Ideal (%)": "{:.1f}%",
        "Margem Líq. Ideal (%)": "{:.1f}%",
        "Margem Líq. Desejada (%)": "{:.1f}%",
        "Dif. Margem Líq. (pp)": "{:.1f} pp"
    }).applymap(lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else ('color: red' if x < 0 else ''), 
    subset=["Dif. Margem Líq. (pp)"]))

    # Gráficos comparativos (novos)
    st.subheader("📊 Análise Comparativa")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Gráfico 1: Preços
    x = np.arange(len(df_itens["Item"]))
    ax1.bar(x - 0.2, df_itens["Preço Ideal (R$)"], 0.4, label='Ideal', color='#4CAF50')
    ax1.bar(x + 0.2, df_itens["Preço Desejável (R$)"], 0.4, label='Desejado', color='#FF9800')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df_itens["Item"])
    ax1.set_ylabel("Preço (R$)")
    ax1.legend()
    
    # Gráfico 2: Margens Líquidas
    ax2.bar(x - 0.2, df_itens["Margem Líq. Ideal (%)"], 0.4, label='Ideal', color='#4CAF50')
    ax2.bar(x + 0.2, df_itens["Margem Líq. Desejada (%)"], 0.4, label='Desejada', color='#FF9800')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df_itens["Item"])
    ax2.set_ylabel("Margem Líquida (%)")
    ax2.legend()

    st.pyplot(fig)

else:
    st.warning("Preencha todos os campos para calcular.")