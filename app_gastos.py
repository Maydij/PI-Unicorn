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

# Creamos el motor agregando el parámetro de seguridad SSL que Aiven exige
try:
    engine = create_engine(uri_real, connect_args={"ssl": {}})
    # Intentamos una conexión de prueba
    with engine.connect() as conn:
        pass 
except Exception as e:
    st.error(f"Error de conexión: {e}")


# 2. Diseño de la página web
st.title('💸 Registro de Gastos de Ingeniería')
st.write('Por favor, llena el formulario para registrar un nuevo gasto.')

# 3. Crear el formulario
with st.form('formulario_gastos'):
    # Campos del formulario (Listas desplegables, fechas, números)
    fecha = st.date_input('Fecha de gasto', datetime.date.today())
    
    proyecto = st.selectbox('Proyecto al que pertenece', 
                            ['Proyecto Sinfonía', 'Proyecto Atlas', 'Proyecto Boreal', 'Otro'])
    
    ingeniero = st.selectbox('Ingeniero que hizo el gasto', 
                             ['Mateo Vargas', 'Andrés Montes', 'Felipe Rojas', 'Otro'])
    
    categoria = st.selectbox('Categoría', 
                             ['Food/Beverage', 'Airfare', 'Taxi/Parking', 'Miscellaneous'])
    
    monto = st.number_input('Monto del gasto ($)', min_value=0.0, format='%f')
    
    metodo = st.selectbox('Método de pago', 
                          ['Fondos Personales', 'Fondos de Empresa', 'Amex'])
    
    factura = st.radio('¿Cuenta con factura?', ['Si', 'No'])

    # Botón de envío
    enviado = st.form_submit_button('Registrar Gasto')

    # 4. ¿Qué pasa cuando el ingeniero presiona el botón?
    if enviado:
        # Transformar el "Si"/"No" al formato booleano que definimos en SQL
        tiene_factura = True if factura == 'Si' else False
        
        # Crear un mini DataFrame con el nuevo registro
        nuevo_gasto = pd.DataFrame({
            'Fecha': [fecha],
            'Proyecto': [proyecto],
            'Ingeniero': [ingeniero],
            'Categoria': [categoria],
            'Monto': [monto],
            'Metodo_Pago': [metodo],
            'Factura': [tiene_factura]
        })
        
        # Enviar este DataFrame a MySQL agregándolo al final (if_exists='append')
        try:
            nuevo_gasto.to_sql(name='gastos_empresa', con=engine, if_exists='append', index=False)
            st.success('¡Registro guardado exitosamente en la base de datos!')
        except Exception as e:
            st.error(f'Hubo un error al guardar: {e}')