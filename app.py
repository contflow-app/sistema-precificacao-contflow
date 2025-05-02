
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Sistema de Precificação CONTFLOW", layout="centered")
st.title("💰 Sistema Interativo de Precificação")

st.markdown("""
Este sistema ajuda a calcular a **Margem de Contribuição Ideal** e analisar o **Preço de Venda Praticado**  
com base nos custos, despesas, impostos e metas financeiras, **otimizado para micro e pequenos negócios**.
""")

# --- 1. Informações Gerais ---
st.header("1. Informações Gerais da Empresa e Metas")

# Valores padrão ajustados para microempresas
faturamento_previsto = st.number_input("Faturamento mensal previsto (R$)", min_value=1.0, value=8000.0, 
                                      format="%.2f", help="Faturamento total esperado por mês")
despesa_fixa_total = st.number_input("Total de despesas fixas mensais (R$)", min_value=0.0, value=3500.0,
                                    format="%.2f", help="Custos fixos (aluguel, salários, etc.)")

st.subheader("Percentuais Médios Incidentes sobre a Venda")
col1, col2 = st.columns(2)

with col1:
    percentual_impostos = st.slider("% Impostos (Ex: Simples Nacional)", 0.0, 50.0, 6.0, step=0.5) / 100
    percentual_taxas = st.slider("% Taxas Variáveis (Cartão, Marketplace)", 0.0, 30.0, 5.0, step=0.5) / 100
    percentual_comissao = st.slider("% Comissão sobre Vendas", 0.0, 50.0, 0.0, step=0.5) / 100

with col2:
    percentual_lucro_desejado = st.slider("% Lucro Líquido Alvo", 0.0, 100.0, 15.0, step=1.0) / 100
    percentual_reserva = st.slider("% Reserva/Reinvestimento", 0.0, 50.0, 5.0, step=1.0) / 100

# Validação de custos variáveis
percentual_variavel_total = percentual_impostos + percentual_taxas + percentual_comissao
if percentual_variavel_total >= 0.8:
    st.error("ERRO: Custos variáveis ultrapassam 80% - modelo inviável para microempresas!")
    st.stop()

# Cálculos percentuais
try:
    percentual_custo_fixo = despesa_fixa_total / faturamento_previsto
except ZeroDivisionError:
    percentual_custo_fixo = 0

valor_lucro = faturamento_previsto * percentual_lucro_desejado
valor_reserva = faturamento_previsto * percentual_reserva
mc_total = despesa_fixa_total + valor_lucro + valor_reserva
mc_media_percentual = mc_total / faturamento_previsto if faturamento_previsto > 0 else 0

# --- 2. Cadastro de Itens ---
st.header("2. Cadastro e Análise de Itens")
num_itens = st.number_input("Quantos itens deseja analisar?", 1, 50, 1)
items_data = []

for i in range(num_itens):
    st.markdown("---")
    st.subheader(f"Item {i+1}")
    item = {"Nome": st.text_input(f"Nome", key=f"n_{i}", value=f"Produto {i+1}")}
    
    # Inputs principais
    item["Custo Unitário"] = st.number_input("Custo Variável Unitário", 0.01, key=f"c_{i}", value=50.0)
    preco_praticado = st.number_input("Preço Praticado", 0.01, key=f"p_{i}", 
                                     value=item["Custo Unitário"] * 2)
    
    # --- Cálculos Praticados ---
    impostos_p = preco_praticado * percentual_impostos
    taxas_p = preco_praticado * percentual_taxas
    comissao_p = preco_praticado * percentual_comissao
    custos_var_p = item["Custo Unitário"] + impostos_p + taxas_p + comissao_p
    mc_p_rs = preco_praticado - custos_var_p
    mc_p_perc = (mc_p_rs / preco_praticado * 100) if preco_praticado else 0
    markup_p = ((preco_praticado / item["Custo Unitário"] - 1) * 100) if item["Custo Unitário"] else float('inf')
    
    # --- Cálculos Ideais ---
    markup_divisor = 1 - (percentual_impostos + percentual_taxas + percentual_comissao + mc_media_percentual)
    if markup_divisor > 0 and item["Custo Unitário"] > 0:
        preco_ideal = item["Custo Unitário"] / markup_divisor
        markup_ideal = ((preco_ideal / item["Custo Unitário"] - 1) * 100)
    else:
        preco_ideal = 0
        markup_ideal = 0
    
    # Armazenamento dos dados
    item.update({
        "Preço Praticado": preco_praticado,
        "Markup Praticado (%)": markup_p,
        "MC Praticada (%)": mc_p_perc,
        "Preço Ideal": preco_ideal,
        "Markup Ideal (%)": markup_ideal,
        "MC Ideal (%)": (preco_ideal - (item["Custo Unitário"] + preco_ideal*(percentual_impostos+percentual_taxas+percentual_comissao))) / preco_ideal * 100 if preco_ideal else 0
    })
    items_data.append(item)

# --- 3. Resultados e Gráficos ---
st.header("3. Resultados Consolidados")

# Tabela principal
df = pd.DataFrame(items_data)
cols = ["Nome", "Custo Unitário", "Preço Praticado", "Markup Praticado (%)", 
        "MC Praticada (%)", "Preço Ideal", "Markup Ideal (%)", "MC Ideal (%)"]
st.dataframe(df[cols].style.format({
    "Custo Unitário": "R$ {:.2f}",
    "Preço Praticado": "R$ {:.2f}",
    "Preço Ideal": "R$ {:.2f}",
    "Markup Praticado (%)": "{:.1f}%",
    "Markup Ideal (%)": "{:.1f}%",
    "MC Praticada (%)": "{:.1f}%",
    "MC Ideal (%)": "{:.1f}%"
}))

# Gráfico Comparativo de Markup
st.subheader("📈 Comparação de Markup")
fig, ax = plt.subplots(figsize=(10,5))
index = np.arange(len(df))
bar_width = 0.35

ax.bar(index - bar_width/2, df["Markup Ideal (%)"], bar_width, label='Ideal', color='#2ecc71')
ax.bar(index + bar_width/2, df["Markup Praticado (%)"], bar_width, label='Praticado', color='#e74c3c')

ax.set_title("Markup Ideal vs Praticado por Produto")
ax.set_xticks(index)
ax.set_xticklabels(df["Nome"], rotation=45)
ax.legend()
st.pyplot(fig)

# Explicações para microempreendedores
with st.expander("💡 Como interpretar os resultados?"):
    st.markdown("""
    **Guia Rápido:**
    - **Markup Ideal:** Percentual necessário para atingir suas metas
    - **Markup Praticado:** Percentual atual praticado
    - **Dica:** Seu markup praticado deve ser igual ou superior ao ideal
    - **Exemplo Prático:**
        - Custo: R$ 50
        - Markup 100% → Preço: R$ 100
        - Margem Bruta: R$ 50 (50%)
    """)

# Avisos contextuais
for idx, row in df.iterrows():
    if row["Markup Praticado (%)"] < row["Markup Ideal (%)"]:
        st.warning(f"⚠️ {row['Nome']}: Aumente o preço em {row['Markup Ideal (%)'] - row['Markup Praticado (%)']:.1f}% ou reduza custos")