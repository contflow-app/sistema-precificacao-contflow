
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np # Necessário para index_bar

st.set_page_config(page_title="Sistema de Precificação CONTFLOW", layout="centered")

st.title("💰 Sistema Interativo de Precificação")
st.markdown("""
Este sistema ajuda a calcular a **Margem de Contribuição Ideal** e analisar o **Preço de Venda Praticado**
com base nos custos, despesas, impostos e metas financeiras gerais.
""")

# --- 1. Informações Gerais ---
st.header("1. Informações Gerais da Empresa e Metas")
faturamento_previsto = st.number_input("Faturamento mensal previsto (R$)", min_value=1.0, value=10000.0, format="%.2f", help="Qual o faturamento total esperado por mês com todos os produtos/serviços?")
despesa_fixa_total = st.number_input("Total de despesas fixas mensais (R$)", min_value=0.0, value=2000.0, format="%.2f", help="Soma de todos os custos que não variam com a venda (Aluguel, salários fixos, pro-labore, etc.)")

st.subheader("Percentuais Médios Incidentes sobre a Venda")
col1, col2 = st.columns(2)
with col1:
    percentual_impostos = st.slider("% Impostos (Ex: Simples Nacional)", 0.0, 50.0, 6.0, step=0.5, help="Percentual médio de impostos sobre o faturamento.") / 100
    percentual_taxas = st.slider("% Taxas Variáveis (Cartão, Marketplace)", 0.0, 30.0, 5.0, step=0.5, help="Percentual médio de taxas que incidem sobre cada venda.") / 100
    percentual_comissao = st.slider("% Comissão sobre Vendas", 0.0, 50.0, 0.0, step=0.5, help="Percentual pago como comissão para vendedores.") / 100
with col2:
    percentual_lucro_desejado_sobre_faturamento = st.slider("% Lucro Líquido Alvo (sobre Faturamento)", 0.0, 100.0, 15.0, step=1.0, help="Qual a meta de lucro líquido total em relação ao faturamento previsto?") / 100
    percentual_reserva_sobre_faturamento = st.slider("% Reserva/Reinvestimento (sobre Faturamento)", 0.0, 50.0, 5.0, step=1.0, help="Qual a meta de reserva/reinvestimento em relação ao faturamento previsto?") / 100

# Calcula o percentual que as despesas fixas representam do faturamento previsto
percentual_custo_fixo_sobre_faturamento = despesa_fixa_total / faturamento_previsto if faturamento_previsto > 0 else 0

# Calcula o Lucro + Reserva em R$ esperado
valor_lucro_esperado = faturamento_previsto * percentual_lucro_desejado_sobre_faturamento
valor_reserva_esperado = faturamento_previsto * percentual_reserva_sobre_faturamento

# Calcula a Margem de Contribuição TOTAL necessária em R$
# MC Total = Custos Fixos + Lucro Desejado + Reserva Desejada
mc_total_necessaria_rs = despesa_fixa_total + valor_lucro_esperado + valor_reserva_esperado

# Calcula a Margem de Contribuição Média Percentual necessária sobre o faturamento
mc_media_necessaria_percentual = mc_total_necessaria_rs / faturamento_previsto if faturamento_previsto > 0 else 0

st.info(f"""
**Metas Globais (Baseadas no Faturamento Previsto de R$ {faturamento_previsto:,.2f}):**
- Despesas Fixas: R$ {despesa_fixa_total:,.2f} ({percentual_custo_fixo_sobre_faturamento*100:.1f}%)
- Lucro Líquido Alvo: R$ {valor_lucro_esperado:,.2f} ({percentual_lucro_desejado_sobre_faturamento*100:.1f}%)
- Reserva/Reinvestimento: R$ {valor_reserva_esperado:,.2f} ({percentual_reserva_sobre_faturamento*100:.1f}%)

**Margem de Contribuição Total Necessária:** R$ {mc_total_necessaria_rs:,.2f} ({mc_media_necessaria_percentual*100:.1f}% do Faturamento)
*Este é o valor total que a soma das vendas de todos os itens precisa gerar (após custos variáveis) para cobrir fixos, lucro e reserva.*
""")

# Verifica a viabilidade básica
percentual_variavel_total_medio = percentual_impostos + percentual_taxas + percentual_comissao
if mc_media_necessaria_percentual + percentual_variavel_total_medio >= 1:
     st.error(f"A Margem de Contribuição Média necessária ({mc_media_necessaria_percentual*100:.1f}%) somada aos custos variáveis percentuais médios ({percentual_variavel_total_medio*100:.1f}%) é igual ou maior que 100%. As metas são inviáveis com os custos/despesas informados. Revise os valores.")
     st.stop()


# --- 2. Produtos ou Serviços ---
st.header("2. Cadastro e Análise de Itens")
st.markdown("Adicione os itens, seus custos variáveis diretos e o preço de venda que você pratica ou deseja praticar.")
num_itens = st.number_input("Quantos itens diferentes deseja analisar?", min_value=1, max_value=50, value=1, step=1)

items_data = [] # Usaremos uma lista de dicionários para armazenar tudo

