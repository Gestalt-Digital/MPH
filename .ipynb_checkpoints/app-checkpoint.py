# Streamlit run MPHv4.py
import streamlit as st
import pandas as pd
import plotly, sys
print("Plotly:", plotly.__version__, "Python:", sys.version)
from plotly import express as px
from UI import render_forecast_simulator

# Set page config
st.set_page_config(page_title="GTM Hub", layout="wide")
st.title("🌍 AI Driven Go-to-Market planning hub")

# Load data
sales_df = pd.read_csv("data/Sales_Data.csv")
distributor_df = pd.read_csv("data/Distributor_Data.csv")
forecast_df = pd.read_csv("data/bajaj_forecast_with_actuals.csv")
merged_df = pd.read_csv("data/Merged data.csv")
cluster_df = pd.read_csv("data/distributor_clusters.csv")
swot_df = pd.read_csv("data/Competitor_SWOT_Data.csv")
Elastic_df = pd.read_csv("data/Adj_Price_Elasticity.csv")

# Clean column headers
cluster_df.columns = cluster_df.columns.str.strip()
swot_df.columns = swot_df.columns.str.strip()


# Initialize session state
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False



# Create four tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Sales Forecast & Analysis", 
    "Distributor Intelligence", 
    "Competitive Analysis",
    "Pricing-Forecast Simulator",
    "Unified BI Dashboard"
    
    ])

# ================= Tab 1: Export Sales Analysis =================
with tab1:
    with st.expander("🤖 Export Forecasting & Analysis Engine"):
        st.markdown("""
        **AI Engine Role:** Assist business teams in interpreting export market performance, growth and decline zones, and forecast generation.

        **Input:** Historical Sales Data

        **Output:**  Sales Forecast Generation, Sales Growth Computations
        """)
            
    with st.expander("📋 Generate Sales Forecast"):
        st.markdown("""
        Generate Sales forecast using historical sales Data Using FOUNDATIONAL SALES FORECAST AI MODEL.
        """)

        st.subheader("🔮 Sales Forecast for Next 2 Quarters")

        # Step 1: Identify next two quarters dynamically
        future_quarters = forecast_df['Quarter'].unique()
        future_quarters.sort()  # Ensure proper chronological order
        future_quarters = [q for q in future_quarters if q not in sales_df['Quarter'].unique()]
        
        # Take only the first 2 future quarters
        next_two_quarters = future_quarters[:2]
        
        if len(next_two_quarters) == 0:
            st.info("No future forecast quarters available in the dataset.")
        else:
            # Step 2: Filter forecast for next 2 quarters
            next_forecast = forecast_df[forecast_df['Quarter'].isin(next_two_quarters)]
            
            # Step 3: Aggregate by Country, Quarter, and Model
            forecast_summary = (
                next_forecast
                .groupby(['Country', 'Quarter', 'Bike_Model'])['Predicted_Units']
                .sum()
                .reset_index()
                .rename(columns={'Predicted_Units': 'Forecast_Units'})
            )
            
            # Step 4: Sort by highest forecast
            forecast_summary = forecast_summary.sort_values('Forecast_Units', ascending=False)

            st.dataframe(forecast_summary)#.style.apply(highlight_top_models, axis=1))

        
    with st.expander("📋 Analysis Tab"):
        st.markdown("""
        This section displays key metrics and visual insights relevant to the selected analysis tab.  
        Use the filters above to interact with charts and explore specific patterns.
        """)

    # === Moved filter + graph section out of expander for better UX ===
        st.markdown("### 📊 Export Sales Performance (Past + Forecast)")
    
        # Create new column layout for filters
        col1, col2 = st.columns(2)
    
        with col1:
            select_all_countries = st.checkbox("Select All Countries", value=True)
            countries = merged_df['Country'].unique()
            selected_country = st.multiselect(
                "Select Country",
                options=countries,
                default=countries if select_all_countries else None
            )
    
        with col2:
            select_all_models = st.checkbox("Select All Bike Models", value=True)
            models = merged_df['Bike_Model'].unique()
            selected_bike_model = st.multiselect(
                "Select Bike Model",
                options=models,
                default=models if select_all_models else None
            )
            # # Filter the merged_df based on selections
        merged_df['Performance_Type'] = merged_df['A_F'].map({'A': 'Actual', 'F': 'Forecast'})
        filtered_df = merged_df[
            (merged_df['Country'].isin(selected_country)) &
            (merged_df['Bike_Model'].isin(selected_bike_model))
        ]
    # --- Summarize data at Quarter + Performance_Type level ---
        summary_df = (
            filtered_df
            .groupby(['Quarter', 'Performance_Type'])['Sales_Units']
            .sum()
            .reset_index()
        )
        
        # Sort quarters correctly
        def quarter_sort_key(q):
            qtr, year = q.split('-')
            return int(year) * 4 + int(qtr[1])
        
        summary_df['Quarter_Sort'] = summary_df['Quarter'].apply(quarter_sort_key)
        summary_df = summary_df.sort_values('Quarter_Sort')
        
        # --- Plotly grouped bar chart ---
        fig = px.bar(
            summary_df,
            x='Quarter',
            y='Sales_Units',
            color='Performance_Type',
            barmode='group',
            color_discrete_map={'Actual': '#1f77b4', 'Forecast': '#ff7f0e'},
            text='Sales_Units'  # This shows one number per bar
        )
        
        fig.update_traces(
            textposition='outside',
            marker_line_width=0
        )
        
        fig.update_layout(
            title="Quarter-wise Export Sales Performance (Total Actual vs Forecast)",
            xaxis_title="Quarter",
            yaxis_title="Sales Units",
            legend_title_text="Performance Type",
            template="plotly_white",
            bargap=0.2,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False)
        )
        
        # --- Display chart ---
        st.plotly_chart(fig, use_container_width=True)

        
                
        st.subheader("📉 Growth vs Decline Zones")
        growth_df = sales_df.groupby(["Country", "Quarter"])["Sales_Units"].sum().reset_index()
        pivot = growth_df.pivot(index="Quarter", columns="Country", values="Sales_Units").fillna(0)
        growth_rate = pivot.pct_change().mean().sort_values(ascending=False).reset_index()
        growth_rate.columns = ["Country", "Avg Growth Rate"]
        st.dataframe(growth_rate)
        fig = px.bar(growth_rate, x="Country", y="Avg Growth Rate", color="Avg Growth Rate", title="Avg Quarterly Growth Rate (actuals)")
        st.plotly_chart(fig, use_container_width=True)

        
        
       
    
