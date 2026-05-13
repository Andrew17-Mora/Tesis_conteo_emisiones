
# CALCULADORA DE EMISIONES VEHICULARES
# Bottom-Up y Top-Down
# Contaminantes: CO, NOx y PM25


import streamlit as st
import pandas as pd
import io


st.set_page_config(
    page_title="Calculadora de Emisiones Vehiculares",
    layout="wide"
)

st.title("Calculadora de Emisiones Vehiculares")



# FACTORES DE EMISIÓN (g/km)
FACTORES = {
    "automovil": {
        "CO": 3.70,
        "NOx": 0.79,
        "PM25": 4.14,
    },
    "motocicleta": {
        "CO": 14.17,
        "NOx": 0.223,
        "PM25": 1.43,
    },
    "camion": {
        "CO": 57.34,
        "NOx": 6.39,
        "PM25": 0.50,
    },
    "bus": {
        "CO": 13.83,
        "NOx": 4.03,
        "PM25": 0.30,
    },
}


# MAPEO DE NOMBRES

MAPEO_VEHICULOS = {
    "carro": "automovil",
    "automovil": "automovil",
    "automóvil": "automovil",
    "moto": "motocicleta",
    "motos": "motocicleta",
    "motocicleta": "motocicleta",
    "camion": "camion",
    "camión": "camion",
    "camiones": "camion",
    "bus": "bus",
    "buses": "bus",
    "buseta": "bus",
    "trasmi": "bus",
    "sitp": "bus",
}


# PARÁMETROS

st.sidebar.header("Parámetros")

longitud_km = st.sidebar.number_input(
    "Longitud de la red vial (km)",
    min_value=0.01,
    value=1.32,
    step=0.01,
)

velocidad_referencia = st.sidebar.number_input(
    "Velocidad de referencia (km/h)",
    min_value=1.0,
    value=50.0,
    step=1.0,
)

# ==========================================
# FUNCIONES AUXILIARES
# ==========================================
def obtener_columna_velocidad(df_sim, condicion):
    """
    Retorna el nombre de la columna de velocidad.
    """
    posibles = [
        f"V prom km/h_{condicion}",
        f"Average speed, km/h_{condicion}",
    ]

    for col in posibles:
        if col in df_sim.columns:
            return col

    return None


def leer_conteo(df, condicion, escenario):
    """
    Extrae el conteo de vehículos usando la columna
    No_vehiculos_Entrado.
    """

  
    if escenario == "escenarios":
        if condicion == "conteo":
            idx = 0
        elif condicion == "fluido":
            idx = 3
        else:  
            idx = 6

    # Escenario: conteo_optimizado
    else:
        if condicion == "conteo":
            idx = 0
        else:  
            idx = 3

    col_veh = df.columns[idx]
    col_num = df.columns[idx + 1]  

    conteo = df[[col_veh, col_num]].copy()
    conteo.columns = ["vehiculos", "cantidad"]
    conteo = conteo.dropna()

    vehiculos = {}

    for _, row in conteo.iterrows():
        nombre = str(row["vehiculos"]).strip().lower()
        cantidad = pd.to_numeric(row["cantidad"], errors="coerce")

        if pd.isna(cantidad):
            continue

        if nombre in ["total", "nan", ""]:
            continue

        if nombre in MAPEO_VEHICULOS:
            categoria = MAPEO_VEHICULOS[nombre]
            vehiculos[categoria] = (
                vehiculos.get(categoria, 0) + float(cantidad)
            )

    return vehiculos



# BOTTOM-UP

def calcular_bottom_up(vehiculos, longitud, factor):
    registros = []

    for tipo, cantidad in vehiculos.items():
        fe = FACTORES[tipo]

        CO = cantidad * longitud * fe["CO"] * factor / 1000
        nox = cantidad * longitud * fe["NOx"] * factor / 1000
        PM25 = cantidad * longitud * fe["PM25"] * factor / 1000

        registros.append({
            "Tipo de vehículo": tipo,
            "No. vehículos": cantidad,
            "CO (kg/h)": CO,
            "NOx (kg/h)": nox,
            "PM25 (kg/h)": PM25,
            "Total (kg/h)": CO + nox + PM25,
        })

    df = pd.DataFrame(registros)

    total = pd.DataFrame([{
        "Tipo de vehículo": "TOTAL",
        "No. vehículos": df["No. vehículos"].sum(),
        "CO (kg/h)": df["CO (kg/h)"].sum(),
        "NOx (kg/h)": df["NOx (kg/h)"].sum(),
        "PM25 (kg/h)": df["PM25 (kg/h)"].sum(),
        "Total (kg/h)": df["Total (kg/h)"].sum(),
    }])

    return pd.concat([df, total], ignore_index=True)



# TOP-DOWN

