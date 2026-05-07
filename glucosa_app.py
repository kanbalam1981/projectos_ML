import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import plotly.express as px
from datetime import datetime, timedelta
import os

# Configuración de la página
st.set_page_config(
    page_title="Control de Glucosa - Diabetes Tipo 2",
    page_icon="🩸",
    layout="wide"
)

# Título y descripción
st.title("🩸 Control de Glucosa - Diabetes Tipo 2")
st.markdown("""
Esta aplicación te ayuda a registrar tus mediciones de glucosa, 
seguir tu evolución y predecir tus niveles futuros basados en tus hábitos.
""")

# Archivo CSV para guardar los datos
DATA_FILE = "glucosa_data.csv"

# Función para cargar datos
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            'fecha', 'hora', 'nivel_glucosa', 'tomar_medication', 
            'tipo_bebida', 'tipo_alimento', 'cantidad_comida',
            'actividad_fisica', 'notas'
        ])

# Función para guardar datos
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Cargar datos existentes
df = load_data()

# Menú lateral
st.sidebar.title("Menú")
opcion = st.sidebar.selectbox(
    "Selecciona una opción:",
    ["Registrar Medición", "Ver Evolución", "Predicción", "Descargar Datos"]
)

# Opción 1: Registrar Medición
if opcion == "Registrar Medición":
    st.header("📝 Registrar Nueva Medición")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fecha = st.date_input("Fecha", datetime.now())
        hora = st.time_input("Hora", datetime.now().time())
        nivel_glucosa = st.number_input(
            "Nivel de Glucosa (mg/dL)", 
            min_value=50, 
            max_value=400, 
            value=100,
            help="Ingresa tu nivel de glucosa actual en mg/dL"
        )
        
    with col2:
        tomar_medication = st.selectbox(
            "¿Tomaste tu medicamento?",
            ["Sí", "No"],
            help="Indica si tomaste tu medicación para la diabetes"
        )
        
        tipo_bebida = st.selectbox(
            "Tipo de bebida consumida",
            ["Agua", "Refresco sin azúcar", "Refresco con azúcar", 
             "Jugo natural", "Jugo empaquetado", "Café/Té sin azúcar",
             "Café/Té con azúcar", "Leche", "Bebida alcohólica", "Otra"],
            help="Selecciona el tipo de bebida que consumiste"
        )
        
        tipo_alimento = st.selectbox(
            "Tipo de alimento consumido",
            ["Verduras", "Fruta baja en azúcar", "Fruta alta en azúcar",
             "Pan blanco", "Pan integral", "Arroz blanco", "Arroz integral",
             "Pasta", "Legumbres", "Proteína (carne/pescado/huevo)",
             "Lácteos", "Dulces/Postres", "Snacks procesados", "Nada"],
            help="Selecciona el tipo principal de alimento que consumiste"
        )
        
        cantidad_comida = st.select_slider(
            "Cantidad de comida",
            options=["Pequeña", "Moderada", "Grande", "Muy grande"],
            value="Moderada"
        )
        
        actividad_fisica = st.selectbox(
            "Actividad física realizada",
            ["Ninguna", "Caminata ligera", "Ejercicio moderado", 
             "Ejercicio intenso"],
            help="Selecciona el nivel de actividad física realizada"
        )
    
    notas = st.text_area("Notas adicionales (opcional)")
    
    if st.button("Guardar Medición"):
        # Crear nuevo registro
        nuevo_registro = {
            'fecha': str(fecha),
            'hora': str(hora),
            'nivel_glucosa': nivel_glucosa,
            'tomar_medication': tomar_medication,
            'tipo_bebida': tipo_bebida,
            'tipo_alimento': tipo_alimento,
            'cantidad_comida': cantidad_comida,
            'actividad_fisica': actividad_fisica,
            'notas': notas
        }
        
        # Agregar al DataFrame
        df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
        
        # Guardar datos
        save_data(df)
        
        st.success("✅ Medición guardada exitosamente!")
        
        # Mostrar resumen
        st.subheader("Resumen de tu medición:")
        st.write(f"- **Nivel de glucosa:** {nivel_glucosa} mg/dL")
        st.write(f"- **Medicamento:** {tomar_medication}")
        st.write(f"- **Bebida:** {tipo_bebida}")
        st.write(f"- **Alimento:** {tipo_alimento} ({cantidad_comida})")
        st.write(f"- **Actividad física:** {actividad_fisica}")

