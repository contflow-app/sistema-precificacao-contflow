
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Sistema de Precificação CONTFLOW", layout="centered")

# --- ESTILO PERSONALIZADO ---
st.markdown("""
    <style>
        .big-font {font-size:28px !important; color: #2c3e50;}
        .stMetric {background-color: #f1f8e9; border-radius: 8px;}
    </style>
""", unsafe_allow_html=True)
st.markdown('<div class="big-font">💡 Otimize sua precificação em poucos passos!</div>', unsafe_allow_html=True)

# --- SIDEBAR: CONFIGURAÇÕES GLOBAIS ---
with st.sidebar:
    st.header("⚙️ Configurações Globais")
    faturamento_previsto = st.number_input("Faturamento mensal previsto (R$)", min_value=0.0, value=0.0, format="%.2f", help="Faturamento total esperado por mês")
    despesa_fixa_total = st.number_input("Despesas fixas mensais (R$)", min_value=0.0, value=0.0, format="%.2f", help="Soma de todos os custos fixos mensais")
    percentual_impostos = st.slider("% Impostos", 0.0, 50.0, 6.0, step=0.5, help="Percentual médio de impostos sobre o faturamento.") / 100
    percentual_taxas = st.slider("% Taxas Variáveis", 0.0, 30.0, 5.0, step=0.5, help="Percentual médio de taxas sobre cada venda, como taxas de máquinas de cartão ou marktplace.") / 100
    percentual_comissao = st.slider("% Comissão sobre Vendas", 0.0, 50.0, 0.0, step=0.5, help="Percentual pago como comissão para vendedores.") / 100
    percentual_lucro_desejado = st.slider("% Lucro Líquido Alvo", 0.0, 100.0, 15.0, step=1.0, help="Meta de lucro líquido em relação ao faturamento.") / 100
    percentual_reserva = st.slider("% Reserva/Reinvestimento", 0.0, 50.0, 5.0, step=1.0, help="Meta de reserva/reinvestimento em relação ao faturamento, caso queira criar reserva com preço de venda.")

# --- CÁLCULOS GLOBAIS ---
percentual_custo_fixo = despesa_fixa_total / faturamento_previsto if faturamento_previsto > 0 else 0
valor_lucro = faturamento_previsto * percentual_lucro_desejado
valor_reserva = faturamento_previsto * percentual_reserva
mc_total = despesa_fixa_total + valor_lucro + valor_reserva
mc_media_percentual = mc_total / faturamento_previsto if faturamento_previsto > 0 else 0
percentual_variavel_total = percentual_impostos + percentual_taxas + percentual_comissao

# --- VIABILIDADE ---
if mc_media_percentual + percentual_variavel_total >= 1:
    st.error("🚨 Suas metas e custos estão inviáveis! Reveja os valores para continuar.")
    st.stop()

# --- EXIBIÇÃO DE METAS ---
st.info(f"""
**Metas Globais (Baseadas no Faturamento Previsto de R$ {faturamento_previsto:,.1f}):**
- Despesas Fixas: R$ {despesa_fixa_total:,.1f} ({percentual_custo_fixo*100:.1f}%)
- Lucro Líquido Alvo: R$ {valor_lucro:,.1f} ({percentual_lucro_desejado*100:.1f}%)
- Reserva/Reinvestimento: R$ {valor_reserva:,.1f} ({percentual_reserva*100:.1f}%)
- Margem de Contribuição Total Necessária:R$ {mc_total:,.1f} ({mc_media_percentual*100:.1f}% do Faturamento)
""")

# --- ABAS DE NAVEGAÇÃO ---
abas = st.tabs(["Cadastro de Itens", "Resultados", "Gráficos"])

with abas[0]:
    st.header("📋 Cadastro e Análise de Itens")
    st.markdown("Adicione os itens, seus custos variáveis diretos e o preço de venda desejado.")
    num_itens = st.number_input("Quantos itens deseja analisar?", 1, 50, 1)
    items_data = []

    for i in range(num_itens):
        st.markdown("---")
        st.subheader(f"Item {i+1}")
        item = {"Nome": st.text_input(f"Nome", key=f"n_{i}", value=f"Produto {i+1}")}
        item["Custo Unitário"] = st.number_input("Custo Variável Unitário", 0.01, key=f"c_{i}", value=50.0)
        preco_desejado = st.number_input("Preço Desejado (R$)", 0.0, key=f"p_{i}", value=0.0, help="Digite o preço que deseja praticar (pode começar em zero)")

        # --- Cálculos Desejados ---
        impostos_p = preco_desejado * percentual_impostos
        taxas_p = preco_desejado * percentual_taxas
        comissao_p = preco_desejado * percentual_comissao
        custos_var_p = item["Custo Unitário"] + impostos_p + taxas_p + comissao_p
        mc_p_rs = preco_desejado - custos_var_p
        mc_p_perc = (mc_p_rs / preco_desejado * 100) if preco_desejado else 0
        markup_p = ((preco_desejado / item["Custo Unitário"] - 1) * 100) if item["Custo Unitário"] else float('inf')

        # --- Cálculos Ideais ---
        markup_divisor = 1 - (percentual_impostos + percentual_taxas + percentual_comissao + mc_media_percentual)
        if markup_divisor > 0 and item["Custo Unitário"] > 0:
            preco_ideal = item["Custo Unitário"] / markup_divisor
            markup_ideal = ((preco_ideal / item["Custo Unitário"] - 1) * 100)
        else:
            preco_ideal = 0
            markup_ideal = 0

        item.update({
            "Preço Desejado": preco_desejado,
            "Markup Praticado (%)": markup_p,
            "MC Desejada (%)": mc_p_perc,
            "Preço Ideal": preco_ideal,
            "Markup Ideal (%)": markup_ideal,
            "MC Ideal (%)": (preco_ideal - (item["Custo Unitário"] + preco_ideal*(percentual_impostos+percentual_taxas+percentual_comissao))) / preco_ideal * 100 if preco_ideal else 0,
            "Impostos (Desejado)": impostos_p,
            "Taxas (Desejado)": taxas_p,
            "Comissão (Desejado)": comissao_p
        })
        items_data.append(item)

        # Explicações interativas
        with st.expander("❓ Como interpretar os resultados deste item?"):
            st.markdown(f"""
            - **Markup Praticado:** {markup_p:.1f}% | **Markup Ideal:** {markup_ideal:.1f}%
            - **MC Desejada:** {mc_p_perc:.1f}% | **MC Ideal:** {item['MC Ideal (%)']:.1f}%
            - Se o Markup Desejado for menor que o Ideal, considere aumentar o preço ou reduzir custos.
            """)

