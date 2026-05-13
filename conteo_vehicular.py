from ultralytics import YOLO
import pandas as pd
import cv2
import os
from collections import defaultdict

# ==========================================
# CONFIGURACION
# ==========================================

VIDEO=r"C:\Users\CORE I5\Downloads\proyecto_tesis\videos\calida_entrada_sur.mp4"
MODELO="yolov8n.pt"

FRAME_SKIP=1
LINE_X=450      
MARGEN=30
CONF=0.25

MAPA={
    2:'carro',
    3:'moto',
    5:'bus',
    7:'camion'
}

# ==========================================
# CARGA
# ==========================================

model=YOLO(MODELO)

cap=cv2.VideoCapture(VIDEO)

if not cap.isOpened():
    print("No se pudo abrir el video.")
    exit()

fps=cap.get(cv2.CAP_PROP_FPS)

if fps<=0:
    fps=20

BASE=os.getcwd()
print("Archivos guardados en:")
print(BASE)

# ==========================================
# VARIABLES
# ==========================================

conteo=defaultdict(int)

ids_contados=set()

trayectorias={}

registros=[]

frame_num=0

# ==========================================
# VIDEO SALIDA
# ==========================================

out=cv2.VideoWriter(
    os.path.join(BASE,'resultado_conteo.avi'),
    cv2.VideoWriter_fourcc(*'XVID'),
    fps,
    (640,360)
)

# ==========================================
# PROCESAMIENTO
# ==========================================

while cap.isOpened():

    ok,frame=cap.read()

    if not ok:
        break

    frame_num+=1

    if frame_num % FRAME_SKIP !=0:
        continue

    frame=cv2.resize(frame,(640,360))

    results=model.track(
        frame,
        persist=True,
        tracker='bytetrack.yaml',
        conf=CONF,
        verbose=False
    )

    if results[0].boxes.id is not None:

        boxes=results[0].boxes

        for i in range(len(boxes)):

            clase=int(boxes.cls[i])

            if clase not in MAPA:
                continue

            tipo=MAPA[clase]

            x1,y1,x2,y2=map(int,boxes.xyxy[i])

            track_id=int(boxes.id[i])

            cx=int((x1+x2)/2)

            if track_id not in trayectorias:
                trayectorias[track_id]=[]

            trayectorias[track_id].append(cx)

            # ==================================
            # CONTEO AL CRUZAR LINEA
            # ==================================

          

            if (
            abs(cx-LINE_X) < MARGEN and
            track_id not in ids_contados
            ):

                ids_contados.add(track_id)

                conteo[tipo]+=1

                tiempo=round(frame_num/fps,2)

                registros.append({
                    "ID":track_id,
                    "Tiempo_seg":tiempo,
                    "Tipo":tipo
                })

            # ==================================
            # DIBUJOS
            # ==================================

            cv2.rectangle(
                frame,
                (x1,y1),
                (x2,y2),
                (0,255,0),
                2
            )

            cv2.putText(
                frame,
                f"{tipo}-{track_id}",
                (x1,y1-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0,255,0),
                2
            )

    # Linea conteo
    cv2.line(
        frame,
        (LINE_X,0),
        (LINE_X,360),
        (255,0,0),
        3
    )

    # ==================================
    # PANEL METRICAS
    # ==================================

    y=30

    total=sum(conteo.values())

    for tipo,cant in conteo.items():

        cv2.putText(
            frame,
            f"{tipo}: {cant}",
            (10,y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255,255,255),
            2
        )

        y+=30

    cv2.putText(
        frame,
        f"TOTAL: {total}",
        (10,y+20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255,255,255),
        2
    )

    out.write(frame)

# ==========================================
# CIERRE
# ==========================================

cap.release()
out.release()

# ==========================================
# EXPORTAR EXCEL + CSV
# ==========================================

if len(registros)>0:

    df=pd.DataFrame(registros)

    resumen=(
        df.groupby("Tipo")
        .size()
        .reset_index(name="Cantidad")
    )

    total_vehiculos=len(df)

    resumen["Porcentaje"]=(
        resumen["Cantidad"]/
        total_vehiculos*100
    ).round(2)

    flujo_hora=round(
        total_vehiculos/
        (frame_num/fps/3600),
        2
    )

    metricas=pd.DataFrame({
        "Metrica":[
            "Total Vehiculos",
            "Flujo veh/h",
            "FPS usado"
        ],
        "Valor":[
            total_vehiculos,
            flujo_hora,
            fps
        ]
    })

    excel_path=os.path.join(
        BASE,
        "conteo_vehicular.xlsx"
    )

    with pd.ExcelWriter(
        excel_path,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="Cruces",
            index=False
        )

        resumen.to_excel(
            writer,
            sheet_name="Resumen",
            index=False
        )

        metricas.to_excel(
            writer,
            sheet_name="Metricas",
            index=False
        )

    

# ==========================================
# RESULTADOS
# ==========================================

print("\n===== CONTEO FINAL =====")

for k,v in conteo.items():
    print(k, v)

print("\nArchivos generados:")
print("resultado_conteo.avi")
print("conteo_vehicular.xlsx")
