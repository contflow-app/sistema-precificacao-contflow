
# improved_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sistema de Precificação CONTFLOW", layout="centered")

st.title("💰 Sistema Interativo de Precificação")
st.markdown("""
Este sistema ajuda a calcular o **preço ideal de venda** e analisar o **preço desejável**
com base em custos, despesas, impostos e margem de lucro desejada.
Preencha os campos abaixo para obter recomendações personalizadas.
""")

# --- 1. Informações Gerais ---
st.header("1. Informações Gerais da Empresa")
faturamento_previsto = st.number_input("Faturamento mensal previsto (R$)", min_value=0.0, value=10000.0, format="%.2f", help="Qual o faturamento total esperado por mês?")
despesa_fixa_total = st.number_input("Total de despesas fixas mensais (R$)", min_value=0.0, value=2000.0, format="%.2f", help="Soma de todos os custos que não variam com a venda (Aluguel, salários fixos, pro-labore, etc.)")

st.subheader("Percentuais Incidentes sobre a Venda")
col1, col2 = st.columns(2)
with col1:
    percentual_impostos = st.slider("% Impostos (Ex: Simples Nacional)", 0.0, 50.0, 6.0, step=0.5, help="Percentual médio de impostos sobre o faturamento.") / 100
    percentual_taxas = st.slider("% Taxas Variáveis (Cartão, Marketplace)", 0.0, 30.0, 5.0, step=0.5, help="Percentual médio de taxas que incidem sobre cada venda.") / 100
    percentual_comissao = st.slider("% Comissão sobre Vendas", 0.0, 50.0, 0.0, step=0.5, help="Percentual pago como comissão para vendedores.") / 100
with col2:
    percentual_lucro = st.slider("% Lucro Líquido Desejado", 0.0, 100.0, 15.0, step=1.0, help="Qual a margem de lucro líquido que você almeja sobre o preço?") / 100
    percentual_reserva = st.slider("% Reserva/Reinvestimento", 0.0, 50.0, 5.0, step=1.0, help="Percentual do preço para guardar ou reinvestir.") / 100

# Calcula o percentual que as despesas fixas representam do faturamento previsto
percentual_custo_fixo_sobre_faturamento = despesa_fixa_total / faturamento_previsto if faturamento_previsto > 0 else 0

# Soma todos os percentuais que "saem" do preço de venda (exceto custo variável)
percentual_total_sobre_venda = (
    percentual_custo_fixo_sobre_faturamento +
    percentual_impostos +
    percentual_taxas +
    percentual_comissao +
    percentual_lucro +
    percentual_reserva
)

st.info(f"Percentual total sobre a venda (Custo Fixo + Impostos + Taxas + Comissão + Lucro + Reserva): {percentual_total_sobre_venda*100:.2f}%")

# Verifica se a soma dos percentuais não ultrapassa 100%
if percentual_total_sobre_venda >= 1:
    st.error(f"A soma dos percentuais ({percentual_total_sobre_venda*100:.2f}%) não pode ser igual ou maior que 100%. Ajuste os valores (principalmente o % de Lucro ou Faturamento Previsto).")
    st.stop() # Interrompe a execução se os percentuais forem inviáveis

# Calcula o Markup Ideal
# Markup é o índice que multiplicado pelo custo variável resulta no preço de venda ideal
markup_divisor = 1 - (
    percentual_impostos +
    percentual_taxas +
    percentual_comissao +
    percentual_lucro +
    percentual_reserva +
    percentual_custo_fixo_sobre_faturamento # Inclui a "parcela" do custo fixo
)
markup_ideal = 1 / markup_divisor if markup_divisor > 0 else 0


# --- 2. Produtos ou Serviços ---
st.header("2. Cadastro de Produtos ou Serviços")
st.markdown("Adicione os itens que deseja precificar e informe o custo variável de cada um.")
num_itens = st.number_input("Quantos itens diferentes deseja cadastrar?", min_value=1, max_value=50, value=1, step=1)

