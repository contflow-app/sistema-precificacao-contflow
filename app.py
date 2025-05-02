
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Sistema de Precificação CONTFLOW", layout="centered")
st.title("💰 Sistema Interativo de Precificação")

st.markdown("""
Este sistema ajuda a calcular a **Margem de Contribuição Ideal** e analisar o **Preço de Venda Praticado**
com base nos custos, despesas, impostos e metas financeiras gerais.
""")

# --- 1. Informações Gerais ---
st.header("1. Informações Gerais da Empresa e Metas")

faturamento_previsto = st.number_input(
    "Faturamento mensal previsto (R$)",
    min_value=0.0,
    value=0.0,
    format="%.2f",
    help="Qual o faturamento total esperado por mês com todos os produtos/serviços?"
)

despesa_fixa_total = st.number_input(
    "Total de despesas fixas mensais (R$)",
    min_value=0.0,
    value=0.0,
    format="%.2f",
    help="Soma de todos os custos que não variam com a venda (Aluguel, salários fixos, pro-labore, etc.)"
)

st.subheader("Percentuais Médios Incidentes sobre a Venda")
col1, col2 = st.columns(2)

with col1:
    percentual_impostos = st.slider(
        "% Impostos (Ex: Simples Nacional)", 0.0, 50.0, 6.0, step=0.5,
        help="Percentual médio de impostos sobre o faturamento."
    ) / 100
    percentual_taxas = st.slider(
        "% Taxas Variáveis (Cartão, Marketplace)", 0.0, 30.0, 5.0, step=0.5,
        help="Percentual médio de taxas que incidem sobre cada venda."
    ) / 100
    percentual_comissao = st.slider(
        "% Comissão sobre Vendas", 0.0, 50.0, 0.0, step=0.5,
        help="Percentual pago como comissão para vendedores."
    ) / 100

with col2:
    percentual_lucro_desejado_sobre_faturamento = st.slider(
        "% Lucro Líquido Alvo (sobre Faturamento)", 0.0, 100.0, 15.0, step=1.0,
        help="Qual a meta de lucro líquido total em relação ao faturamento previsto?"
    ) / 100
    percentual_reserva_sobre_faturamento = st.slider(
        "% Reserva/Reinvestimento (sobre Faturamento)", 0.0, 50.0, 5.0, step=1.0,
        help="Qual a meta de reserva/reinvestimento em relação ao faturamento previsto?"
    ) / 100

percentual_custo_fixo_sobre_faturamento = despesa_fixa_total / faturamento_previsto if faturamento_previsto > 0 else 0
valor_lucro_esperado = faturamento_previsto * percentual_lucro_desejado_sobre_faturamento
valor_reserva_esperado = faturamento_previsto * percentual_reserva_sobre_faturamento
mc_total_necessaria_rs = despesa_fixa_total + valor_lucro_esperado + valor_reserva_esperado
mc_media_necessaria_percentual = mc_total_necessaria_rs / faturamento_previsto if faturamento_previsto > 0 else 0

st.info(f"""
**Metas Globais (Baseadas no Faturamento Previsto de R$ {faturamento_previsto:,.2f}):**
- Despesas Fixas: R$ {despesa_fixa_total:,.2f} ({percentual_custo_fixo_sobre_faturamento*100:.1f}%)
- Lucro Líquido Alvo: R$ {valor_lucro_esperado:,.2f} ({percentual_lucro_desejado_sobre_faturamento*100:.1f}%)
- Reserva/Reinvestimento: R$ {valor_reserva_esperado:,.2f} ({percentual_reserva_sobre_faturamento*100:.1f}%)
**Margem de Contribuição Total Necessária:** R$ {mc_total_necessaria_rs:,.2f} ({mc_media_necessaria_percentual*100:.1f}% do Faturamento)
*Este é o valor total que a soma das vendas de todos os itens precisa gerar (após custos variáveis) para cobrir fixos, lucro e reserva.*
""")

percentual_variavel_total_medio = percentual_impostos + percentual_taxas + percentual_comissao

if mc_media_necessaria_percentual + percentual_variavel_total_medio >= 1:
    st.error(
        f"A Margem de Contribuição Média necessária ({mc_media_necessaria_percentual*100:.1f}%) somada aos custos variáveis percentuais médios ({percentual_variavel_total_medio*100:.1f}%) é igual ou maior que 100%. As metas são inviáveis com os custos/despesas informados. Revise os valores.")
    st.stop()

# --- 2. Produtos ou Serviços ---
st.header("2. Cadastro e Análise de Itens")
st.markdown("Adicione os itens, seus custos variáveis diretos e o preço de venda que você pratica ou deseja praticar.")

num_itens = st.number_input(
    "Quantos itens diferentes deseja analisar?",
    min_value=1, max_value=50, value=1, step=1
)
items_data = []