with abas[1]:
    st.header("📊 Resultados Consolidados")
    if items_data:
        df = pd.DataFrame(items_data)
        cols = ["Nome", "Custo Unitário", "Preço Desejado", "Markup Praticado (%)", "MC Desejada (%)", "Preço Ideal", "Markup Ideal (%)", "MC Ideal (%)"]
        st.dataframe(df[cols].style.format({
            "Custo Unitário": "R$ {:.2f}",
            "Preço Desejado": "R$ {:.2f}",
            "Preço Ideal": "R$ {:.2f}",
            "Markup Praticado (%)": "{:.1f}%",
            "Markup Ideal (%)": "{:.1f}%",
            "MC Desejada (%)": "{:.1f}%",
            "MC Ideal (%)": "{:.1f}%"
        }))
        for idx, row in df.iterrows():
            if row["Markup Praticado (%)"] < row["Markup Ideal (%)"]:
                st.warning(f"⚠️ {row['Nome']}: O preço está abaixo do ideal. Considere aumentar o preço ou reduzir custos.")

with abas[2]:
    st.header("📈 Gráficos Interativos")
    if items_data:
        df = pd.DataFrame(items_data)
        # Gráfico Comparativo de Markup
        fig = go.Figure(data=[
            go.Bar(name='Ideal', x=df["Nome"], y=df["Markup Ideal (%)"], marker_color='seagreen'),
            go.Bar(name='Desejado', x=df["Nome"], y=df["Markup Praticado (%)"], marker_color='indianred')
        ])
        fig.update_layout(barmode='group', title='Markup Ideal vs Desejado por Produto', yaxis_title='Markup (%)')
        st.plotly_chart(fig, use_container_width=True)

        # Gráfico de MC
        fig2 = go.Figure(data=[
            go.Bar(name='MC Ideal (%)', x=df["Nome"], y=df["MC Ideal (%)"], marker_color='royalblue'),
            go.Bar(name='MC Desejada (%)', x=df["Nome"], y=df["MC Desejada (%)"], marker_color='orange')
        ])
        fig2.update_layout(barmode='group', title='Margem de Contribuição: Ideal vs Desejada', yaxis_title='MC (%)')
        st.plotly_chart(fig2, use_container_width=True)

        # Gráfico de Composição de Preço
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            name='Custo Unitário', x=df["Nome"], y=df["Custo Unitário"], marker_color='gray'
        ))
        fig3.add_trace(go.Bar(
            name='Impostos', x=df["Nome"], y=df["Impostos (Desejado)"], marker_color='gold'
        ))
        fig3.add_trace(go.Bar(
            name='Taxas', x=df["Nome"], y=df["Taxas (Desejado)"], marker_color='purple'
        ))
        fig3.add_trace(go.Bar(
            name='Comissão', x=df["Nome"], y=df["Comissão (Desejado)"], marker_color='pink'
        ))
        fig3.add_trace(go.Bar(
            name='Margem Contribuição', x=df["Nome"], y=df["Preço Desejado"] - (df["Custo Unitário"] + df["Impostos (Desejado)"] + df["Taxas (Desejado)"] + df["Comissão (Desejado)"]), marker_color='lightgreen'
        ))
        fig3.update_layout(barmode='stack', title='Composição do Preço Desejado', yaxis_title='Valor (R$)')
        st.plotly_chart(fig3, use_container_width=True)

# --- CHAMADA FINAL ---
st.info("🚀 Pronto para vender com lucro? Ajuste seus preços e atinja suas metas!")

# --- EXPLICAÇÕES GERAIS ---
with st.expander("💡 Dicas e Conceitos"):
    st.markdown("""
    - **Markup:** Percentual aplicado sobre o custo para formar o preço de venda.
    - **Margem de Contribuição:** Quanto sobra da venda para cobrir despesas fixas, lucro e reserva.
    - **Dica:** Sempre busque praticar um markup igual ou superior ao ideal calculado!
    """)
