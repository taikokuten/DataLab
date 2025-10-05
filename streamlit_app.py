import pandas as pd
import streamlit as st
import io

st.title('🎈 Calculo de nominas de los conductores')
data_fact = st.file_uploader('Subir archivo CSV de facturacion de Uber', type='csv')
data_acept = st.file_uploader('Subir archivo CSV de aceptacion de Uber', type='csv')

if data_fact is not None and data_acept is not None:
    df_fact = pd.read_csv(data_fact)
    df_acept = pd.read_csv(data_acept)

    #Cambio de nombres de las columnas
    df_fact.rename(columns={'Importe que se te ha pagado : Tus ganancias': 'Total facturado', 'Importe que se te ha pagado:Tus ganancias:Propina': 'Propina', 'Importe que se te ha pagado:Tus ganancias:Promoción:Reto': 'Reto'}, inplace=True)
    df_acept.rename(columns={'Índice de aceptación': 'Aceptacion'}, inplace=True)
    #Union de columnas
    df_fact['Nombre'] = df_fact['Nombre del conductor'] + ' ' + df_fact['Apellido del conductor']
    df_acept['Nombre'] = df_acept['Nombre del conductor'] + ' ' + df_acept['Apellido del conductor']

    conductores_70 = list(df_acept[df_acept['Aceptacion'] >= 0.70]['Nombre'])
    conductores_menos_70 = list(df_acept[df_acept['Aceptacion'] < 0.70]['Nombre'])
    if 'Alquiler Alc Siete SL' in conductores_menos_70:
        conductores_menos_70.remove('Alquiler Alc Siete SL')
    conductores_menos_70.sort()
    conductores_70.sort()

    data = []

    for conductor in conductores_70:
        total_facturado = df_fact[df_fact['Nombre'] == conductor]['Total facturado'].sum()
        total_propina = df_fact[df_fact['Nombre'] == conductor]['Propina'].sum()
        total_promociones = df_fact[df_fact['Nombre'] == conductor]['Reto'].sum()
        total_facturado_viajes = total_facturado - total_promociones - total_propina
        total_facturado_sin_iva = total_facturado_viajes/1.1
        nomina_conductor = (total_facturado_sin_iva*0.3) + total_propina + (total_promociones/1.1)
        efectivo = total_facturado_sin_iva*0.05
        aceptacion = df_acept[df_acept['Nombre'] == conductor]['Aceptacion'].values[0] * 100
        my_dict = {}
        my_dict.update({'Nombre': conductor, 'Nomina Uber': round(nomina_conductor, 2), 'Efectivo Uber': round(efectivo, 2), 'Aceptacion %': aceptacion})
        data.append(my_dict)

    for conductor in conductores_menos_70:
        total_facturado = df_fact[df_fact['Nombre'] == conductor]['Total facturado'].sum()
        total_propina = df_fact[df_fact['Nombre'] == conductor]['Propina'].sum()
        total_promociones = df_fact[df_fact['Nombre'] == conductor]['Reto'].sum()
        total_facturado_viajes = total_facturado - total_promociones - total_propina
        total_facturado_sin_iva = total_facturado_viajes/1.1
        nomina_conductor = (total_facturado_sin_iva*0.25) + total_propina + (total_promociones/1.1)
        efectivo = total_facturado_sin_iva*0.05
        aceptacion = df_acept[df_acept['Nombre'] == conductor]['Aceptacion'].values[0] * 100
        my_dict = {}
        my_dict.update({'Nombre': conductor, 'Nomina Uber': round(nomina_conductor, 2), 'Efectivo Uber': round(efectivo, 2), 'Aceptacion %': aceptacion})
        data.append(my_dict)

    df_personalizado = pd.DataFrame(data)
    st.dataframe(df_personalizado)

    output = io.BytesIO()
    df_personalizado.to_excel(output, index=False)
    output.seek(0)

    st.download_button(
        label='Descargar Excel',
        data=output,
        file_name='Nominas_de_conductores_Uber.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        icon=":material/download:"
    )
