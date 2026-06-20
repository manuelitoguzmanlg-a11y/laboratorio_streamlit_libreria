import streamlit as st
import pandas as pd

from modulos.login import mostrar_login
from modulos.menu import inicializar_sesion, mostrar_sidebar
from modulos.clientes import mostrar_clientes
from modulos.libros import mostrar_libros
from modulos.ventas import mostrar_ventas
from modulos.config.conexion import obtener_conexion


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Sistema de Librería",
    page_icon="📚",
    layout="wide"
)


# =========================================================
# ESTILO GLOBAL
# =========================================================

def aplicar_estilo_global():
    st.markdown("""
        <style>
            .stApp {
                background: radial-gradient(circle at top left, #1e293b 0%, #0f172a 45%, #020617 100%);
            }

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #020617, #0f172a, #1e293b);
                border-right: 1px solid rgba(212, 175, 55, 0.35);
            }

            .main-card {
                background: linear-gradient(135deg, #0f172a, #1e293b);
                border: 1px solid #d4af37;
                border-radius: 24px;
                padding: 34px;
                margin-bottom: 28px;
                box-shadow: 0 14px 35px rgba(0,0,0,0.40);
            }

            .main-title {
                color: #f8fafc;
                font-size: 44px;
                font-weight: 950;
                margin-bottom: 8px;
            }

            .main-subtitle {
                color: #cbd5e1;
                font-size: 17px;
                line-height: 1.6;
            }

            .gold-line {
                height: 3px;
                background: linear-gradient(90deg, #d4af37, #f5d76e, #d4af37);
                border-radius: 20px;
                margin: 20px 0;
            }

            .info-card {
                background: #0f172a;
                border-left: 5px solid #d4af37;
                border-radius: 14px;
                padding: 18px 22px;
                color: #e5e7eb;
                margin-bottom: 20px;
            }

            .section-title {
                color: #f5d76e;
                font-size: 26px;
                font-weight: 900;
                margin-bottom: 14px;
            }

            .stButton button {
                border-radius: 12px;
                font-weight: 800;
            }
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# FUNCIONES DE APOYO
# =========================================================

def tabla_existe(nombre_tabla):
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            AND table_name = %s
        """, (nombre_tabla,))

        existe = cursor.fetchone()[0]

        cursor.close()
        con.close()

        return existe > 0

    except Exception:
        return False


def contar_registros(nombre_tabla):
    try:
        if not tabla_existe(nombre_tabla):
            return 0

        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")

        total = cursor.fetchone()[0]

        cursor.close()
        con.close()

        return total

    except Exception:
        return 0


def calcular_total_ventas():
    try:
        if not tabla_existe("Venta_Lab"):
            return 0

        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(Total), 0)
            FROM Venta_Lab
        """)

        total = cursor.fetchone()[0]

        cursor.close()
        con.close()

        return float(total)

    except Exception:
        return 0


# =========================================================
# PÁGINA DE INICIO
# =========================================================

def mostrar_inicio():

    st.markdown("""
        <div class="main-card">
            <div class="main-title">📚 Sistema de Gestión de Librería</div>
            <div class="main-subtitle">
                Aplicación desarrollada en Streamlit con conexión a base de datos MySQL en Clever Cloud.
                El sistema permite gestionar clientes, libros, ventas y usuarios mediante un inicio de sesión
                validado desde la base de datos.
            </div>
            <div class="gold-line"></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Resumen general del sistema</div>',
        unsafe_allow_html=True
    )

    total_clientes = contar_registros("Cliente_Lab")
    total_libros = contar_registros("Libro_Lab")
    total_ventas = contar_registros("Venta_Lab")
    total_ingresos = calcular_total_ventas()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Clientes registrados", total_clientes)

    with col2:
        st.metric("Libros registrados", total_libros)

    with col3:
        st.metric("Ventas registradas", total_ventas)

    with col4:
        st.metric("Ingresos totales", f"${total_ingresos:.2f}")

    st.divider()

    st.markdown(
        '<div class="section-title">Módulos disponibles</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info(
            "👥 **Clientes**\n\n"
            "Permite registrar, consultar, editar y eliminar clientes."
        )

    with col2:
        st.info(
            "📚 **Libros**\n\n"
            "Permite administrar libros, categorías, precios y stock."
        )

    with col3:
        st.info(
            "💰 **Ventas**\n\n"
            "Permite registrar ventas, descontar stock y consultar ingresos."
        )

    st.divider()

    st.markdown("""
        <div class="info-card">
            <b>Usuarios de prueba:</b><br><br>
            Administrador: <b>admin / 1234</b><br>
            Vendedor: <b>vendedor / 1234</b>
        </div>
    """, unsafe_allow_html=True)


# =========================================================
# USUARIOS
# =========================================================

def mostrar_usuarios():

    st.markdown("""
        <div class="main-card">
            <div class="main-title">👤 Usuarios del Sistema</div>
            <div class="main-subtitle">
                Consulta de usuarios registrados para el acceso a la aplicación.
            </div>
            <div class="gold-line"></div>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("rol", "") != "Administrador":
        st.error("Solo el administrador puede ver esta sección.")
        return

    try:
        if not tabla_existe("Usuario_Lab"):
            st.info("La tabla de usuarios todavía no ha sido creada.")
            return

        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT
                Usuario,
                Nombre,
                Rol,
                Fecha_Registro
            FROM Usuario_Lab
            ORDER BY Rol ASC, Nombre ASC
        """)

        usuarios = cursor.fetchall()

        cursor.close()
        con.close()

        if usuarios:
            datos = []

            for usuario in usuarios:
                datos.append({
                    "Usuario": usuario[0],
                    "Nombre": usuario[1],
                    "Rol": usuario[2],
                    "Fecha registro": usuario[3]
                })

            df = pd.DataFrame(datos)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.info("No hay usuarios registrados.")

    except Exception as e:
        st.error(f"Error al cargar usuarios: {e}")


# =========================================================
# INICIO DE LA APP
# =========================================================

aplicar_estilo_global()
inicializar_sesion()

if not st.session_state["logueado"]:
    mostrar_login()
    st.stop()

mostrar_sidebar()

pagina = st.session_state.get("pagina", "Inicio")

if pagina == "Inicio":
    mostrar_inicio()

elif pagina == "Clientes":
    mostrar_clientes()

elif pagina == "Libros":
    mostrar_libros()

elif pagina == "Ventas":
    mostrar_ventas()

elif pagina == "Usuarios":
    mostrar_usuarios()

else:
    mostrar_inicio()
