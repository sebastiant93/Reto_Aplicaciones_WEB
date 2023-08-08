#*****************Importación de librerías
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.express as px
import altair as alt

#*****************Funciones

def markdown_style():
#Función encargada de dar formato a los KPIs usados en el dashboard (https://discuss.streamlit.io/t/change-metric-color-font-background-and-style/25309/5)
    st.markdown("""
    <style>
    div[data-testid="metric-container"] {
       background-color: rgba(209,238,238);
       border: 1px solid rgba(28, 131, 225, 0.1);
       padding: 5% 5% 5% 10%;
       border-radius: 5px;
       color: black;
       overflow-wrap: break-word;
    }

    /* breakline for metric text         */
    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
       overflow-wrap: break-word;
       white-space: break-spaces;
       color: rgb(25,25,112);
    }
    </style>
"""
    , unsafe_allow_html=True)

#*************************** Main *********************************************************************************

#**********Lectura de Archivos

#Se toma el archivo fuente
data=pd.read_csv("Employee_data.csv")

#Se mantienen únicamente los campos indicados en el ejercicio

data=data[["name_employee","birth_date","age","gender","marital_status","hiring_date","position","salary","performance_score","last_performance_date","average_work_hours","satisfaction_level","absences"]]

#**********Configuración del layout y formato de métricas

st.set_page_config(layout="wide",initial_sidebar_state="expanded")
markdown_style()

#**********Barra lateral con controles de filtrado para el dashboard

with st.sidebar:
    logo=Image.open("Logo.png")
    st.image(logo)
    st.markdown("## Controles")
    genero=st.sidebar.radio("Elige el género",data["gender"].unique())
    e_civil=st.sidebar.radio("Indique el estado civil",data["marital_status"].unique())
    rango=st.sidebar.slider("Indique el rango de performance Score",data["performance_score"].min(),data["performance_score"].max(),[data["performance_score"].min(),data["performance_score"].max()])

#********** Cálculo de métricas y dataframes para gráficos y cifras

#Métricas generales por hombres y mujeres

#Cálculo de medianas para el performance score y las horas trabajadas
mediana_ps_hombres=data.loc[data["gender"]=="M ","performance_score"].median()
mediana_ps_mujeres=data.loc[data["gender"]=="F","performance_score"].median()

#Horas promedio trabajadas por género
prom_ht_hombres=int(data.loc[data["gender"]=="M ","average_work_hours"].mean())
prom_ht_mujeres=int(data.loc[data["gender"]=="F","average_work_hours"].mean())

#Métricas particulares del grupo filtrado
data_plots=data.copy() #Se realiza una copia del df original para preservar datos
data_plots=data_plots[(data_plots["gender"]==genero) &
    (data_plots["marital_status"]==e_civil) &
    (data_plots["performance_score"]>=rango[0]) &
    (data_plots["performance_score"]<=rango[1])] #Se filtra la información de los datos de acuerdo al género, estado civil, y rango del performance score seleccionado
mediana_grupo=data_plots["performance_score"].median() #Mediana del grupo de datos seleccionado de acuerdo con el filtro

data_marital=data.copy() #Filtrado de acuerdo al estado civil. Luego se usa para el gráfico de barras en comparación de horas trabajadas
data_marital=data_marital[(data_marital["marital_status"]==e_civil) &
    (data_marital["performance_score"]>=rango[0]) &
    (data_marital["performance_score"]<=rango[1])] #Se filtra de acuerdo al rango del performance score y estado civil

horas_trabajo=data_marital[["average_work_hours","gender"]].groupby(["gender"]).mean().reset_index() #Mediana de horas de trabajo agrupadas por género


#********** Traducción de textos para conclusiones en el dashboard

#Traducción género
if genero=="M ":
   gender_text="Hombres"
else:
   gender_text="Mujeres"

#Traducción estado
estado_dic={"Single":"Solter@s","Married":"Casad@s","Divorced":"Divorciad@s","Separated":"Separad@s","Widowed":"Viud@s"}
e_civil_text=estado_dic[e_civil]

#********************************* Diseño del dashboard ****************************

#**********Título

st.title("Desempeño en Socialize your Knowledge")

#**********Descripción y logo

with st.container():
    description,image=st.columns([0.7,0.3])
    with description:
        st.markdown("### El siguiente dashboard muestra los KPIs de desempeño de los trabajadores en Socialize your Knowledge")
    with image:
        st.image(logo)

st.write("---")

#********** Cuadros con métricas de los KPIs

st.markdown("## Métricas generales")

with st.container():
    met1,met2,met3,met4=st.columns(4)
    met1.metric("Score Hombres",f"{mediana_ps_hombres}")
    met2.metric("Score Mujeres",f"{mediana_ps_mujeres}")
    met3.metric("Horas Promedio Hombres",f"{prom_ht_hombres}")
    met4.metric("Horas Promedio Mujer",f"{prom_ht_mujeres}")

#********** Visualización Distribución de puntajes de acuerdo con filtros seleccionados

with st.container():
    col1,col2,col3=st.columns([0.2,0.1,0.7])
    with col1: #Texto conclusivo
        st.markdown(f"<h2 style='text-align: center; color: grey;'>Se tiene {mediana_grupo} como tendencia central del performance score  de {gender_text} {e_civil_text}  </h2>", unsafe_allow_html=True)

    with col3: #Histograma de distribución de performance Score
        histogram=px.histogram(data_plots,x="performance_score",title="Distribución del performance Score").update_layout(yaxis_title="Conteo",xaxis_title="Performance Score")
        histogram.add_vline(x=mediana_grupo,fillcolor="red",line_dash="dash", line_color="green",annotation_text="Tendencia",annotation_font_size=20, annotation_font_color="green",annotation_position="top")
        st.plotly_chart(histogram,use_container_width=True)

#********** Visualización Promedio horas trabajadas por género, relación edad salario, y promedio horas versus puntaje

with st.container(): # Segunda línea de gráficos con información particular de los grupos filtrados
    col1,col2,col3=st.columns(3)

    with col1:  #Promedio de horas trabajadas por género
        bar_htrabjo=px.bar(horas_trabajo,x="gender",y="average_work_hours",title="Horas de trabajo por género").update_layout(xaxis_title="Género",yaxis_title="Horas promedio de trabajo")
        st.plotly_chart(bar_htrabjo,title="Horas de trabajo por género",use_container_width=True)

    with col2: #Relación entre edad y salario
        scatt_1=px.scatter(data_plots,x="age",y="salary",title="Edad vs Sueldo").update_layout(xaxis_title="Edad",yaxis_title="Sueldo")
        st.plotly_chart(scatt_1,use_container_width=True)

    with col3: #Relación entre horas y performance score
        scatt_2=px.scatter(data_plots,x="average_work_hours",y="performance_score",title="Performance Score vs horas de trabajo").update_layout(xaxis_title="Performance Score",yaxis_title="Horas promedio de trabajo")
        st.plotly_chart(scatt_2,use_container_width=True)

#********** Texto descriptivo de gráficas

with st.container():
    conc1,conc,conc3=st.columns(3)

    with col1:
        st.markdown(f'#### <div style="text-align: left;">Comparación horas trabajadas entre hombres y mujeres {e_civil_text}</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'#### <div style="text-align: left;">Relación entre edad y sueldo de {gender_text} {e_civil_text}</div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'#### <div style="text-align: left;">Relación entre performance score y horas de trabajo de {gender_text} {e_civil_text}</div>', unsafe_allow_html=True)
