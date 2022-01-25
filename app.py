from ast import While
from csv import writer
from datetime import date
from enum import unique
from optparse import Values
from matplotlib import markers
from matplotlib.pyplot import title
import streamlit as st
import pandas as pd
import numpy as np
from re import sub
from markdown import markdown
import plotly.express as px 
import time
from PIL import Image
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb


# ---- Start App ----- 


img = Image.open('oca.jpg')
img1=Image.open('oca1.png')
 
# --- Web App Title ----

st.set_page_config(page_title="ITO Enel", page_icon=img, layout="wide")

st.image(img1 , width=250)
st.markdown('''

# **DashBoard ITO Enel **
Esta es una app web creada para facilitar la visualización de datos del proyecto.
---
''')


@st.cache(ttl=60)
def load_csv():
    df = pd.read_csv('BD_ITO_ENEL.csv')
    df['FECHA'] = pd.to_datetime(df['FECHA'], infer_datetime_format=True)
    df["DIAS ENTREGA DOCUMENTACION"] = df["DIAS ENTREGA DOCUMENTACION"].replace(["FALTAN DOCUMENTOS"],0)
    df["DIAS ENTREGA DOCUMENTACION"] = df["DIAS ENTREGA DOCUMENTACION"].astype(int)
    return df

    
df = load_csv()   

with st.container():
    st.write("---")
    left_column,right_column = st.columns(2)
    with left_column:
        st.header("")
        st.write("##")


# ---- PROJECTS ----

st.sidebar.header("Filtrar Aqui:")

year=st.sidebar.multiselect(
    "Seleccione el Año:",
    options=df["AÑO"].unique(),
    default=2022
    # default=df["AÑO"].unique(),
)



month= st.sidebar.multiselect(
     "Seleccione el Mes:",
    options=df["MES"].unique(),
    default ="ENERO",
 )
ito_type = st.sidebar.multiselect(
    "Seccione el tipo de ITO:",
    options=df["AREA"].unique(),
    default=df["AREA"].unique(),
)

ito = st.sidebar.multiselect(
    "Seleccione el ITO:",
    options=df["INSPECTOR"].unique(),
    default=df["INSPECTOR"].unique()
)

df_selection = df.query(
    "AÑO == @year & MES == @month & AREA == @ito_type & INSPECTOR == @ito"
)

# ---- MainPage ----

st.title(":bar_chart: Producción ITO Enel")
st.markdown("##")

# ---- DownLoad Buttons ----

# ---- To Excel ----
def to_excel(df_selection):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df_selection.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data
 
today = date.today()
today = today.strftime("%d/%m/%Y")

df_selection_xlsx = to_excel(df_selection)   
st.download_button(label='📥 Descargar Excel',
                                data=df_selection_xlsx ,
                                file_name='Control_ITO_ENEL'+today +'.xlsx')


st.download_button(label='Descargar CSV', data=df_selection.to_csv(), mime='text/csv')


# ----- MarkDown ----
most_recent_date = df["FECHA"].max().strftime("%d-%m-%y")

st.subheader("Datos actualizados al: ")
st.subheader(f"{most_recent_date}")

# ---- TOP KPI'S ----
total_produccion = int(df_selection["REALIZADO $"].sum())
produccion_ito_enel = int(df_selection["REALIZADO $"].sum())

left_column, middle_column, right_column = st.columns(3)

with left_column:
    st.subheader("Total Producción:")
    st.subheader(f"$ {total_produccion:,}")

with middle_column:
    st.subheader("Meta Mensual")
    st.subheader("$200.000.000")   

with right_column:
    st.subheader("% Avance Meta Mensual")
    st.subheader(f"% {round((100 * total_produccion)/200000000)}")


st.markdown("----")

total_by_ito=(
    df_selection.groupby(by=["INSPECTOR"]).sum()[["REALIZADO $"]].sort_values(by="REALIZADO $"))


fig_producion_ito = px.bar(

    total_by_ito,
    x=total_by_ito.index,
    y="REALIZADO $",
    orientation="v",
    title="<b> Producción por ITO</b>",
    color_discrete_sequence=["#0083b8"] * len(total_by_ito),
    template="plotly_white",
)



fig_producion_ito.update_layout(

    plot_bgcolor="rgba (0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

st.plotly_chart(fig_producion_ito)

produccion_ito_date = (
    df_selection.groupby(by="FECHA").sum()[["REALIZADO $"]]
)

##----

fig_produccion_ito_date = px.bar(

    produccion_ito_date,
    x=produccion_ito_date.index,
    y="REALIZADO $",
    orientation="v",
    title="<b> Producción Total Según Fecha (Días)</b>",
    color_discrete_sequence=["#0083b8"] * len(total_by_ito),
    template="plotly_white",
)



fig_produccion_ito_date.update_layout(

    plot_bgcolor="rgba (0,0,0,0)",
    xaxis=(dict(showgrid=False))
)


result =st.button(
    label="Ocultar"
)

if result==True:
    del(fig_produccion_ito_date)
    result =st.button(
    label="Mostrar"
)
else:
    st.plotly_chart(fig_produccion_ito_date)

    
orden_date = ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO', 'JULIO', 'AGOSTO',
'SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']

df_selection["MES"] = pd.Categorical(df_selection["MES"], orden_date)
total_by_month=(

    df_selection.groupby(by=["MES"]).sum()[["REALIZADO $"]]
)

fig_total_by_month=px.line(
    total_by_month,
    x=total_by_month.index,
    y="REALIZADO $",
    title="<b>Total por Mes <b>",
    markers=True
)

st.plotly_chart(fig_total_by_month)

total_by_baremo = (
    df_selection.groupby(by=["CODIGO"]).sum()[["REALIZADO $"]]
)

pie_chart = px.pie(
    total_by_baremo,
    values="REALIZADO $",
    names=total_by_baremo.index,
    title="<b>Realizado por Codigo de Baremo<b>",
)

st.plotly_chart(pie_chart)

st.subheader("Promedio Entrega de documentación al mandante")
average =(df_selection.groupby(by=["INSPECTOR"]).sum()["DIAS ENTREGA DOCUMENTACION"])/(df_selection.groupby(by=["INSPECTOR"])["DIAS ENTREGA DOCUMENTACION"]).size()
st.write(average)

# st.table(average_doc_ito)

while True:
     # Update every 1 seg
     load_csv()
     time.sleep(1)  