# Opción 2: Ver Evolución
elif opcion == "Ver Evolución":
    st.header("📊 Evolución de Niveles de Glucosa")
    
    if len(df) > 0:
        # Convertir fecha a datetime
        df['fecha_datetime'] = pd.to_datetime(df['fecha'] + ' ' + df['hora'])
        
        # Gráfico de línea
        fig = px.line(
            df.sort_values('fecha_datetime'),
            x='fecha_datetime',
            y='nivel_glucosa',
            title='Evolución de Niveles de Glucosa',
            labels={'nivel_glucosa': 'Glucosa (mg/dL)', 'fecha_datetime': 'Fecha y Hora'},
            markers=True
        )
        
        # Añadir líneas de referencia
        fig.add_hline(y=70, line_dash="dash", line_color="green", 
                     annotation_text="Límite inferior (70 mg/dL)")
        fig.add_hline(y=140, line_dash="dash", line_color="orange", 
                     annotation_text="Objetivo post-comida (140 mg/dL)")
        fig.add_hline(y=180, line_dash="dash", line_color="red", 
                     annotation_text="Límite superior (180 mg/dL)")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Última Medición", f"{df.iloc[-1]['nivel_glucosa']} mg/dL")
        
        with col2:
            st.metric("Promedio", f"{df['nivel_glucosa'].mean():.1f} mg/dL")
        
        with col3:
            st.metric("Mínimo", f"{df['nivel_glucosa'].min()} mg/dL")
        
        with col4:
            st.metric("Máximo", f"{df['nivel_glucosa'].max()} mg/dL")
        
        # Análisis por categoría
        st.subheader("Análisis por Categoría")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Glucosa promedio según medicamento:**")
            med_df = df.groupby('tomar_medication')['nivel_glucosa'].mean().reset_index()
            st.dataframe(med_df, hide_index=True)
        
        with col2:
            st.write("**Glucosa promedio según tipo de bebida:**")
            beb_df = df.groupby('tipo_bebida')['nivel_glucosa'].mean().reset_index()
            beb_df = beb_df.sort_values('nivel_glucosa', ascending=False)
            st.dataframe(beb_df, hide_index=True)
        
        # Tabla de datos
        st.subheader("Todos los registros")
        st.dataframe(df.sort_values('fecha_datetime', ascending=False), hide_index=True)
        
    else:
        st.info("No hay datos registrados aún. Ve a 'Registrar Medición' para comenzar.")

