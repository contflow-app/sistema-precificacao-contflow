
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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

if faturamento_previsto > 0 and not df_itens.empty:
    percentual_despesas = despesa_fixa_total / faturamento_previsto
    percentual_total = percentual_despesas + percentual_impostos + percentual_taxas + percentual_comissao + percentual_lucro + percentual_reserva
    markup_ideal = 1 / (1 - percentual_total)
    margem_ideal = (1 - (percentual_despesas + percentual_impostos + percentual_taxas + percentual_comissao)) * 100

    preco_desejavel_list = []
    markup_desejavel_list = []
    margem_desejavel_list = []
    margem_contribuicao_real = []
    margem_liquida_final = []

    for index, row in df_itens.iterrows():
        preco_desejavel = st.number_input(
            f"Preço desejável para '{row['Item']}' (R$)",
            min_value=0.0,
            format="%.2f",
            key=f"preco_desejavel_{index}"
        )
        preco_desejavel_list.append(preco_desejavel)

        if row["Custo Unitário (R$)"] > 0:
            markup_desejavel = preco_desejavel / row["Custo Unitário (R$)"]
            margem_desejavel = ((preco_desejavel - row["Custo Unitário (R$)"]) / preco_desejavel) * 100 if preco_desejavel > 0 else 0.0
        else:
            markup_desejavel = 0
            margem_desejavel = 0

        impostos = preco_desejavel * percentual_impostos
        taxas = preco_desejavel * percentual_taxas
        comissao = preco_desejavel * percentual_comissao
        despesas_fixas_unit = despesa_fixa_total / num_itens

        contribuicao = preco_desejavel - row["Custo Unitário (R$)"] - impostos - taxas - comissao
        margem_contrib = (contribuicao / preco_desejavel) * 100 if preco_desejavel > 0 else 0
        lucro_final = contribuicao - despesas_fixas_unit
        margem_liquida = (lucro_final / preco_desejavel) * 100 if preco_desejavel > 0 else 0

        markup_desejavel_list.append(markup_desejavel)
        margem_desejavel_list.append(margem_desejavel)
        margem_contribuicao_real.append(margem_contrib)
        margem_liquida_final.append(margem_liquida)

    df_itens["Preço Ideal (R$)"] = df_itens["Custo Unitário (R$)"] * markup_ideal
    df_itens["Preço Desejável (R$)"] = preco_desejavel_list
    df_itens["Markup Ideal"] = markup_ideal
    df_itens["Markup com Preço Desejável"] = markup_desejavel_list
    df_itens["Margem com Preço Ideal (%)"] = margem_ideal
    df_itens["Margem com Preço Desejável (%)"] = margem_desejavel_list
    df_itens["Margem de Contribuição Real (%)"] = margem_contribuicao_real
    df_itens["Margem Líquida Final (%)"] = margem_liquida_final

    ponto_equilibrio = despesa_fixa_total / (1 - (percentual_despesas + percentual_impostos + percentual_taxas + percentual_comissao)) if (1 - (percentual_despesas + percentual_impostos + percentual_taxas + percentual_comissao)) > 0 else 0

    st.success("Preços e comparações calculados com sucesso!")
    st.dataframe(df_itens.style.format({
        "Preço Ideal (R$)": "R$ {:.2f}",
        "Preço Desejável (R$)": "R$ {:.2f}",
        "Markup Ideal": "{:.2f}",
        "Markup com Preço Desejável": "{:.2f}",
        "Margem com Preço Ideal (%)": "{:.1f}%",
        "Margem com Preço Desejável (%)": "{:.1f}%",
        "Margem de Contribuição Real (%)": "{:.1f}%",
        "Margem Líquida Final (%)": "{:.1f}%"
    }))

    st.markdown("""
    ### 🧠 Entendendo as Margens

    - **Margem com Preço Ideal (%):** margem de contribuição estimada que cobre todos os custos e garante o lucro desejado.
    - **Margem com Preço Desejável (%):** margem bruta com base no preço que você inseriu, sem considerar impostos, taxas e comissões.
    - **Margem de Contribuição Real (%):** margem considerando impostos, taxas e comissões, com o preço desejado.
    - **Margem Líquida Final (%):** quanto sobra, de fato, para você após todos os custos variáveis e fixos, com o preço desejado.
    """)

    st.subheader("Resumo dos Indicadores")
    st.markdown(f"""
    - **Markup aplicado (ideal):** {markup_ideal:.2f}
    - **Margem de contribuição ideal:** {margem_ideal:.1f}%
    - **Ponto de equilíbrio (faturamento mínimo):** R$ {ponto_equilibrio:,.2f}
    """)

    if st.checkbox("Mostrar abertura dos cálculos do preço"):
        for index, row in df_itens.iterrows():
            st.markdown(f"""
            ### 📦 {row['Item']}
            - Custo variável unitário: R$ {row["Custo Unitário (R$)"]:.2f}
            - Preço ideal de venda: R$ {row["Preço Ideal (R$)"]:.2f}
            - Preço desejável informado: R$ {row["Preço Desejável (R$)"]:.2f}
            - Markup ideal: {row["Markup Ideal"]:.2f}
            - Markup com preço desejável: {row["Markup com Preço Desejável"]:.2f}
            - Margem com preço ideal: {row["Margem com Preço Ideal (%)"]:.1f}%
            - Margem bruta com preço desejável: {row["Margem com Preço Desejável (%)"]:.1f}%
            - Margem de contribuição real: {row["Margem de Contribuição Real (%)"]:.1f}%
            - Margem líquida final: {row["Margem Líquida Final (%)"]:.1f}%
            """)

    st.subheader("📊 Comparativo Visual")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df_itens["Item"], df_itens["Preço Ideal (R$)"], label="Preço Ideal", color="green", alpha=0.6)
    ax.bar(df_itens["Item"], df_itens["Preço Desejável (R$)"], label="Preço Desejável", color="orange", alpha=0.6)
    ax.set_ylabel("Preço (R$)")
    ax.set_title("Comparativo: Preço Ideal vs. Preço Desejável")
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("Insira o faturamento previsto e os itens para calcular os preços sugeridos.")
