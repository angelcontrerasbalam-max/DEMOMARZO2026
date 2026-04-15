import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración de la página --- #
st.set_page_config(page_title="Dashboard de Ventas", page_icon=":bar_chart:", layout="wide")

st.title(":bar_chart: Dashboard de Análisis de Ventas")
st.markdown("##")

# --- Cargar datos --- #
# Asegúrate de que esta ruta sea accesible si ejecutas en Colab o ajusta para local
file_path = 'datos/SalidaVentas.xlsx'

# --- Preprocesamiento de datos (si es necesario) --- #
# Asegurar que las columnas de fecha sean de tipo datetime
df['Order Date'] = pd.to_datetime(df['Order Date'])

# Añadir columnas útiles para filtros de tiempo
df['Year'] = df['Order Date'].dt.year
df['Month'] = df['Order Date'].dt.month_name()

# --- Barra lateral para filtros --- #
st.sidebar.header("Filtros")

# Filtro por Región
selected_regions = st.sidebar.multiselect(
    "Selecciona la(s) Región(es):",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

# Filtro por Categoría
selected_categories = st.sidebar.multiselect(
    "Selecciona la(s) Categoría(s):",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

# Filtro por Rango de Fechas
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
    "Region == @selected_regions & Category == @selected_categories "
)

df_selection = df_selection[
    (df_selection['Order Date'] >= date_range[0]) & (df_selection['Order Date'] <= date_range[1])
]

# --- Verificar si hay datos después del filtrado --- #
if df_selection.empty:
    st.warning("No hay datos disponibles según los filtros seleccionados.")
    st.stop() # Detiene la ejecución si no hay datos

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

st.markdown("--- #")

# --- Gráficos --- #

# 1. Ventas por Región
sales_by_region = df_selection.groupby("Region")["Sales"].sum().reset_index()
fig_region_sales = px.bar(
    sales_by_region, 
    x="Region", 
    y="Sales", 
    title="**Ventas por Región**",
    color_discrete_sequence=px.colors.sequential.Plotly3, # Utiliza una secuencia de colores
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
    color_discrete_sequence=px.colors.sequential.Viridis_r, # Otra secuencia de colores
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
# Asegurarse de que los nombres de los estados sean consistentes si hay variaciones.
# Para este ejemplo, asumimos que 'State' es suficiente para mapear con Plotly.
sales_by_state = df_selection.groupby("State")["Sales"].sum().reset_index()

fig_map = px.choropleth(
    sales_by_state,
    locations="State",
    locationmode="USA-states", # Si los datos son de EE.UU. o ajusta según tu país
    color="Sales",
    hover_name="State",
    color_continuous_scale="agsunset", # Escala de color
    title="**Ventas Totales por Estado**",
    scope="usa" # Para enfocar el mapa en EE.UU. o ajusta según tu país
)
fig_map.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

# --- Mostrar datos filtrados --- #
st.markdown("### Datos Filtrados")
st.dataframe(df_selection)
