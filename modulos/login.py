import streamlit as st
import hashlib
from modulos.config.conexion import obtener_conexion, obtener_fecha_hora


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def asegurar_tabla_usuarios():
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario_Lab (
            Id_Usuario INT AUTO_INCREMENT PRIMARY KEY,
            Usuario VARCHAR(50) NOT NULL UNIQUE,
            Nombre VARCHAR(100) NOT NULL,
            Password_Hash VARCHAR(255) NOT NULL,
            Rol VARCHAR(50) NOT NULL,
            Fecha_Registro DATETIME
        )
    """)

    usuarios_base = [
        ("admin", "Administrador del Sistema", "1234", "Administrador"),
        ("vendedor", "Usuario Vendedor", "1234", "Vendedor")
    ]

    for usuario, nombre, password, rol in usuarios_base:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM Usuario_Lab 
            WHERE Usuario = %s
        """, (usuario,))

        existe = cursor.fetchone()[0]

        if existe == 0:
            cursor.execute("""
                INSERT INTO Usuario_Lab
                (Usuario, Nombre, Password_Hash, Rol, Fecha_Registro)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                usuario,
                nombre,
                hash_password(password),
                rol,
                obtener_fecha_hora()
            ))

    con.commit()
    cursor.close()
    con.close()


def aplicar_estilo_login():
    st.markdown("""
        <style>
            .login-card {
                background: linear-gradient(135deg, #0f172a, #1e293b);
                border: 1px solid #d4af37;
                border-radius: 22px;
                padding: 35px;
                margin: 40px auto;
                max-width: 650px;
                box-shadow: 0 12px 30px rgba(0,0,0,0.35);
            }

            .login-title {
                color: #f8fafc;
                font-size: 40px;
                font-weight: 900;
                text-align: center;
                margin-bottom: 10px;
            }

            .login-subtitle {
                color: #cbd5e1;
                font-size: 16px;
                text-align: center;
                margin-bottom: 20px;
            }

            .gold-line {
                height: 3px;
                background: linear-gradient(90deg, #d4af37, #f5d76e, #d4af37);
                border-radius: 20px;
                margin: 20px 0;
            }
        </style>
    """, unsafe_allow_html=True)


def mostrar_login():
    aplicar_estilo_login()

    try:
        asegurar_tabla_usuarios()
    except Exception as e:
        st.error(f"Error al preparar usuarios: {e}")
        return

    st.markdown("""
        <div class="login-card">
            <div class="login-title">📚 Sistema de Librería</div>
            <div class="login-subtitle">
                Aplicación Streamlit conectada a MySQL en Clever Cloud
            </div>
            <div class="gold-line"></div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        usuario = st.text_input("Usuario", placeholder="Ejemplo: admin")
        password = st.text_input("Contraseña", type="password", placeholder="Ejemplo: 1234")

        ingresar = st.button("🔐 Iniciar sesión", use_container_width=True)

        if ingresar:
            if usuario.strip() == "" or password.strip() == "":
                st.warning("Debe ingresar usuario y contraseña.")
                return

            try:
                con = obtener_conexion()
                cursor = con.cursor()

                cursor.execute("""
                    SELECT Usuario, Nombre, Password_Hash, Rol
                    FROM Usuario_Lab
                    WHERE Usuario = %s
                """, (usuario.strip().lower(),))

                resultado = cursor.fetchone()

                cursor.close()
                con.close()

                if resultado is None:
                    st.error("Usuario no registrado.")
                    return

                usuario_db = resultado[0]
                nombre_db = resultado[1]
                password_hash_db = resultado[2]
                rol_db = resultado[3]

                if hash_password(password.strip()) == password_hash_db:
                    st.session_state["logueado"] = True
                    st.session_state["usuario"] = usuario_db
                    st.session_state["nombre_usuario"] = nombre_db
                    st.session_state["rol"] = rol_db

                    st.success(f"Bienvenido, {nombre_db}")
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta.")

            except Exception as e:
                st.error(f"Error al iniciar sesión: {e}")
