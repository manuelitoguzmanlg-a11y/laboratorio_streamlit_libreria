from modulos.config.conexion import obtener_conexion, obtener_fecha_hora
import streamlit as st
import pandas as pd


# =========================================================
# BASE DE DATOS
# =========================================================

def asegurar_tabla_ventas():
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Venta_Lab (
            Id_Venta INT AUTO_INCREMENT PRIMARY KEY,
            Id_Cliente INT,
            Id_Libro INT NOT NULL,
            Cantidad INT NOT NULL,
            Precio_Unitario DECIMAL(10,2) NOT NULL,
            Total DECIMAL(10,2) NOT NULL,
            Metodo_Pago VARCHAR(50),
            Fecha_Venta DATETIME
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
            Telefono
        FROM Cliente_Lab
        ORDER BY Nombre ASC
    """)

    clientes = cursor.fetchall()

    cursor.close()
    con.close()

    return clientes


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
            Stock
        FROM Libro_Lab
        ORDER BY Titulo ASC
    """)

    libros = cursor.fetchall()

    cursor.close()
    con.close()

    return libros


def obtener_ventas():
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("""
        SELECT
            v.Id_Venta,
            COALESCE(c.Nombre, 'Cliente no especificado') AS Cliente,
            l.Titulo,
            l.Autor,
            v.Cantidad,
            v.Precio_Unitario,
            v.Total,
            v.Metodo_Pago,
            v.Fecha_Venta,
            v.Id_Libro
        FROM Venta_Lab v
        LEFT JOIN Cliente_Lab c
            ON v.Id_Cliente = c.Id_Cliente
        INNER JOIN Libro_Lab l
            ON v.Id_Libro = l.Id_Libro
        ORDER BY v.Id_Venta DESC
    """)

    ventas = cursor.fetchall()

    cursor.close()
    con.close()

    return ventas


# =========================================================
# ESTILO
# =========================================================

def aplicar_estilo_ventas():
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

