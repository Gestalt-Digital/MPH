# UI.py
import streamlit as st
import pandas as pd

# --- Load Data ---
@st.cache_data
def load_data():
    forecast_df = pd.read_csv("bajaj_monthly_forecast_with_mape.csv")
    elasticity_df = pd.read_csv("Adj_Price_Elasticity.csv")
    return forecast_df, elasticity_df

def render_forecast_simulator():
    forecast_df, elasticity_df = load_data()

    st.title("🔮 Forecast Simulator with Price Sensitivity")

    # --- User Selections ---
    selected_country = st.selectbox("Select Country", sorted(forecast_df["Country"].unique()))
    selected_bike = st.selectbox("Select Bike Model", sorted(forecast_df["Bike_Model"].unique()))

    # --- Filter forecast ---
    filtered_df = forecast_df[
        (forecast_df["Country"] == selected_country) &
        (forecast_df["Bike_Model"] == selected_bike)
    ].copy()

    if filtered_df.empty:
        st.warning("No forecast data for selected Country and Bike Model.")
        return

    # --- Get Elasticity ---
    elasticity_row = elasticity_df[
        (elasticity_df["Country"] == selected_country) &
        (elasticity_df["Bike_Model"] == selected_bike)
    ]
    elasticity = elasticity_row["Elasticity"].values[0] if not elasticity_row.empty else -1.0
    intensity = elasticity_row["Comp_Intensity"].values[0] if "Comp_Intensity" in elasticity_row.columns else 1.0
    effective_elasticity = elasticity * intensity

    st.markdown(f"**Price Elasticity:** {round(elasticity, 2)}")
    st.markdown(f"**Competitive Intensity Multiplier:** {round(intensity, 2)}")
    st.markdown(f"**Effective Elasticity:** {round(effective_elasticity, 2)}")

    # --- Base Price and Adjustment ---
    base_price = filtered_df["Unit_Price"].mean()
    # Styled input using text_input
    st.markdown(
    """
    <div style="
        background-color: #fef5e7;
        padding: 8px 14px;
        margin-bottom: 5px;
        border-left: 5px solid #ff6b2e;
        font-weight: 600;
        color: #434b74;
        border-radius: 6px;
        display: inline-block;
    ">
        Enter New Price:
    </div>
    """,
    unsafe_allow_html=True
)

    # Native input below it
    new_price = st.number_input("", value=round(base_price, 2))
    price_change_pct = (new_price - base_price) / base_price

    filtered_df["Adjusted_Forecast"] = filtered_df["Predicted_Units"] * (1 + effective_elasticity * price_change_pct)
    filtered_df["Revenue"] = filtered_df["Adjusted_Forecast"] * new_price

    # --- Display Results ---
    st.subheader("📈 Forecast vs Adjusted Forecast")
    
    # Inject CSS to shrink column widths
    st.markdown("""
        <style>
            .dataframe th, .dataframe td {
                padding: 2px 6px !important;
                font-size: 14px;
            }
        </style>
    """, unsafe_allow_html=True)
    # --- Show Table ---
    display_df = (filtered_df[["Month", "Predicted_Units", "Adjusted_Forecast", "Revenue"]])
    st.dataframe(display_df, use_container_width=False, height=400)
#st.dataframe(filtered_df[["Month", "Predicted_Units", "Adjusted_Forecast", "Revenue"]])

    # --- Chart ---
    filtered_df["Month_Label"] = pd.to_datetime(filtered_df["Month"], format="%b-%y").dt.strftime("%b-%y")
    filtered_df = filtered_df.sort_values("Month_Label").copy()
    filtered_df["Month_Label"] = pd.Categorical(
        filtered_df["Month_Label"],
        ordered=True,
        categories=sorted(filtered_df["Month_Label"].unique(), key=lambda x: pd.to_datetime(x, format="%b-%y"))
    )

    st.line_chart(filtered_df.set_index("Month_Label")[["Predicted_Units", "Adjusted_Forecast"]])
    st.success("Simulation complete. Adjust the price above to see its effect on your forecast.")
