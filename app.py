from io import BytesIO
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Analisador de Vendas", page_icon="📊", layout="wide")

REQUIRED = {"data", "produto", "quantidade", "preco_unitario", "custo_unitario"}

def sample_data():
    rng = np.random.default_rng(42)
    dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
    products = [
        ("Café", 18.0, 8.0), ("Chá", 12.0, 4.5), ("Biscoito", 7.5, 3.2),
        ("Chocolate", 9.0, 4.0), ("Suco", 8.0, 3.0), ("Pão", 6.0, 2.2),
        ("Queijo", 22.0, 13.0), ("Arroz", 28.0, 21.0)
    ]
    rows = []
    for _ in range(1800):
        date = rng.choice(dates)
        name, price, cost = products[int(rng.integers(0, len(products)))]
        seasonal = 1.35 if pd.Timestamp(date).month in [11, 12] else 1.0
        qty = max(1, int(rng.poisson(3 * seasonal)))
        discount = rng.choice([0, 0, 0, 0.05, 0.1])
        rows.append({
            "data": date,
            "produto": name,
            "quantidade": qty,
            "preco_unitario": round(price * (1 - discount), 2),
            "custo_unitario": cost,
            "categoria": "Alimentos"
        })
    return pd.DataFrame(rows)

def normalize_columns(df):
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    aliases = {
        "date": "data", "data_venda": "data", "product": "produto", "product_name": "produto",
        "qty": "quantidade", "quantity": "quantidade", "preco": "preco_unitario",
        "preço_unitário": "preco_unitario", "unit_price": "preco_unitario",
        "custo": "custo_unitario", "unit_cost": "custo_unitario"
    }
    return df.rename(columns={c: aliases.get(c, c) for c in df.columns})