def mostrar_ventas():

    aplicar_estilo_ventas()

    st.markdown("""
        <div class="module-card">
            <div class="module-title">💰 Gestión de Ventas</div>
            <div class="module-subtitle">
                Registro de ventas de libros, control de stock y consulta de historial.
            </div>
            <div class="gold-line"></div>
        </div>
    """, unsafe_allow_html=True)

    try:
        asegurar_tabla_ventas()
    except Exception as e:
        st.error(f"Error al preparar la tabla de ventas: {e}")
        return

    tab_registrar, tab_listado, tab_eliminar = st.tabs(
        [
            "➕ Registrar venta",
            "📋 Ver ventas",
            "🗑️ Eliminar venta"
        ]
    )

    # =====================================================
    # REGISTRAR VENTA
    # =====================================================

    with tab_registrar:

        st.subheader("Registrar nueva venta")

        try:
            clientes = obtener_clientes()
            libros = obtener_libros()

            if not libros:
                st.warning("Primero debés registrar libros antes de hacer ventas.")
                return

            libros_disponibles = [
                libro for libro in libros if int(libro[5]) > 0
            ]

            if not libros_disponibles:
                st.warning("No hay libros con stock disponible para vender.")
                return

            opciones_clientes = {
                "Cliente no especificado": None
            }

            for cliente in clientes:
                texto_cliente = f"{cliente[1]} | Tel: {cliente[2]} | ID: {cliente[0]}"
                opciones_clientes[texto_cliente] = cliente[0]

            opciones_libros = {}

            for libro in libros_disponibles:
                texto_libro = (
                    f"{libro[1]} | Autor: {libro[2]} | "
                    f"Precio: ${float(libro[4]):.2f} | Stock: {libro[5]}"
                )

                opciones_libros[texto_libro] = libro

            with st.form("form_registrar_venta"):

                cliente_seleccionado = st.selectbox(
                    "Cliente",
                    list(opciones_clientes.keys())
                )

                libro_seleccionado = st.selectbox(
                    "Libro",
                    list(opciones_libros.keys())
                )

                libro_actual = opciones_libros[libro_seleccionado]

                id_libro = libro_actual[0]
                titulo_libro = libro_actual[1]
                precio = float(libro_actual[4])
                stock_actual = int(libro_actual[5])

                col1, col2, col3 = st.columns(3)

                with col1:
                    cantidad = st.number_input(
                        "Cantidad",
                        min_value=1,
                        max_value=stock_actual,
                        step=1
                    )

                with col2:
                    st.metric(
                        "Precio unitario",
                        f"${precio:.2f}"
                    )

                with col3:
                    total = float(cantidad) * precio

                    st.metric(
                        "Total",
                        f"${total:.2f}"
                    )

                metodo_pago = st.selectbox(
                    "Método de pago",
                    [
                        "Efectivo",
                        "Tarjeta",
                        "Transferencia"
                    ]
                )

                guardar = st.form_submit_button("💾 Registrar venta")

                if guardar:

                    if cantidad <= 0:
                        st.warning("La cantidad debe ser mayor a cero.")

                    elif cantidad > stock_actual:
                        st.warning("No hay suficiente stock disponible.")

                    else:
                        try:
                            con = obtener_conexion()
                            cursor = con.cursor()

                            id_cliente = opciones_clientes[cliente_seleccionado]

                            cursor.execute("""
                                INSERT INTO Venta_Lab
                                (
                                    Id_Cliente,
                                    Id_Libro,
                                    Cantidad,
                                    Precio_Unitario,
                                    Total,
                                    Metodo_Pago,
                                    Fecha_Venta
                                )
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (
                                id_cliente,
                                id_libro,
                                int(cantidad),
                                precio,
                                total,
                                metodo_pago,
                                obtener_fecha_hora()
                            ))

                            cursor.execute("""
                                UPDATE Libro_Lab
                                SET Stock = Stock - %s
                                WHERE Id_Libro = %s
                            """, (
                                int(cantidad),
                                id_libro
                            ))

                            con.commit()
                            cursor.close()
                            con.close()

                            st.success(
                                f"Venta registrada correctamente. Libro vendido: {titulo_libro}"
                            )
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error al registrar venta: {e}")

        except Exception as e:
            st.error(f"Error al cargar datos para venta: {e}")

    # =====================================================
    # VER VENTAS
    # =====================================================

    with tab_listado:

        st.subheader("Historial de ventas")

        try:
            ventas = obtener_ventas()

            if ventas:

                datos = []

                total_ingresos = 0
                total_unidades = 0

                for venta in ventas:
                    total_ingresos += float(venta[6])
                    total_unidades += int(venta[4])

                    datos.append({
                        "ID": venta[0],
                        "Cliente": venta[1],
                        "Libro": venta[2],
                        "Autor": venta[3],
                        "Cantidad": venta[4],
                        "Precio unitario": f"${float(venta[5]):.2f}",
                        "Total": f"${float(venta[6]):.2f}",
                        "Método de pago": venta[7],
                        "Fecha": venta[8]
                    })

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Ventas registradas", len(ventas))

                with col2:
                    st.metric("Unidades vendidas", total_unidades)

                with col3:
                    st.metric("Ingresos totales", f"${total_ingresos:.2f}")

                df = pd.DataFrame(datos)

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("Todavía no hay ventas registradas.")

        except Exception as e:
            st.error(f"Error al cargar ventas: {e}")

    # =====================================================
    # ELIMINAR VENTA
    # =====================================================

    with tab_eliminar:

        st.subheader("Eliminar venta")

        st.info(
            "Al eliminar una venta, el sistema devuelve automáticamente la cantidad vendida al stock del libro."
        )

        try:
            ventas = obtener_ventas()

            if ventas:

                opciones = {}

                for venta in ventas:
                    texto = (
                        f"Venta #{venta[0]} | Libro: {venta[2]} | "
                        f"Cantidad: {venta[4]} | Total: ${float(venta[6]):.2f}"
                    )

                    opciones[texto] = venta

                seleccion = st.selectbox(
                    "Seleccione la venta a eliminar",
                    list(opciones.keys())
                )

                venta_actual = opciones[seleccion]

                id_venta = venta_actual[0]
                cantidad = int(venta_actual[4])
                id_libro = venta_actual[9]

                st.warning(
                    f"Vas a eliminar la venta #{id_venta}. Se devolverán {cantidad} unidades al stock."
                )

                confirmar = st.checkbox(
                    "Confirmo que deseo eliminar esta venta"
                )

                if st.button("🗑️ Eliminar venta"):

                    if not confirmar:
                        st.warning("Debés confirmar la eliminación.")

                    else:
                        try:
                            con = obtener_conexion()
                            cursor = con.cursor()

                            cursor.execute("""
                                DELETE FROM Venta_Lab
                                WHERE Id_Venta = %s
                            """, (id_venta,))

                            cursor.execute("""
                                UPDATE Libro_Lab
                                SET Stock = Stock + %s
                                WHERE Id_Libro = %s
                            """, (
                                cantidad,
                                id_libro
                            ))

                            con.commit()
                            cursor.close()
                            con.close()

                            st.success("Venta eliminada correctamente y stock restaurado.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Error al eliminar venta: {e}")

            else:
                st.info("No hay ventas disponibles para eliminar.")

        except Exception as e:
            st.error(f"Error al cargar eliminación de ventas: {e}")
