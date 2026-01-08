import pandas as pd
import streamlit as st

st.set_page_config(page_title="Dashboard Ventas", layout="wide")
st.title("Análisis de Ventas")
archivo = st.file_uploader("Sube tu archivo CSV", type=["csv"])

if archivo:

    df = pd.read_csv(archivo)
    pestana1, pestana2, pestana3, pestana4 = st.tabs(["Ventas", "Tienda", "Estado", "Comparativa"])

    with pestana1:

        st.header("Visión global")

        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Número de tiendas", df["store_nbr"].nunique())
            col2.metric("Productos vendidos", df["family"].nunique())
            col3.metric("Estados", df["state"].nunique())
            meses_disponibles = df[["year", "month"]].drop_duplicates()
            col4.metric("Meses disponibles", meses_disponibles.shape[0])

        with st.container():
            st.write("")
            st.header("Análisis medio")
            st.caption("RANKINGS")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Top 10 productos")
                data = df.groupby("family")["sales"].sum().sort_values(ascending=False).head(10)
                st.bar_chart(data)
            
            with col2:
                st.subheader("Ventas por tienda")
                data = df.groupby("store_nbr")["sales"].sum().sort_values(ascending=False).head(20)
                st.bar_chart(data)
            
            st.subheader("Top 10 tiendas de ventas en promoción")
            tiendas_promocion = df.loc[df["onpromotion"]>0, :]
            data = tiendas_promocion.groupby("store_nbr")["sales"].sum().sort_values(ascending=False).head(10)
            st.bar_chart(data)

        with st.container():
            st.header("Análisis de estacionalidad")
            st.caption("Patrones temporales")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Por día")
                data = df.groupby("day_of_week")["sales"].mean()
                st.bar_chart(data)
            
            with col2:
                st.subheader("Por semana")
                data = df.groupby("week")["sales"].mean().sort_index()
                st.line_chart(data)
            
            st.subheader("Por mes")
            data = df.groupby("month")["sales"].mean().sort_index()
            st.line_chart(data)

    with pestana2:

        st.header("Análisis por tienda")
        st.caption(("Selecciona una tienda para ver sus datos").upper())

        tienda = st.selectbox("Número de tienda", sorted(df["store_nbr"].unique()))
        data = df[df["store_nbr"] == tienda]


        total_ventas = data["sales"].sum()
        total_prod = data["family"].nunique()
        total_prod_promo = data.loc[data["onpromotion"] > 0, :]["family"].nunique()

        ventas_total = f"{total_ventas:,.0f}"

        with st.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Ventas totales", ventas_total)
            col2.metric("Productos vendidos", total_prod)
            col3.metric("Productos en promo", total_prod_promo)

        st.write("")
        st.subheader("Insights de la tienda")

        col1, col2, col3 = st.columns(3)
    
        with col1:
            st.caption("Ventas por año")
            ventas_ano = data.groupby("year")["sales"].sum().sort_index()
            st.bar_chart(ventas_ano)

        with col2:
            st.caption("Top productos vendidos")
            top_productos = data.groupby("family")["sales"].sum().sort_values(ascending=False).head(10)
            st.bar_chart(top_productos)

        with col3:
            st.caption("Top productos vendidos en promoción")
            data_promo = data.loc[data["onpromotion"] > 0, :]
            top_prod_promo = data_promo.groupby("family")["sales"].sum().sort_values(ascending=False).head(10)
            st.bar_chart(top_prod_promo)

    with pestana3:

        st.header("Análisis por estado")
        st.caption(("Selecciona un estado para ver sus datos").upper())

        estado = st.selectbox("Estado", sorted(df["state"].unique()))
        data = df[df["state"] == estado]

        total_ventas = data["sales"].sum()
        total_transacciones = data["transactions"].sum()
        total_tiendas = data["store_nbr"].nunique()

        ventas = f"{total_ventas:,.0f}"
        transacciones = f"{total_transacciones:,.0f}"

        with st.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Ventas totales", ventas)
            col2.metric("Transacciones", transacciones)
            col3.metric("Tiendas", total_tiendas)

        st.write("")
        st.subheader("Insights del estado")
        col1, col2 = st.columns(2)

        with col1:
            st.caption("Transacciones por año")
            transacciones_ano = data.groupby("year")["transactions"].sum().sort_index()
            st.bar_chart(transacciones_ano)

        with col2:
            st.caption("Top tiendas por ventas")
            top_tiendas = data.groupby("store_nbr")["sales"].sum().sort_values(ascending=False).head(10)
            st.bar_chart(top_tiendas)

        st.write("")

        left, center, right = st.columns([1, 3, 1])
        with center:
            st.caption("Producto más vendido por tienda")
            productos_tiendas = data.groupby(["store_nbr", "family"])["sales"].sum().reset_index()
            idx = productos_tiendas.groupby("store_nbr")["sales"].idxmax()
            top_producto_tienda = productos_tiendas.loc[idx].sort_values("sales", ascending=False).head(10)
            st.dataframe(top_producto_tienda.rename(columns={"store_nbr": "Tienda","family": "Producto","sales": "Ventas"}), use_container_width=True)

    with pestana4:
        st.header("Insights")
        st.caption(("Promoción vs No promoción").upper())

        col1, col2 = st.columns(2)

        with col1:
            estados = ["Todos"] + sorted(df["state"].unique())
            estado = st.selectbox("Estado", estados)

        with col2:
            years = ["Todos"] + sorted(df["year"].unique())
            year = st.selectbox("Año", years)

        data = df.copy()
        if estado != "Todos":
            data = data.loc[data["state"] == estado,:]
        if year != "Todos":
            data = data.loc[data["year"] == year,:]

        ventas_totales = data["sales"].sum()
        ventas_promocion = data.loc[data["onpromotion"] > 0, :]["sales"].sum()
        ventas_sin_promocion = data.loc[data["onpromotion"] == 0, :]["sales"].sum()

        ventas = f"{ventas_totales:,.0f}"
        promocion = f"{ventas_promocion:,.0f}"
        nopromocion = f"{ventas_sin_promocion:,.0f}"

        with st.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("Ventas totales", ventas)
            col2.metric("Ventas en promoción", promocion)
            col3.metric("Ventas sin promoción", nopromocion)

        st.write("")
        st.subheader("Impacto de ventas")
        col1, col2 = st.columns(2)

        with col1:
            st.caption("Evolución mensual de las ventas")
            data["year_month"] = data["year"].astype(str) + "-" + data["month"].astype(str).str.zfill(2)
            ventas_mensual =  data.groupby("year_month")["sales"].sum()
            st.line_chart(ventas_mensual)

        with col2:
            st.caption("Promoción vs No promoción")
            comparacion = pd.Series({"Promo": ventas_promocion, "No promo": ventas_sin_promocion})
            st.bar_chart(comparacion)

        st.write("")
  
        st.subheader("Productos con más ventas en promoción")
        st.caption("TOP 10")

        left, center, right = st.columns([1, 3, 1])
        with center:
            data_promo = data.loc[data["onpromotion"] > 0, :]
            top_promocion_productos = data_promo.groupby("family")["sales"].sum().sort_values(ascending=False).head(10)
            st.bar_chart(top_promocion_productos)
