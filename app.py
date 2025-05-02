import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Sistema de Precificação CONTFLOW", layout="centered")

st.title("💰 Sistema Interativo de Precificação")
st.markdown(""" 
Calcule preços ideais com base em custos, impostos e margem desejada.
""")

# Seção 1: Informações Gerais
st.header("1. Informações Gerais")
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        faturamento_previsto = st.number_input("Faturamento mensal previsto (R$)", 
                                             min_value=0.0, 
                                             value=10000.0,
                                             format="%.2f")
    with col2:
        despesa_fixa_total = st.number_input("Total de despesas fixas mensais (R$)", 
                                           min_value=0.0, 
                                           value=5000.0,
                                           format="%.2f")

st.subheader("Percentuais incidentes sobre a venda")
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        percentual_impostos = st.number_input("% Impostos", 
                                            min_value=0.0, 
                                            max_value=50.0, 
                                            value=6.0, 
                                            step=0.5) / 100
        percentual_comissao = st.number_input("% Comissão", 
                                            min_value=0.0, 
                                            max_value=50.0, 
                                            value=0.0, 
                                            step=0.5) / 100
    with col2:
        percentual_taxas = st.number_input("% Taxas", 
                                         min_value=0.0, 
                                         max_value=30.0, 
                                         value=5.0, 
                                         step=0.5) / 100
        percentual_lucro = st.number_input("% Lucro", 
                                         min_value=0.0, 
                                         max_value=100.0, 
                                         value=20.0, 
                                         step=1.0) / 100
    with col3:
        percentual_reserva = st.number_input("% Reserva", 
                                           min_value=0.0, 
                                           max_value=50.0, 
                                           value=5.0, 
                                           step=1.0) / 100

# Seção 2: Produtos/Serviços
st.header("2. Cadastro de Itens")
num_itens = st.number_input("Quantidade de itens", 
                          min_value=1, 
                          max_value=50, 
                          value=3,
                          step=1)

data = []
for i in range(num_itens):
    with st.expander(f"Item {i+1}", expanded=(i < 3)):
        nome = st.text_input(f"Nome", 
                           value=f"Produto {i+1}", 
                           key=f"nome_{i}")
        custo = st.number_input(f"Custo Unitário (R$)", 
                              min_value=0.0, 
                              value=50.0*(i+1), 
                              format="%.2f",
                              key=f"custo_{i}")
        data.append({"Item": nome, "Custo Unitário (R$)": custo})

if not data:
    st.warning("Adicione pelo menos um item")
    st.stop()

df_itens = pd.DataFrame(data)

