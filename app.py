import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 Sistema Avançado de Precificação com Análise Comparativa")

# ========================================
# SEÇÃO 1: DADOS DE ENTRADA
# ========================================
with st.expander("🔧 Dados Gerais da Operação", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        despesa_fixa_total = st.number_input("Despesas Fixas Totais (R$)", 
                                           min_value=0.0, 
                                           value=15000.0,
                                           help="Custos fixos mensais como aluguel, salários, etc.")
        
    with col2:
        percentual_impostos = st.number_input("Impostos (% faturamento)", 
                                             min_value=0.0, 
                                             max_value=100.0, 
                                             value=12.0,
                                             help="Ex: ICMS, ISS, PIS/COFINS")/100
        
    with col3:
        percentual_taxas = st.number_input("Taxas (% faturamento)", 
                                          min_value=0.0, 
                                          max_value=100.0, 
                                          value=3.5,
                                          help="Taxas de cartão, plataformas, etc.")/100

    col4, col5, col6 = st.columns(3)
    with col4:
        percentual_comissao = st.number_input("Comissões (% faturamento)", 
                                             min_value=0.0, 
                                             max_value=100.0, 
                                             value=8.0)/100
        
    with col5:
        percentual_lucro = st.number_input("Lucro Desejado (% faturamento)", 
                                         min_value=0.0, 
                                         max_value=100.0, 
                                         value=20.0)/100
        
    with col6:
        percentual_reserva = st.number_input("Reserva (% faturamento)", 
                                           min_value=0.0, 
                                           max_value=100.0, 
                                           value=5.0,
                                           help="Para imprevistos ou investimentos")/100

# ========================================
# SEÇÃO 2: CADASTRO DE ITENS
# ========================================
st.subheader("📦 Cadastro de Produtos/Serviços")
num_itens = st.number_input("Quantidade de Itens", min_value=1, value=3, key="num_itens")

data = []
for i in range(num_itens):
    st.markdown(f"### Item {i+1}")
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        item = st.text_input(f"Nome", value=f"Produto {i+1}", key=f"nome_{i}")
    with col2:
        custo = st.number_input(f"Custo Unitário (R$)", min_value=0.0, value=50.0*(i+1), key=f"custo_{i}")
    with col3:
        volume = st.number_input(f"Volume Estimado", min_value=1, value=100*(i+1), key=f"volume_{i}")
    data.append({"Item": item, 
                 "Custo Unitário (R$)": custo,
                 "Volume Estimado": volume})

df_itens = pd.DataFrame(data)

# ========================================
# SEÇÃO 3: CÁLCULOS
# ========================================
if st.button("📈 Calcular Precificação Completa", type="primary"):
    if not df_itens.empty:
        # Cálculos base
        percentual_total = (percentual_impostos + percentual_taxas + 
                          percentual_comissao + percentual_lucro + 
                          percentual_reserva)
        
        markup_ideal = 1 / (1 - percentual_total)
        margem_contribuicao_ideal = 1 - (percentual_impostos + percentual_taxas + percentual_comissao)
        
        # Cálculo do faturamento total necessário
        faturamento_necessario = despesa_fixa_total / (1 - (percentual_total + (sum(df_itens["Custo Unitário (R$)"] * df_itens["Volume Estimado"]) / 
                                                           (sum(df_itens["Custo Unitário (R$)"] * df_itens["Volume Estimado"]) * markup_ideal))))

        # Cálculos por item
        resultados = []
        for index, row in df_itens.iterrows():
            preco_ideal = row["Custo Unitário (R$)"] * markup_ideal
            
            with st.expander(f"🔍 Análise para '{row['Item']}'", expanded=False):
                colA, colB = st.columns(2)
                with colA:
                    preco_desejavel = st.number_input(
                        f"Preço desejável (R$)", 
                        min_value=0.0, 
                        value=round(preco_ideal, 2),
                        key=f"preco_desejavel_{index}"
                    )
                
                # Cálculos com preço ideal
                receita_liquida_ideal = preco_ideal * (1 - (percentual_impostos + percentual_taxas + percentual_comissao))
                lucro_liquido_ideal = receita_liquida_ideal - row["Custo Unitário (R$)"] - (despesa_fixa_total/num_itens)
                margem_liquida_ideal = (lucro_liquido_ideal / preco_ideal) * 100
                
                # Cálculos com preço desejado
                if preco_desejavel > 0:
                    receita_liquida_desejada = preco_desejavel * (1 - (percentual_impostos + percentual_taxas + percentual_comissao))
                    lucro_liquido_desejado = receita_liquida_desejada - row["Custo Unitário (R$)"] - (despesa_fixa_total/num_itens)
                    margem_liquida_desejada = (lucro_liquido_desejado / preco_desejavel) * 100
                    markup_desejavel = preco_desejavel / row["Custo Unitário (R$)"]
                    margem_contrib_desejada = (preco_desejavel - row["Custo Unitário (R$)"]) / preco_desejavel * 100
                else:
                    margem_liquida_desejada = 0
                    markup_desejavel = 0
                    margem_contrib_desejada = 0
                
                # Ponto de equilíbrio
                ponto_equilibrio = (despesa_fixa_total/num_itens + row["Custo Unitário (R$)"]) / (1 - (percentual_impostos + percentual_taxas + percentual_comissao))
                
                resultados.append({
                    "Item": row["Item"],
                    "Custo Unitário (R$)": row["Custo Unitário (R$)"],
                    "Preço Ideal (R$)": preco_ideal,
                    "Preço Desejável (R$)": preco_desejavel,
                    "Markup Ideal": markup_ideal,
                    "Markup Desejável": markup_desejavel,
                    "Margem Contrib. Ideal (%)": margem_contribuicao_ideal * 100,
                    "Margem Contrib. Real (%)": margem_contrib_desejada,
                    "Margem Líquida Ideal (%)": margem_liquida_ideal,
                    "Margem Líquida Desejada (%)": margem_liquida_desejada,
                    "Dif. Margem Líquida (pp)": margem_liquida_desejada - margem_liquida_ideal,
                    "Ponto Equilíbrio (R$)": ponto_equilibrio,
                    "Volume Estimado": row["Volume Estimado"]
                })

        df_resultados = pd.DataFrame(resultados)
        
        # ========================================
        # SEÇÃO 4: RESULTADOS
        # ========================================
        st.success("✅ Análise completa gerada com sucesso!")
        
        # Tabela de resultados
        st.subheader("📋 Tabela Comparativa")
        st.dataframe(df_resultados.style.format({
            "Custo Unitário (R$)": "R$ {:.2f}",
            "Preço Ideal (R$)": "R$ {:.2f}", 
            "Preço Desejável (R$)": "R$ {:.2f}",
            "Markup Ideal": "{:.2f}x", 
            "Markup Desejável": "{:.2f}x",
            "Margem Contrib. Ideal (%)": "{:.1f}%",
            "Margem Contrib. Real (%)": "{:.1f}%",
            "Margem Líquida Ideal (%)": "{:.1f}%",
            "Margem Líquida Desejada (%)": "{:.1f}%",
            "Dif. Margem Líquida (pp)": "{:.1f} pp",
            "Ponto Equilíbrio (R$)": "R$ {:.2f}"
        }).applymap(lambda x: 'color: #4CAF50' if isinstance(x, (int, float)) and x > 0 else ('color: #FF5722' if x < 0 else ''), 
        subset=["Dif. Margem Líquida (pp)"]))
        
        # ========================================
        # SEÇÃO 5: GRÁFICOS COMPARATIVOS
        # ========================================
        st.subheader("📊 Visualização Comparativa")
        
        # Gráfico 1: Comparativo de Margens Líquidas
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        x = np.arange(len(df_resultados["Item"]))
        width = 0.35
        
        rects1 = ax1.bar(x - width/2, df_resultados["Margem Líquida Ideal (%)"], 
                        width, label='Margem Ideal', color='#4CAF50', alpha=0.9)
        rects2 = ax1.bar(x + width/2, df_resultados["Margem Líquida Desejada (%)"], 
                        width, label='Margem Desejada', color='#FF9800', alpha=0.9)
        
        ax1.set_ylabel('Margem Líquida (%)')
        ax1.set_title('Comparação: Margem Líquida Ideal vs. Margem com Preço Desejado')
        ax1.set_xticks(x)
        ax1.set_xticklabels(df_resultados["Item"])
        ax1.legend(loc='upper right')
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Adiciona valores nas barras
        for rect in rects1 + rects2:
            height = rect.get_height()
            ax1.annotate(f'{height:.1f}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        st.pyplot(fig1)
        
        # Gráfico 2: Comparativo de Preços
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        rects3 = ax2.bar(x - width/2, df_resultados["Preço Ideal (R$)"], 
                        width, label='Preço Ideal', color='#2196F3', alpha=0.9)
        rects4 = ax2.bar(x + width/2, df_resultados["Preço Desejável (R$)"], 
                        width, label='Preço Desejado', color='#9C27B0', alpha=0.9)
        
        ax2.set_ylabel('Valor (R$)')
        ax2.set_title('Comparação: Preço Ideal vs. Preço Desejado')
        ax2.set_xticks(x)
        ax2.set_xticklabels(df_resultados["Item"])
        ax2.legend(loc='upper right')
        ax2.grid(axis='y', linestyle='--', alpha=0.7)
        
        for rect in rects3 + rects4:
            height = rect.get_height()
            ax2.annotate(f'R$ {height:.2f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        st.pyplot(fig2)
        
        # ========================================
        # SEÇÃO 6: ANÁLISE DETALHADA
        # ========================================
        with st.expander("🔍 Detalhes Técnicos dos Cálculos", expanded=False):
            st.markdown("""
            ### 📝 Metodologia de Cálculo
            
            **1. Preço Ideal:**
            ```
            Preço Ideal = Custo Unitário × Markup Ideal
            Markup Ideal = 1 / (1 - Total de Percentuais)
            Total de Percentuais = Impostos + Taxas + Comissões + Lucro + Reserva
            ```
            
            **2. Margem Líquida Ideal:**
            ```
            Receita Líquida Ideal = Preço Ideal × (1 - Impostos - Taxas - Comissões)
            Custo Total = Custo Unitário + (Despesas Fixas / Número de Itens)
            Margem Líquida Ideal = (Receita Líquida Ideal - Custo Total) / Preço Ideal
            ```
            
            **3. Margem Líquida Desejada:**
            ```
            Receita Líquida Desejada = Preço Desejado × (1 - Impostos - Taxas - Comissões)
            Margem Líquida Desejada = (Receita Líquida Desejada - Custo Total) / Preço Desejado
            ```
            
            **4. Ponto de Equilíbrio:**
            ```
            Ponto de Equilíbrio = (Despesas Fixas Proporcionais + Custo Unitário) / 
                                 (1 - Impostos - Taxas - Comissões)
            ```
            """)

# ========================================
# INSTRUÇÕES PARA USO
# ========================================
with st.expander("ℹ️ Como usar este sistema", expanded=False):
    st.markdown("""
    1. **Preencha os dados gerais** da operação (impostos, taxas, etc.)
    2. **Cadastre cada item** com seu custo e volume estimado
    3. Clique em **"Calcular Precificação Completa"**
    4. **Ajuste os preços desejados** para cada item
    5. **Analise os resultados**:
       - Compare as margens ideais vs. desejadas
       - Verifique se os preços cobrem todos os custos
       - Identifique oportunidades de ajuste
    6. Utilize os **gráficos comparativos** para tomada de decisão
    """)

# Para executar:
# streamlit run precificacao_avancada.py