for i in range(num_itens):
    st.markdown("---")
    st.subheader(f"Item {i+1}")
    item_dict = {}
    item_dict["Nome"] = st.text_input(
        f"Nome do Item {i+1}", key=f"nome_{i}", value=f"Produto {i+1}"
    )
    item_dict["Custo Variável Unitário (R$)"] = st.number_input(
        f"Custo Variável Unitário Direto (R$) do Item {i+1}",
        min_value=0.0,  # Agora pode ser zero
        format="%.2f",
        key=f"custo_{i}",
        value=0.0,  # Agora começa em zero
        help="Custo direto para produzir/adquirir uma unidade (matéria-prima, embalagem, mercadoria). Não inclua impostos/taxas aqui."
    )
    preco_praticado = st.number_input(
        f"Preço de Venda Praticado/Desejado (R$)",
        min_value=0.0,  # Agora pode ser zero
        format="%.2f",
        value=0.0,  # Agora começa em zero
        key=f"preco_praticado_{i}",
        help="Qual o preço final de venda deste item para o cliente?"
    )
    item_dict["Preço de Venda Praticado (R$)"] = preco_praticado

    # --- Cálculos para o Preço Praticado ---
    custo_var_unit = item_dict["Custo Variável Unitário (R$)"]
    impostos_praticado = preco_praticado * percentual_impostos
    taxas_praticado = preco_praticado * percentual_taxas
    comissao_praticado = preco_praticado * percentual_comissao
    custos_variaveis_totais_praticado = custo_var_unit + impostos_praticado + taxas_praticado + comissao_praticado

    item_dict["Custos Variáveis Totais Praticado (R$)"] = custos_variaveis_totais_praticado
    item_dict["Impostos Praticado (R$)"] = impostos_praticado
    item_dict["Taxas Praticado (R$)"] = taxas_praticado
    item_dict["Comissão Praticado (R$)"] = comissao_praticado

    contribuicao_praticada_rs = preco_praticado - custos_variaveis_totais_praticado
    item_dict["Margem Contribuição Praticada (R$)"] = contribuicao_praticada_rs
    contribuicao_praticada_perc = (contribuicao_praticada_rs / preco_praticado) * 100 if preco_praticado > 0 else 0
    item_dict["Margem Contribuição Praticada (%)"] = contribuicao_praticada_perc

    # --- Cálculo da Margem de Contribuição Ideal (%) e Preço Ideal ---
    markup_divisor_ideal = 1 - (percentual_impostos + percentual_taxas + percentual_comissao + mc_media_necessaria_percentual)
    preco_ideal_calculado = 0
    contribuicao_ideal_perc = 0
    contribuicao_ideal_rs = 0
    impostos_ideal = 0
    taxas_ideal = 0
    comissao_ideal = 0
    markup_ideal_percentual = 0

    if markup_divisor_ideal > 0 and custo_var_unit > 0:
        preco_ideal_calculado = custo_var_unit / markup_divisor_ideal
        impostos_ideal = preco_ideal_calculado * percentual_impostos
        taxas_ideal = preco_ideal_calculado * percentual_taxas
        comissao_ideal = preco_ideal_calculado * percentual_comissao
        custos_variaveis_totais_ideal = custo_var_unit + impostos_ideal + taxas_ideal + comissao_ideal
        contribuicao_ideal_rs = preco_ideal_calculado - custos_variaveis_totais_ideal
        contribuicao_ideal_perc = (contribuicao_ideal_rs / preco_ideal_calculado) * 100 if preco_ideal_calculado > 0 else 0
        markup_ideal_percentual = ((preco_ideal_calculado - custo_var_unit) / custo_var_unit) * 100 if custo_var_unit > 0 else float('inf')
        item_dict["Margem Contribuição Ideal (%)"] = contribuicao_ideal_perc
        item_dict["Preço Ideal Sugerido (R$)"] = preco_ideal_calculado
        item_dict["Markup Ideal (%)"] = markup_ideal_percentual
        item_dict["Impostos Ideal (R$)"] = impostos_ideal
        item_dict["Taxas Ideal (R$)"] = taxas_ideal
        item_dict["Comissão Ideal (R$)"] = comissao_ideal
        item_dict["Margem Contribuição Ideal (R$)"] = contribuicao_ideal_rs
    else:
        item_dict["Margem Contribuição Ideal (%)"] = -999
        item_dict["Preço Ideal Sugerido (R$)"] = 0
        item_dict["Markup Ideal (%)"] = 0
        item_dict["Impostos Ideal (R$)"] = 0
        item_dict["Taxas Ideal (R$)"] = 0
        item_dict["Comissão Ideal (R$)"] = 0
        item_dict["Margem Contribuição Ideal (R$)"] = 0
        st.warning(f"Não foi possível calcular o Preço/Margem/Markup Ideal para '{item_dict['Nome']}'. Verifique se as metas gerais e custos variáveis percentuais são viáveis.")

    items_data.append(item_dict)

# --- 3. Resultados Consolidados ---
st.header("3. Resultados Consolidados")

if items_data:
    df_resultados = pd.DataFrame(items_data)
    cols_order = [
        "Nome", "Custo Variável Unitário (R$)", "Preço de Venda Praticado (R$)",
        "Margem Contribuição Praticada (R$)", "Margem Contribuição Praticada (%)",
        "Preço Ideal Sugerido (R$)", "Margem Contribuição Ideal (R$)", "Margem Contribuição Ideal (%)", "Markup Ideal (%)"
    ]
    cols_order = [col for col in cols_order if col in df_resultados.columns]
    df_resultados = df_resultados[cols_order]

    st.subheader("Tabela Comparativa")
    st.dataframe(df_resultados.style.format({
        "Custo Variável Unitário (R$)": "R$ {:,.2f}",
        "Preço de Venda Praticado (R$)": "R$ {:,.2f}",
        "Margem Contribuição Praticada (R$)": "R$ {:,.2f}",
        "Margem Contribuição Praticada (%)": "{:.1f}%",
        "Preço Ideal Sugerido (R$)": "R$ {:,.2f}",
        "Margem Contribuição Ideal (R$)": "R$ {:,.2f}",
        "Margem Contribuição Ideal (%)": "{:.1f}%",
        "Markup Ideal (%)": "{:.1f}%"
    }))