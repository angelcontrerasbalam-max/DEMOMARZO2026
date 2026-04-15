import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- Configuración de la página --- #
st.set_page_config(page_title="Dashboard de Ventas", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: Dashboard de Análisis de Ventas")
st.markdown("##")

# --- Diccionario: Nombre completo → Abreviación (necesario para el mapa) --- #
state_abbrev = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
    "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

# --- Cargar datos --- #
file_path = 'datos/SalidaVentas.xlsx'
try:
    df = pd.read_excel(file_path)
except FileNotFoundError:
    st.error(f"Error: El archivo no se encontró en {file_path}. Asegúrate de que la ruta es correcta.")
    st.stop()

# --- Preprocesamiento de datos --- #
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month_name()

# --- Barra lateral para filtros --- #
st.sidebar.header("Filtros")

selected_regions = st.sidebar.multiselect(
    "Selecciona la(s) Región(es):",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

selected_categories = st.sidebar.multiselect(
    "Selecciona la(s) Categoría(s):",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

min_date = df['Order Date'].min().to_pydatetime()
max_date = df['Order Date'].max().to_pydatetime()

date_range = st.sidebar.slider(
    "Selecciona el Rango de Fechas:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

# --- Aplicar filtros --- #
df_selection = df.query(
    "Region == @selected_regions & Category == @selected_categories"
)

df_selection = df_selection[
    (df_selection['Order Date'] >= date_range[0]) & (df_selection['Order Date'] <= date_range[1])
]

# --- Verificar si hay datos después del filtrado --- #
if df_selection.empty:
    st.warning("No hay datos disponibles según los filtros seleccionados.")
    st.stop()

# --- Métricas Clave (KPIs) --- #
total_sales = df_selection["Sales"].sum()
total_profit = df_selection["Profit"].sum()
total_quantity = df_selection["Quantity"].sum()

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Total de Ventas:")
    st.subheader(f"$ {total_sales:,.2f}")

with col2:
    st.subheader("Ganancia Total:")
    st.subheader(f"$ {total_profit:,.2f}")

with col3:
    st.subheader("Cantidad Total:")
    st.subheader(f"{total_quantity:,.0f}")

st.markdown("---")

# --- Gráficos --- #

# 1. Ventas por Región
sales_by_region = df_selection.groupby("Region")["Sales"].sum().reset_index()
fig_region_sales = px.bar(
    sales_by_region,
    x="Region",
    y="Sales",
    title="**Ventas por Región**",
    color_discrete_sequence=px.colors.sequential.Plotly3,
    template="plotly_white"
)
fig_region_sales.update_layout(xaxis_title="Región", yaxis_title="Ventas ($)")
st.plotly_chart(fig_region_sales, use_container_width=True)

# 2. Ventas por Categoría
sales_by_category = df_selection.groupby("Category")["Sales"].sum().reset_index()
fig_category_sales = px.bar(
    sales_by_category,
    x="Category",
    y="Sales",
    title="**Ventas por Categoría**",
    color_discrete_sequence=px.colors.sequential.Viridis_r,
    template="plotly_white"
)
fig_category_sales.update_layout(xaxis_title="Categoría", yaxis_title="Ventas ($)")
st.plotly_chart(fig_category_sales, use_container_width=True)

# 3. Ventas por Sub-Categoría (Top 10)
sales_by_sub_category = df_selection.groupby("Sub-Category")["Sales"].sum().nlargest(10).reset_index()
fig_sub_category_sales = px.bar(
    sales_by_sub_category,
    x="Sub-Category",
    y="Sales",
    title="**Top 10 Ventas por Sub-Categoría**",
    color_discrete_sequence=px.colors.sequential.Plasma,
    template="plotly_white"
)
fig_sub_category_sales.update_layout(xaxis_title="Sub-Categoría", yaxis_title="Ventas ($)")
st.plotly_chart(fig_sub_category_sales, use_container_width=True)

# 4. Ventas a lo largo del tiempo (por mes/año)
df_selection['Order_Month_Year'] = df_selection['Order Date'].dt.to_period('M').astype(str)
sales_over_time = df_selection.groupby('Order_Month_Year')['Sales'].sum().reset_index()
sales_over_time['Order_Month_Year'] = pd.to_datetime(sales_over_time['Order_Month_Year'])
sales_over_time = sales_over_time.sort_values(by='Order_Month_Year')

fig_time_series = px.line(
    sales_over_time,
    x='Order_Month_Year',
    y='Sales',
    title='**Ventas a lo largo del tiempo**',
    template='plotly_white'
)
fig_time_series.update_layout(xaxis_title="Fecha de Pedido", yaxis_title="Ventas ($)")
st.plotly_chart(fig_time_series, use_container_width=True)

# 5. Mapa Coroplético de Ventas por Estado
sales_by_state = df_selection.groupby("State")["Sales"].sum().reset_index()

# ✅ Convertir nombres completos a abreviaciones
sales_by_state["State_Code"] = sales_by_state["State"].map(state_abbrev)

# ✅ Escala logarítmica: evita que California "apague" a todos los demás estados
# Todos los estados tendrán un color visible de rojo, proporcional a sus ventas reales
sales_by_state["Sales_Log"] = np.log10(sales_by_state["Sales"].clip(lower=1))

log_min = sales_by_state["Sales_Log"].min()
log_max = sales_by_state["Sales_Log"].max()

# Etiquetas para el colorbar mostrando valores reales (no logarítmicos)
tickvals = [3, 4, 5, 6]  # log10 equivale a $1K, $10K, $100K, $1M
ticktext = ["$1K", "$10K", "$100K", "$1M"]

fig_map = px.choropleth(
    sales_by_state,
    locations="State_Code",
    locationmode="USA-states",
    color="Sales_Log",                         # 🔴 Color basado en escala log
    hover_name="State",
    hover_data={"Sales": ":,.0f", "Sales_Log": False, "State_Code": False},
    color_continuous_scale=[
        [0.0, "#fee0d2"],   # Rojo muy claro (ventas bajas)
        [0.3, "#fc9272"],   # Rojo claro-medio
        [0.6, "#ef3b2c"],   # Rojo medio-fuerte
        [1.0, "#67000d"],   # Rojo muy oscuro (ventas altas)
    ],
    range_color=(log_min, log_max),
    title="**Ventas Totales por Estado**",
    scope="usa",
)
fig_map.update_layout(
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    coloraxis_colorbar=dict(
        title="Ventas ($)",
        tickvals=tickvals,
        ticktext=ticktext
    )
)
st.plotly_chart(fig_map, use_container_width=True)

# 6. Tabla de datos filtrados
st.markdown("### 📋 Datos Filtrados")
st.dataframe(df_selection, use_container_width=True)
