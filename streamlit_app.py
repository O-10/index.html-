# requirements.py
requirements
import streamlit as st
import pandas as pd
import stripe
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

# --- USUARIOS ---
users = {
    "usuario1": "clave123",
    "oscar": "segura456"
}

# --- CLAVE SECRETA STRIPE ---
stripe.api_key = "sk_test_tu_clave_privada"  # 🔁 Reemplázala por tu clave real

# --- LOGIN ---
def login():
    st.sidebar.title("🔐 Iniciar sesión")
    username = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    if st.sidebar.button("Ingresar"):
        if username in users and users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.success(f"Bienvenido, {username}")
        else:
            st.error("Credenciales incorrectas")

# --- BOTÓN DE PAGO ---
def show_payment_button():
    st.write("💳 Esta sección es Premium. Realiza el pago para continuar.")
    if st.button("Pagar con Stripe"):
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Acceso Premium - App detección de riesgos'},
                    'unit_amount': 3000,  # 30 USD
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://TU-APP.streamlit.app?paid=true',
            cancel_url='https://TU-APP.streamlit.app',
        )
        st.markdown(f"[Haz clic aquí para pagar]({session.url})", unsafe_allow_html=True)

# --- PDF ---
def generar_pdf(interpretacion):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, interpretacion)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file.name

# --- INTERPRETACIÓN SST ---
def interpretar_grafico(df):
    area_mayor_riesgo = df.loc[df["Nivel de Riesgo"].idxmax(), "Área"]
    riesgo_max = df["Nivel de Riesgo"].max()
    riesgo_promedio = df["Nivel de Riesgo"].mean()

    texto = f"""📊 INTERPRETACIÓN:
- Área con mayor riesgo: {area_mayor_riesgo} (nivel {riesgo_max})
- Riesgo promedio: {riesgo_promedio:.2f}\n"""

    if riesgo_max >= 8:
        texto += f"""\n⚠️ Riesgo ALTO:
- Intervención inmediata
- Inspecciones
- Verificar EPP
- Reentrenar personal
- Controles de ingeniería"""
    elif 5 <= riesgo_max < 8:
        texto += f"""\n🔶 Riesgo MODERADO:
- Plan preventivo
- Procedimientos seguros
- Señalización
- Monitoreo continuo"""
    else:
        texto += f"""\n🟢 Riesgo BAJO:
- Mantener controles
- Buenas prácticas
- Seguimiento periódico"""

    st.markdown(texto)
    return texto

# --- APP PRINCIPAL ---
def main_app():
    st.title("🛠️ App de Detección de Riesgos Laborales")

    uploaded_file = st.file_uploader("Sube tu archivo Excel (.xlsx)", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.subheader("Datos cargados:")
        st.dataframe(df)

        st.subheader("📈 Gráfico de Niveles de Riesgo por Área")
        fig, ax = plt.subplots()
        ax.bar(df["Área"], df["Nivel de Riesgo"], color="orange")
        ax.set_xlabel("Área")
        ax.set_ylabel("Nivel de Riesgo")
        ax.set_title("Análisis de Riesgo por Área")
        st.pyplot(fig)

        interpretacion = interpretar_grafico(df)

        if st.button("📄 Descargar informe en PDF"):
            pdf_path = generar_pdf(interpretacion)
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Descargar PDF", data=f, file_name="informe_riesgos.pdf")

# --- CONTROL DE FLUJO ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
else:
    query_params = st.experimental_get_query_params()
    if "paid" in query_params and query_params["paid"][0] == "true":
        main_app()
    else:
        show_payment_button()
