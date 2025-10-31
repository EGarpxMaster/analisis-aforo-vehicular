import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os

# Configuración de la página
st.set_page_config(page_title="Reporte de Aforo Vehicular", page_icon="�", layout="wide")

# Título principal
st.title("Reporte de Aforo Vehicular")
st.markdown("### Resultados del Modelo de Visión Computacional")

# Función para cargar metadatos
@st.cache_data
def cargar_metadatos(ruta_metadatos="datos/Metadatos.csv"):
    """Carga el archivo de metadatos con información de los videos"""
    try:
        df = pd.read_csv(ruta_metadatos)
        return df
    except FileNotFoundError:
        st.error(f"No se encontró el archivo de metadatos en: {ruta_metadatos}")
        return None
    except Exception as e:
        st.error(f"Error al cargar metadatos: {e}")
        return None

# Función para cargar conteos de un video
@st.cache_data
def cargar_conteos(nombre_video, carpeta_datos="datos"):
    """Carga el archivo CSV con los conteos de un video específico"""
    # Intentar primero con el nombre exacto
    nombre_archivo = f"{nombre_video}_counts.csv"
    ruta_completa = os.path.join(carpeta_datos, nombre_archivo)
    
    # Si el archivo no existe, buscar archivos similares
    if not os.path.exists(ruta_completa):
        # Buscar archivos CSV que contengan el nombre base (sin extensión)
        nombre_base = nombre_video.replace('.avi', '').replace('.mp4', '').strip().lower()
        archivos_disponibles = [f for f in os.listdir(carpeta_datos) if f.endswith('_counts.csv')]
        
        # Buscar coincidencias flexibles (ignorando mayúsculas y espacios)
        for archivo in archivos_disponibles:
            archivo_normalizado = archivo.replace('_counts.csv', '').strip().lower()
            if archivo_normalizado == nombre_base or nombre_base in archivo_normalizado:
                nombre_archivo = archivo
                ruta_completa = os.path.join(carpeta_datos, nombre_archivo)
                st.info(f"Archivo encontrado: {nombre_archivo}")
                break
    
    try:
        df = pd.read_csv(ruta_completa)
        # Asegurar que la columna count sea numérica
        df['count'] = pd.to_numeric(df['count'], errors='coerce').fillna(0)
        return df
    except FileNotFoundError:
        st.error(f"No se encontró el archivo: {nombre_archivo}")
        st.warning("Archivos disponibles en la carpeta datos:")
        try:
            archivos = [f for f in os.listdir(carpeta_datos) if f.endswith('_counts.csv')]
            for archivo in archivos:
                st.write(f"  • {archivo}")
        except:
            pass
        return None
    except Exception as e:
        st.error(f"Error al cargar {nombre_archivo}: {e}")
        return None

# Función para procesar datos de conteo
def procesar_conteos(df):
    """Procesa el dataframe de conteos para análisis"""
    # Filtrar datos por línea (solo líneas individuales, no ALL)
    linea_1 = df[df['line_id'] == 1].copy()
    linea_2 = df[df['line_id'] == 2].copy()
    
    # Crear resumen total combinando línea 1 y 2
    todos = pd.concat([linea_1, linea_2]).groupby('class', as_index=False)['count'].sum()
    todos['line_id'] = 'ALL'
    
    return linea_1, linea_2, todos

# Función auxiliar para obtener conteo de una clase
def obtener_conteo(df, clase):
    """Obtiene el conteo de una clase específica de forma segura"""
    resultado = df[df['class'] == clase]['count'].values
    return int(resultado[0]) if len(resultado) > 0 else 0

# Cargar metadatos
df_metadatos = cargar_metadatos()

