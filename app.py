"""Aplicación de programación de producción para área de prensas con pisos."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.prensas import (
    PRENSAS, PRENSAS_BASE, obtener_pisos_compatibles, obtener_prensa_base,
    MAX_DIFERENCIA_TIEMPO, MAX_DIFERENCIA_PRESION
)
from src.scheduler import (
    generar_resumen_carga,
    generar_resumen_pisos,
    calcular_eficiencia_emparejamiento,
    validar_orden,
)
from src.services.scheduler_service import SchedulerService


def main():
    st.set_page_config(
        page_title="Programación de Prensas",
        page_icon="🏭",
        layout="wide"
    )

    st.title("🏭 Programación de Producción - Área de Prensas")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        estrategia = st.radio(
            "Estrategia de asignación:",
            options=["menor_costo", "balancear_carga"],
            format_func=lambda x: "Menor costo primero" if x == "menor_costo" else "Balancear carga",
            index=0
        )

        st.markdown("---")
        st.subheader("📋 Prensas disponibles")

        for pid, p in PRENSAS_BASE.items():
            st.write(f"**{pid}**: {p['dim_x']}x{p['dim_y']} mm | {p['costo_hora']} €/h | 2 pisos")

        st.markdown("---")
        st.subheader("📏 Restricciones")
        st.write(f"• Diferencia de tiempo máx: {int(MAX_DIFERENCIA_TIEMPO*100)}%")
        st.write(f"• Diferencia de presión máx: {MAX_DIFERENCIA_PRESION} PSI")

        st.markdown("---")
        st.download_button(
            label="📥 Descargar plantilla Excel",
            data=generar_plantilla(),
            file_name="plantilla_ordenes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Área principal
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📤 Cargar órdenes")
        archivo = st.file_uploader(
            "Selecciona un archivo Excel",
            type=["xlsx", "xls"],
            help="Columnas requeridas: id, dim_x, dim_y, cantidad, tiempo_unitario"
        )

    with col2:
        st.subheader("📊 Formato esperado")
        st.code("""
