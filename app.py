import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# =============================================================================
# ⚠️ CONFIGURACIÓN DE NUBE: PEGA EL LINK DE TU GOOGLE SHEET AQUÍ ⚠️
# =============================================================================
URL_GOOGLE_SHEET = "PEGA_EL_LINK_AQUI"

st.set_page_config(
    page_title="Forecast financiero | Valgardena",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MESES_HIST = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul"]
MESES_PROY = ["Ago", "Sep", "Oct", "Nov", "Dic"]
MESES = MESES_HIST + MESES_PROY
COLUMNAS_TEXTO = ["Categoría", "Área", "Grupo", "Cuenta / Ítem", "Detalle / Tipo"]
TASA_IDPC = 0.27
PORCENTAJE_REBAJA_14E = 0.50
GASTOS_RECHAZADOS = 7_595_894

st.markdown(
    """
    <style>
      :root {
        --navy:#0d2b4f; --ink:#102944; --muted:#687b91; --line:#d7e1eb;
        --wash:#f1f4f7; --blue:#286bc5; --red:#d65b55; --green:#0d917b;
      }
      html, body, button, input, textarea, select { font-family:"Segoe UI",Arial,sans-serif; }
      .stApp { background:var(--wash); }
      [data-testid="stHeader"] { height:0; background:transparent; }
      #MainMenu, footer, [data-testid="stDeployButton"] { visibility:hidden; }
      .block-container { max-width:1680px; padding:1.75rem 2.8rem 3.5rem; }
      .top-strip { position:fixed; z-index:999; inset:0 0 auto; height:10px; background:#0b2747; }

      .hero { display:flex; align-items:flex-end; justify-content:space-between; gap:2rem; margin:.55rem 0 1.15rem; }
      .eyebrow,.section-label { margin:0 0 .38rem; color:#587796; font-size:.68rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
      .hero h1 { margin:0; color:#0b2848; font-family:Georgia,"Times New Roman",serif; font-size:clamp(2.55rem,4vw,4rem); font-weight:500; letter-spacing:-.045em; line-height:.98; }
      .hero p:last-child { margin:.75rem 0 0; color:var(--muted); font-size:1rem; }
      .phase-track { display:grid; grid-template-columns:7fr 5fr; width:min(440px,36vw); overflow:hidden; border:1px solid #ccdae8; border-radius:10px; background:white; color:#49617c; font-size:.72rem; font-weight:700; text-align:center; }
      .phase-track span { padding:.65rem .8rem; }
      .phase-track span:last-child { background:#dbeafd; color:#17548f; }

      .metric-grid { display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:.72rem; margin-bottom:.9rem; }
      .metric-card { min-width:0; min-height:118px; padding:.9rem 1rem .85rem; border:1px solid var(--line); border-top:3px solid var(--accent); border-radius:13px; background:white; box-shadow:0 5px 14px rgba(22,49,78,.045); }
      .metric-label { display:flex; min-height:34px; align-items:flex-start; justify-content:space-between; gap:.5rem; color:#596d83; font-size:.67rem; font-weight:850; letter-spacing:.03em; line-height:1.3; text-transform:uppercase; }
      .metric-icon { display:grid; width:28px; height:28px; flex:0 0 auto; place-items:center; border-radius:8px; background:color-mix(in srgb,var(--accent) 11%,white); color:var(--accent); font-size:.95rem; }
      .metric-value { overflow:hidden; margin-top:.25rem; color:var(--ink); font-size:clamp(1.05rem,1.35vw,1.46rem); font-weight:800; letter-spacing:-.035em; text-overflow:ellipsis; white-space:nowrap; }
      .metric-hint { margin-top:.38rem; color:#7a899b; font-size:.67rem; }

      [data-testid="stVerticalBlockBorderWrapper"] { overflow:hidden; border-color:var(--line)!important; border-radius:15px!important; background:white; box-shadow:0 6px 18px rgba(22,49,78,.045); }
      [data-testid="stVerticalBlockBorderWrapper"]>div { padding:.1rem .45rem; }
      .section-title { margin:0; color:#0d2b4f; font-family:Georgia,"Times New Roman",serif; font-size:1.3rem; font-weight:500; letter-spacing:-.018em; }

      .tax-bridge { position:relative; min-height:476px; overflow:hidden; padding:1.25rem 1.3rem; border:1px solid #264a73; border-radius:15px; background:#102f55; color:white; box-shadow:0 6px 18px rgba(22,49,78,.08); }
      .tax-bridge::after { position:absolute; right:-65px; bottom:-80px; width:180px; height:180px; border:1px solid rgba(255,255,255,.08); border-radius:50%; content:""; }
      .tax-bridge .section-label { color:#70b8fb; }
      .tax-bridge .section-title { color:white; font-size:1.45rem; }
      .tax-icon { position:absolute; top:1.15rem; right:1.15rem; display:grid; width:35px; height:35px; place-items:center; border:1px solid rgba(255,255,255,.16); border-radius:10px; color:#a9cff5; }
      .tax-list { margin:1.35rem 0 0; }
      .tax-row { display:flex; justify-content:space-between; gap:1rem; padding:.8rem 0; border-bottom:1px solid rgba(255,255,255,.12); }
      .tax-row span { max-width:58%; color:#c1d2e4; font-size:.71rem; line-height:1.35; }
      .tax-row strong { font-family:Consolas,monospace; font-size:.74rem; text-align:right; }
      .tax-row .positive { color:#59d9b6; }
      .tax-total { border-bottom:0; }
      .tax-total span { color:white; font-weight:800; }
      .tax-total strong { color:#ffd27c; font-size:.9rem; }
      .tax-note { position:relative; z-index:1; margin:.8rem 0 0; padding-top:.8rem; border-top:1px solid rgba(255,255,255,.12); color:#9eb4ca; font-size:.61rem; line-height:1.5; }

      .editor-copy { margin:.35rem 0 0; color:#718298; font-size:.75rem; }
      [data-testid="stDataEditor"] { overflow:hidden; border:1px solid #dce5ee; border-radius:11px; }
      .stButton>button,.stDownloadButton>button { min-height:38px; border-color:#d1dce8; border-radius:9px; color:#17385d; font-size:.78rem; font-weight:650; }
      .stButton>button:hover,.stDownloadButton>button:hover { border-color:#6c91b9; background:#edf5ff; color:#123d6a; }

      @media(max-width:1220px){ .metric-grid{grid-template-columns:repeat(3,minmax(0,1fr));} }
      @media(max-width:760px){ .block-container{padding:1.25rem .9rem 3rem;} .hero{align-items:flex-start;flex-direction:column;} .phase-track{width:100%;} .metric-grid{grid-template-columns:repeat(2,minmax(0,1fr));} }
    </style>
    <div class="top-strip"></div>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(ttl=60)
def cargar_datos() -> pd.DataFrame | None:
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(spreadsheet=URL_GOOGLE_SHEET)
        return df
    except Exception as e:
        st.error(f"Error conectando a Google Sheets: {e}")
        return None

def es_ingreso(categoria: object) -> bool:
    texto = str(categoria).upper()
    return any(palabra in texto for palabra in ("INGRESO", "VENTA", "GANANCIA"))

def moneda(valor: float) -> str:
    signo = "−" if valor < 0 else ""
    return f"{signo}${abs(valor):,.0f}".replace(",", ".")

def porcentaje(valor: float) -> str:
    return f"{valor:.1f}%".replace(".", ",")

def tarjeta(etiqueta: str, valor: str, ayuda: str, color: str, icono: str) -> str:
    return (
        f'<article class="metric-card" style="--accent:{color}">'
        f'<div class="metric-label"><span>{etiqueta}</span>'
        f'<i class="metric-icon">{icono}</i></div>'
        f'<div class="metric-value">{valor}</div>'
        f'<div class="metric-hint">{ayuda}</div>'
        '</article>'
    )

def estado_forecast(row: pd.Series) -> str:
    variacion = float(row["Variación firmada"])
    if abs(variacion) < 0.5:
        return "● Sin cambio"
    if es_ingreso(row["Categoría"]):
        return f"▲ Ingreso {moneda(abs(variacion))}" if variacion > 0 else f"▼ Ingreso {moneda(abs(variacion))}"
    return f"▼ Mayor gasto {moneda(abs(variacion))}" if variacion < 0 else f"▲ Ahorro {moneda(abs(variacion))}"

def color_estado(valor: object) -> str:
    texto = str(valor)
    if "Ahorro" in texto or texto.startswith("▲ Ingreso"):
        return "color:#087965;background-color:#e5f7f1;font-weight:700"
    if "Mayor gasto" in texto or texto.startswith("▼ Ingreso"):
        return "color:#ad4540;background-color:#fff0ef;font-weight:700"
    return "color:#6b7c90"

# -----------------------------------------------------------------------------
# Base de datos de trabajo
# -----------------------------------------------------------------------------
df_base = cargar_datos()
if df_base is None:
    st.error("No encontré la base de datos en el enlace de Google Sheets proporcionado.")
    st.stop()

faltantes = [columna for columna in COLUMNAS_TEXTO if columna not in df_base.columns]
if faltantes:
    st.error("Faltan columnas requeridas en el Sheet: " + ", ".join(faltantes))
    st.stop()

df_base = df_base[df_base["Categoría"] != "RESULTADO DEL EJERCICIO"].copy()
df_base[COLUMNAS_TEXTO] = df_base[COLUMNAS_TEXTO].fillna("Sin clasificar")
for mes in MESES:
    if mes not in df_base.columns:
        df_base[mes] = 0.0
    df_base[mes] = pd.to_numeric(df_base[mes], errors="coerce").fillna(0.0)
if "Total_Original_Base" not in df_base.columns:
    df_base["Total_Original_Base"] = df_base[MESES].sum(axis=1)

if "forecast_data" not in st.session_state:
    st.session_state.forecast_data = df_base.copy()
if "editor_version" not in st.session_state:
    st.session_state.editor_version = 0
df_global = st.session_state.forecast_data.copy()

# -----------------------------------------------------------------------------
# Filtros laterales en cascada
# -----------------------------------------------------------------------------
st.sidebar.markdown("## Valgardena")
st.sidebar.caption("Filtros del panel financiero")
df_filtrado = df_global.copy()
for columna, clave in [
    ("Categoría", "f_categoria"), ("Área", "f_area"), ("Grupo", "f_grupo"),
    ("Cuenta / Ítem", "f_cuenta"), ("Detalle / Tipo", "f_detalle"),
]:
    opciones = sorted(df_filtrado[columna].astype(str).unique().tolist())
    seleccion = st.sidebar.multiselect(columna, opciones, key=clave)
    if seleccion:
        df_filtrado = df_filtrado[df_filtrado[columna].astype(str).isin(seleccion)]

if st.sidebar.button("Restablecer filtros", use_container_width=True):
    for clave in ("f_categoria", "f_area", "f_grupo", "f_cuenta", "f_detalle"):
        st.session_state.pop(clave, None)
    st.rerun()

# -----------------------------------------------------------------------------
# Motor financiero y tributario
# -----------------------------------------------------------------------------
mascara_ingresos = df_filtrado["Categoría"].map(es_ingreso)
ingresos_mes = [float(df_filtrado.loc[mascara_ingresos, mes].sum()) for mes in MESES]
gastos_firmados_mes = [float(df_filtrado.loc[~mascara_ingresos, mes].sum()) for mes in MESES]
gastos_mes = [abs(valor) for valor in gastos_firmados_mes]
resultado_mes = [ingreso + gasto for ingreso, gasto in zip(ingresos_mes, gastos_firmados_mes)]

total_ingresos = sum(ingresos_mes)
total_gastos_firmados = sum(gastos_firmados_mes)
total_gastos = abs(total_gastos_firmados)
resultado_antes_impuestos = total_ingresos + total_gastos_firmados
margen = (resultado_antes_impuestos / total_ingresos * 100) if total_ingresos else 0.0
ratio_gastos = (total_gastos / total_ingresos * 100) if total_ingresos else 0.0

if resultado_antes_impuestos > 0:
    base_beneficio = max(0.0, resultado_antes_impuestos - GASTOS_RECHAZADOS)
    rebaja_14e = base_beneficio * PORCENTAJE_REBAJA_14E
    base_afecta = max(0.0, resultado_antes_impuestos - rebaja_14e)
    impuesto = base_afecta * TASA_IDPC
else:
    rebaja_14e = base_afecta = impuesto = 0.0
resultado_liquido = resultado_antes_impuestos - impuesto
tasa_efectiva = (impuesto / resultado_antes_impuestos * 100) if resultado_antes_impuestos > 0 else 0.0

# -----------------------------------------------------------------------------
# Cabecera y tarjetas ejecutivas
# -----------------------------------------------------------------------------
st.markdown(
    """
    <section class="hero">
      <div>
        <p class="eyebrow">Cierre anual · 2026</p>
        <h1>Forecast financiero</h1>
        <p>Resultado, margen e impacto tributario en una sola vista ejecutiva.</p>
      </div>
      <div class="phase-track"><span>7 meses históricos</span><span>5 meses forecast</span></div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<section class="metric-grid">'
    + tarjeta("Ingresos proyectados", moneda(total_ingresos), "Acumulado anual", "#286bc5", "↗")
    + tarjeta("Gastos proyectados", moneda(total_gastos), porcentaje(ratio_gastos) + " de los ingresos", "#d65b55", "▣")
    + tarjeta("Resultado antes de impuesto", moneda(resultado_antes_impuestos), "Resultado económico", "#7c5bb4", "◉")
    + tarjeta("Margen operacional", porcentaje(margen), "Resultado / ingresos", "#0d917b", "↗")
    + tarjeta("Impuesto estimado", moneda(impuesto), porcentaje(tasa_efectiva) + " tasa efectiva", "#d18419", "♜")
    + tarjeta("Resultado líquido", moneda(resultado_liquido), "Proyección al 31 de diciembre", "#173e6e", "✣")
    + "</section>",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Evolución mensual y puente tributario
# -----------------------------------------------------------------------------
grafico_col, impuesto_col = st.columns([3.45, 1], gap="small")

with grafico_col:
    with st.container(border=True):
        st.markdown(
            '<p class="section-label">Evolución mensual</p>'
            '<h2 class="section-title">Ingresos, gastos y resultado acumulado</h2>',
            unsafe_allow_html=True,
        )
        acumulado = pd.Series(resultado_mes).cumsum().tolist()
        fase = ["Histórico" if mes in MESES_HIST else "Forecast" for mes in MESES]

        figura = go.Figure()
        figura.add_trace(
            go.Bar(
                x=MESES,
                y=ingresos_mes,
                name="Ingresos",
                marker_color=["#286bc5" if etapa == "Histórico" else "#a8c8ed" for etapa in fase],
                hovertemplate="%{x}<br>Ingresos: $%{y:,.0f}<extra></extra>",
            )
        )
        figura.add_trace(
            go.Bar(
                x=MESES,
                y=gastos_mes,
                name="Gastos",
                marker_color=["#d65b55" if etapa == "Histórico" else "#efaaa6" for etapa in fase],
                hovertemplate="%{x}<br>Gastos: $%{y:,.0f}<extra></extra>",
            )
        )
        figura.add_trace(
            go.Scatter(
                x=MESES,
                y=acumulado,
                name="Resultado",
                mode="lines+markers",
                line=dict(color="#0d917b", width=3),
                marker=dict(size=7, color="#0d917b"),
                hovertemplate="%{x}<br>Resultado acumulado: $%{y:,.0f}<extra></extra>",
            )
        )
        figura.add_vrect(
            x0=6.5, x1=11.5, fillcolor="#e7f1ff", opacity=0.72,
            layer="below", line_width=0,
        )
        figura.add_vline(x=6.5, line_color="#aac2df", line_dash="dot", line_width=1)
        figura.update_layout(
            barmode="group",
            hovermode="x unified",
            height=392,
            margin=dict(l=12, r=8, t=34, b=4),
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="#51657c", size=11),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.04,
                xanchor="right", x=1, font=dict(size=10),
            ),
            xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10)),
            yaxis=dict(
                showgrid=True, gridcolor="#e4ebf2", zeroline=False,
                tickprefix="$", tickformat="~s", tickfont=dict(size=10),
            ),
        )
        st.plotly_chart(figura, use_container_width=True, config={"displayModeBar": False})
        st.caption("▧ El área celeste corresponde a la proyección editable")

