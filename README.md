# Analisador Inteligente de Vendas

Dashboard de análise de vendas feito com Python, Pandas, NumPy, Plotly e Streamlit.

## Funcionalidades
- Importação de CSV e Excel
- Limpeza básica dos dados
- Indicadores de faturamento, lucro estimado, unidades, ticket médio por registro e margem
- Ranking de produtos por volume, faturamento e lucro
- Evolução mensal e análise por mês do ano
- Exportação de resultados para CSV e Excel


## Formato dos dados

Colunas obrigatórias:
- `data`: data da venda
- `produto`: nome do produto
- `quantidade`: unidades vendidas
- `preco_unitario`: preço de venda por unidade
- `custo_unitario`: custo por unidade

Coluna opcional:
- `categoria`

Exemplo CSV:

```csv
data,produto,quantidade,preco_unitario,custo_unitario,categoria
2025-01-05,Café,3,18.00,8.00,Mercearia
2025-01-06,Chá,2,12.00,4.50,Mercearia
```

A aplicação tenta reconhecer algumas variações comuns nos nomes das colunas, mas use os nomes acima para evitar erros.

## Limitações importantes
- O lucro é uma estimativa: não desconta impostos, despesas fixas, frete, taxas ou devoluções separadamente.
- Cada linha é tratada como um registro de venda. Para calcular ticket médio real por pedido, adicione um identificador como `pedido_id` e agrupe por ele.
- Para concluir que existe sazonalidade, prefira comparar vários anos e períodos equivalentes.
- Os dados demonstrativos são artificiais e não representam uma loja real.

