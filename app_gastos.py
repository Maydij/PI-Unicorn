import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import datetime

# 1. Configurar la conexión a MySQL (Reemplaza con tus datos reales)
usuario = 'avnadmin'
contrasena = 'AVNS_3nrYLzTlHETLzfbvu88'
host = 'mysql-361b747a-piunicorn2026.a.aivencloud.com'
puerto = '26898'
base_datos = 'defaultdb'

uri_real = f'mysql+pymysql://{usuario}:{contrasena}@{host}:{puerto}/{base_datos}'

@st.cache_data
def obtener_opciones():
    engine = create_engine(uri_real, connect_args={"ssl": {}})
    
    # 2. Traemos ambas columnas (ID y Nombre) de cada tabla y creamos Diccionarios
    # Un diccionario funciona así: {'Mateo Vargas': 1, 'Andrés Montes': 2}
    
    df_proy = pd.read_sql("SELECT id_proyecto, nombre_proyecto FROM proyectos", engine)
    dict_proyectos = dict(zip(df_proy.nombre_proyecto, df_proy.id_proyecto))
    
    # Nota: Usé 'nombre' basado en la consulta JOIN que hiciste antes. Si es 'nombre_completo', cámbialo aquí.
    df_ing = pd.read_sql("SELECT id_ingeniero, nombre FROM ingenieros", engine)
    dict_ingenieros = dict(zip(df_ing.nombre, df_ing.id_ingeniero))
    
    df_cat = pd.read_sql("SELECT id_categoria, nombre_categoria FROM categoria", engine)
    dict_categorias = dict(zip(df_cat.nombre_categoria, df_cat.id_categoria))
    
    df_met = pd.read_sql("SELECT id_metodo, nombre_metodo FROM metodo_pago", engine)
    dict_metodos = dict(zip(df_met.nombre_metodo, df_met.id_metodo))
    
    return dict_proyectos, dict_ingenieros, dict_categorias, dict_metodos

# Intentamos conectar y traer las listas dinámicas
try:
    dict_proyectos, dict_ingenieros, dict_categorias, dict_metodos = obtener_opciones()
    engine = create_engine(uri_real, connect_args={"ssl": {}})
except Exception as e:
    st.error(f"Error al conectar con la base de datos: {e}")
    st.stop()


# 2. Diseño de la página web
st.title('💸 Registro de Gastos de Ingeniería')
st.write('Por favor, llena el formulario para registrar un nuevo gasto.')

# 3. Crear el formulario
with st.form('formulario_gastos', clear_on_submit=True):
    st.subheader("Ingrese los detalles del gasto")
    # Campos del formulario (Listas desplegables, fechas, números)
    fecha = st.date_input('Fecha de gasto', datetime.date.today())
    
    # Las listas muestran las "llaves" del diccionario (Los textos legibles)
    proyecto = st.selectbox('Proyecto *', ['Seleccione un proyecto...'] + list(dict_proyectos.keys()))
    ingeniero = st.selectbox('Ingeniero *', ['Seleccione un ingeniero...'] + list(dict_ingenieros.keys()))
    categoria = st.selectbox('Categoría *', ['Seleccione una categoría...'] + list(dict_categorias.keys()))
    
    monto = st.number_input('Monto del gasto ($) *', min_value=0.0, step=0.01)
    metodo = st.selectbox('Método de pago *', ['Seleccione un método...'] + list(dict_metodos.keys()))
    factura = st.radio('¿Cuenta con factura? *', ['Si', 'No'])

    st.caption("* Campos obligatorios")

    # Botón de envío
    enviado = st.form_submit_button('Registrar Gasto')

    # 4. Lógica de validación
    if enviado:
        errores = []
        if proyecto == 'Seleccione un proyecto...': errores.append("Proyecto")
        if ingeniero == 'Seleccione un ingeniero...': errores.append("Ingeniero")
        if categoria == 'Seleccione una categoría...': errores.append("Categoría")
        if metodo == 'Seleccione un método...': errores.append("Método de pago")
        if monto <= 0: errores.append("Monto (debe ser mayor a 0)")

        if errores:
            st.error(f"Por favor, complete los siguientes campos obligatorios: {', '.join(errores)}")
        else:
            # 5. TRADUCCIÓN MAESTRA: Convertimos el texto seleccionado en su ID correspondiente
            id_proyecto_final = dict_proyectos[proyecto]
            id_ingeniero_final = dict_ingenieros[ingeniero]
            id_categoria_final = dict_categorias[categoria]
            id_metodo_final = dict_metodos[metodo]
            tiene_factura = True if factura == 'Si' else False
            
            # 6. Guardamos enviando las nuevas columnas (IDs) a tu tabla gastos_macro
            nuevo_gasto = pd.DataFrame({
                'Fecha': [fecha],
                'ID_Proyecto': [id_proyecto_final],
                'ID_Ingeniero': [id_ingeniero_final],
                'ID_Categoria': [id_categoria_final],
                'Monto': [monto],
                'ID_metodo': [id_metodo_final],
                'Factura': [tiene_factura]
            })
            
            try:
                # Ahora apuntamos a gastos_macro
                nuevo_gasto.to_sql('gastos_macro', con=engine, if_exists='append', index=False)
                st.success('¡Registro guardado exitosamente en la nueva base de datos relacional!')
                st.balloons()
                st.cache_data.clear() # Limpiamos caché para que todo se actualice
            except Exception as e:
                st.error(f'Hubo un error al guardar: {e}')