def calcular_top_down(vehiculos, factor):
    total_veh = sum(vehiculos.values())

    # Flujo vehicular (veh/h)
   
    flujo_total = total_veh

    
    fe_prom = {"CO": 0, "NOx": 0, "PM25": 0}

    for tipo, cantidad in vehiculos.items():
        peso = cantidad / total_veh
        fe = FACTORES[tipo]

        fe_prom["CO"] += fe["CO"] * peso
        fe_prom["NOx"] += fe["NOx"] * peso
        fe_prom["PM25"] += fe["PM25"] * peso

    # Emisiones Top-Down
    CO_total = fe_prom["CO"] * factor * flujo_total / 1000
    nox_total = fe_prom["NOx"] * factor * flujo_total / 1000
    PM25_total = fe_prom["PM25"] * factor * flujo_total / 1000

    total = pd.DataFrame([{
        "Tipo de vehículo": "TOTAL FLOTA",
        "No. vehículos": total_veh,
        "Flujo vehicular (veh/h)": flujo_total,
        "FE CO promedio": fe_prom["CO"],
        "FE NOx promedio": fe_prom["NOx"],
        "FE PM25 promedio": fe_prom["PM25"],
        "CO (kg/h)": CO_total,
        "NOx (kg/h)": nox_total,
        "PM25 (kg/h)": PM25_total,
        "Total (kg/h)": CO_total + nox_total + PM25_total,
    }])

    return total


# CARGA DEL ARCHIVO

archivo = st.file_uploader(
    "Cargar archivo Excel",
    type=["xlsx"],
)

if archivo is not None:

    xls = pd.ExcelFile(archivo)

    hojas_requeridas = [
        "simulacion_escenarios",
        "simulacion_optimizada",
        "conteo_escenarios",
        "conteo_optimizado",
    ]

    faltantes = [h for h in hojas_requeridas if h not in xls.sheet_names]

    if faltantes:
        st.error(f"Faltan hojas en el archivo: {faltantes}")
        st.stop()

    # SELECCIÓN DE ESCENARIO

    escenario = st.selectbox(
        "Escenario",
        ["escenarios", "optimizado"],
    )

    if escenario == "escenarios":
        condiciones = ["conteo", "fluido", "moderado", "pesado"]
        hoja_sim = "simulacion_escenarios"
        hoja_conteo = "conteo_escenarios"
    else:
        condiciones = ["conteo", "moderado", "pesado"]
        hoja_sim = "simulacion_optimizada"
        hoja_conteo = "conteo_optimizado"

    condicion = st.selectbox(
        "Condición de tráfico",
        condiciones,
    )

    
    # LEER SIMULACIÓN

    df_sim = pd.read_excel(xls, sheet_name=hoja_sim)

    col_vel = obtener_columna_velocidad(df_sim, condicion)

    if col_vel is None:
        st.error("No se encontró la columna de velocidad.")
        st.write("Columnas disponibles:")
        st.write(df_sim.columns.tolist())
        st.stop()

    vel_prom = pd.to_numeric(
        df_sim[col_vel],
        errors="coerce"
    ).dropna().mean()


    # FACTOR DE ACTIVIDAD
    
    if vel_prom > 0:
        factor_actividad = velocidad_referencia / vel_prom
    else:
        factor_actividad = 1.0


    # LEER CONTEO
   
    df_conteo = pd.read_excel(
        xls,
        sheet_name=hoja_conteo,
        header=1
    )

    vehiculos = leer_conteo(
        df_conteo,
        condicion,
        escenario
    )

    if len(vehiculos) == 0:
        st.error("No se encontraron vehículos válidos.")
        st.stop()

    total_vehiculos = sum(vehiculos.values())


    # INDICADORES
   
    st.subheader("Indicadores principales")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Velocidad promedio", f"{vel_prom:.2f} km/h")
    c2.metric("Factor de actividad", f"{factor_actividad:.3f}")
    c3.metric("Total vehículos", f"{total_vehiculos:.0f}")
    c4.metric("Longitud", f"{longitud_km:.2f} km")

    # CÁLCULOS

    resultado_bottom = calcular_bottom_up(
        vehiculos,
        longitud_km,
        factor_actividad
    )

    resultado_top = calcular_top_down(
        vehiculos,
        factor_actividad
    )


    # RESULTADOS
   
    st.subheader("Resultados Bottom-Up")
    st.dataframe(
        resultado_bottom.round(4),
        use_container_width=True
    )

    st.subheader("Resultados Top-Down")
    st.dataframe(
        resultado_top.round(4),
        use_container_width=True
    )

   
    # GRÁFICA
    
    st.subheader("Emisiones por tipo de vehículo")

    graf = resultado_bottom[
        resultado_bottom["Tipo de vehículo"] != "TOTAL"
    ].set_index("Tipo de vehículo")[[
        "CO (kg/h)",
        "NOx (kg/h)",
        "PM25 (kg/h)",
    ]]

    st.bar_chart(graf)

    
    # EXPORTAR A EXCEL
    
    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        resultado_bottom.to_excel(
            writer,
            sheet_name="Bottom_Up",
            index=False,
        )

        resultado_top.to_excel(
            writer,
            sheet_name="Top_Down",
            index=False,
        )

        parametros = pd.DataFrame({
            "Parámetro": [
                "Escenario",
                "Condición",
                "Velocidad promedio (km/h)",
                "Velocidad referencia (km/h)",
                "Factor de actividad",
                "Longitud (km)",
                "Total vehículos",
            ],
            "Valor": [
                escenario,
                condicion,
                round(vel_prom, 2),
                velocidad_referencia,
                round(factor_actividad, 4),
                longitud_km,
                total_vehiculos,
            ],
        })

        parametros.to_excel(
            writer,
            sheet_name="Parametros",
            index=False,
        )

    buffer.seek(0)

    st.download_button(
        label="Descargar resultados en Excel",
        data=buffer.getvalue(),
        file_name=f"emisiones_{escenario}_{condicion}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

else:
    st.info("")