# Cálculos principais
if st.button("Calcular Precificação", type="primary"):
    try:
        # Cálculos base
        percentual_despesas = despesa_fixa_total / faturamento_previsto if faturamento_previsto > 0 else 0
        percentual_total = (percentual_despesas + percentual_impostos + 
                          percentual_taxas + percentual_comissao + 
                          percentual_lucro + percentual_reserva)
        
        if percentual_total >= 1:
            st.error("Erro: A soma dos percentuais não pode ser 100% ou mais")
            st.stop()

        markup_ideal = 1 / (1 - percentual_total)
        margem_contrib_ideal = (1 - (percentual_impostos + percentual_taxas + percentual_comissao)) * 100

        # Processamento por item
        resultados = []
        for index, row in df_itens.iterrows():
            preco_ideal = row["Custo Unitário (R$)"] * markup_ideal
            
            with st.container():
                col1, col2 = st.columns([3,1])
                with col1:
                    st.markdown(f"**{row['Item']}**")
                with col2:
                    preco_desejavel = st.number_input(
                        "Preço desejável (R$)", 
                        min_value=0.0, 
                        value=round(preco_ideal, 2),
                        key=f"preco_{index}"
                    )

            # Cálculos com preço ideal
            receita_liq_ideal = preco_ideal * (1 - (percentual_impostos + percentual_taxas + percentual_comissao))
            custo_total_ideal = row["Custo Unitário (R$)"] + (despesa_fixa_total/num_itens)
            margem_liq_ideal = ((receita_liq_ideal - custo_total_ideal) / preco_ideal) * 100

            # Cálculos com preço desejado
            if preco_desejavel > 0:
                receita_liq_desejada = preco_desejavel * (1 - (percentual_impostos + percentual_taxas + percentual_comissao))
                margem_liq_desejada = ((receita_liq_desejada - custo_total_ideal) / preco_desejavel) * 100
                markup_desejado = preco_desejavel / row["Custo Unitário (R$)"] if row["Custo Unitário (R$)"] > 0 else 0
            else:
                margem_liq_desejada = 0
                markup_desejado = 0

            resultados.append({
                "Item": row["Item"],
                "Custo (R$)": row["Custo Unitário (R$)"],
                "Preço Ideal (R$)": preco_ideal,
                "Preço Desejado (R$)": preco_desejavel,
                "Markup Ideal": markup_ideal,
                "Markup Desejado": markup_desejado,
                "Margem Contrib. (%)": margem_contrib_ideal,
                "Margem Liq. Ideal (%)": margem_liq_ideal,
                "Margem Liq. Desejada (%)": margem_liq_desejada,
                "Diferença (%)": margem_liq_desejada - margem_liq_ideal
            })

        df_resultados = pd.DataFrame(resultados)

        # Exibição dos resultados
        st.success("Cálculos concluídos com sucesso!")
        
        # Formatação da tabela
        st.dataframe(
            df_resultados.style.format({
                "Custo (R$)": "R$ {:.2f}",
                "Preço Ideal (R$)": "R$ {:.2f}",
                "Preço Desejado (R$)": "R$ {:.2f}",
                "Markup Ideal": "{:.2f}x",
                "Markup Desejado": "{:.2f}x",
                "Margem Contrib. (%)": "{:.1f}%",
                "Margem Liq. Ideal (%)": "{:.1f}%",
                "Margem Liq. Desejada (%)": "{:.1f}%",
                "Diferença (%)": "{:.1f}%"
            }).applymap(
                lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else 'color: red' if x < 0 else '',
                subset=["Diferença (%)"]
            ),
            height=(min(len(df_resultados), 10) * 35 + 38),
            width=1200
        )

        # Gráficos comparativos
        st.subheader("📊 Análise Visual")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Gráfico 1: Comparação de preços
        x = np.arange(len(df_resultados))
        width = 0.35
        ax1.bar(x - width/2, df_resultados["Preço Ideal (R$)"], width, label='Ideal', color='#4CAF50')
        ax1.bar(x + width/2, df_resultados["Preço Desejado (R$)"], width, label='Desejado', color='#FF9800')
        ax1.set_title('Comparação de Preços')
        ax1.set_xticks(x)
        ax1.set_xticklabels(df_resultados["Item"], rotation=45)
        ax1.legend()
        
        # Gráfico 2: Comparação de margens
        ax2.bar(x - width/2, df_resultados["Margem Liq. Ideal (%)"], width, label='Ideal', color='#4CAF50')
        ax2.bar(x + width/2, df_resultados["Margem Liq. Desejada (%)"], width, label='Desejada', color='#FF9800')
        ax2.set_title('Comparação de Margens Líquidas')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df_resultados["Item"], rotation=45)
        ax2.legend()

        st.pyplot(fig)

        # Resumo financeiro
        st.subheader("📌 Resumo Financeiro")
        st.markdown(f"""
        - **Markup Ideal Médio:** {markup_ideal:.2f}x
        - **Margem de Contribuição Ideal:** {margem_contrib_ideal:.1f}%
        - **Ponto de Equilíbrio:** R$ {despesa_fixa_total / (1 - (percentual_impostos + percentual_taxas + percentual_comissao)):,.2f}
        """)

    except Exception as e:
        st.error(f"Ocorreu um erro: {str(e)}")
        st.stop()