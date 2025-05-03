
import streamlit as st 
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Sistema de Precificação CONTFLOW", layout="centered")

# --- ESTILO PERSONALIZADO COM PALETA CONTFlow ---
st.markdown("""
    <style>
        .big-font {
            font-size:28px !important;
            color: #1A237E;
            font-weight: bold;
        }
        .stMetric {
            background-color: #A5D6A7;
            border-radius: 8px;
        }
        .css-1v3fvcr, .st-bf, .st-dc, .st-dd {
            color: #3949AB !important;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-font">💡 Otimize sua precificação em poucos passos com o APP!</div>', unsafe_allow_html=True)

# BARRA DE CONFIGURAÇÕES GLOBAIS (sem menu lateral)

# Menu de Ajuda
with st.expander("❓ Ajuda e Explicações dos Termos"):
    st.markdown("""
**Faturamento Mensal Previsto**: Quanto você espera faturar por mês.

**Despesas Fixas**: Custos que não mudam com a produção, como aluguel, energia, salários.

**Custos Variáveis**: Custos que variam com as vendas ou produção (matéria-prima, taxas, impostos).

**Lucro Líquido Alvo**: Percentual que você deseja lucrar sobre o faturamento.

**Markup**: Diferença percentual entre o custo e o preço de venda.

**Margem de Contribuição (MC)**: Parte da receita que "sobra" para cobrir custos fixos e gerar lucro.

**Reserva/Reinvestimento**: Valor reservado para expansão, emergências ou reinvestimento.

Você pode incluir mais explicações ou ajustar conforme o seu público.
""")


st.header("⚙️ Configurações Globais")
faturamento_previsto = st.number_input("Faturamento mensal previsto (R$)", min_value=0.0, value=0.0, format="%.2f")
despesa_fixa_total = st.number_input("Despesas fixas mensais (R$)", min_value=0.0, value=0.0, format="%.2f")
percentual_impostos = st.slider("% Impostos", 0.0, 50.0, 6.0, step=0.5) / 100
percentual_taxas = st.slider("% Taxas Variáveis", 0.0, 30.0, 5.0, step=0.5) / 100
percentual_comissao = st.slider("% Comissão sobre Vendas", 0.0, 50.0, 0.0, step=0.5) / 100
percentual_lucro_desejado = st.slider("% Lucro Líquido Alvo", 0.0, 100.0, 15.0, step=1.0) / 100
percentual_reserva = st.slider("% Reserva/Reinvestimento", 0.0, 50.0, 5.0, step=1.0) / 100

# CÁLCULOS
percentual_custo_fixo = despesa_fixa_total / faturamento_previsto if faturamento_previsto > 0 else 0
valor_lucro = faturamento_previsto * percentual_lucro_desejado
valor_reserva = faturamento_previsto * percentual_reserva
mc_total = despesa_fixa_total + valor_lucro + valor_reserva
mc_media_percentual = mc_total / faturamento_previsto if faturamento_previsto > 0 else 0
percentual_variavel_total = percentual_impostos + percentual_taxas + percentual_comissao

if mc_media_percentual + percentual_variavel_total >= 1:
    st.error("🚨 Suas metas e custos estão inviáveis! Reveja os valores para continuar.")
    st.stop()

st.info(f"""
**Metas Globais (Baseadas no Faturamento Previsto de R$ {faturamento_previsto:,.1f}):**
- Despesas Fixas: R$ {despesa_fixa_total:,.1f} ({percentual_custo_fixo*100:.1f}%)
- Lucro Líquido Alvo: R$ {valor_lucro:,.1f} ({percentual_lucro_desejado*100:.1f}%)
- Reserva/Reinvestimento: R$ {valor_reserva:,.1f} ({percentual_reserva*100:.1f}%)
- Margem de Contribuição Total Necessária: R$ {mc_total:,.1f} ({mc_media_percentual*100:.1f}% do Faturamento)
""")

# CADASTRO DE ITENS
st.header("📋 Cadastro e Análise de Itens")
num_itens = st.number_input("Quantos itens deseja analisar?", 1, 50, 1)
items_data = []

for i in range(num_itens):
    st.markdown("---")
    st.subheader(f"Item {i+1}")
    item = {"Nome": st.text_input(f"Nome", key=f"n_{i}", value=f"Produto {i+1}")}
    item["Custo Unitário"] = st.number_input("Custo Variável Unitário", 0.01, key=f"c_{i}", value=50.0)
    preco_desejado = st.number_input("Preço Desejado (R$)", 0.0, key=f"p_{i}", value=0.0)

    impostos_p = preco_desejado * percentual_impostos
    taxas_p = preco_desejado * percentual_taxas
    comissao_p = preco_desejado * percentual_comissao
    custos_var_p = item["Custo Unitário"] + impostos_p + taxas_p + comissao_p
    mc_p_rs = preco_desejado - custos_var_p
    mc_p_perc = (mc_p_rs / preco_desejado * 100) if preco_desejado else 0
    markup_p = ((preco_desejado / item["Custo Unitário"] - 1) * 100) if item["Custo Unitário"] else float('inf')

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

    
    with st.expander("❓ Como interpretar os resultados deste item?"):
        st.markdown(f'''
        - **Markup Praticado:** {markup_p:.1f}% | **Markup Ideal:** {markup_ideal:.1f}%
        - **MC Desejada:** {mc_p_perc:.1f}% | **MC Ideal:** {item["MC Ideal (%)"]:.1f}%
        ''')

    with st.expander("📌 Detalhamento dos Cálculos"):
        st.markdown(f'''
        - Preço Desejado: R$ {preco_desejado:.2f}
        - Custo Unitário: R$ {item["Custo Unitário"]:.2f}
        - Impostos: R$ {impostos_p:.2f}
        - Taxas: R$ {taxas_p:.2f}
        - Comissão: R$ {comissao_p:.2f}
        - Margem de Contribuição: R$ {mc_p_rs:.2f} ({mc_p_perc:.2f}%)
        - Preço Ideal: R$ {preco_ideal:.2f}
        - Markup Ideal: {markup_ideal:.2f}%
        ''')

        st.markdown(f"""
        - **Markup Praticado:** {markup_p:.1f}% | **Markup Ideal:** {markup_ideal:.1f}%
        - **MC Desejada:** {mc_p_perc:.1f}% | **MC Ideal:** {item['MC Ideal (%)']:.1f}%
        """)

# RESULTADOS CONSOLIDADOS
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
            st.warning(f"⚠️ {row['Nome']}: O preço está abaixo do ideal.")

# GRÁFICOS
st.header("📈 Gráficos Interativos")
if items_data:
    df = pd.DataFrame(items_data)

    fig = go.Figure(data=[
        go.Bar(name='Ideal', x=df["Nome"], y=df["Markup Ideal (%)"], marker_color='#388E3C'),
        go.Bar(name='Desejado', x=df["Nome"], y=df["Markup Praticado (%)"], marker_color='#FFA726')
    ])
    fig.update_layout(barmode='group', title='Markup Ideal vs Desejado por Produto', yaxis_title='Markup (%)')
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure(data=[
        go.Bar(name='MC Ideal (%)', x=df["Nome"], y=df["MC Ideal (%)"], marker_color='#3949AB'),
        go.Bar(name='MC Desejada (%)', x=df["Nome"], y=df["MC Desejada (%)"], marker_color='#FFA726')
    ])
    fig2.update_layout(barmode='group', title='Margem de Contribuição: Ideal vs Desejada', yaxis_title='MC (%)')
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name='Custo Unitário', x=df["Nome"], y=df["Custo Unitário"], marker_color='#7986CB'))
    fig3.add_trace(go.Bar(name='Impostos', x=df["Nome"], y=df["Impostos (Desejado)"], marker_color='#FFA726'))
    fig3.add_trace(go.Bar(name='Taxas', x=df["Nome"], y=df["Taxas (Desejado)"], marker_color='#3949AB'))
    fig3.add_trace(go.Bar(name='Comissão', x=df["Nome"], y=df["Comissão (Desejado)"], marker_color='#A5D6A7'))
    fig3.add_trace(go.Bar(name='Margem Contribuição', x=df["Nome"],
                          y=df["Preço Desejado"] - (df["Custo Unitário"] + df["Impostos (Desejado)"] + df["Taxas (Desejado)"] + df["Comissão (Desejado)"]),
                          marker_color='#388E3C'))
    fig3.update_layout(barmode='stack', title='Composição do Preço Desejado', yaxis_title='Valor (R$)')
    st.plotly_chart(fig3, use_container_width=True)


# Exportar Relatório
if df is not None and not df.empty:
    with st.expander("📁 Exportar Relatório"):
        export_format = st.selectbox("Escolha o formato:", ["Excel", "CSV"])
        if export_format == "Excel":
            file_export = df.to_excel("/mnt/data/relatorio_precificacao.xlsx", index=False)
            st.download_button("📥 Baixar Excel", data=open("/mnt/data/relatorio_precificacao.xlsx", "rb").read(), file_name="relatorio_precificacao.xlsx")
        elif export_format == "CSV":
            file_export = df.to_csv("/mnt/data/relatorio_precificacao.csv", index=False)
            st.download_button("📥 Baixar CSV", data=open("/mnt/data/relatorio_precificacao.csv", "rb").read(), file_name="relatorio_precificacao.csv")