# Opción 3: Predicción
elif opcion == "Predicción":
    st.header("🔮 Predicción de Niveles de Glucosa")
    
    if len(df) >= 5:
        st.markdown("""
        Nuestro modelo predictivo analiza tus registros anteriores junto con tus hábitos 
        para estimar tu próximo nivel de glucosa.
        """)
        
        # Preparar datos para el modelo
        df_modelo = df.copy()
        
        # Codificar variables categóricas
        le_med = LabelEncoder()
        le_beb = LabelEncoder()
        le_ali = LabelEncoder()
        le_can = LabelEncoder()
        le_act = LabelEncoder()
        
        df_modelo['tomar_medication_enc'] = le_med.fit_transform(df_modelo['tomar_medication'])
        df_modelo['tipo_bebida_enc'] = le_beb.fit_transform(df_modelo['tipo_bebida'])
        df_modelo['tipo_alimento_enc'] = le_ali.fit_transform(df_modelo['tipo_alimento'])
        df_modelo['cantidad_comida_enc'] = le_can.fit_transform(df_modelo['cantidad_comida'])
        df_modelo['actividad_fisica_enc'] = le_act.fit_transform(df_modelo['actividad_fisica'])
        
        # Características para el modelo
        features = ['tomar_medication_enc', 'tipo_bebida_enc', 'tipo_alimento_enc', 
                   'cantidad_comida_enc', 'actividad_fisica_enc']
        
        X = df_modelo[features]
        y = df_modelo['nivel_glucosa']
        
        # Entrenar modelo
        modelo = LinearRegression()
        modelo.fit(X, y)
        
        st.success("✅ Modelo entrenado con tus datos")
        
        # Formulario para predicción
        st.subheader("Realiza una predicción")
        
        col1, col2 = st.columns(2)
        
        with col1:
            pred_med = st.selectbox(
                "¿Vas a tomar tu medicamento?",
                ["Sí", "No"],
                key="pred_med"
            )
            
            pred_beb = st.selectbox(
                "Tipo de bebida que consumirás",
                ["Agua", "Refresco sin azúcar", "Refresco con azúcar", 
                 "Jugo natural", "Jugo empaquetado", "Café/Té sin azúcar",
                 "Café/Té con azúcar", "Leche", "Bebida alcohólica", "Otra"],
                key="pred_beb"
            )
            
            pred_ali = st.selectbox(
                "Tipo de alimento que consumirás",
                ["Verduras", "Fruta baja en azúcar", "Fruta alta en azúcar",
                 "Pan blanco", "Pan integral", "Arroz blanco", "Arroz integral",
                 "Pasta", "Legumbres", "Proteína (carne/pescado/huevo)",
                 "Lácteos", "Dulces/Postres", "Snacks procesados", "Nada"],
                key="pred_ali"
            )
        
        with col2:
            pred_can = st.select_slider(
                "Cantidad de comida",
                options=["Pequeña", "Moderada", "Grande", "Muy grande"],
                value="Moderada",
                key="pred_can"
            )
            
            pred_act = st.selectbox(
                "Actividad física que realizarás",
                ["Ninguna", "Caminata ligera", "Ejercicio moderado", 
                 "Ejercicio intenso"],
                key="pred_act"
            )
        
        if st.button("Predecir Nivel de Glucosa"):
            # Codificar entrada
            try:
                entrada = pd.DataFrame({
                    'tomar_medication_enc': [le_med.transform([pred_med])[0]],
                    'tipo_bebida_enc': [le_beb.transform([pred_beb])[0]],
                    'tipo_alimento_enc': [le_ali.transform([pred_ali])[0]],
                    'cantidad_comida_enc': [le_can.transform([pred_can])[0]],
                    'actividad_fisica_enc': [le_act.transform([pred_act])[0]]
                })
                
                # Hacer predicción
                prediccion = modelo.predict(entrada)[0]
                
                # Mostrar resultado
                st.subheader("Resultado de la Predicción:")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Glucosa Predicha", 
                        f"{prediccion:.1f} mg/dL",
                        delta=f"{prediccion - df['nivel_glucosa'].mean():.1f} vs promedio"
                    )
                
                with col2:
                    if prediccion < 70:
                        st.warning("⚠️ Hipoglucemia prevista")
                    elif prediccion < 140:
                        st.success("✅ Nivel normal previsto")
                    elif prediccion < 180:
                        st.warning("⚠️ Nivel ligeramente alto")
                    else:
                        st.error("🚨 Nivel alto previsto")
                
                with col3:
                    recomendacion = ""
                    if prediccion < 70:
                        recomendacion = "Considera consumir carbohidratos de acción rápida"
                    elif prediccion < 140:
                        recomendacion = "¡Excelente! Mantén tus hábitos actuales"
                    elif prediccion < 180:
                        recomendacion = "Considera aumentar actividad física o ajustar porciones"
                    else:
                        recomendacion = "Consulta con tu médico sobre ajustes en medicación o dieta"
                    
                    st.info(f"💡 Recomendación: {recomendacion}")
                
                # Mostrar importancia de características
                st.subheader("Factores que más influyen:")
                
                importancia = pd.DataFrame({
                    'Factor': features,
                    'Importancia': abs(modelo.coef_)
                }).sort_values('Importancia', ascending=False)
                
                st.bar_chart(importancia.set_index('Factor'))
                
            except Exception as e:
                st.error(f"Error en la predicción: {str(e)}")
        
        # Mostrar calidad del modelo
        r2 = modelo.score(X, y)
        st.write(f"**Precisión del modelo (R²):** {r2:.2f}")
        st.caption("Un valor cercano a 1 indica que el modelo explica bien la variabilidad de tus datos")
        
    else:
        st.warning("⚠️ Necesitas al menos 5 registros para hacer predicciones. Registra más mediciones.")

# Opción 4: Descargar Datos
elif opcion == "Descargar Datos":
    st.header("💾 Descargar Datos")
    
    if len(df) > 0:
        st.write(f"Tienes **{len(df)}** registros guardados.")
        
        # Vista previa
        st.subheader("Vista previa de los datos:")
        st.dataframe(df, hide_index=True)
        
        # Convertir a CSV
        csv = df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Descargar CSV",
            data=csv,
            file_name=f"glucosa_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="Haz clic para descargar tus datos en formato CSV"
        )
        
        st.info("""
        **Uso de los datos:**
        - Puedes abrir este archivo en Excel, Google Sheets o cualquier programa de hojas de cálculo
        - Los datos incluyen todas tus mediciones y hábitos registrados
        - Útil para compartir con tu médico o nutricionista
        """)
    else:
        st.info("No hay datos para descargar. Registra algunas mediciones primero.")

# Pie de página
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>⚠️ <strong>Importante:</strong> Esta aplicación es solo para fines informativos y de seguimiento. 
    No sustituye el consejo médico profesional. Consulta siempre con tu médico antes de hacer cambios 
    en tu medicación o dieta.</p>
</div>
""", unsafe_allow_html=True)
