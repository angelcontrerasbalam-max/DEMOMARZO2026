import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuración de la página de Streamlit ---
st.set_page_config(page_title="Dashboard de Ventas", layout="wide")

st.title("📈 Dashboard Interactivo de Ventas")
st.markdown("--- ")

# --- Cargar datos ---
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        # Asegurarse de que 'Order Date' sea datetime para el filtrado, si existe
        if 'Order Date' in df.columns:
            df['Order Date'] = pd.to_datetime(df['Order Date'])
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return pd.DataFrame()

file_path = 'datos/SalidaVentas.xlsx'
df = load_data(file_path)

if not df.empty:
    # --- Barra lateral para filtros ---
    st.sidebar.header("Filtros")

    # Filtro por Región
    all_regions = ['All'] + list(df['Region'].unique())
    selected_region = st.sidebar.selectbox("Selecciona una Región:", all_regions)

    # Filtro por Categoría
    all_categories = ['All'] + list(df['Category'].unique())
    selected_category = st.sidebar.selectbox("Selecciona una Categoría:", all_categories)

    # Aplicar filtros
    filtered_df = df.copy()
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]

    # --- Mostrar KPIs (Key Performance Indicators) ---
    st.subheader("Métricas Clave")
    total_sales = filtered_df['Sales'].sum()
    total_profit = filtered_df['Profit'].sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Ventas Totales", value=f"${total_sales:,.2f}")
    with col2:
        st.metric(label="Ganancia Total", value=f"${total_profit:,.2f}")

    st.markdown("--- ")

    # --- Visualizaciones ---
    st.subheader("Análisis de Ventas")

    # Gráfico de ventas por Región
    if 'Region' in filtered_df.columns:
        sales_by_region = filtered_df.groupby('Region')['Sales'].sum().reset_index()
        fig_region_sales = px.bar(
            sales_by_region,
            x='Region',
            y='Sales',
            title='Ventas por Región',
            labels={'Sales': 'Ventas', 'Region': 'Región'}
        )
        st.plotly_chart(fig_region_sales, use_container_width=True)

    # Gráfico de ventas por Sub-Categoría
    if 'Sub-Category' in filtered_df.columns:
        sales_by_subcategory = filtered_df.groupby('Sub-Category')['Sales'].sum().reset_index().sort_values(by='Sales', ascending=False)
        fig_subcategory_sales = px.bar(
            sales_by_subcategory.head(10), # Mostrar top 10 subcategorías
            x='Sub-Category',
            y='Sales',
            title='Top 10 Ventas por Sub-Categoría',
            labels={'Sales': 'Ventas', 'Sub-Category': 'Sub-Categoría'}
        )
        st.plotly_chart(fig_subcategory_sales, use_container_width=True)

    st.markdown("--- ")
    st.subheader("Datos Crudos")
    st.dataframe(filtered_df)
else:
    st.warning("No se pudieron cargar los datos o el DataFrame está vacío.")