data = []
for i in range(num_itens):
    st.subheader(f"Item {i+1}")
    nome = st.text_input(f"Nome do Item {i+1}", key=f"nome_{i}", value=f"Produto {i+1}")
    custo_unitario = st.number_input(f"Custo Variável Unitário (R$) do Item {i+1}", min_value=0.01, format="%.2f", key=f"custo_{i}", value=50.0, help="Custo direto para produzir uma unidade ou prestar um serviço (matéria-prima, embalagem, etc.).")
    data.append({"Item": nome, "Custo Unitário (R$)": custo_unitario})

df_itens = pd.DataFrame(data)

# --- 3. Cálculos e Resultados ---
st.header("3. Resultados da Precificação")

if faturamento_previsto > 0 and not df_itens.empty and markup_ideal > 0:

    # --- Cálculo do Ponto de Equilíbrio ---
    # Margem de Contribuição Média Percentual (considerando apenas custos/despesas variáveis percentuais)
    percentual_custos_variaveis_sobre_venda = percentual_impostos + percentual_taxas + percentual_comissao
    margem_contribuicao_media_percentual = 1 - percentual_custos_variaveis_sobre_venda

    # Ponto de equilíbrio financeiro (quanto faturar para cobrir custos fixos e variáveis)
    # Nota: Este cálculo é simplificado e assume que a margem de contribuição % é constante em todas as vendas.
    # Uma análise mais precisa exigiria a margem de contribuição individual e o mix de vendas.
    ponto_equilibrio_financeiro = 0
    if margem_contribuicao_media_percentual > 0:
        ponto_equilibrio_financeiro = despesa_fixa_total / margem_contribuicao_media_percentual

    st.subheader("Análise Geral")
    st.metric("Markup Multiplicador Ideal", f"{markup_ideal:.2f}x", help="Multiplique este valor pelo Custo Variável Unitário para achar o Preço Ideal que cubra todos os custos, despesas, impostos e lucro desejado, baseado no faturamento previsto.")
    st.metric("Ponto de Equilíbrio Financeiro Estimado", f"R$ {ponto_equilibrio_financeiro:.2f}", help="Faturamento mínimo mensal necessário para cobrir Despesas Fixas e Custos Variáveis Percentuais (Impostos, Taxas, Comissões). Abaixo disso, há prejuízo.")
    st.markdown(f"**Atenção:** O Ponto de Equilíbrio acima é uma estimativa. Ele assume que a proporção de custos variáveis percentuais ({percentual_custos_variaveis_sobre_venda*100:.1f}%) se mantém constante em todo o faturamento. Ele não considera o custo variável unitário específico de cada produto.")


    # --- Cálculos por Item ---
    st.subheader("Precificação por Item")

    preco_ideal_list = []
    preco_desejavel_list = []
    markup_desejavel_list = []
    margem_contribuicao_ideal_list = []
    margem_liquida_ideal_list = []
    margem_contribuicao_desejavel_list = []
    margem_liquida_desejavel_list = []

    # **Alocação Simplificada do Custo Fixo por Item**
    # Dividindo igualmente entre os TIPOS de item.
    # ATENÇÃO: Esta é uma simplificação! O ideal seria alocar baseado no volume de vendas esperado de cada item.
    # Usaremos isso apenas para o cálculo da "margem líquida" individual, com ressalvas.
    despesas_fixas_unit_alocada = despesa_fixa_total / num_itens if num_itens > 0 else 0

    for index, row in df_itens.iterrows():
        custo_var_unit = row["Custo Unitário (R$)"]

        # --- Cálculos para o Preço Ideal ---
        preco_ideal = custo_var_unit * markup_ideal
        preco_ideal_list.append(preco_ideal)

        impostos_i = preco_ideal * percentual_impostos
        taxas_i = preco_ideal * percentual_taxas
        comissao_i = preco_ideal * percentual_comissao

        # Margem de Contribuição Ideal = Preço Ideal - Custos Variáveis (Unitário + Percentuais)
        custos_variaveis_totais_i = custo_var_unit + impostos_i + taxas_i + comissao_i
        contribuicao_i = preco_ideal - custos_variaveis_totais_i
        margem_contrib_percentual_i = (contribuicao_i / preco_ideal) * 100 if preco_ideal > 0 else 0
        margem_contribuicao_ideal_list.append(margem_contrib_percentual_i)

        # Lucro Líquido Ideal (APÓS alocação SIMPLIFICADA do fixo)
        lucro_final_i = contribuicao_i - despesas_fixas_unit_alocada
        margem_liquida_percentual_i = (lucro_final_i / preco_ideal) * 100 if preco_ideal > 0 else 0
        margem_liquida_ideal_list.append(margem_liquida_percentual_i)


        # --- Input e Cálculos para o Preço Desejável ---
        st.markdown("---")
        st.markdown(f"#### Item: {row['Item']}")
        col_preco1, col_preco2 = st.columns([0.7, 0.3]) # Coluna maior para input, menor para ideal
        with col_preco1:
             preco_desejavel = st.number_input(
                f"Preço de Venda Desejável para '{row['Item']}' (R$)",
                min_value=0.01,
                format="%.2f",
                value=preco_ideal, # Sugere o preço ideal como valor inicial
                key=f"preco_desejavel_{index}"
            )
        with col_preco2:
            st.metric("Preço Ideal Calculado", f"R$ {preco_ideal:.2f}")

        preco_desejavel_list.append(preco_desejavel)

        markup_desejavel = preco_desejavel / custo_var_unit if custo_var_unit > 0 else 0
        markup_desejavel_list.append(markup_desejavel)

        impostos_d = preco_desejavel * percentual_impostos
        taxas_d = preco_desejavel * percentual_taxas
        comissao_d = preco_desejavel * percentual_comissao

        # Margem de Contribuição Desejável = Preço Desejável - Custos Variáveis (Unitário + Percentuais)
        custos_variaveis_totais_d = custo_var_unit + impostos_d + taxas_d + comissao_d
        contribuicao_d = preco_desejavel - custos_variaveis_totais_d
        margem_contrib_percentual_d = (contribuicao_d / preco_desejavel) * 100 if preco_desejavel > 0 else 0
        margem_contribuicao_desejavel_list.append(margem_contrib_percentual_d)

        # Lucro Líquido Desejável (APÓS alocação SIMPLIFICADA do fixo)
        lucro_final_d = contribuicao_d - despesas_fixas_unit_alocada
        margem_liquida_percentual_d = (lucro_final_d / preco_desejavel) * 100 if preco_desejavel > 0 else 0
        margem_liquida_desejavel_list.append(margem_liquida_percentual_d)

        # --- Expander com Detalhes do Cálculo (Preço Desejável) ---
        with st.expander(f"Ver detalhes do cálculo para '{row['Item']}' com Preço Desejável (R$ {preco_desejavel:.2f})"):
            st.markdown("**Receita Bruta (Preço de Venda):**")
            st.write(f"R$ {preco_desejavel:.2f}")

            st.markdown("**(-) Custos Variáveis:**")
            st.write(f"- Custo Variável Unitário Direto: R$ {custo_var_unit:.2f}")
            st.write(f"- Impostos ({percentual_impostos*100:.1f}%): R$ {impostos_d:.2f}")
            st.write(f"- Taxas Variáveis ({percentual_taxas*100:.1f}%): R$ {taxas_d:.2f}")
            st.write(f"- Comissão ({percentual_comissao*100:.1f}%): R$ {comissao_d:.2f}")
            st.markdown(f"**= (=) Margem de Contribuição Unitária:** R$ {contribuicao_d:.2f} ({margem_contrib_percentual_d:.1f}%)")
            st.caption("Este valor representa quanto sobra de cada venda deste item para cobrir os custos fixos e gerar lucro.")

            st.markdown("**(-) Custo Fixo Alocado (Simplificado):**")
            st.write(f"- Parcela do Custo Fixo Total (R$ {despesa_fixa_total:.2f} / {num_itens} itens): R$ {despesas_fixas_unit_alocada:.2f}")
            st.caption("Atenção: Custo fixo alocado igualmente entre os tipos de item cadastrados. Uma análise real dependeria do volume de vendas de cada um.")

            st.markdown(f"**= (=) Lucro Líquido Unitário Estimado:** R$ {lucro_final_d:.2f}")
            st.markdown(f"**Margem Líquida Estimada:** {margem_liquida_percentual_d:.1f}%")

    # Adiciona as colunas calculadas ao DataFrame
    df_itens["Preço Ideal Sugerido (R$)"] = preco_ideal_list
    df_itens["Preço de Venda Praticado (R$)"] = preco_desejavel_list
    df_itens["Markup Ideal"] = markup_ideal # É o mesmo para todos baseado nas premissas gerais
    df_itens["Markup Praticado"] = markup_desejavel_list
    df_itens["Margem Contribuição Ideal (%)"] = margem_contribuicao_ideal_list
    df_itens["Margem Contribuição Praticada (%)"] = margem_contribuicao_desejavel_list
    df_itens["Margem Líquida Ideal Estimada (%)"] = margem_liquida_ideal_list
    df_itens["Margem Líquida Praticada Estimada (%)"] = margem_liquida_desejavel_list


    # --- Exibição da Tabela de Resultados ---
    st.subheader("Tabela Comparativa de Preços e Margens")
    st.dataframe(df_itens.style
                 .format({
                     "Custo Unitário (R$)": "R$ {:,.2f}",
                     "Preço Ideal Sugerido (R$)": "R$ {:,.2f}",
                     "Preço de Venda Praticado (R$)": "R$ {:,.2f}",
                     "Markup Ideal": "{:.2f}x",
                     "Markup Praticado": "{:.2f}x",
                     "Margem Contribuição Ideal (%)": "{:.1f}%",
                     "Margem Contribuição Praticada (%)": "{:.1f}%",
                     "Margem Líquida Ideal Estimada (%)": "{:.1f}%",
                     "Margem Líquida Praticada Estimada (%)": "{:.1f}%"
                 })
                 .highlight_between(subset=["Margem Líquida Praticada Estimada (%)"], color='rgba(255,0,0,0.1)', right=0) # Destaca margens negativas
                 .highlight_between(subset=["Margem Contribuição Praticada (%)"], color='rgba(255,165,0,0.1)', right=0) # Destaca margens de contribuição negativas
    )
    st.caption("Margens Líquidas Estimadas consideram a alocação simplificada do custo fixo.")


    # --- Gráficos Comparativos ---
    st.subheader("📊 Gráficos Comparativos")

    # Gráfico de Margem de Contribuição
    fig_mc, ax_mc = plt.subplots(figsize=(max(6, num_itens*1.5), 4)) # Ajusta largura
    bar_width = 0.35
    index_bar = df_itens.index
    bar1 = ax_mc.bar(index_bar - bar_width/2, df_itens["Margem Contribuição Ideal (%)"], bar_width, label='MC Ideal', color='skyblue')
    bar2 = ax_mc.bar(index_bar + bar_width/2, df_itens["Margem Contribuição Praticada (%)"], bar_width, label='MC Praticada', color='lightcoral')

    ax_mc.set_ylabel('Margem de Contribuição (%)')
    ax_mc.set_title('Comparativo: Margem de Contribuição Ideal vs. Praticada')
    ax_mc.set_xticks(index_bar)
    ax_mc.set_xticklabels(df_itens["Item"], rotation=45, ha="right")
    ax_mc.legend()
    ax_mc.axhline(0, color='grey', linewidth=0.8) # Linha zero
    fig_mc.tight_layout()
    st.pyplot(fig_mc)

    # Gráfico de Margem Líquida (Estimada)
    fig_ml, ax_ml = plt.subplots(figsize=(max(6, num_itens*1.5), 4)) # Ajusta largura
    bar3 = ax_ml.bar(index_bar - bar_width/2, df_itens["Margem Líquida Ideal Estimada (%)"], bar_width, label='ML Ideal Estimada', color='mediumseagreen')
    bar4 = ax_ml.bar(index_bar + bar_width/2, df_itens["Margem Líquida Praticada Estimada (%)"], bar_width, label='ML Praticada Estimada', color='sandybrown')

    ax_ml.set_ylabel('Margem Líquida Estimada (%)')
    ax_ml.set_title('Comparativo: Margem Líquida Estimada Ideal vs. Praticada')
    ax_ml.set_xticks(index_bar)
    ax_ml.set_xticklabels(df_itens["Item"], rotation=45, ha="right")
    ax_ml.legend()
    ax_ml.axhline(0, color='grey', linewidth=0.8) # Linha zero
    fig_ml.tight_layout()
    st.pyplot(fig_ml)


else:
    st.warning("Preencha as Informações Gerais (Faturamento > 0) e cadastre pelo menos um item para ver os resultados.")