# ================= Tab 2: Distributor Analysis =================
with tab2:
    with st.expander("🤖 Distributor Evaluation Engine"):
        st.markdown("""
        **AI Engine Role:** It uses the CLUSTERING AI MODEL to seggregate the clusters of distributors. Assists business teams in interpreting distributor performance, and identify high potential distributors. 

        **Input:** Historical Sales Data, Distributor Data

        **Output:** Segmentation of distributors by their potential 
        """)

    

    with st.expander("📋 Distributor KPI Computation"):
        st.markdown("""
        Compute the Distributor KPIs based on the matrix explained below
        """)
        st.image("assets/KPI Compute.png", width=900)

        
        cluster_label = {0: "High Potential Distributor", 1: "Very Good Potential Distributor", 2: "Average Potential Distributor"}
        cluster_df['Cluster_Labels'] = cluster_df['Cluster'].map(cluster_label)
        st.subheader("🥇 KPIs for High Potential Distributors")
        high_df = cluster_df[cluster_df['Cluster_Labels'] == "High Potential Distributor"]
        available_countries = sorted(high_df['Country'].dropna().unique())
        selected_country = st.selectbox("🌍 Select Country", available_countries, key="high_potential_country")
        country_high_df = high_df[high_df['Country'] == selected_country]
        cols_to_show = ['Distributor_Name', 'Country', 'Cluster_Labels', 'KPI_Score', 'Engagement_Score', 'Lead_Time_Compliance', 'Return_Rate', 'Exclusive']
        st.dataframe(country_high_df[cols_to_show])
        
    with st.expander("📋 Distributor Segmentation"):
        st.markdown("""
        Each distributor is evaluated across multiple KPIs and engagement metrics.The clustering algorithm then groups them by potential and strategic importance.
        """)

        st.subheader("📦 Distributor Segmentation")

        cluster_summary = cluster_df['Cluster_Labels'].value_counts().reset_index()
        cluster_summary.columns = ['Cluster_Labels', 'Count']
        st.dataframe(cluster_summary)
        # fig = px.pie(cluster_summary, names='Cluster_Label', values='Count', title='Distributor Segmentation')
        fig = px.pie(
            cluster_summary,
            names="Cluster_Labels",
            values="Count",
            title="Distributor Segmentation by Potential",
            hole=0.4  # if you're using a donut
        )
        
        fig.update_traces(
            textinfo='percent+label',
            textposition='inside'
        )
        
        fig.update_layout(
            height=400,              # Shrinks total vertical height
            width=500,               # Optional: Shrinks horizontal spread
            margin=dict(t=40, b=40, l=10, r=10),  # Reduce outer padding
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.05,  # Push legend close to pie
                font=dict(size=10)
            )
        )

        
        st.plotly_chart(fig, use_container_width=True)

