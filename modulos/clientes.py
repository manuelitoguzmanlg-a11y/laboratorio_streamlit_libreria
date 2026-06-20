from modulos.config.conexion import obtener_conexion, obtener_fecha_hora
import streamlit as st
import pandas as pd


# =========================================================
# BASE DE DATOS
# =========================================================

def asegurar_tabla_clientes():
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Cliente_Lab (
            Id_Cliente INT AUTO_INCREMENT PRIMARY KEY,
            Nombre VARCHAR(120) NOT NULL,
            Telefono VARCHAR(30),
            Correo VARCHAR(120),
            Direccion VARCHAR(200),
            Fecha_Registro DATETIME
        )
    """)

    con.commit()
    cursor.close()
    con.close()


def obtener_clientes():
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("""
        SELECT
            Id_Cliente,
            Nombre,
            Telefono,
            Correo,
            Direccion,
            Fecha_Registro
        FROM Cliente_Lab
        ORDER BY Id_Cliente DESC
    """)

    clientes = cursor.fetchall()

    cursor.close()
    con.close()

    return clientes


# =========================================================
# ESTILO
# =========================================================

def aplicar_estilo_clientes():
    st.markdown("""
        <style>
            .module-card {
                background: linear-gradient(135deg, #0f172a, #1e293b);
                border: 1px solid #d4af37;
                border-radius: 20px;
                padding: 25px;
                margin-bottom: 25px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.35);
            }

            .module-title {
                color: #f8fafc;
                font-size: 34px;
                font-weight: 900;
                margin-bottom: 8px;
            }

            .module-subtitle {
                color: #cbd5e1;
                font-size: 16px;
                margin-bottom: 12px;
            }

            .gold-line {
                height: 3px;
                background: linear-gradient(90deg, #d4af37, #f5d76e, #d4af37);
                border-radius: 20px;
                margin: 18px 0;
            }
        </style>
    """, unsafe_allow_html=True)


# =========================================================
# MÓDULO PRINCIPAL
# =========================================================

def mostrar_clientes():

    aplicar_estilo_clientes()

    st.markdown("""
        <div class="module-card">
            <div class="module-title">👥 Gestión de Clientes</div>
            <div class="module-subtitle">
                Registro, consulta, edición y eliminación de clientes de la librería.
            </div>
            <div class="gold-line"></div>
        </div>
    """, unsafe_allow_html=True)

    try:
        asegurar_tabla_clientes()
    except Exception as e:
        st.error(f"Error al preparar la tabla de clientes: {e}")
        return

    tab_registrar, tab_listado, tab_editar, tab_eliminar = st.tabs(
        [
            "➕ Registrar cliente",
            "📋 Ver clientes",
            "✏️ Editar cliente",
            "🗑️ Eliminar cliente"
        ]
    )

    # =====================================================
    # REGISTRAR CLIENTE
    # =====================================================

    with tab_registrar:

        st.subheader("Registrar nuevo cliente")

        with st.form("form_registrar_cliente"):

            nombre = st.text_input(
                "Nombre del cliente",
                placeholder="Ejemplo: Ana López"
            )

            telefono = st.text_input(
                "Teléfono",
                placeholder="Ejemplo: 7000-0000"
            )

            correo = st.text_input(
                "Correo electrónico",
                placeholder="Ejemplo: cliente@gmail.com"
            )

            direccion = st.text_area(
                "Dirección",
                placeholder="Ejemplo: San Salvador, El Salvador"
            )

            guardar = st.form_submit_button("💾 Guardar cliente")

            if guardar:

                if nombre.strip() == "":
                    st.warning("El nombre del cliente es obligatorio.")

                else:
                    try:
                        con = obtener_conexion()
                        cursor = con.cursor()

                        cursor.execute("""
                            INSERT INTO Cliente_Lab
                            (
                                Nombre,
                                Telefono,
                                Correo,
                                Direccion,
                                Fecha_Registro
                            )
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            nombre.strip(),
                            telefono.strip(),
                            correo.strip(),
                            direccion.strip(),
                            obtener_fecha_hora()
                        ))

                        con.commit()
                        cursor.close()
                        con.close()

                        st.success("Cliente registrado correctamente.")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error al registrar cliente: {e}")

    # =====================================================
    # VER CLIENTES
    # =====================================================

    with tab_listado:

        st.subheader("Clientes registrados")

        try:
            clientes = obtener_clientes()

            if clientes:

                datos = []

                for cliente in clientes:
                    datos.append({
                        "ID": cliente[0],
                        "Nombre": cliente[1],
                        "Teléfono": cliente[2],
                        "Correo": cliente[3],
                        "Dirección": cliente[4],
                        "Fecha registro": cliente[5]
                    })

                df = pd.DataFrame(datos)

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("Todavía no hay clientes registrados.")

        except Exception as e:
            st.error(f"Error al cargar clientes: {e}")

    # =====================================================
    # EDITAR CLIENTE
    # =====================================================

    with tab_editar:

        st.subheader("Editar cliente")

        try:
            clientes = obtener_clientes()

            if clientes:

                opciones = {}

                for cliente in clientes:
                    texto = f"{cliente[1]} | Tel: {cliente[2]} | ID: {cliente[0]}"
                    opciones[texto] = cliente

                seleccion = st.selectbox(
                    "Seleccione el cliente a editar",
                    list(opciones.keys())
                )

                cliente_actual = opciones[seleccion]

                id_cliente = cliente_actual[0]

                with st.form("form_editar_cliente"):

                    nombre_editado = st.text_input(
                        "Nombre",
                        value=cliente_actual[1]
                    )

                    telefono_editado = st.text_input(
                        "Teléfono",
                        value=cliente_actual[2] if cliente_actual[2] else ""
                    )

                    correo_editado = st.text_input(
                        "Correo",
                        value=cliente_actual[3] if cliente_actual[3] else ""
                    )

                    direccion_editada = st.text_area(
                        "Dirección",
                        value=cliente_actual[4] if cliente_actual[4] else ""
                    )

                    actualizar = st.form_submit_button("💾 Guardar cambios")

                    if actualizar:

                        if nombre_editado.strip() == "":
                            st.warning("El nombre no puede quedar vacío.")

                        else:
                            try:
                                con = obtener_conexion()
                                cursor = con.cursor()

                                cursor.execute("""
                                    UPDATE Cliente_Lab
                                    SET
                                        Nombre = %s,
                                        Telefono = %s,
                                        Correo = %s,
                                        Direccion = %s
                                    WHERE Id_Cliente = %s
                                """, (
                                    nombre_editado.strip(),
                                    telefono_editado.strip(),
                                    correo_editado.strip(),
                                    direccion_editada.strip(),
                                    id_cliente
                                ))

                                con.commit()
                                cursor.close()
                                con.close()

                                st.success("Cliente actualizado correctamente.")
                                st.rerun()

                            except Exception as e:
                                st.error(f"Error al actualizar cliente: {e}")

            else:
                st.info("No hay clientes disponibles para editar.")

        except Exception as e:
            st.error(f"Error al cargar editor de clientes: {e}")

    # =====================================================
    # ELIMINAR CLIENTE
    # =====================================================

    with tab_eliminar:

        st.subheader("Eliminar cliente")

        try:
            clientes = obtener_clientes()

            if clientes:

                opciones = {}

                for cliente in clientes:
                    texto = f"{cliente[1]} | Tel: {cliente[2]} | ID: {cliente[0]}"
                    opciones[texto] = cliente

                seleccion = st.selectbox(
                    "Seleccione el cliente a eliminar",
                    list(opciones.keys()),
                    key="select_eliminar_cliente"
                )

                cliente_actual = opciones[seleccion]

                st.warning(
                    f"Vas a eliminar al cliente: {cliente_actual[1]}"
                )

                confirmar = st.checkbox(
                    "Confirmo que deseo eliminar este cliente"
                )

                if st.button("🗑️ Eliminar cliente"):

                    if not confirmar:
                        st.warning("Debés confirmar la eliminación.")

                    else:
                        try:
                            con = obtener_conexion()
                            cursor = con.cursor()

                            cursor.execute("""
                                DELETE FROM Cliente_Lab
                                WHERE Id_Cliente = %s
                            """, (cliente_actual[0],))

                            con.commit()
                            cursor.close()
                            con.close()

                            st.success("Cliente eliminado correctamente.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error al eliminar cliente: {e}")

            else:
                st.info("No hay clientes disponibles para eliminar.")

        except Exception as e:
            st.error(f"Error al cargar eliminación de clientes: {e}")
