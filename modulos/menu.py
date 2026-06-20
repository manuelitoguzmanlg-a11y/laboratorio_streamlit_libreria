import streamlit as st


def inicializar_sesion():
    if "logueado" not in st.session_state:
        st.session_state["logueado"] = False

    if "usuario" not in st.session_state:
        st.session_state["usuario"] = ""

    if "nombre_usuario" not in st.session_state:
        st.session_state["nombre_usuario"] = ""

    if "rol" not in st.session_state:
        st.session_state["rol"] = ""

    if "pagina" not in st.session_state:
        st.session_state["pagina"] = "Inicio"


def cerrar_sesion():
    st.session_state["logueado"] = False
    st.session_state["usuario"] = ""
    st.session_state["nombre_usuario"] = ""
    st.session_state["rol"] = ""
    st.session_state["pagina"] = "Inicio"
    st.rerun()


def mostrar_sidebar():
    with st.sidebar:

        st.markdown("""
            <div style="
                background: linear-gradient(135deg, #0f172a, #1e293b);
                border: 1px solid #d4af37;
                border-radius: 18px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.35);
            ">
                <h2 style="color:white; margin-bottom:5px;">📚 Librería</h2>
                <p style="color:#cbd5e1; margin-bottom:0;">
                    Sistema de gestión con Streamlit y MySQL
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.write(f"**Usuario:** {st.session_state.get('nombre_usuario', '')}")
        st.write(f"**Rol:** {st.session_state.get('rol', '')}")

        st.divider()

        rol = st.session_state.get("rol", "")

        opciones = [
            "Inicio",
            "Clientes",
            "Libros",
            "Ventas"
        ]

        if rol == "Administrador":
            opciones.append("Usuarios")

        pagina = st.radio(
            "Menú del sistema",
            opciones,
            key="menu_principal"
        )

        st.session_state["pagina"] = pagina

        st.divider()

        if st.button("🚪 Cerrar sesión", use_container_width=True):
            cerrar_sesion()
