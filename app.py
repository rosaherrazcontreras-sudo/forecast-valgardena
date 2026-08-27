"""
===================================================================================
FORECAST FINANCIERO Y PROYECCIÓN TRIBUTARIA - VALGARDENA / SCT SOLUCIONES
Arquitectura: Streamlit + Google Sheets Connection + Plotly + Data Editor
Versión: 4.0 (Diseño Corporativo Ultra-Legible, Alto Contraste & Corrección de Colores)
===================================================================================
"""

import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
import io

try:
    from streamlit_gsheets import GSheetsConnection
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False

# =============================================================================
# CONFIGURACIÓN DE NUBE (GOOGLE SHEETS & RESPALDO LOCAL)
# =============================================================================
URL_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/1_D8MgvLX8-KdaAdH35GhcIlNQPWzBwk8-8fgWSVnhxg/edit?gid=0#gid=0"

st.set_page_config(
    page_title="Forecast Financiero | Valgardena",
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

# =============================================================================
# ESTILOS CSS CORPORATIVOS DE ALTO CONTRASTE (CORRECCIÓN DE COLORES)
# =============================================================================
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Lora:ital,wght@0,500;0,600;1,400&display=swap');
      
      :root {
        --navy: #0b2239;
        --ink: #0f1e2f;
        --title-color: #0b2848;
        --subtitle-color: #475569;
        --muted: #64748b;
        --line: #cbd5e1;
        --card-bg: #ffffff;
        --page-bg: #f8fafc;
        --blue-primary: #1d4ed8;
        --blue-accent: #2563eb;
        --red-accent: #dc2626;
        --green-accent: #059669;
        --amber-accent: #d97706;
        --purple-accent: #7c3aed;
      }
      
      html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        background-color: var(--page-bg) !important;
        color: #1e293b !important;
      }
      
      [data-testid="stHeader"] { height: 0; background: transparent; }
      #MainMenu, footer, [data-testid="stDeployButton"] { visibility: hidden; }
      
      .block-container {
        max-width: 1680px;
        padding: 1.5rem 2.5rem 3.5rem !important;
      }
      
      .top-strip {
        position: fixed;
        z-index: 999;
        inset: 0 0 auto;
        height: 8px;
        background: linear-gradient(90deg, #0b2848 0%, #1e40af 50%, #059669 100%);
      }

      /* Hero Header */
      .hero {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 2rem;
        margin: 0.5rem 0 1.25rem;
      }
      .hero h1 {
        margin: 0;
        color: var(--title-color) !important;
        font-family: 'Lora', Georgia, serif !important;
        font-size: clamp(2.2rem, 3.5vw, 3.2rem) !important;
        font-weight: 600 !important;
        letter-spacing: -0.03em;
        line-height: 1.05;
      }
      .hero p {
        margin: 0.5rem 0 0 !important;
        color: var(--subtitle-color) !important;
        font-size: 0.98rem !important;
      }
      
      .eyebrow, .section-label {
        margin: 0 0 0.35rem !important;
        color: #1d4ed8 !important;
        font-size: 0.72rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
      }
      
      .section-title {
        margin: 0 0 0.25rem !important;
        color: #0b2848 !important;
        font-family: 'Lora', Georgia, serif !important;
        font-size: 1.45rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.015em;
      }
      
      .editor-copy {
        margin: 0.35rem 0 0.75rem !important;
        color: #475569 !important;
        font-size: 0.85rem !important;
        line-height: 1.4;
      }

      /* Track de Fases */
      .phase-track {
        display: grid;
        grid-template-columns: 7fr 5fr;
        width: min(420px, 36vw);
        overflow: hidden;
        border: 1.5px solid #cbd5e1;
        border-radius: 10px;
        background: #ffffff;
        color: #334155;
        font-size: 0.75rem;
        font-weight: 700;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
      }
      .phase-track span { padding: 0.65rem 0.8rem; }
      .phase-track span:first-child { background: #f8fafc; color: #475569; }
      .phase-track span:last-child { background: #dbeafe; color: #1e40af; border-left: 1.5px solid #bfdbfe; }

      /* Tarjetas de Métricas KPI */
      .metric-grid {
        display: grid;
        grid-template-columns: repeat(6, minmax(0, 1fr));
        gap: 0.85rem;
        margin-bottom: 1.1rem;
      }
      .metric-card {
        min-width: 0;
        min-height: 120px;
        padding: 1rem 1.1rem;
        border: 1px solid #e2e8f0;
        border-top: 4px solid var(--accent) !important;
        border-radius: 12px;
        background: #ffffff;
        box-shadow: 0 4px 12px rgba(15, 30, 47, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }
      .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(15, 30, 47, 0.07);
      }
      .metric-label {
        display: flex;
        min-height: 32px;
        align-items: flex-start;
        justify-content: space-between;
        gap: 0.5rem;
        color: #475569 !important;
        font-size: 0.72rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.03em;
        line-height: 1.3;
        text-transform: uppercase;
      }
      .metric-icon {
        display: grid;
        width: 28px;
        height: 28px;
        flex: 0 0 auto;
        place-items: center;
        border-radius: 8px;
        background: color-mix(in srgb, var(--accent) 12%, white);
        color: var(--accent);
        font-size: 0.95rem;
        font-weight: bold;
      }
      .metric-value {
        overflow: hidden;
        margin-top: 0.35rem;
        color: #0f1e2f !important;
        font-size: clamp(1.15rem, 1.45vw, 1.55rem) !important;
        font-weight: 800 !important;
        letter-spacing: -0.035em;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .metric-hint {
        margin-top: 0.35rem;
        color: #64748b !important;
        font-size: 0.72rem !important;
        font-weight: 500;
      }

      /* Contenedores con Borde */
      [data-testid="stVerticalBlockBorderWrapper"] {
        overflow: hidden;
        border: 1px solid #e2e8f0 !important;
        border-radius: 14px !important;
        background: #ffffff !important;
        box-shadow: 0 4px 14px rgba(15, 30, 47, 0.04) !important;
        padding: 0.6rem 0.8rem !important;
      }

      /* Puente Tributario (Tarjeta Azul Oscura Ejecutiva) */
      .tax-bridge {
        position: relative;
        min-height: 480px;
        overflow: hidden;
        padding: 1.4rem 1.5rem;
        border: 1px solid #1e3a5f;
        border-radius: 14px;
        background: linear-gradient(145deg, #0b2239 0%, #0f2d4e 100%);
        color: #ffffff !important;
        box-shadow: 0 6px 20px rgba(11, 34, 57, 0.15);
      }
      .tax-bridge .section-label { color: #60a5fa !important; }
      .tax-bridge .section-title { color: #ffffff !important; font-size: 1.5rem !important; }
      .tax-icon {
        position: absolute;
        top: 1.25rem;
        right: 1.25rem;
        display: grid;
        width: 38px;
        height: 38px;
        place-items: center;
        border: 1.5px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        color: #93c5fd;
        font-size: 1.1rem;
      }
      .tax-list { margin: 1.35rem 0 0; }
      .tax-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding: 0.85rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.12);
      }
      .tax-row span {
        max-width: 58%;
        color: #cbd5e1 !important;
        font-size: 0.78rem !important;
        line-height: 1.35;
      }
      .tax-row strong {
        font-family: 'Plus Jakarta Sans', monospace !important;
        font-size: 0.88rem !important;
        color: #ffffff !important;
        font-weight: 700;
        text-align: right;
      }
      .tax-row .positive { color: #34d399 !important; }
      .tax-total {
        border-bottom: 0;
        padding-top: 1.1rem;
      }
      .tax-total span { color: #ffffff !important; font-weight: 800 !important; font-size: 0.88rem !important; }
      .tax-total strong { color: #fbbf24 !important; font-size: 1.2rem !important; font-weight: 800 !important; }
      .tax-note {
        position: relative;
        z-index: 1;
        margin: 1rem 0 0;
        padding-top: 0.9rem;
        border-top: 1px solid rgba(255, 255, 255, 0.12);
        color: #94a3b8 !important;
        font-size: 0.68rem !important;
        line-height: 1.5;
      }

      /* BOTONES CORREGIDOS CON ALTO CONTRASTE */
      .stButton > button {
        background-color: #ffffff !important;
        color: #0f2942 !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        transition: all 0.2s ease !important;
      }
      .stButton > button:hover {
        background-color: #f1f5f9 !important;
        border-color: #2563eb !important;
        color: #1d4ed8 !important;
      }
      
      /* Botón Primario Guardar */
      .stButton > button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: #ffffff !important;
        border: 1px solid #b91c1c !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(220, 38, 38, 0.25) !important;
      }
      .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.35) !important;
      }

      /* Botón de Descarga */
      .stDownloadButton > button {
        background-color: #0b2848 !important;
        color: #ffffff !important;
        border: 1px solid #081d34 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 0.82rem !important;
        box-shadow: 0 2px 6px rgba(11, 40, 72, 0.2) !important;
      }
      .stDownloadButton > button:hover {
        background-color: #1e40af !important;
        color: #ffffff !important;
      }

      /* Control Segmentado (Todas / Ingresos / Gastos) */
      [data-testid="stSegmentedControl"] {
        background-color: #e2e8f0 !important;
        padding: 3px !important;
        border-radius: 8px !important;
      }
      [data-testid="stSegmentedControl"] button {
        font-weight: 700 !important;
        color: #475569 !important;
        border-radius: 6px !important;
      }
      [data-testid="stSegmentedControl"] button[aria-checked="true"] {
        background-color: #ffffff !important;
        color: #0b2848 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08) !important;
      }

      @media(max-width: 1220px){ .metric-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
      @media(max-width: 760px){ 
        .block-container { padding: 1.25rem 1rem 3rem !important; }
        .hero { align-items: flex-start; flex-direction: column; }
        .phase-track { width: 100%; }
        .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      }
    </style>
    <div class="top-strip"></div>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# FUNCIONES DE CARGA Y TRANSFORMACIÓN DE DATOS (CON FALLBACK RESILIENTE)
# =============================================================================
def generate_mock_backup() -> pd.DataFrame:
    """Genera datos de respaldo si no hay conexión a Google Sheets ni archivo local."""
    rows = [
        {
            'Categoría': '1. INGRESOS OPERACIONALES', 'Área': 'SANTIAGO', 'Grupo': 'SERVICIOS CONTABLES',
            'Cuenta / Ítem': 'Honorarios Mensuales Asesoría', 'Detalle / Tipo': 'Servicio Recurrente',
            'Ene': 6500000, 'Feb': 7100000, 'Mar': 6800000, 'Abr': 7500000, 'May': 7200000, 'Jun': 7400000, 'Jul': 7600000,
            'Ago': 7600000, 'Sep': 7600000, 'Oct': 7600000, 'Nov': 7600000, 'Dic': 7600000
        },
        {
            'Categoría': '1. INGRESOS OPERACIONALES', 'Área': 'FUNDO', 'Grupo': 'ASESORÍA TRIBUTARIA',
            'Cuenta / Ítem': 'Planificación Fiscal Anual', 'Detalle / Tipo': 'Proyecto Especial',
            'Ene': 4200000, 'Feb': 5300000, 'Mar': 4500000, 'Abr': 5800000, 'May': 5000000, 'Jun': 5200000, 'Jul': 5500000,
            'Ago': 5500000, 'Sep': 5500000, 'Oct': 5500000, 'Nov': 5500000, 'Dic': 5500000
        },
        {
            'Categoría': '1.2 VENTAS', 'Área': 'FUNDO', 'Grupo': 'EXPLOTACIÓN AGRÍCOLA',
            'Cuenta / Ítem': 'Venta Bosque Pino & Maderas', 'Detalle / Tipo': 'Venta Directa',
            'Ene': 0, 'Feb': 8900000, 'Mar': 0, 'Abr': 9200000, 'May': 0, 'Jun': 4500000, 'Jul': 0,
            'Ago': 6000000, 'Sep': 0, 'Oct': 8000000, 'Nov': 0, 'Dic': 10000000
        },
        {
            'Categoría': '1.1 ARRIENDOS', 'Área': 'SANTIAGO', 'Grupo': 'INMUEBLE',
            'Cuenta / Ítem': 'Arriendo Oficinas Providencia', 'Detalle / Tipo': 'Infraestructura',
            'Ene': -1500000, 'Feb': -1500000, 'Mar': -1500000, 'Abr': -1500000, 'May': -1500000, 'Jun': -1500000, 'Jul': -1500000,
            'Ago': -1500000, 'Sep': -1500000, 'Oct': -1500000, 'Nov': -1500000, 'Dic': -1500000
        },
        {
            'Categoría': '1.3 GASTOS BÁSICOS', 'Área': 'SANTIAGO', 'Grupo': 'SUMINISTROS',
            'Cuenta / Ítem': 'Luz, Agua y Conectividad', 'Detalle / Tipo': 'Servicios Básicos',
            'Ene': -395000, 'Feb': -420000, 'Mar': -405000, 'Abr': -430000, 'May': -410000, 'Jun': -440000, 'Jul': -425000,
            'Ago': -430000, 'Sep': -430000, 'Oct': -430000, 'Nov': -430000, 'Dic': -430000
        },
        {
            'Categoría': '1.4 ADMINISTRACION Y TI', 'Área': 'SANTIAGO', 'Grupo': 'TECNOLOGÍA',
            'Cuenta / Ítem': 'Licencias Cloud & AWS', 'Detalle / Tipo': 'Software Corporativo',
            'Ene': -420000, 'Feb': -380000, 'Mar': -290000, 'Abr': -350000, 'May': -360000, 'Jun': -370000, 'Jul': -380000,
            'Ago': -380000, 'Sep': -380000, 'Oct': -380000, 'Nov': -380000, 'Dic': -380000
        },
        {
            'Categoría': '1.5 HONORARIOS PROFESIONALES', 'Área': 'FUNDO', 'Grupo': 'PROFESIONALES',
            'Cuenta / Ítem': 'Asesoría Agronómica y Peritajes', 'Detalle / Tipo': 'Honorarios Directos',
            'Ene': -650000, 'Feb': -520000, 'Mar': -700000, 'Abr': -850000, 'May': -600000, 'Jun': -650000, 'Jul': -700000,
            'Ago': -700000, 'Sep': -700000, 'Oct': -700000, 'Nov': -700000, 'Dic': -700000
        }
    ]
    return pd.DataFrame(rows)


@st.cache_data(ttl=60)
def cargar_datos() -> pd.DataFrame:
    """Carga desde Google Sheets; si falla, lee Dashboard.xlsx local o genera mock."""
    if GSHEETS_AVAILABLE:
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df = conn.read(spreadsheet=URL_GOOGLE_SHEET)
            if df is not None and not df.empty:
                return df
        except Exception:
            pass

    excel_path = "Dashboard.xlsx"
    if os.path.exists(excel_path):
        try:
            df = pd.read_excel(excel_path, sheet_name="EERR Mensual")
            return df
        except Exception:
            pass

    return generate_mock_backup()


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
        return "color:#065f46;background-color:#d1fae5;font-weight:700;border-radius:4px"
    if "Mayor gasto" in texto or texto.startswith("▼ Ingreso"):
        return "color:#991b1b;background-color:#fee2e2;font-weight:700;border-radius:4px"
    return "color:#475569;font-weight:500"


# =============================================================================
# PREPARACIÓN Y VALIDACIÓN DE LA BASE DE DATOS
# =============================================================================
df_base = cargar_datos()
if df_base is None:
    st.error("No se pudo cargar la base de datos.")
    st.stop()

# Limpieza y filtrado
df_base.columns = [str(c).strip() for c in df_base.columns]
if "Categoría" in df_base.columns:
    df_base = df_base[~df_base["Categoría"].astype(str).str.upper().str.contains("RESULTADO DEL EJERCICIO", na=False)].copy()

for col in COLUMNAS_TEXTO:
    if col not in df_base.columns:
        df_base[col] = "Sin clasificar"
    else:
        df_base[col] = df_base[col].fillna("Sin clasificar").astype(str).str.strip()

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


# =============================================================================
# FILTROS LATERALES EN CASCADA
# =============================================================================
with st.sidebar:
    st.markdown("## 🏢 **Valgardena**")
    st.caption("Panel de Control & Filtros Financieros")
    st.markdown("---")

df_filtrado = df_global.copy()
with st.sidebar:
    for columna, clave in [
        ("Categoría", "f_categoria"), ("Área", "f_area"), ("Grupo", "f_grupo"),
        ("Cuenta / Ítem", "f_cuenta"), ("Detalle / Tipo", "f_detalle"),
    ]:
        opciones = sorted(df_filtrado[columna].astype(str).unique().tolist())
        seleccion = st.multiselect(columna, opciones, key=clave)
        if seleccion:
            df_filtrado = df_filtrado[df_filtrado[columna].astype(str).isin(seleccion)]

    st.markdown("---")
    if st.button("🔄 Restablecer Filtros", use_container_width=True):
        for clave in ("f_categoria", "f_area", "f_grupo", "f_cuenta", "f_detalle"):
            st.session_state.pop(clave, None)
        st.rerun()


# =============================================================================
# MOTOR FINANCIERO Y TRIBUTARIO
# =============================================================================
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


# =============================================================================
# CABECERA Y TARJETAS EJECUTIVAS
# =============================================================================
st.markdown(
    """
    <section class="hero">
      <div>
        <p class="eyebrow">Cierre Anual · Ejercicio 2026</p>
        <h1>Forecast Financiero</h1>
        <p>Resultado operacional, márgenes e impacto tributario consolidado en tiempo real.</p>
      </div>
      <div class="phase-track"><span>7 meses históricos</span><span>5 meses forecast</span></div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<section class="metric-grid">'
    + tarjeta("Ingresos Proyectados", moneda(total_ingresos), "Acumulado anual proyectado", "#2563eb", "↗")
    + tarjeta("Gastos Proyectados", moneda(total_gastos), porcentaje(ratio_gastos) + " de los ingresos", "#dc2626", "▣")
    + tarjeta("Resultado Antes Impuesto", moneda(resultado_antes_impuestos), "Resultado operacional bruto", "#7c3aed", "◉")
    + tarjeta("Margen Operacional", porcentaje(margen), "Utilidad / Ingresos", "#059669", "↗")
    + tarjeta("Impuesto Estimado", moneda(impuesto), porcentaje(tasa_efectiva) + " tasa efectiva IDPC", "#d97706", "♜")
    + tarjeta("Resultado Líquido Final", moneda(resultado_liquido), "Utilidad disponible final", "#0b2848", "✣")
    + "</section>",
    unsafe_allow_html=True,
)


# =============================================================================
# EVOLUCIÓN MENSUAL Y PUENTE TRIBUTARIO
# =============================================================================
grafico_col, impuesto_col = st.columns([3.4, 1.1], gap="medium")

with grafico_col:
    with st.container(border=True):
        st.markdown(
            '<p class="section-label">Evolución Mensual</p>'
            '<h2 class="section-title">Ingresos, Gastos y Resultado Acumulado</h2>',
            unsafe_allow_html=True,
        )
        acumulado = pd.Series(resultado_mes).cumsum().tolist()
        fase = ["Histórico" if mes in MESES_HIST else "Forecast" for mes in MESES]

        figura = go.Figure()
        
        # 1. Ingresos: Azul vibrante para histórico, Azul suave para forecast
        figura.add_trace(
            go.Bar(
                x=MESES,
                y=ingresos_mes,
                name="Ingresos",
                marker_color=["#2563eb" if etapa == "Histórico" else "#93c5fd" for etapa in fase],
                marker_line=dict(color="#1d4ed8", width=1),
                hovertemplate="<b>%{x}</b><br>Ingresos: $%{y:,.0f}<extra></extra>",
            )
        )
        # 2. Gastos: Rojo vibrante para histórico, Rosa suave para forecast
        figura.add_trace(
            go.Bar(
                x=MESES,
                y=gastos_mes,
                name="Gastos (Abs)",
                marker_color=["#ef4444" if etapa == "Histórico" else "#fca5a5" for etapa in fase],
                marker_line=dict(color="#dc2626", width=1),
                hovertemplate="<b>%{x}</b><br>Gastos: $%{y:,.0f}<extra></extra>",
            )
        )
        # 3. Línea de Resultado Acumulado (Verde Esmeralda Corporativo)
        figura.add_trace(
            go.Scatter(
                x=MESES,
                y=acumulado,
                name="Resultado Acumulado",
                mode="lines+markers",
                line=dict(color="#059669", width=3.5, shape="spline"),
                marker=dict(size=8, color="#047857", symbol="circle"),
                hovertemplate="<b>%{x}</b><br>Resultado Acumulado: $%{y:,.0f}<extra></extra>",
            )
        )
        # Sombra de fondo para el Forecast (Ago - Dic)
        figura.add_vrect(
            x0=6.5, x1=11.5, fillcolor="#eff6ff", opacity=0.8,
            layer="below", line_width=0,
        )
        figura.add_vline(
            x=6.5, line_color="#3b82f6", line_dash="dash", line_width=1.5,
            annotation_text="<b>Inicio Forecast</b>", annotation_position="top left",
            annotation_font=dict(size=11, color="#1e40af")
        )
        figura.update_layout(
            barmode="group",
            hovermode="x unified",
            height=395,
            margin=dict(l=12, r=12, t=32, b=8),
            paper_bgcolor="#ffffff",
            plot_bgcolor="#ffffff",
            font=dict(color="#334155", size=11, family="Plus Jakarta Sans"),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.04,
                xanchor="right", x=1, font=dict(size=11, weight="bold"),
            ),
            xaxis=dict(
                showgrid=False, zeroline=False,
                tickfont=dict(size=11, weight="bold", color="#1e293b")
            ),
            yaxis=dict(
                showgrid=True, gridcolor="#f1f5f9", zeroline=False,
                tickprefix="$", tickformat="~s",
                tickfont=dict(size=10, color="#64748b"),
            ),
        )
        st.plotly_chart(figura, use_container_width=True, config={"displayModeBar": False})
        st.caption("💡 *El área sombreada en azul claro delimita la proyección editable (Agosto a Diciembre).*")

with impuesto_col:
    st.markdown(
        f"""
        <section class="tax-bridge">
          <div class="tax-icon">🏛️</div>
          <p class="section-label">Puente Tributario</p>
          <h2 class="section-title">Estimación Cierre</h2>
          <div class="tax-list">
            <div class="tax-row"><span>Resultado Antes Impuesto</span><strong>{moneda(resultado_antes_impuestos)}</strong></div>
            <div class="tax-row"><span>Gastos Rechazados Estimados</span><strong>{moneda(GASTOS_RECHAZADOS)}</strong></div>
            <div class="tax-row"><span>Rebaja Estimada Art. 14 E</span><strong class="positive">− {moneda(rebaja_14e)}</strong></div>
            <div class="tax-row"><span>Base Afecta IDPC</span><strong>{moneda(base_afecta)}</strong></div>
            <div class="tax-row tax-total"><span>IDPC Estimado (27%)</span><strong>{moneda(impuesto)}</strong></div>
          </div>
          <p class="tax-note">Simulación gerencial régimen 14A. Los requisitos e incentivos deben validarse en la DJ final.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# EDITOR DE PROYECCIONES INTERACTIVO
# =============================================================================
st.write("")
with st.container(border=True):
    encabezado_col, controles_col = st.columns([1.4, 1.6], vertical_alignment="bottom")

    with encabezado_col:
        st.markdown(
            """
            <p class="section-label">Ingreso de Proyecciones</p>
            <h2 class="section-title">Forecast · Agosto a Diciembre</h2>
            <p class="editor-copy">Haz doble clic en las celdas para modificar. En gastos, ingresa el monto positivo; el sistema lo descuenta automáticamente.</p>
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
        guardar = boton_guardar.button("💾 Guardar", type="primary", use_container_width=True)
        limpiar = boton_limpiar.button("🗑️ Limpiar", use_container_width=True)
        restaurar = boton_restaurar.button("🔄 Restaurar", use_container_width=True)

    if actualizar:
        cargar_datos.clear()
        st.session_state.pop("forecast_data", None)
        st.session_state.editor_version += 1
        st.rerun()

    if guardar:
        if GSHEETS_AVAILABLE:
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                conn.update(
                    spreadsheet=URL_GOOGLE_SHEET,
                    data=st.session_state.forecast_data
                )
                st.toast("Forecast guardado en la nube exitosamente", icon="✅")
            except Exception as e:
                st.error(f"Error guardando en Google Sheets: {e}")
        else:
            st.toast("Edición guardada en la sesión local", icon="✅")

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
            format="$ %,.0f",
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
        height=min(640, max(280, 38 * (len(vista_editor) + 1))),
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

    st.markdown("<br>", unsafe_allow_html=True)
    descarga = st.session_state.forecast_data.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 Descargar Forecast en CSV",
        data=descarga,
        file_name="Forecast_Valgardena.csv",
        mime="text/csv",
    )