for i in range(num_itens):
    st.markdown("---")
    st.subheader(f"Item {i+1}")
    item_dict = {} # Dicionário para este item específico

    item_dict["Nome"] = st.text_input(f"Nome do Item {i+1}", key=f"nome_{i}", value=f"Produto {i+1}")
    item_dict["Custo Variável Unitário (R$)"] = st.number_input(f"Custo Variável Unitário Direto (R$) do Item {i+1}", min_value=0.01, format="%.2f", key=f"custo_{i}", value=50.0, help="Custo direto para produzir/adquirir uma unidade (matéria-prima, embalagem, mercadoria). Não inclua impostos/taxas aqui.")

    preco_praticado = st.number_input(
        f"Preço de Venda Praticado/Desejado (R$)",
        min_value=0.01,
        format="%.2f",
        value=item_dict["Custo Variável Unitário (R$)"] * 2, # Chute inicial
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

    # Margem de Contribuição (Praticada) = Preço Praticado - Custos Variáveis Totais
    contribuicao_praticada_rs = preco_praticado - custos_variaveis_totais_praticado
    item_dict["Margem Contribuição Praticada (R$)"] = contribuicao_praticada_rs
    contribuicao_praticada_perc = (contribuicao_praticada_rs / preco_praticado) * 100 if preco_praticado > 0 else 0
    item_dict["Margem Contribuição Praticada (%)"] = contribuicao_praticada_perc

    # --- Cálculo da Margem de Contribuição Ideal (%) ---
    # É a margem que o item PRECISA ter para cobrir sua parte dos custos variáveis
    # percentuais E ainda gerar a contribuição necessária para fixos+lucro+reserva.
    # MC Ideal % = 100% - Custo Var Direto % - Impostos % - Taxas % - Comissão %
    # Onde Custo Var Direto % é o Custo Unitário / Preço Ideal.
    # Para achar o Preço Ideal, usamos o conceito de Markup que inclui a MC Média Necessária.
    markup_divisor_ideal = 1 - (percentual_impostos + percentual_taxas + percentual_comissao + mc_media_necessaria_percentual)
    preco_ideal_calculado = 0
    if markup_divisor_ideal > 0 and custo_var_unit > 0 :
         preco_ideal_calculado = custo_var_unit / markup_divisor_ideal

         impostos_ideal = preco_ideal_calculado * percentual_impostos
         taxas_ideal = preco_ideal_calculado * percentual_taxas
         comissao_ideal = preco_ideal_calculado * percentual_comissao
         custos_variaveis_totais_ideal = custo_var_unit + impostos_ideal + taxas_ideal + comissao_ideal
         contribuicao_ideal_rs = preco_ideal_calculado - custos_variaveis_totais_ideal
         contribuicao_ideal_perc = (contribuicao_ideal_rs / preco_ideal_calculado) * 100 if preco_ideal_calculado > 0 else 0
         item_dict["Margem Contribuição Ideal (%)"] = contribuicao_ideal_perc
         item_dict["Preço Ideal Sugerido (R$)"] = preco_ideal_calculado
    else:
         item_dict["Margem Contribuição Ideal (%)"] = -999 # Valor indicando erro/inviabilidade
         item_dict["Preço Ideal Sugerido (R$)"] = 0
         st.warning(f"Não foi possível calcular o Preço/Margem Ideal para '{item_dict['Nome']}'. Verifique se as metas gerais e custos variáveis percentuais são viáveis.")


    # --- Expander com Detalhes do Cálculo (Preço Praticado) ---
    with st.expander(f"Ver detalhes do cálculo da Margem de Contribuição para '{item_dict['Nome']}' (Preço Praticado R$ {preco_praticado:.2f})"):
        st.markdown("**Receita Bruta (Preço de Venda Praticado):**")
        st.write(f"R$ {preco_praticado:.2f}")

        st.markdown("**(-) Custos e Despesas Variáveis:**")
        st.write(f"- Custo Variável Unitário Direto: R$ {custo_var_unit:.2f}")
        st.write(f"- Impostos ({percentual_impostos*100:.1f}%): R$ {impostos_praticado:.2f}")
        st.write(f"- Taxas Variáveis ({percentual_taxas*100:.1f}%): R$ {taxas_praticado:.2f}")
        st.write(f"- Comissão ({percentual_comissao*100:.1f}%): R$ {comissao_praticado:.2f}")
        st.markdown(f"**= (=) Margem de Contribuição Unitária:** R$ {contribuicao_praticada_rs:.2f} **({contribuicao_praticada_perc:.1f}%)**")
        st.caption(f"""
        Este é o valor que *esta unidade específica* contribui para:
        1. Pagar todas as Despesas Fixas da empresa (R$ {despesa_fixa_total:,.2f}/mês).
        2. Gerar o Lucro Líquido total desejado (Meta: R$ {valor_lucro_esperado:,.2f}/mês).
        3. Gerar a Reserva/Reinvestimento total (Meta: R$ {valor_reserva_esperado:,.2f}/mês).

        Compare a Margem de Contribuição Praticada ({contribuicao_praticada_perc:.1f}%) com a Ideal ({item_dict.get('Margem Contribuição Ideal (%)', 0):.1f}%).
        Se a praticada for menor, este item está contribuindo menos do que o necessário para atingir as metas gerais com o faturamento previsto.
        """)

    items_data.append(item_dict) # Adiciona o dicionário do item à lista

# --- 3. Resultados Consolidados ---
st.header("3. Resultados Consolidados")

if items_data:
    df_resultados = pd.DataFrame(items_data)

    # Reordenar colunas para melhor visualização
    cols_order = [
        "Nome", "Custo Variável Unitário (R$)", "Preço de Venda Praticado (R$)",
        "Margem Contribuição Praticada (R$)", "Margem Contribuição Praticada (%)",
        "Margem Contribuição Ideal (%)", "Preço Ideal Sugerido (R$)"
    ]
    df_resultados = df_resultados[cols_order]

    st.subheader("Tabela Comparativa")
    st.dataframe(df_resultados.style
                 .format({
                     "Custo Variável Unitário (R$)": "R$ {:,.2f}",
                     "Preço de Venda Praticado (R$)": "R$ {:,.2f}",
                     "Margem Contribuição Praticada (R$)": "R$ {:,.2f}",
                     "Margem Contribuição Praticada (%)": "{:.1f}%",
                     "Margem Contribuição Ideal (%)": "{:.1f}%",
                     "Preço Ideal Sugerido (R$)": "R$ {:,.2f}",
                 })
                 #.applymap(lambda x: 'color: red' if x < 0 else '', subset=["Margem Contribuição Praticada (%)"])
                 .apply(lambda s: ['background-color: rgba(255,0,0,0.1)' if s.name == "Margem Contribuição Praticada (%)" and v < s["Margem Contribuição Ideal (%)"] else '' for v in s], axis=1)
                 .apply(lambda s: ['background-color: rgba(255,165,0,0.1)' if s.name == "Margem Contribuição Praticada (%)" and v < 0 else '' for v in s], axis=1) # Destaca MC negativa
    )
    st.caption("Células da 'Margem Contribuição Praticada (%)' ficam vermelhas se estiverem abaixo da 'Ideal (%)' ou laranjas se forem negativas.")


    # --- Gráficos Comparativos ---
    st.subheader("📊 Gráficos Comparativos")
    df_plot = df_resultados.set_index("Nome")

    # Gráfico de Margem de Contribuição (%)
    fig_mc, ax_mc = plt.subplots(figsize=(max(6, len(df_plot)*0.8), 4)) # Ajusta largura
    bar_width = 0.35
    index_bar = np.arange(len(df_plot)) # Usar numpy arange para posições

    bar1 = ax_mc.bar(index_bar - bar_width/2, df_plot["Margem Contribuição Ideal (%)"], bar_width, label='MC Ideal (%)', color='skyblue')
    bar2 = ax_mc.bar(index_bar + bar_width/2, df_plot["Margem Contribuição Praticada (%)"], bar_width, label='MC Praticada (%)', color='lightcoral')

    ax_mc.set_ylabel('Margem de Contribuição (%)')
    ax_mc.set_title('Margem de Contribuição: Ideal vs. Praticada')
    ax_mc.set_xticks(index_bar)
    ax_mc.set_xticklabels(df_plot.index, rotation=45, ha="right")
    ax_mc.legend()
    ax_mc.axhline(0, color='grey', linewidth=0.8) # Linha zero
    # Adiciona linha da MC Média Necessária
    ax_mc.axhline(mc_media_necessaria_percentual*100, color='blue', linestyle='--', linewidth=0.8, label=f'MC Média Nec. ({mc_media_necessaria_percentual*100:.1f}%)')
    ax_mc.legend()


    fig_mc.tight_layout()
    st.pyplot(fig_mc)

    # Gráfico de Preços (R$)
    fig_p, ax_p = plt.subplots(figsize=(max(6, len(df_plot)*0.8), 4)) # Ajusta largura

    bar3 = ax_p.bar(index_bar - bar_width/2, df_plot["Preço Ideal Sugerido (R$)"], bar_width, label='Preço Ideal (R$)', color='mediumseagreen')
    bar4 = ax_p.bar(index_bar + bar_width/2, df_plot["Preço de Venda Praticado (R$)"], bar_width, label='Preço Praticado (R$)', color='sandybrown')
    bar5 = ax_p.bar(index_bar, df_plot["Custo Variável Unitário (R$)"], bar_width*0.6, label='Custo Variável (R$)', color='grey', alpha=0.7) # Barra de custo

    ax_p.set_ylabel('Valor (R$)')
    ax_p.set_title('Preços: Ideal vs. Praticado vs. Custo Variável')
    ax_p.set_xticks(index_bar)
    ax_p.set_xticklabels(df_plot.index, rotation=45, ha="right")
    ax_p.legend()

    fig_p.tight_layout()
    st.pyplot(fig_p)


else:
    st.warning("Cadastre pelo menos um item para ver os resultados consolidados.")