| Columna         | Descripción                    |
|-----------------|--------------------------------|
| id              | Identificador único de orden   |
| dim_x           | Dimensión X en mm              |
| dim_y           | Dimensión Y en mm              |
| cantidad        | Cantidad a producir            |
| tiempo_unitario | Horas por unidad               |
| presion_psi     | Presión (opcional)             |
| prioridad       | Prioridad (opcional)           |
| prensas_permit  | Prensas específicas (opcional)|
        """, language=None)

    if archivo is not None:
        try:
            df_ordenes = pd.read_excel(archivo)

            required_cols = ["id", "dim_x", "dim_y", "cantidad", "tiempo_unitario"]
            missing = [c for c in required_cols if c not in df_ordenes.columns]

            if missing:
                st.error(f"Columnas faltantes: {', '.join(missing)}")
                return

            # Validación
            errores_validacion = []
            for idx, row in df_ordenes.iterrows():
                es_valido, errores = validar_orden(row)
                if not es_valido:
                    errores_validacion.append(f"Fila {idx + 2}: {', '.join(errores)}")

            if errores_validacion:
                st.warning(f"⚠️ {len(errores_validacion)} errores de validación:")
                with st.expander("Ver errores"):
                    for err in errores_validacion[:10]:
                        st.write(f"- {err}")
                    if len(errores_validacion) > 10:
                        st.write(f"... y {len(errores_validacion) - 10} más")

                if not st.checkbox("Continuar a pesar de los errores", value=False):
                    return

            st.markdown("---")
            st.subheader("📋 Órdenes cargadas")

            # Mostrar compatibilidad
            df_ordenes["prensas_compatibles"] = df_ordenes.apply(
                lambda r: ", ".join([obtener_prensa_base(p[0]) for p in obtener_pisos_compatibles(
                    r["dim_x"], r["dim_y"], r.get("id")
                )]) if obtener_pisos_compatibles(r["dim_x"], r["dim_y"], r.get("id")) else "Ninguna",
                axis=1
            )

            st.dataframe(
                df_ordenes.style.apply(
                    lambda x: ['background-color: #ffe6e6' if 'Ninguna' in str(v) else ''
                              for v in x],
                    subset=["prensas_compatibles"]
                ),
                use_container_width=True,
                hide_index=True
            )

            if st.button("🔄 Programar Órdenes", type="primary"):
                with st.spinner("Programando con algoritmo de pisos emparejados..."):
                    df_asignaciones = SchedulerService().generate_schedule(df_ordenes, estrategia)

                st.session_state["asignaciones"] = df_asignaciones
                st.session_state["ordenes"] = df_ordenes

            if "asignaciones" in st.session_state:
                mostrar_resultados(
                    st.session_state["asignaciones"],
                    st.session_state.get("ordenes", df_ordenes)
                )

        except Exception as e:
            st.error(f"Error al procesar archivo: {str(e)}")
            import traceback
            st.code(traceback.format_exc())


def mostrar_resultados(df_asign: pd.DataFrame, df_ordenes: pd.DataFrame):
    """Muestra los resultados de la programación."""
    st.markdown("---")
    st.header("📊 Resultados de la Programación")

    # Métricas de eficiencia
    eficiencia = calcular_eficiencia_emparejamiento(df_asign)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Emparejamiento", f"{eficiencia['eficiencia']}%")
    with col2:
        st.metric("Órdenes Emparejadas", eficiencia['ordenes_emparejadas'])
    with col3:
        st.metric("Tiempo Ahorrado", f"{eficiencia['tiempo_ahorrado_horas']} h")
    with col4:
        st.metric("Costo Ahorrado", f"{eficiencia['costo_ahorrado']} €")

    tabs = st.tabs([
        "📝 Asignaciones", "🏢 Por Piso", "📈 Carga por Prensa",
        "📊 Utilización", "📅 Diagrama Gantt"
    ])

    df_validas = df_asign[df_asign["prensa_id"].notna()]
    ordenes_sin_prensa = df_asign[df_asign["prensa_id"].isna()]

    if not ordenes_sin_prensa.empty:
        st.warning(f"⚠️ {len(ordenes_sin_prensa)} orden(es) sin prensa compatible")
        with st.expander("Ver órdenes no programadas"):
            st.dataframe(ordenes_sin_prensa[["orden_id", "error"]], hide_index=True)

    with tabs[0]:  # Asignaciones
        st.subheader("Asignaciones realizadas")

        if not df_validas.empty:
            display_df = df_validas[[
                "orden_id", "prensa_id", "piso_id", "inicio", "fin",
                "tiempo_horas", "emparejado_con", "costo_total"
            ]].copy()

            # Formatear columnas
            display_df["inicio"] = display_df["inicio"].apply(
                lambda x: x.strftime("%m/%d %H:%M") if pd.notna(x) else ""
            )
            display_df["fin"] = display_df["fin"].apply(
                lambda x: x.strftime("%m/%d %H:%M") if pd.notna(x) else ""
            )
            display_df["emparejado_con"] = display_df["emparejado_con"].fillna("-")

            display_df = display_df.rename(columns={
                "orden_id": "Orden",
                "prensa_id": "Prensa",
                "piso_id": "Piso",
                "inicio": "Inicio",
                "fin": "Fin",
                "tiempo_horas": "Horas",
                "emparejado_con": "Emparejada con",
                "costo_total": "Costo (€)"
            })

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Métricas generales
            costo_total = df_validas["costo_total"].sum()
            tiempo_total_prensa = df_validas["tiempo_prensa"].sum() if "tiempo_prensa" in df_validas.columns else df_validas["tiempo_horas"].sum()
            tiempo_total_ordenes = df_validas["tiempo_horas"].sum()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Costo Total", f"{costo_total:,.2f} €")
            with col2:
                st.metric("Tiempo Prensa", f"{tiempo_total_prensa:,.1f} h")
            with col3:
                st.metric("Tiempo Órdenes", f"{tiempo_total_ordenes:,.1f} h")
            with col4:
                st.metric("Órdenes Programadas", len(df_validas))

            # Descarga CSV
            csv = df_validas.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar programación (CSV)",
                data=csv,
                file_name=f"programacion_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )

    with tabs[1]:  # Por Piso
        st.subheader("Detalle por Piso")

        df_pisos = generar_resumen_pisos(df_asign)

        if df_pisos.empty:
            st.info("No hay asignaciones para mostrar")
        else:
            # Heatmap de utilización por piso
            pivot = df_pisos.pivot_table(
                index="prensa",
                columns="piso",
                values="horas_trabajo",
                aggfunc="sum"
            )

            fig_heatmap = px.imshow(
                pivot.values,
                labels=dict(x="Piso", y="Prensa", color="Horas"),
                x=pivot.columns,
                y=pivot.index,
                color_continuous_scale="Blues",
                title="Horas de trabajo por Piso"
            )
            fig_heatmap.update_layout(height=400)
            st.plotly_chart(fig_heatmap, use_container_width=True)

            # Tabla detallada
            st.dataframe(df_pisos, hide_index=True, use_container_width=True)

            # Estadísticas de emparejamiento
            total_emparejadas = df_pisos["emparejadas"].sum()
            total_solas = df_pisos["solas"].sum()
            total_ordenes = total_emparejadas + total_solas

            pct_emparejadas = (total_emparejadas / total_ordenes * 100) if total_ordenes > 0 else 0

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Órdenes Emparejadas", f"{total_emparejadas} ({pct_emparejadas:.0f}%)")
            with col2:
                st.metric("Órdenes Solas", f"{total_solas}")
            with col3:
                st.metric("Total Órdenes", total_ordenes)

    with tabs[2]:  # Carga por Prensa
        st.subheader("Carga por Prensa")

        df_resumen = generar_resumen_carga(df_asign)

        if df_resumen.empty:
            st.info("No hay asignaciones para mostrar")
        else:
            fig_carga = px.bar(
                df_resumen,
                x="prensa",
                y="horas_prensa",
                color="prensa",
                title="Horas de prensado por prensa",
                labels={"prensa": "Prensa", "horas_prensa": "Horas totales"},
                text="horas_prensa",
                hover_data=["ordenes", "ciclos", "pisos_utilizados"]
            )
            fig_carga.update_traces(texttemplate='%{text:.1f}h', textposition='outside')
            fig_carga.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_carga, use_container_width=True)

            st.dataframe(df_resumen, hide_index=True, use_container_width=True)

    with tabs[3]:  # Utilización
        st.subheader("Utilización por Prensa")

        if not df_resumen.empty:
            dias_planificacion = 3
            horas_disponibles = dias_planificacion * 24

            colores = {
                "P1": "#1f77b4", "P2": "#ff7f0e", "P5": "#2ca02c",
                "P6": "#d62728", "P7": "#9467bd"
            }

            fig_util = go.Figure()

            for _, row in df_resumen.iterrows():
                fig_util.add_trace(go.Bar(
                    name=row["prensa"],
                    x=[row["prensa"]],
                    y=[row["horas_prensa"]],
                    marker_color=colores.get(row["prensa"], "#333333"),
                    text=f"{row['utilizacion']:.1f}%",
                    textposition="outside"
                ))

            fig_util.update_layout(
                title="Utilización de prensas",
                yaxis_title="Horas programadas",
                showlegend=False,
                height=400
            )

            fig_util.add_hline(
                y=horas_disponibles,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Capacidad ({horas_disponibles}h)",
                annotation_position="right"
            )

            st.plotly_chart(fig_util, use_container_width=True)

            # Métricas por prensa
            cols = st.columns(5)
            for idx, (_, row) in enumerate(df_resumen.iterrows()):
                if idx < len(cols):
                    with cols[idx]:
                        st.metric(
                            row["prensa"],
                            f"{row['utilizacion']:.1f}%",
                            f"{row['horas_prensa']:.1f}h"
                        )

    with tabs[4]:  # Gantt
        st.subheader("Diagrama de Gantt")

        df_gantt = df_validas.copy()

        if df_gantt.empty:
            st.info("No hay datos para el diagrama Gantt")
        else:
            # Agrupar por prensa + instante de inicio: las órdenes emparejadas comparten
            # prensa_id e inicio exacto, por lo que reciben el mismo color.
            # Órdenes solas tienen un instante único → color propio.
            df_gantt["color_grupo"] = df_gantt.apply(
                lambda r: f"{r['prensa_id']}-{r['inicio'].strftime('%Y%m%d%H%M%S')}",
                axis=1
            )

            # Pasar text= como nombre de columna para que Plotly asigne una
            # etiqueta por fila en lugar de aplicar el array a todas las trazas.
            fig_gantt = px.timeline(
                df_gantt,
                x_start="inicio",
                x_end="fin",
                y="piso_id",
                color="color_grupo",
                text="orden_id",
                hover_data=["orden_id", "prensa_id", "tiempo_horas", "emparejado_con"],
                title="Cronograma de producción por piso"
            )

            fig_gantt.update_traces(textposition="inside")
            fig_gantt.update_yaxes(autorange="reversed")
            fig_gantt.update_layout(
                height=500,
                xaxis_title="Tiempo",
                yaxis_title="Piso",
                showlegend=False
            )

            st.plotly_chart(fig_gantt, use_container_width=True)

            st.info("**Leyenda:** Los bloques del mismo color en los dos pisos de una misma prensa indican órdenes emparejadas que se ejecutan simultáneamente.")


def generar_plantilla() -> bytes:
    """Genera un archivo Excel con la plantilla de órdenes."""
    df_plantilla = pd.DataFrame({
        "id": ["ORD-001", "ORD-002", "ORD-003", "ORD-004", "ORD-005", "ORD-006", "ORD-007", "ORD-008"],
        "dim_x": [1000, 1100, 1200, 1400, 1500, 1000, 1700, 1900],
        "dim_y": [500, 550, 580, 550, 550, 500, 700, 1900],
        "cantidad": [100, 50, 200, 75, 30, 150, 60, 20],
        "tiempo_unitario": [1.0, 1.5, 0.8, 1.2, 2.0, 1.0, 1.8, 2.5],
        "presion_psi": [100, 110, 100, 120, 110, 100, 130, 140],
        "prioridad": [1, 2, 3, 1, 2, 3, 1, 2]
    })

    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_plantilla.to_excel(writer, index=False, sheet_name='Ordenes')

        # Añadir hoja de instrucciones
        instrucciones = pd.DataFrame({
            "Campo": ["id", "dim_x", "dim_y", "cantidad", "tiempo_unitario", "presion_psi", "prioridad"],
            "Descripción": [
                "Identificador único de la orden",
                "Dimensión X en milímetros",
                "Dimensión Y en milímetros",
                "Cantidad de piezas a producir",
                "Horas de prensado por unidad",
                "Presión en PSI (opcional)",
                "Prioridad: 1=alta, 5=baja (opcional)"
            ]
        })
        instrucciones.to_excel(writer, index=False, sheet_name='Instrucciones')

    output.seek(0)
    return output.getvalue()


if __name__ == "__main__":
    main()
