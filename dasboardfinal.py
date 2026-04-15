%%writefile app.py

import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración de la página de Streamlit ---
st.set_page_config(page_title="Dashboard de Ventas USA", layout="wide")

st.title("Dashboard de Ventas en USA")

# --- Cargar datos ---
file_path = 'datos/SalidaVentas.xlsx'

    # Asegurarse de que las columnas 'State' y 'Sales' existan
    if 'State' not in df.columns:
        possible_state_cols = [col for col in df.columns if 'state' in col.lower() or 'estado' in col.lower()]
        if possible_state_cols:
            df['State'] = df[possible_state_cols[0]]
        else:
            st.error("Columna 'State' o 'Estado' no encontrada. Por favor, ajuste el nombre de la columna en el archivo o en el código.")
            st.stop()

    if 'Sales' not in df.columns:
        possible_sales_cols = [col for col in df.columns if 'sales' in col.lower() or 'ventas' in col.lower() or 'total' in col.lower()]
        if possible_sales_cols:
            df['Sales'] = df[possible_sales_cols[0]]
        else:
            st.error("Columna 'Sales' o 'Ventas' no encontrada. Por favor, ajuste el nombre de la columna en el archivo o en el código.")
            st.stop()

    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)
    
    # Puedes añadir más columnas para gráficos si existen (ej. 'Category', 'Date')
    # if 'Category' in df.columns: df['Category'] = df['Category'].astype(str)
    # if 'Date' in df.columns: df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    return df

# Ruta del archivo (ajuste si el archivo no está en la misma carpeta que app.py)
file_path = 'SalidaVentas.xlsx' # Asume que el archivo está en la misma carpeta que app.py

df = load_data(file_path)

# --- Sidebar para filtros ---
st.sidebar.header("Filtros")

# Ejemplo de filtro por estado (si hay muchos estados, considere un multiselect)
all_states = ['Todos'] + sorted(df['State'].unique().tolist())
selected_state = st.sidebar.selectbox('Seleccionar Estado', all_states)

filtered_df = df.copy()
if selected_state != 'Todos':
    filtered_df = df[df['State'] == selected_state]

# --- Visualizaciones ---

st.subheader("Ventas Totales por Estado (Mapa de USA)")

# Agrupar ventas por estado para el mapa
sales_by_state = filtered_df.groupby('State')['Sales'].sum().reset_index()
sales_by_state.columns = ['State', 'Total Sales']

# Crear el mapa de coropletas de USA
# Plotly puede usar nombres de estados completos o códigos de 2 letras.
# Si sus estados no son reconocidos, necesitará un mapeo. Ver documentación de Plotly.
fig_map = px.choropleth(
    sales_by_state,
    locations='State',
    locationmode='USA-states', # Asegúrate que tus estados coinciden con este modo
    color='Total Sales',
    scope="usa",
    color_continuous_scale="Reds", # Escala de rojos para ventas intensas
    title="Distribución de Ventas por Estado en USA",
    hover_name='State',
    hover_data={'Total Sales': True}
)
fig_map.update_layout(geo_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin={"r":0,"t":50,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

# --- Otros Gráficos (Ejemplos) ---

st.subheader("Gráficos de Ventas Adicionales")

col1, col2 = st.columns(2)

with col1:
    st.write("#### Top 10 Estados por Ventas")
    top_states = sales_by_state.sort_values(by='Total Sales', ascending=False).head(10)
    fig_top_states = px.bar(
        top_states,
        x='State',
        y='Total Sales',
        title='Top 10 Estados',
        labels={'Total Sales': 'Ventas Totales'}
    )
    st.plotly_chart(fig_top_states, use_container_width=True)

with col2:
    # Gráfico de ventas por categoría (si existe la columna 'Category')
    if 'Category' in filtered_df.columns:
        st.write("#### Ventas por Categoría de Producto")
        sales_by_category = filtered_df.groupby('Category')['Sales'].sum().reset_index()
        fig_category = px.pie(
            sales_by_category,
            values='Sales',
            names='Category',
            title='Ventas por Categoría'
        )
        st.plotly_chart(fig_category, use_container_width=True)
    else:
        st.info("Para mostrar ventas por categoría, asegúrese de que su archivo tiene una columna 'Category'.")

# Gráfico de Ventas a lo largo del tiempo (si existe una columna 'Date')
if 'Date' in filtered_df.columns:
    st.subheader("Ventas a lo Largo del Tiempo")
    sales_over_time = filtered_df.groupby('Date')['Sales'].sum().reset_index()
    fig_time = px.line(
        sales_over_time,
        x='Date',
        y='Sales',
        title='Ventas Diarias',
        labels={'Sales': 'Ventas'}
    )
    st.plotly_chart(fig_time, use_container_width=True)
else:
    st.info("Para mostrar las ventas a lo largo del tiempo, asegúrese de que su archivo tiene una columna 'Date' en formato de fecha.")


st.markdown("--- ")
st.markdown("Dashboard creado con Streamlit y Plotly.")
