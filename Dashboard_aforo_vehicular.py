import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Aforo Vehicular",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_data(file_path):
    """
    Carga los datos del archivo CSV con los metadatos de los semáforos.
    
    Args:
        file_path (str): Ruta del archivo CSV
        
    Returns:
        pd.DataFrame: DataFrame con los datos cargados
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return None

def create_map(data):
    """
    Crea un mapa interactivo con Folium mostrando las ubicaciones de los puntos de medición.
    
    Args:
        data (pd.DataFrame): DataFrame con columnas 'latitud', 'longitud' y 'nombre'
        
    Returns:
        folium.Map: Objeto mapa de Folium
    """
    # Calcular el centro del mapa basado en las coordenadas
    center_lat = data['latitud'].mean()
    center_lon = data['longitud'].mean()
    
    # Crear el mapa
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Añadir marcadores para cada punto de medición
    for idx, row in data.iterrows():
        # Crear el contenido del popup
        popup_html = f"""
        <div style="font-family: Arial; width: 300px;">
            <h4 style="margin-bottom: 10px; color: #1f2937;">{row['nombre']}</h4>
            <p style="margin: 5px 0;"><b>Duración:</b> {row.get('Duracion_video', 'N/A')}</p>
            <p style="margin: 5px 0;"><b>Fecha inicio:</b> {row.get('Fecha_inicio', 'N/A')}</p>
            <p style="margin: 5px 0;"><b>Fecha fin:</b> {row.get('Fecha_fin', 'N/A')}</p>
            <p style="margin: 5px 0;"><b>Coordenadas:</b> {row.get('Coordenadas', 'N/A')}</p>
            <p style="margin: 5px 0;"><b>Observaciones:</b><br>{row.get('Comentarios', 'Sin observaciones')}</p>
        </div>
        """
        
        folium.Marker(
            location=[row['latitud'], row['longitud']],
            popup=folium.Popup(popup_html, max_width=350),
            tooltip=row['nombre'],
            icon=folium.Icon(color='red', icon='video-camera', prefix='fa')
        ).add_to(m)
    
    return m

def parse_coordinates(coord_string):
    """
    Extrae latitud y longitud de una cadena de coordenadas.
    
    Args:
        coord_string (str): Cadena con formato "latitud, longitud"
        
    Returns:
        tuple: (latitud, longitud) o (None, None) si hay error
    """
    try:
        parts = coord_string.split(',')
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        return lat, lon
    except:
        return None, None

def load_metadata():
    """
    Carga y procesa el archivo de metadatos.
    
    Returns:
        pd.DataFrame: DataFrame procesado con columnas normalizadas
    """
    try:
        # Leer el archivo CSV
        df = pd.read_csv('datos/Metadatos.csv')
        
        # Extraer latitud y longitud de la columna Coordenadas
        df[['latitud', 'longitud']] = df['Coordenadas'].apply(
            lambda x: pd.Series(parse_coordinates(x))
        )
        
        # Renombrar columna para compatibilidad con el mapa
        df['nombre'] = df['Nombre_archivo']
        
        # Eliminar filas con coordenadas inválidas
        df = df.dropna(subset=['latitud', 'longitud'])
        
        return df
    except Exception as e:
        st.error(f"Error al cargar los metadatos: {str(e)}")
        return None

def main():
    """Función principal de la aplicación."""
    
    # Título principal
    st.markdown('<h1 class="main-title">Sistema de Análisis de Aforo Vehicular mediante Visión Computacional</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Resultados del monitoreo automatizado de tráfico en intersecciones semaforizadas</p>', unsafe_allow_html=True)
    
    # Sección: Introducción
    st.markdown('<h2 class="section-header">1. Introducción</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    El presente sistema constituye una herramienta de análisis para la visualización y evaluación de datos 
    de aforo vehicular obtenidos mediante técnicas de visión computacional. La implementación de algoritmos 
    de detección y seguimiento de vehículos permite la cuantificación objetiva del flujo vehicular en 
    intersecciones críticas de la red vial urbana.
    </div>
    """, unsafe_allow_html=True)
    
    # Sección: Metodología
    st.markdown('<h2 class="section-header">2. Metodología</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 2.1 Adquisición de Datos")
        st.markdown("""
        El proceso de adquisición de datos se realizó mediante la instalación de cámaras de video en 
        puntos estratégicos de la red vial. Las grabaciones fueron procesadas utilizando modelos de 
        aprendizaje profundo especializados en la detección de objetos en tiempo real.
        """)
        
    with col2:
        st.markdown("### 2.2 Procesamiento")
        st.markdown("""
        Se aplicaron algoritmos de visión computacional basados en redes neuronales convolucionales 
        para la identificación, clasificación y conteo de vehículos. El sistema implementa técnicas 
        de seguimiento multi-objeto para evitar el doble conteo de unidades vehiculares.
        """)
    
    # Sección: Resultados
    st.markdown('<h2 class="section-header">3. Resultados</h2>', unsafe_allow_html=True)
    
    # Cargar datos desde el archivo
    data = load_metadata()
    
    if data is not None and len(data) > 0:
        # Métricas generales
        st.markdown("### 3.1 Estadísticas Generales")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            # Calcular duración total de videos
            total_duration = data['Duracion_video'].count()
            st.metric("Videos Analizados", total_duration)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            # Calcular periodo de análisis
            fechas_inicio = pd.to_datetime(data['Fecha_inicio'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            fechas_fin = pd.to_datetime(data['Fecha_fin'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
            
            if not fechas_inicio.isna().all() and not fechas_fin.isna().all():
                fecha_min = fechas_inicio.min().strftime('%d/%m/%Y')
                fecha_max = fechas_fin.max().strftime('%d/%m/%Y')
                st.metric("Periodo de Análisis", f"{fecha_min} - {fecha_max}")
            else:
                st.metric("Periodo de Análisis", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Mapa de ubicaciones
        st.markdown("### 3.2 Distribución Geográfica de Puntos de Medición")
        
        st.markdown("""
        El siguiente mapa interactivo muestra la ubicación de los puntos donde se realizó 
        el aforo vehicular. Cada marcador representa un punto de medición e incluye información 
        detallada sobre el video analizado y las observaciones técnicas registradas.
        """)
        
        traffic_map = create_map(data)
        st_folium(traffic_map, width=1400, height=600)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6b7280; font-size: 0.9rem;'>
    Sistema de Análisis de Aforo Vehicular | Universidad del Caribe & IMPLAN © 2025
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()