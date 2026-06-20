from modulos.config.conexion import obtener_conexion, obtener_fecha_hora
import streamlit as st
import pandas as pd


# =========================================================
# BASE DE DATOS
# =========================================================

def asegurar_tabla_libros():
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Libro_Lab (
            Id_Libro INT AUTO_INCREMENT PRIMARY KEY,
            Titulo VARCHAR(150) NOT NULL,
            Autor VARCHAR(120),
            Categoria VARCHAR(80),
            Precio DECIMAL(10,2) NOT NULL,
            Stock INT NOT NULL,
            Fecha_Registro DATETIME
        )
    """)

    con.commit()
    cursor.close()
    con.close()


def obtener_libros():
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("""
        SELECT
            Id_Libro,
            Titulo,
            Autor,
            Categoria,
            Precio,
            Stock,
            Fecha_Registro
        FROM Libro_Lab
        ORDER BY Id_Libro DESC
    """)

    libros = cursor.fetchall()

    cursor.close()
    con.close()

    return libros


# =========================================================
# ESTILO
# =========================================================

def aplicar_estilo_libros():
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

def mostrar_libros():

    aplicar_estilo_libros()

    st.markdown("""
        <div class="module-card">
            <div class="module-title">📚 Gestión de Libros</div>
            <div class="module-subtitle">
                Registro, consulta, edición y eliminación de libros disponibles en la librería.
            </div>
            <div class="gold-line"></div>
        </div>
    """, unsafe_allow_html=True)

    try:
        asegurar_tabla_libros()
    except Exception as e:
        st.error(f"Error al preparar la tabla de libros: {e}")
        return

    tab_registrar, tab_listado, tab_editar, tab_eliminar = st.tabs(
        [
            "➕ Registrar libro",
            "📋 Ver libros",
            "✏️ Editar libro",
            "🗑️ Eliminar libro"
        ]
    )

    # =====================================================
    # REGISTRAR LIBRO
    # =====================================================

    with tab_registrar:

        st.subheader("Registrar nuevo libro")

        with st.form("form_registrar_libro"):

            titulo = st.text_input(
                "Título del libro",
                placeholder="Ejemplo: El Principito"
            )

            autor = st.text_input(
                "Autor",
                placeholder="Ejemplo: Antoine de Saint-Exupéry"
            )

            categoria = st.selectbox(
                "Categoría",
                [
                    "Novela",
                    "Cuento",
                    "Educativo",
                    "Infantil",
                    "Tecnología",
                    "Historia",
                    "Administración",
                    "Otro"
                ]
            )

            col1, col2 = st.columns(2)

            with col1:
                precio = st.number_input(
                    "Precio",
                    min_value=0.00,
                    step=0.50,
                    format="%.2f"
                )

            with col2:
                stock = st.number_input(
                    "Stock",
                    min_value=0,
                    step=1
                )

            guardar = st.form_submit_button("💾 Guardar libro")

            if guardar:

                if titulo.strip() == "":
                    st.warning("El título del libro es obligatorio.")

                elif precio <= 0:
                    st.warning("El precio debe ser mayor a cero.")

                else:
                    try:
                        con = obtener_conexion()
                        cursor = con.cursor()

                        cursor.execute("""
                            INSERT INTO Libro_Lab
                            (
                                Titulo,
                                Autor,
                                Categoria,
                                Precio,
                                Stock,
                                Fecha_Registro
                            )
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            titulo.strip(),
                            autor.strip(),
                            categoria,
                            float(precio),
                            int(stock),
                            obtener_fecha_hora()
                        ))

                        con.commit()
                        cursor.close()
                        con.close()

                        st.success("Libro registrado correctamente.")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error al registrar libro: {e}")

    # =====================================================
    # VER LIBROS
    # =====================================================

    with tab_listado:

        st.subheader("Libros registrados")

        try:
            libros = obtener_libros()

            if libros:

                datos = []

                for libro in libros:
                    datos.append({
                        "ID": libro[0],
                        "Título": libro[1],
                        "Autor": libro[2],
                        "Categoría": libro[3],
                        "Precio": f"${float(libro[4]):.2f}",
                        "Stock": libro[5],
                        "Fecha registro": libro[6]
                    })

                df = pd.DataFrame(datos)

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("Todavía no hay libros registrados.")

        except Exception as e:
            st.error(f"Error al cargar libros: {e}")

    # =====================================================
    # EDITAR LIBRO
    # =====================================================

    with tab_editar:

        st.subheader("Editar libro")

        try:
            libros = obtener_libros()

            if libros:

                opciones = {}

                for libro in libros:
                    texto = f"{libro[1]} | Stock: {libro[5]} | ID: {libro[0]}"
                    opciones[texto] = libro

                seleccion = st.selectbox(
                    "Seleccione el libro a editar",
                    list(opciones.keys())
                )

                libro_actual = opciones[seleccion]

                id_libro = libro_actual[0]

                categorias = [
                    "Novela",
                    "Cuento",
                    "Educativo",
                    "Infantil",
                    "Tecnología",
                    "Historia",
                    "Administración",
                    "Otro"
                ]

                categoria_actual = libro_actual[3] if libro_actual[3] in categorias else "Otro"

                with st.form("form_editar_libro"):

                    titulo_editado = st.text_input(
                        "Título",
                        value=libro_actual[1]
                    )

                    autor_editado = st.text_input(
                        "Autor",
                        value=libro_actual[2] if libro_actual[2] else ""
                    )

                    categoria_editada = st.selectbox(
                        "Categoría",
                        categorias,
                        index=categorias.index(categoria_actual)
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        precio_editado = st.number_input(
                            "Precio",
                            min_value=0.00,
                            step=0.50,
                            format="%.2f",
                            value=float(libro_actual[4])
                        )

                    with col2:
                        stock_editado = st.number_input(
                            "Stock",
                            min_value=0,
                            step=1,
                            value=int(libro_actual[5])
                        )

                    actualizar = st.form_submit_button("💾 Guardar cambios")

                    if actualizar:

                        if titulo_editado.strip() == "":
                            st.warning("El título no puede quedar vacío.")

                        elif precio_editado <= 0:
                            st.warning("El precio debe ser mayor a cero.")

                        else:
                            try:
                                con = obtener_conexion()
                                cursor = con.cursor()

                                cursor.execute("""
                                    UPDATE Libro_Lab
                                    SET
                                        Titulo = %s,
                                        Autor = %s,
                                        Categoria = %s,
                                        Precio = %s,
                                        Stock = %s
                                    WHERE Id_Libro = %s
                                """, (
                                    titulo_editado.strip(),
                                    autor_editado.strip(),
                                    categoria_editada,
                                    float(precio_editado),
                                    int(stock_editado),
                                    id_libro
                                ))

                                con.commit()
                                cursor.close()
                                con.close()

                                st.success("Libro actualizado correctamente.")
                                st.rerun()

                            except Exception as e:
                                st.error(f"Error al actualizar libro: {e}")

            else:
                st.info("No hay libros disponibles para editar.")

        except Exception as e:
            st.error(f"Error al cargar editor de libros: {e}")

    # =====================================================
    # ELIMINAR LIBRO
    # =====================================================

    with tab_eliminar:

        st.subheader("Eliminar libro")

        try:
            libros = obtener_libros()

            if libros:

                opciones = {}

                for libro in libros:
                    texto = f"{libro[1]} | Stock: {libro[5]} | ID: {libro[0]}"
                    opciones[texto] = libro

                seleccion = st.selectbox(
                    "Seleccione el libro a eliminar",
                    list(opciones.keys()),
                    key="select_eliminar_libro"
                )

                libro_actual = opciones[seleccion]

                st.warning(
                    f"Vas a eliminar el libro: {libro_actual[1]}"
                )

                confirmar = st.checkbox(
                    "Confirmo que deseo eliminar este libro"
                )

                if st.button("🗑️ Eliminar libro"):

                    if not confirmar:
                        st.warning("Debés confirmar la eliminación.")

                    else:
                        try:
                            con = obtener_conexion()
                            cursor = con.cursor()

                            cursor.execute("""
                                DELETE FROM Libro_Lab
                                WHERE Id_Libro = %s
                            """, (libro_actual[0],))

                            con.commit()
                            cursor.close()
                            con.close()

                            st.success("Libro eliminado correctamente.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error al eliminar libro: {e}")

            else:
                st.info("No hay libros disponibles para eliminar.")

        except Exception as e:
            st.error(f"Error al cargar eliminación de libros: {e}")
