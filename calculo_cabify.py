import pandas as pd
import streamlit as st
import io

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

st.header('📶 Calculo nomina - Cabify', divider=True)

cabify_acept_data = st.file_uploader('Subir archivos excel de aceptacion de Cabify (Reporte semanal > Ganancias totales).', accept_multiple_files=True)

conductores_70 = []
conductores_menos_70 = []

if cabify_acept_data:
    all_df = []

    for data in cabify_acept_data:
        df = pd.read_excel(data)
        all_df.append(df)

    combined_df_acept = pd.concat(all_df, ignore_index=True)

    combined_df_acept.rename(columns={'Nombre conductor/compañía':'Nombre', 'Media % de aceptación':'Aceptacion'}, inplace=True)
    #Se crea un set de conductores
    set_de_conductores = set(combined_df_acept['Nombre'])
    if 'Alquiler Alc 7 SL' in set_de_conductores or 'Totales por compañía' in set_de_conductores:
        set_de_conductores.remove('Alquiler Alc 7 SL')
        set_de_conductores.remove('Totales por compañía')

    #Creacion de listas de conductores que han llegado a 70% de aceptacion y los que no.
    
    data_aceptacion = []
    for conductor in set_de_conductores:
        promedio_de_aceptacion = combined_df_acept[combined_df_acept['Nombre'] == conductor]['Aceptacion'].mean()
        if promedio_de_aceptacion >= 70:
            conductores_70.append(conductor)
        else:
            conductores_menos_70.append(conductor)
        dict_aceptacion = {}
        dict_aceptacion.update({'Nombre': conductor, 'Aceptacion': round(promedio_de_aceptacion, 0)})
        data_aceptacion.append(dict_aceptacion)

    #Funcion para colorear la columna aceptacion
    def color_aceptacion(val):
        if val >= 70:
            return 'background-color: #d4edda; color: #155724'
        else:
            return 'background-color: #f8d7da; color: #721c24'

    df_acept = pd.DataFrame(data_aceptacion)
    df_acept = df_acept.sort_values(by='Nombre', ignore_index=True)
    styled_df = df_acept.style.map(color_aceptacion, subset=['Aceptacion']) \
                            .format({'Aceptacion': '{:.0f}'})

    st.dataframe(styled_df)

    st.write(f'Han llegado a 70%:  {len(conductores_70)} conductores.')
    st.write(f'No han llegado a 70%: {len(conductores_menos_70)} conductores.')
    st.write(f'La media de aceptacion es {round(df_acept['Aceptacion'].mean(), 2)} %')   
st.divider()
#Calculo de la nomina de conductores.
cabify_fact_data = st.file_uploader('Subir archivo excel de facturacion (Finanzas > Descargar totales).')
#Se calcula la nomina a 30% + 5% efectivo.
def calculo_30_nomina(nombre_conductor):
    ganancias = df_fact[df_fact['Nombre'] == nombre_conductor]['Ganancias'].sum()
    propinas = df_fact[df_fact['Nombre'] == nombre_conductor]['Propinas'].sum()
    bonificaciones = df_fact[df_fact['Nombre'] == nombre_conductor]['Bonificaciones'].sum()

    ganancias_netas = ganancias - propinas - bonificaciones
    ganancias_sin_iva = ganancias_netas/1.1
    bonificaciones_sin_iva = bonificaciones/1.1

    nomina_conductor = (ganancias_sin_iva*0.3) + bonificaciones_sin_iva + propinas
    efectivo = ganancias_sin_iva*0.05

    return nomina_conductor, efectivo

#Se calcula la nomina a 25% + 5% efectivo.
def calculo_25_nomina(nombre_conductor):
    ganancias = df_fact[df_fact['Nombre'] == nombre_conductor]['Ganancias'].sum()
    propinas = df_fact[df_fact['Nombre'] == nombre_conductor]['Propinas'].sum()
    bonificaciones = df_fact[df_fact['Nombre'] == nombre_conductor]['Bonificaciones'].sum()

    ganancias_netas = ganancias - propinas - bonificaciones
    ganancias_sin_iva = ganancias_netas/1.1
    bonificaciones_sin_iva = bonificaciones/1.1

    nomina_conductor = (ganancias_sin_iva*0.25) + bonificaciones_sin_iva + propinas
    efectivo = ganancias_sin_iva*0.05
    return nomina_conductor, efectivo

if cabify_fact_data is not None:
    df_fact = pd.read_excel(cabify_fact_data)

    df_fact.rename(columns={'Nombre conductor': 'Nombre', 'Total ganancias': 'Ganancias'}, inplace=True)
    #Se crea un listado de conductores del excel de facturacion
    conductores_facturacion = list(df_fact['Nombre'])
    if "Alquiler Alc 7 SL" in conductores_facturacion and "Totales compañía" in conductores_facturacion:
        conductores_facturacion.remove("Alquiler Alc 7 SL")
        conductores_facturacion.remove("Totales compañía")

    data_facturacion = []
    for conductor in conductores_facturacion:
        dict_facturacion = {}

        if conductor in conductores_70:
            nomina_conductor, efectivo = calculo_30_nomina(conductor)
            promedio_de_aceptacion = combined_df_acept[combined_df_acept['Nombre'] == conductor]['Aceptacion'].mean()

            dict_facturacion.update({'Nombre': conductor, 'Nomina': round(nomina_conductor, 2), 'Efectivo': round(efectivo, 2), 'Aceptacion': round(promedio_de_aceptacion, 2)})
            data_facturacion.append(dict_facturacion)

        elif conductor in conductores_menos_70:
            nomina_conductor, efectivo = calculo_25_nomina(conductor)
            promedio_de_aceptacion = combined_df_acept[combined_df_acept['Nombre'] == conductor]['Aceptacion'].mean()

            dict_facturacion.update({'Nombre': conductor, 'Nomina': round(nomina_conductor, 2), 'Efectivo': round(efectivo, 2), 'Aceptacion': round(promedio_de_aceptacion, 2)})
            data_facturacion.append(dict_facturacion)
        else:
            nomina_conductor_30, efectivo_30 = calculo_30_nomina(conductor)
            promedio_de_aceptacion = combined_df_acept[combined_df_acept['Nombre'] == conductor]['Aceptacion'].mean()
            dict_facturacion_30 = {'Nombre': conductor, 'Nomina': round(nomina_conductor_30, 2), 'Efectivo': round(efectivo_30, 2), 'Aceptacion': round(promedio_de_aceptacion, 2)}
            data_facturacion.append(dict_facturacion_30)
            
            nomina_conductor_20, efectivo_20 = calculo_25_nomina(conductor)
            promedio_de_aceptacion = combined_df_acept[combined_df_acept['Nombre'] == conductor]['Aceptacion'].mean()
            dict_facturacion_20 = {'Nombre': conductor, 'Nomina': round(nomina_conductor_20, 2), 'Efectivo': round(efectivo_20, 2), 'Aceptacion': round(promedio_de_aceptacion, 2)}
            data_facturacion.append(dict_facturacion_20)

    temp_df_fact = pd.DataFrame(data_facturacion)
    temp_df_fact = temp_df_fact.sort_values(by='Nombre', ignore_index=True)

    st.dataframe(temp_df_fact)

    #Descarga del archivo de la tabla de nominas a excel
    output = io.BytesIO()
    temp_df_fact.to_excel(output, index=False)
    output.seek(0)

    st.download_button(
        label='Descargar Excel',
        data=output,
        file_name='Nominas_de_conductores_Cabify.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        icon=":material/download:"
    )
