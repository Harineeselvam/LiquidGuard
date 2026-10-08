import streamlit as st
import pandas as pd
import joblib
import serial
import time
from serial.tools import list_ports

# =========================================================
# LOAD MODEL
# =========================================================

model = joblib.load("model/liquidguard_model.pkl")

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="LiquidGuard",
    page_icon="🧪",
    layout="wide"
)

# =========================================================
# CUSTOM DESIGN
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f4f8fb;
}

.title {
    text-align: center;
    color: #0066cc;
    font-size: 42px;
    font-weight: bold;
}

.subtitle {
    text-align: center;
    color: #555555;
    font-size: 18px;
}

.sensor-card {
    background-color: white;
    padding: 18px;
    border-radius: 15px;
    border: 1px solid #d9e6f2;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.08);
}

.result-box {
    padding: 25px;
    border-radius: 18px;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="title">🧪 LIQUIDGUARD</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Based Multimodal Liquid Quality Monitoring System'
    '</div>',
    unsafe_allow_html=True
)

st.write("")

# =========================================================
# LIQUID SELECTION
# =========================================================

st.subheader("🥤 Select Liquid Product")

liquid_type = st.selectbox(
    "Choose the liquid being tested",
    [
        "Milk",
        "Fruit Juice",
        "Edible Oil",
        "Soft Drink",
        "Other Liquid"
    ]
)

st.info(
    f"Currently selected liquid: **{liquid_type}**"
)

# =========================================================
# INPUT MODE
# =========================================================

st.subheader("⚙️ Sensor Input Mode")

mode = st.radio(
    "Select how sensor values are provided:",
    [
        "Manual / Demo Mode",
        "Live ESP32 Sensor Mode"
    ],
    horizontal=True
)

# =========================================================
# SENSOR VARIABLES
# =========================================================

mq3 = 420.0
mq135 = 580.0
ph = 6.6
tds = 300.0
temperature = 27.0
humidity = 60.0

# =========================================================
# MANUAL MODE
# =========================================================

if mode == "Manual / Demo Mode":

    st.subheader("🧪 Enter Sensor Values")

    col1, col2, col3 = st.columns(3)

    with col1:
        mq3 = st.number_input(
            "🟠 MQ-3 Gas Sensor",
            min_value=0.0,
            value=420.0
        )

    with col2:
        mq135 = st.number_input(
            "🔵 MQ-135 Gas Sensor",
            min_value=0.0,
            value=580.0
        )

    with col3:
        ph = st.number_input(
            "🧪 pH Value",
            min_value=0.0,
            max_value=14.0,
            value=6.6
        )

    col4, col5, col6 = st.columns(3)

    with col4:
        tds = st.number_input(
            "💧 TDS Value",
            min_value=0.0,
            value=300.0
        )

    with col5:
        temperature = st.number_input(
            "🌡 Temperature (°C)",
            min_value=0.0,
            value=27.0
        )

    with col6:
        humidity = st.number_input(
            "💦 Humidity (%)",
            min_value=0.0,
            max_value=100.0,
            value=60.0
        )

# =========================================================
# LIVE ESP32 MODE
# =========================================================

else:

    st.subheader("🔌 Live ESP32 Sensor Connection")

    ports = list_ports.comports()

    port_names = [port.device for port in ports]

    if len(port_names) == 0:

        st.warning(
            "No ESP32/USB sensor device detected. "
            "Connect the ESP32 and refresh the page."
        )

    else:

        selected_port = st.selectbox(
            "Select ESP32 COM Port",
            port_names
        )

        baud_rate = st.selectbox(
            "Baud Rate",
            [9600, 115200]
        )

        if st.button(
            "📡 READ LIVE SENSOR VALUES",
            use_container_width=True
        ):

            try:

                ser = serial.Serial(
                    selected_port,
                    baud_rate,
                    timeout=3
                )

                time.sleep(2)

                line = ser.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                ser.close()

                values = [
                    float(x.strip())
                    for x in line.split(",")
                ]

                if len(values) == 6:

                    mq3 = values[0]
                    mq135 = values[1]
                    ph = values[2]
                    tds = values[3]
                    temperature = values[4]
                    humidity = values[5]

                    st.success(
                        "✅ Live sensor values received successfully!"
                    )

                else:

                    st.error(
                        "ESP32 data format is incorrect."
                    )

            except Exception as e:

                st.error(
                    f"Unable to read sensor data: {e}"
                )

# =========================================================
# DISPLAY CURRENT SENSOR VALUES
# =========================================================

st.divider()

st.subheader("📊 Current Sensor Readings")

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("MQ-3", f"{mq3:.1f}")
c2.metric("MQ-135", f"{mq135:.1f}")
c3.metric("pH", f"{ph:.2f}")
c4.metric("TDS", f"{tds:.1f}")
c5.metric("Temperature", f"{temperature:.1f} °C")
c6.metric("Humidity", f"{humidity:.1f} %")

# =========================================================
# ANALYSIS
# =========================================================

st.divider()

if st.button(
    "🔍 ANALYZE LIQUID SAMPLE",
    use_container_width=True
):

    input_data = pd.DataFrame(
        [[
            mq3,
            mq135,
            ph,
            tds,
            temperature,
            humidity
        ]],
        columns=[
            "MQ3",
            "MQ135",
            "pH",
            "TDS",
            "Temperature",
            "Humidity"
        ]
    )

    prediction = model.predict(input_data)[0]

    probabilities = model.predict_proba(input_data)[0]

    confidence = max(probabilities) * 100

    # =====================================================
    # RESULT
    # =====================================================

    st.divider()

    st.subheader("🤖 LIQUIDGUARD ANALYSIS RESULT")

    if prediction == "Fresh":

        st.success(
            "🟢 FRESH"
        )

    elif prediction == "Going to Spoil":

        st.warning(
            "🟡 GOING TO SPOIL"
        )

    else:

        st.error(
            "🔴 SPOILED"
        )

    st.metric(
        "AI Prediction Confidence",
        f"{confidence:.2f}%"
    )

    st.write(
        f"**Liquid Tested:** {liquid_type}"
    )

    # =====================================================
    # RESULT TABLE
    # =====================================================

    st.subheader("📋 Sensor Analysis")

    result_df = pd.DataFrame({
        "Parameter": [
            "MQ-3",
            "MQ-135",
            "pH",
            "TDS",
            "Temperature",
            "Humidity"
        ],

        "Reading": [
            mq3,
            mq135,
            ph,
            tds,
            temperature,
            humidity
        ]
    })

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )

    # =====================================================
    # GRAPH
    # =====================================================

    st.subheader("📈 Sensor Reading Visualization")

    graph_df = pd.DataFrame({
        "Sensor": [
            "MQ-3",
            "MQ-135",
            "pH",
            "TDS"
        ],

        "Value": [
            mq3,
            mq135,
            ph,
            tds
        ]
    })

    st.bar_chart(
        graph_df.set_index("Sensor")
    )

# =========================================================
# INFORMATION
# =========================================================

st.divider()

st.subheader("ℹ️ About LiquidGuard")

st.write(
    """
    LiquidGuard combines E-Nose and E-Tongue sensor information
    with machine learning to provide a preliminary liquid-quality
    classification.

    E-Nose sensors:
    MQ-3 and MQ-135

    E-Tongue sensors:
    pH and TDS

    Environmental monitoring:
    Temperature and Humidity

    The final classification is:
    Fresh / Going to Spoil / Spoiled
    """
)

st.caption(
    "LiquidGuard Software Prototype | "
    "ML-based preliminary quality screening"
)