def prepare_data(df):
    df = normalize_columns(df)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(sorted(missing)))
    df["data"] = pd.to_datetime(df["data"], errors="coerce", dayfirst=True)
    for col in ["quantidade", "preco_unitario", "custo_unitario"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["produto"] = df["produto"].astype("string").str.strip()
    df = df.dropna(subset=["data", "produto", "quantidade", "preco_unitario", "custo_unitario"])
    df = df[(df["quantidade"] > 0) & (df["preco_unitario"] >= 0) & (df["custo_unitario"] >= 0)]
    df["faturamento"] = df["quantidade"] * df["preco_unitario"]
    df["custo_total"] = df["quantidade"] * df["custo_unitario"]
    df["lucro"] = df["faturamento"] - df["custo_total"]
    df["margem_pct"] = np.where(df["faturamento"] > 0, 100 * df["lucro"] / df["faturamento"], 0)
    df["mes"] = df["data"].dt.to_period("M").dt.to_timestamp()
    return df.sort_values("data")

st.title("📊 Analisador Inteligente de Vendas")
st.caption("Explore faturamento, lucratividade, produtos campeões e padrões sazonais.")

with st.sidebar:
    st.header("Dados")
    uploaded = st.file_uploader("Importe CSV ou Excel", type=["csv", "xlsx"])
    st.caption("Sem arquivo? Use os dados demonstrativos.")
    st.divider()
    st.markdown("**Formato esperado**")
    st.code("data, produto, quantidade, preco_unitario, custo_unitario", language="text")

if uploaded:
    try:
        raw = pd.read_csv(uploaded, sep=None, engine="python") if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
        df = prepare_data(raw)
    except Exception as e:
        st.error(f"Não foi possível processar o arquivo: {e}")
        st.stop()
else:
    df = prepare_data(sample_data())
    st.info("Você está visualizando dados fictícios de demonstração. Importe sua própria planilha na barra lateral.")

if df.empty:
    st.warning("Não há linhas válidas após a limpeza dos dados.")
    st.stop()

with st.sidebar:
    min_date, max_date = df["data"].min().date(), df["data"].max().date()
    date_range = st.date_input("Período", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    products = sorted(df["produto"].dropna().unique().tolist())
    selected_products = st.multiselect("Produtos", products, default=products)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

filtered = df[
    df["data"].dt.date.between(start_date, end_date)
    & df["produto"].isin(selected_products)
].copy()

if filtered.empty:
    st.warning("Nenhuma venda corresponde aos filtros selecionados.")
    st.stop()

revenue = filtered["faturamento"].sum()
profit = filtered["lucro"].sum()
units = filtered["quantidade"].sum()
orders = len(filtered)
ticket = revenue / orders if orders else 0
margin = 100 * profit / revenue if revenue else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Faturamento", f"R$ {revenue:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
k2.metric("Lucro estimado", f"R$ {profit:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
k3.metric("Unidades vendidas", f"{units:,.0f}".replace(",", "."))
k4.metric("Ticket médio por registro", f"R$ {ticket:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
k5.metric("Margem de lucro", f"{margin:.1f}%")

st.divider()
left, right = st.columns(2)

monthly = filtered.groupby("mes", as_index=False).agg(
    faturamento=("faturamento", "sum"), lucro=("lucro", "sum"), unidades=("quantidade", "sum")
)
with left:
    st.subheader("Evolução mensal")
    monthly_long = monthly.melt(id_vars="mes", value_vars=["faturamento", "lucro"],
                                var_name="indicador", value_name="valor")
    fig = px.line(monthly_long, x="mes", y="valor", color="indicador", markers=True,
                  labels={"mes": "Mês", "valor": "Valor (R$)", "indicador": "Indicador"})
    st.plotly_chart(fig, use_container_width=True)

product_stats = filtered.groupby("produto", as_index=False).agg(
    unidades=("quantidade", "sum"), faturamento=("faturamento", "sum"),
    lucro=("lucro", "sum"), custo=("custo_total", "sum")
)
product_stats["margem_pct"] = np.where(product_stats["faturamento"] > 0,
                                       product_stats["lucro"] / product_stats["faturamento"] * 100, 0)
with right:
    st.subheader("Produtos mais vendidos")
    top = product_stats.nlargest(10, "unidades").sort_values("unidades")
    fig = px.bar(top, x="unidades", y="produto", orientation="h",
                 labels={"unidades": "Unidades vendidas", "produto": "Produto"})
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Sazonalidade por mês do ano")
season = filtered.groupby(filtered["data"].dt.month).agg(
    faturamento=("faturamento", "sum"), unidades=("quantidade", "sum")
).reset_index(names="numero_mes")
month_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
season["mes"] = season["numero_mes"].map(lambda x: month_names[int(x)-1])
fig = px.bar(season, x="mes", y="faturamento", labels={"mes": "Mês", "faturamento": "Faturamento (R$)"})
st.plotly_chart(fig, use_container_width=True)
st.caption("A sazonalidade compara os meses selecionados somando os anos disponíveis; períodos com quantidades diferentes de dias podem afetar a comparação.")

st.subheader("Rentabilidade por produto")
st.dataframe(
    product_stats.sort_values("lucro", ascending=False).style.format({
        "unidades": "{:,.0f}", "faturamento": "R$ {:,.2f}", "lucro": "R$ {:,.2f}",
        "custo": "R$ {:,.2f}", "margem_pct": "{:.1f}%"
    }),
    use_container_width=True, hide_index=True
)

best_revenue = product_stats.loc[product_stats["faturamento"].idxmax()]
best_profit = product_stats.loc[product_stats["lucro"].idxmax()]
best_units = product_stats.loc[product_stats["unidades"].idxmax()]
peak_month = monthly.loc[monthly["faturamento"].idxmax()] if not monthly.empty else None

st.subheader("Resumo automático")
st.markdown(
    f"- **Maior faturamento por produto:** {best_revenue['produto']} (R$ {best_revenue['faturamento']:,.2f}).\n"
    f"- **Maior lucro por produto:** {best_profit['produto']} (R$ {best_profit['lucro']:,.2f}).\n"
    f"- **Maior volume vendido:** {best_units['produto']} ({best_units['unidades']:,.0f} unidades).\n"
    + (f"- **Melhor mês no período:** {peak_month['mes'].strftime('%m/%Y')} (R$ {peak_month['faturamento']:,.2f})." if peak_month is not None else "")
)

def brl(x):
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

report = BytesIO()
with pd.ExcelWriter(report, engine="openpyxl") as writer:
    filtered.to_excel(writer, sheet_name="Vendas tratadas", index=False)
    product_stats.sort_values("lucro", ascending=False).to_excel(writer, sheet_name="Resumo por produto", index=False)
    monthly.to_excel(writer, sheet_name="Resumo mensal", index=False)
report.seek(0)

csv_bytes = product_stats.sort_values("lucro", ascending=False).to_csv(index=False).encode("utf-8-sig")
st.subheader("Exportar resultados")
c1, c2 = st.columns(2)
c1.download_button("⬇️ Baixar resumo CSV", data=csv_bytes, file_name="resumo_vendas.csv", mime="text/csv")
c2.download_button("⬇️ Baixar relatório Excel", data=report.getvalue(), file_name="relatorio_vendas.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with st.expander("Como interpretar os resultados"):
    st.markdown("""
    - **Faturamento:** soma de quantidade × preço unitário.
    - **Lucro estimado:** faturamento menos custo unitário × quantidade. Não inclui despesas fixas, impostos, frete ou taxas, a menos que estejam incorporados nos custos.
    - **Margem:** lucro estimado dividido pelo faturamento.
    - **Ticket médio por registro:** faturamento dividido pelo número de linhas de venda; não equivale necessariamente ao ticket por pedido, pois o arquivo precisa ter um identificador de pedido para isso.
    - **Sazonalidade:** padrões recorrentes exigem dados de vários períodos comparáveis; correlação visual não prova causalidade.
    """)