if df_metadatos is not None:
    # Sidebar para selección de video
    st.sidebar.header("Selección de Video")
    
    # Verificar que existe la columna de nombre de video (ajustar según tu CSV)
    columnas_posibles = ['Nombre_archivo']
    columna_video = None
    
    for col in columnas_posibles:
        if col in df_metadatos.columns:
            columna_video = col
            break
    
    if columna_video is None:
        st.error("No se encontró la columna con nombres de videos en Metadatos.csv")
        st.info(f"Columnas disponibles: {', '.join(df_metadatos.columns)}")
        st.stop()
    
    # Selector de video
    videos_disponibles = df_metadatos[columna_video].tolist()
    video_seleccionado = st.sidebar.selectbox(
        "Selecciona un video:",
        videos_disponibles,
        index=0
    )
    
    # Mostrar información del video seleccionado
    info_video = df_metadatos[df_metadatos[columna_video] == video_seleccionado].iloc[0]
    
    with st.sidebar.expander("Información del Video", expanded=True):
        for col in df_metadatos.columns:
            if col != columna_video:
                st.write(f"**{col}:** {info_video[col]}")
    
    # Cargar conteos del video seleccionado
    df_conteos = cargar_conteos(video_seleccionado)
    
    if df_conteos is not None:
        # Procesar conteos
        linea_1, linea_2, todos = procesar_conteos(df_conteos)
        
        # Tabs para organizar la información
        tab1, tab2, tab3, tab4 = st.tabs([
            "Resumen General", 
            "Línea 1", 
            "Línea 2", 
            "Comparativa"
        ])
        
        # TAB 1: RESUMEN GENERAL
        with tab1:
            st.header("Resumen General - Todas las Líneas")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            
            total_vehiculos = int(todos['count'].sum())
            total_autos = obtener_conteo(todos, 'car')
            total_personas = obtener_conteo(todos, 'person')
            total_camiones = obtener_conteo(todos, 'truck')
            
            with col1:
                st.metric("Total Vehículos", f"{total_vehiculos:,}")
            with col2:
                st.metric("Autos", f"{total_autos:,}")
            with col3:
                st.metric("Camiones", f"{total_camiones:,}")
            with col4:
                st.metric("Personas", f"{total_personas:,}")
            # Mostrar GIF del video seleccionado si aplica
            # Requerimiento: mostrar el GIF en la pestaña cuando el video sea 'Fracc kusamil C2.avi'
            try:
                if isinstance(video_seleccionado, str) and video_seleccionado.strip() == "Fracc kusamil C2.avi":
                    gif_path = "gifs/kusamil_corto.gif"
                    st.divider()
                    st.subheader("Preview del Video (GIF)")
                    if os.path.exists(gif_path):
                        # st.image reproducirá el GIF animado en Streamlit
                        # use_column_width está obsoleto; usar use_container_width
                        st.image(gif_path, caption="kusamil_corto.gif", use_container_width=True)
                    else:
                        st.warning(f"GIF no encontrado en: {gif_path}")

                if isinstance(video_seleccionado, str) and video_seleccionado.strip() == "Filtro merida C2.avi":
                    gif_path = "gifs/filtro_corto.gif"
                    st.divider()
                    st.subheader("Preview del Video (GIF)")
                    if os.path.exists(gif_path):
                        # st.image reproducirá el GIF animado en Streamlit
                        # use_column_width está obsoleto; usar use_container_width
                        st.image(gif_path, caption="filtro_corto.gif", use_container_width=True)
                    else:
                        st.warning(f"GIF no encontrado en: {gif_path}")

                if isinstance(video_seleccionado, str) and video_seleccionado.strip() == "Fracc kusamil C2 2.avi":
                    gif_path = "gifs/kusamil_2.gif"
                    st.divider()
                    st.subheader("Preview del Video (GIF)")
                    if os.path.exists(gif_path):
                        # st.image reproducirá el GIF animado en Streamlit
                        # use_column_width está obsoleto; usar use_container_width
                        st.image(gif_path, caption="kusamil_2.gif", use_container_width=True)
                    else:
                        st.warning(f"GIF no encontrado en: {gif_path}")

                if isinstance(video_seleccionado, str) and video_seleccionado.strip() == "Portillo - Lakin.avi":
                    gif_path = "gifs/port_lakin.gif"
                    st.divider()
                    st.subheader("Preview del Video (GIF)")
                    if os.path.exists(gif_path):
                        # st.image reproducirá el GIF animado en Streamlit
                        # use_column_width está obsoleto; usar use_container_width
                        st.image(gif_path, caption="port_lakin.gif", use_container_width=True)
                    else:
                        st.warning(f"GIF no encontrado en: {gif_path}")

                if isinstance(video_seleccionado, str) and video_seleccionado.strip() == "272 (2025-06-30 18'00'00 - 2025-06-30 18'30'00).avi":
                    gif_path = "gifs/272.gif"
                    st.divider()
                    st.subheader("Preview del Video (GIF)")
                    if os.path.exists(gif_path):
                        # st.image reproducirá el GIF animado en Streamlit
                        # use_column_width está obsoleto; usar use_container_width
                        st.image(gif_path, caption="port_lakin.gif", use_container_width=True)
                    else:
                        st.warning(f"GIF no encontrado en: {gif_path}") 

                if isinstance(video_seleccionado, str) and video_seleccionado.strip() == "28 (2025-06-30 08'00'00 - 2025-06-30 08'30'00).avi":
                    gif_path = "gifs/zh.gif"
                    st.divider()
                    st.subheader("Preview del Video (GIF)")
                    if os.path.exists(gif_path):
                        # st.image reproducirá el GIF animado en Streamlit
                        # use_column_width está obsoleto; usar use_container_width
                        st.image(gif_path, caption="port_lakin.gif", use_container_width=True)
                    else:
                        st.warning(f"GIF no encontrado en: {gif_path}")        

                if isinstance(video_seleccionado, str) and video_seleccionado.strip() == "Portillo - Lakin 2.avi":
                    gif_path = "gifs/port_lakin_2.gif"
                    st.divider()
                    st.subheader("Preview del Video (GIF)")
                    if os.path.exists(gif_path):
                        # st.image reproducirá el GIF animado en Streamlit
                        # use_column_width está obsoleto; usar use_container_width
                        st.image(gif_path, caption="video", use_container_width=True)
                    else:
                        st.warning(f"GIF no encontrado en: {gif_path}")      

                if isinstance(video_seleccionado, str) and video_seleccionado.strip() == "Av Portillo - Av Paraiso Maya.avi":
                    gif_path = "gifs/port_maya.gif"
                    st.divider()
                    st.subheader("Video")
                    if os.path.exists(gif_path):
                        # st.image reproducirá el GIF animado en Streamlit
                        # use_column_width está obsoleto; usar use_container_width
                        st.image(gif_path, caption="kusamil_corto.gif", use_container_width=True)
                    else:
                        st.warning(f"GIF no encontrado en: {gif_path}")  

            except Exception as _e:
                # No dejar que un error de visualización rompa la página
                st.error("No se pudo mostrar el GIF del video seleccionado.")

            st.divider()
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Distribución por Tipo de Objeto")
                fig_pie = px.pie(
                    todos, 
                    values='count', 
                    names='class',
                    title='Distribución Total de Detecciones',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label+value')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.subheader("Conteo por Categoría")
                fig_bar = px.bar(
                    todos.sort_values('count', ascending=True),
                    x='count',
                    y='class',
                    orientation='h',
                    title='Cantidad por Tipo de Objeto',
                    color='count',
                    color_continuous_scale='Blues',
                    text='count'
                )
                fig_bar.update_traces(textposition='outside')
                st.plotly_chart(fig_bar, use_container_width=True)
            
            # Tabla de datos completa
            st.subheader("Datos Detallados")
            st.dataframe(
                todos.style.background_gradient(subset=['count'], cmap='YlOrRd'),
                use_container_width=True
            )
        
        # TAB 2: LÍNEA 1
        with tab2:
            st.header("Análisis Línea 1")
            
            if len(linea_1) > 0:
                # Métricas de línea 1
                col1, col2, col3, col4 = st.columns(4)
                
                total_l1 = int(linea_1['count'].sum())
                autos_l1 = obtener_conteo(linea_1, 'car')
                personas_l1 = obtener_conteo(linea_1, 'person')
                camiones_l1 = obtener_conteo(linea_1, 'truck')
                
                with col1:
                    st.metric("Total Línea 1", f"{total_l1:,}")
                with col2:
                    st.metric("Autos", f"{autos_l1:,}")
                with col3:
                    st.metric("Camiones", f"{camiones_l1:,}")
                with col4:
                    st.metric("Personas", f"{personas_l1:,}")

                st.divider()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico de torta
                    fig_pie_l1 = px.pie(
                        linea_1,
                        values='count',
                        names='class',
                        title='Distribución Línea 1',
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    st.plotly_chart(fig_pie_l1, use_container_width=True)
                
                with col2:
                    # Gráfico de barras
                    fig_bar_l1 = px.bar(
                        linea_1.sort_values('count', ascending=False),
                        x='class',
                        y='count',
                        title='Conteo por Categoría - Línea 1',
                        color='count',
                        color_continuous_scale='Greens',
                        text='count'
                    )
                    fig_bar_l1.update_traces(textposition='outside')
                    st.plotly_chart(fig_bar_l1, use_container_width=True)
                
                # Tabla
                st.dataframe(
                    linea_1.style.background_gradient(subset=['count'], cmap='Greens'),
                    use_container_width=True
                )
            else:
                st.warning("No hay datos disponibles para la Línea 1")
        
        # TAB 3: LÍNEA 2
        with tab3:
            st.header("Análisis Línea 2")
            
            if len(linea_2) > 0:
                # Métricas de línea 2
                col1, col2, col3, col4 = st.columns(4)
                
                total_l2 = int(linea_2['count'].sum())
                autos_l2 = obtener_conteo(linea_2, 'car')
                personas_l2 = obtener_conteo(linea_2, 'person')
                camiones_l2 = obtener_conteo(linea_2, 'truck')
                
                with col1:
                    st.metric("Total Línea 2", f"{total_l2:,}")
                with col2:
                    st.metric("Autos", f"{autos_l2:,}")
                with col3:
                    st.metric("Camiones", f"{camiones_l2:,}")
                with col4:
                    st.metric("Personas", f"{personas_l2:,}")
                
                st.divider()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Gráfico de torta
                    fig_pie_l2 = px.pie(
                        linea_2,
                        values='count',
                        names='class',
                        title='Distribución Línea 2',
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    st.plotly_chart(fig_pie_l2, use_container_width=True)
                
                with col2:
                    # Gráfico de barras
                    fig_bar_l2 = px.bar(
                        linea_2.sort_values('count', ascending=False),
                        x='class',
                        y='count',
                        title='Conteo por Categoría - Línea 2',
                        color='count',
                        color_continuous_scale='Oranges',
                        text='count'
                    )
                    fig_bar_l2.update_traces(textposition='outside')
                    st.plotly_chart(fig_bar_l2, use_container_width=True)
                
                # Tabla
                st.dataframe(
                    linea_2.style.background_gradient(subset=['count'], cmap='Oranges'),
                    use_container_width=True
                )
            else:
                st.warning("No hay datos disponibles para la Línea 2")
        
        # TAB 4: COMPARATIVA
        with tab4:
            st.header("Comparativa entre Líneas")
            
            if len(linea_1) > 0 and len(linea_2) > 0:
                # Preparar datos para comparación
                comparacion = pd.DataFrame()
                
                # Unir datos de ambas líneas
                linea_1_comp = linea_1.copy()
                linea_1_comp['line_id'] = 'Línea 1'
                linea_2_comp = linea_2.copy()
                linea_2_comp['line_id'] = 'Línea 2'
                
                comparacion = pd.concat([linea_1_comp, linea_2_comp], ignore_index=True)
                
                # Métricas comparativas
                col1, col2, col3 = st.columns(3)
                
                total_l1_comp = int(linea_1['count'].sum())
                total_l2_comp = int(linea_2['count'].sum())
                
                with col1:
                    diff_total = total_l1_comp - total_l2_comp
                    st.metric(
                        "Diferencia Total",
                        f"{abs(diff_total):,}",
                        delta=f"L1 {'mayor' if diff_total > 0 else 'menor'}"
                    )
                
                with col2:
                    porcentaje_l1 = (total_l1_comp / total_vehiculos * 100) if total_vehiculos > 0 else 0
                    st.metric("% Línea 1", f"{porcentaje_l1:.1f}%")
                
                with col3:
                    porcentaje_l2 = (total_l2_comp / total_vehiculos * 100) if total_vehiculos > 0 else 0
                    st.metric("% Línea 2", f"{porcentaje_l2:.1f}%")
                
                st.divider()
                
                # Gráfico de barras agrupadas
                st.subheader("Comparación por Categoría")
                fig_comp = px.bar(
                    comparacion,
                    x='class',
                    y='count',
                    color='line_id',
                    barmode='group',
                    title='Comparación de Conteos entre Líneas',
                    color_discrete_map={'Línea 1': '#2E86AB', 'Línea 2': '#A23B72'},
                    text='count'
                )
                fig_comp.update_traces(textposition='outside')
                fig_comp.update_layout(height=500)
                st.plotly_chart(fig_comp, use_container_width=True)
                
                # Heatmap de comparación
                st.subheader("Mapa de Calor Comparativo")
                
                # Crear pivot table para heatmap
                pivot_data = comparacion.pivot_table(
                    index='class',
                    columns='line_id',
                    values='count',
                    fill_value=0
                )
                
                fig_heatmap = px.imshow(
                    pivot_data,
                    labels=dict(x="Línea", y="Categoría", color="Conteo"),
                    x=pivot_data.columns,
                    y=pivot_data.index,
                    color_continuous_scale='RdYlGn',
                    text_auto=True,
                    aspect='auto'
                )
                fig_heatmap.update_layout(height=400)
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Tabla comparativa
                st.subheader("Tabla Comparativa")
                tabla_comp = comparacion.pivot_table(
                    index='class',
                    columns='line_id',
                    values='count',
                    fill_value=0,
                    aggfunc='sum'
                )
                tabla_comp['Diferencia'] = tabla_comp['Línea 1'] - tabla_comp['Línea 2']
                tabla_comp['Total'] = tabla_comp['Línea 1'] + tabla_comp['Línea 2']
                
                st.dataframe(
                    tabla_comp.style.background_gradient(cmap='RdYlGn', axis=1),
                    use_container_width=True
                )
            else:
                st.warning("Se necesitan datos de ambas líneas para realizar la comparativa")
        
        # Sección de descarga
        st.divider()
        st.subheader("Descargar Datos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_todos = todos.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar Resumen General",
                data=csv_todos,
                file_name=f"{video_seleccionado}_resumen_general.csv",
                mime="text/csv"
            )
        
        with col2:
            if len(linea_1) > 0:
                csv_l1 = linea_1.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar Línea 1",
                    data=csv_l1,
                    file_name=f"{video_seleccionado}_linea1.csv",
                    mime="text/csv"
                )
        
        with col3:
            if len(linea_2) > 0:
                csv_l2 = linea_2.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar Línea 2",
                    data=csv_l2,
                    file_name=f"{video_seleccionado}_linea2.csv",
                    mime="text/csv"
                )

else:
    st.error("No se pudo cargar el archivo de metadatos. Verifica la ruta 'datos/Metadatos.csv'")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; font-size: 0.9rem;'>
Sistema de Análisis de Aforo Vehicular | Universidad del Caribe & IMPLAN © 2025
</div>
""", unsafe_allow_html=True)