with impuesto_col:
    st.markdown(
        f"""
        <section class="tax-bridge">
          <div class="tax-icon">▦</div>
          <p class="section-label">Puente tributario</p>
          <h2 class="section-title">Estimación de cierre</h2>
          <div class="tax-list">
            <div class="tax-row"><span>Resultado antes de impuesto</span><strong>{moneda(resultado_antes_impuestos)}</strong></div>
            <div class="tax-row"><span>Gastos rechazados considerados</span><strong>{moneda(GASTOS_RECHAZADOS)}</strong></div>
            <div class="tax-row"><span>Rebaja estimada Art. 14 E</span><strong class="positive">− {moneda(rebaja_14e)}</strong></div>
            <div class="tax-row"><span>Base afecta estimada</span><strong>{moneda(base_afecta)}</strong></div>
            <div class="tax-row tax-total"><span>IDPC estimado · 27%</span><strong>{moneda(impuesto)}</strong></div>
          </div>
          <p class="tax-note">Simulación gerencial. Los requisitos y topes del beneficio deben validarse en la determinación tributaria definitiva.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Editor de proyecciones
# -----------------------------------------------------------------------------
st.write("")
with st.container(border=True):
    encabezado_col, controles_col = st.columns([1.55, 1.45], vertical_alignment="bottom")

    with encabezado_col:
        st.markdown(
            """
            <p class="section-label">Ingreso de proyecciones</p>
            <h2 class="section-title">Forecast · agosto a diciembre</h2>
            <p class="editor-copy">Los puntos de miles se aplican al confirmar con Enter. En gastos, ingresa el monto positivo; el panel lo descuenta automáticamente.</p>
            """,
            unsafe_allow_html=True,
        )

    with controles_col:
        if hasattr(st, "segmented_control"):
            vista = st.segmented_control(
                "Vista", ["Todas", "Ingresos", "Gastos"],
                default="Todas", label_visibility="collapsed",
            )
        else:
            vista = st.radio(
                "Vista", ["Todas", "Ingresos", "Gastos"],
                horizontal=True, label_visibility="collapsed",
            )

        boton_actualizar, boton_guardar, boton_limpiar, boton_restaurar = st.columns(4)
        actualizar = boton_actualizar.button("↻ Actualizar", use_container_width=True)
        guardar = boton_guardar.button("▣ Guardar", type="primary", use_container_width=True)
        limpiar = boton_limpiar.button("Limpiar", use_container_width=True)
        restaurar = boton_restaurar.button("Restaurar", use_container_width=True)

    if actualizar:
        cargar_datos.clear()
        st.session_state.pop("forecast_data", None)
        st.session_state.editor_version += 1
        st.rerun()

    if guardar:
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            conn.update(
                spreadsheet=URL_GOOGLE_SHEET,
                data=st.session_state.forecast_data
            )
            st.toast("Forecast guardado en la nube exitosamente", icon="✅")
        except Exception as e:
            st.error(f"Error guardando en la nube: {e}")

    if limpiar:
        datos_limpios = st.session_state.forecast_data.copy()
        datos_limpios.loc[df_filtrado.index, MESES_PROY] = 0.0
        st.session_state.forecast_data = datos_limpios
        st.session_state.editor_version += 1
        st.rerun()

    if restaurar:
        datos_restaurados = st.session_state.forecast_data.copy()
        indices = df_filtrado.index.intersection(df_base.index)
        datos_restaurados.loc[indices, MESES_PROY] = df_base.loc[indices, MESES_PROY]
        st.session_state.forecast_data = datos_restaurados
        st.session_state.editor_version += 1
        st.rerun()

    df_vista = df_filtrado.copy()
    if vista == "Ingresos":
        df_vista = df_vista[df_vista["Categoría"].map(es_ingreso)]
    elif vista == "Gastos":
        df_vista = df_vista[~df_vista["Categoría"].map(es_ingreso)]

    df_vista["Total original"] = pd.to_numeric(
        df_vista["Total_Original_Base"], errors="coerce"
    ).fillna(0.0)
    df_vista["Total forecast"] = df_vista[MESES].sum(axis=1)
    df_vista["Variación firmada"] = df_vista["Total forecast"] - df_vista["Total original"]
    df_vista["Estado"] = df_vista.apply(estado_forecast, axis=1)

    columnas_editor = COLUMNAS_TEXTO + MESES + ["Total original", "Total forecast", "Variación", "Estado"]
    vista_editor = df_vista.copy()
    mascara_gastos_editor = ~vista_editor["Categoría"].map(es_ingreso)

    for columna in MESES + ["Total original", "Total forecast"]:
        vista_editor.loc[mascara_gastos_editor, columna] = vista_editor.loc[
            mascara_gastos_editor, columna
        ].abs()

    vista_editor["Variación"] = vista_editor["Variación firmada"]
    vista_editor.loc[mascara_gastos_editor, "Variación"] = (
        vista_editor.loc[mascara_gastos_editor, "Total forecast"]
        - vista_editor.loc[mascara_gastos_editor, "Total original"]
    )
    vista_editor = vista_editor[columnas_editor]

    configuracion_columnas = {
        columna: st.column_config.NumberColumn(
            columna,
            help="Monto en pesos chilenos",
            format="localized",
            step=1,
        )
        for columna in MESES + ["Total original", "Total forecast", "Variación"]
    }
    configuracion_columnas["Estado"] = st.column_config.TextColumn("Estado", width="medium")

    tabla_estilada = vista_editor.style.map(color_estado, subset=["Estado"])
    tabla_editada = st.data_editor(
        tabla_estilada,
        key=f"forecast_editor_{st.session_state.editor_version}",
        use_container_width=True,
        height=min(640, max(260, 38 * (len(vista_editor) + 1))),
        hide_index=True,
        column_config=configuracion_columnas,
        disabled=COLUMNAS_TEXTO + MESES_HIST + ["Total original", "Total forecast", "Variación", "Estado"],
    )

    hubo_cambio = False
    datos_actualizados = st.session_state.forecast_data.copy()
    for indice in tabla_editada.index:
        categoria = datos_actualizados.at[indice, "Categoría"]
        for mes in MESES_PROY:
            valor_visible = pd.to_numeric(pd.Series([tabla_editada.at[indice, mes]]), errors="coerce").iloc[0]
            valor_visible = 0.0 if pd.isna(valor_visible) else float(valor_visible)
            valor_interno = abs(valor_visible) if es_ingreso(categoria) else -abs(valor_visible)
            valor_anterior = float(datos_actualizados.at[indice, mes])
            if abs(valor_interno - valor_anterior) >= 0.5:
                datos_actualizados.at[indice, mes] = valor_interno
                hubo_cambio = True

    if hubo_cambio:
        st.session_state.forecast_data = datos_actualizados
        st.session_state.editor_version += 1
        st.rerun()

    descarga = st.session_state.forecast_data.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Descargar forecast en CSV",
        data=descarga,
        file_name="Forecast_Valgardena.csv",
        mime="text/csv",
    )