# ================= Tab 3: Competitor Analysis =================
with tab3:
    with st.expander("🤖 Competitor Analysis Engine"):
        st.markdown("""
        **AI Agent Role:** Scrapes web data, static interview data, social media ads etc, to develop insights using AI-NLP engine to get competitor dynamics.

        **Expected Input:** Competitor Market Share, Strengths, Weaknesses

        **Output:** Analysis & insights
        """)

        st.subheader("🥧 Overall Competitor Market Share")
        
        # Aggregate total market share
        overall_market_share = swot_df.groupby("Competitor")["Market_Share_%"].sum().reset_index()
        
        # Create pie chart
        fig = px.pie(
            overall_market_share,
            names="Competitor",
            values="Market_Share_%",
            title="🧭 Overall Market Share by Competitor",
            hole=0.3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        st.plotly_chart(fig, use_container_width=True)

        
    with st.expander("📋 Analysis Tab"):
        st.markdown("""
           Using NLP and text analytics, extract insights on product launches, pricing, promotional strategies, and market messaging. Generate a strengths-and-weaknesses map for each competitor, helping us understand where we can win.
            """)
     
        st.subheader("📊 Competitor strength & weakness map")

        st.image("assets/Suzuki_SWOT_Card.png", width=500)
        st.image("assets/TVS_SWOT_Card.png", width=500)
        st.image("assets/Yamaha_SWOT_Card.png", width=500)
        st.image("assets/Bajaj_Auto_SWOT_Card.png", width=500)
        st.image("assets/Honda_SWOT_Card.png", width=500)
    
# ================= Tab 4: Forecast Pricing Simulator =================
with tab4:
    with st.expander("🤖 Pricing Forecast Simulator"):
        st.markdown("""
        **AI Engine Role:** Apply ELASTICITY FEEDER AI MODEL to determine the price elasticity by country and model. Compute Competitive intensity by country. Generate the adjusted forecast taking these two computed values into account.

        **Input:** Historical pricing Data, historical sales

        **Output:**  Adjusted Sales Forecast units after applying the adjusted elasticity
        """)
    
    with st.expander("📋 Generate Price Elasticity"):
        st.markdown("""
        Compute price elasticity using historical pricing and applying the Log linear Regression model
        """)
        # --- Filter Columns to Display ---
        display_df = Elastic_df[["Country", "Bike_Model", "Elasticity"]]

        # --- Optional Sorting ---
        display_df = display_df.sort_values(by=["Country", "Bike_Model"])
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
        st.dataframe(display_df, use_container_width=False, height=400)

    with st.expander("📋 Generate Competitor Intensity"):
        st.markdown("""
        * Intensity Index is computed by weighing the 5 factors, summing them and normalizing the resulting value. It indicates how aggressive each brand is in the region,
        """)
        st.image("assets/Factors1.png", width=600)    
        st.write("")
        st.markdown("""
        * Computed competitor intensity by Country, calculated as an average of competitive intensity of top 3 competitors
        """)
        # --- Filter Columns to Display ---
        display_df = Elastic_df[["Country", "Comp_Intensity"]]
        display_df = display_df.drop_duplicates()

        # --- Optional Sorting ---
        display_df = display_df.sort_values(by=["Country"])

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
        st.dataframe(display_df, use_container_width=False, height=400)

    with st.expander("📋Pricing Simulator "):
        st.markdown("""
        Simulate Impact of price elasticity & competitor index on forecast
                    """)
        render_forecast_simulator()

# --- Tab 5: Power BI Dashboard ---
with tab5:
    # Theme adaptive slide: semi-transparent bg + dark text with shadow
    st.markdown(
        """
        <div style="
            background-color: rgba(255, 255, 255, 0.7);  /* visible in light & dark */
            backdrop-filter: blur(4px);
            padding: 25px;
            border-radius: 12px;
            border-left: 8px solid #ff6b2e;
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 25px;
            color: #222222;  /* dark text for light mode */
            text-shadow: 0 0 3px rgba(0,0,0,0.4);  /* readable on dark mode */
        ">
        <b>When we bring all three pillars together—</b><br><br>
        • <b>Predictive forecasting</b>,<br>
        • <b>Distributor prioritization</b>, and<br>
        • <b>Competitive intelligence</b>—<br><br>
        We create a <b>holistic GTM hub</b> that enables faster decision-making,
        sharper resource allocation, and stronger market outcomes.
        </div>
        """,
        unsafe_allow_html=True
    )

    # Power BI Button

    st.markdown(
        """
        <table>
            <tr>
                <td>
                    <a href="https://app.powerbi.com/groups/me/reports/bbd5d530-71e2-4050-96a3-58976484342e/a46caf4a9d9d882880b0?experience=power-bi">
                        <button style="
                            background-color:#ff6b2e;
                            color:white;
                            border:none;
                            padding:12px 28px;
                            border-radius:8px;
                            font-size:16px;
                            font-weight:bold;
                            cursor:pointer;
                        ">
                            Unified BI Dashboard
                        </button>
                    </a>
                </td>
                <td style="width: 20px;"></td> <!-- Spacer -->
                <td>
                    <a href="http://localhost:8502/" target="_blank">
                        <button style="
                            background-color:#ff6b2e;
                            color:white;
                            border:none;
                            padding:12px 28px;
                            border-radius:8px;
                            font-size:16px;
                            font-weight:bold;
                            cursor:pointer;
                        ">
                            Generate Export Performance PPT by Country
                        </button>
                    </a>
                </td>
            </tr>
        </table>
        """,
        unsafe_allow_html=True
    )




