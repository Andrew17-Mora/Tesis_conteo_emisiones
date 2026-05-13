# Tesis Conteo Vehicular y Modelo de Emisiones

Este repositorio contiene las herramientas desarrolladas para el trabajo de grado titulado:

**“Simulación del flujo vehicular y emisiones de CO, NOₓ y PM₂.₅ en la intersección Avenida Américas – Avenida Ciudad de Cali (Kennedy, El Tintal), mediante conteo vehicular en Python, simulación en AnyLogic y escenarios de optimización vial.”**

## Descripción general

El proyecto integra dos componentes principales:

1. Conteo vehicular automático mediante visión por computador.
2. Modelo de estimación de emisiones contaminantes.

El objetivo es cuantificar el comportamiento del tránsito en la intersección de estudio y evaluar su impacto ambiental bajo diferentes escenarios operacionales.

---

## 1. Conteo vehicular automático

El archivo `conteo_vehicular.py` implementa un sistema de conteo automático de vehículos a partir de videos de tráfico.

### Funcionalidades

- Detección y seguimiento de vehículos.
- Clasificación en las categorías:
  - Automóviles
  - Motos
  - Camiones
  - Buses
- Conteo de vehículos que ingresan y salen.
- Exportación de resultados a archivos Excel.
- Generación de video procesado con las detecciones.

### Tecnologías utilizadas

- Python
- OpenCV
- YOLO
- Pandas

### Resultados generados

- Conteo por categoría vehicular.
- Archivos Excel con estadísticas.
- Video con anotaciones del proceso de detección.

---

## 2. Modelo de estimación de emisiones

La carpeta `modelo_emisiones/` contiene una aplicación desarrollada en Streamlit para estimar emisiones de:

- CO
- NOₓ
- PM₂.₅

### Metodologías implementadas

#### Bottom-Up

Calcula las emisiones por categoría vehicular utilizando los factores de emisión específicos de cada tipo de vehículo.

#### Top-Down

Calcula las emisiones totales de la flota mediante un factor de emisión promedio ponderado.

### Variables de entrada

- Conteo vehicular por categoría.
- Velocidades promedio obtenidas en AnyLogic.
- Factores de emisión.
- Longitud de la red vial.
- Velocidad de referencia.

### Hojas requeridas en el archivo Excel

- `simulacion_escenarios`
- `simulacion_optimizada`
- `conteo_escenarios`
- `conteo_optimizado`

### Resultados generados

- Emisiones por categoría vehicular.
- Emisiones totales por contaminante.
- Comparación entre metodologías Bottom-Up y Top-Down.
- Exportación de resultados a Excel.

---

## Flujo general de trabajo

1. Captura y procesamiento de videos de tráfico.
2. Conteo vehicular automático con Python.
3. Simulación del flujo vehicular en AnyLogic.
4. Exportación de resultados a Excel.
5. Estimación de emisiones con Streamlit.
6. Comparación entre escenario actual y escenario optimizado.

---

## Ejecución del proyecto

### Conteo vehicular


python conteo_vehicular.py
 
 ### modelo de emisiones
  streamlit run modelo_emisiones.py