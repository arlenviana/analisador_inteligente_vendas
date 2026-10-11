# Analisador Inteligente de Vendas

Dashboard de análise de vendas feito com Python, Pandas, NumPy, Plotly e Streamlit.

## Funcionalidades
- Importação de CSV e Excel
- Limpeza básica dos dados
- Indicadores de faturamento, lucro estimado, unidades, ticket médio por registro e margem
- Ranking de produtos por volume, faturamento e lucro
- Evolução mensal e análise por mês do ano
- Exportação de resultados para CSV e Excel



## Limitações importantes
- O lucro é uma estimativa: não desconta impostos, despesas fixas, frete, taxas ou devoluções separadamente.
- Cada linha é tratada como um registro de venda. Para calcular ticket médio real por pedido, adicione um identificador como `pedido_id` e agrupe por ele.
- Para concluir que existe sazonalidade, prefira comparar vários anos e períodos equivalentes.
- Os dados demonstrativos são artificiais e não representam uma loja real.

