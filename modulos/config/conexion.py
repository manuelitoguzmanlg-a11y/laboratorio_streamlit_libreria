import streamlit as st
import mysql.connector
from datetime import datetime
from zoneinfo import ZoneInfo


def obtener_conexion():
    conexion = mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=int(st.secrets["mysql"]["port"])
    )

    return conexion


def obtener_fecha_hora():
    fecha_hora = datetime.now(ZoneInfo("America/El_Salvador"))
    return fecha_hora.strftime("%Y-%m-%d %H:%M:%S")
