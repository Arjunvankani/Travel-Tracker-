import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="🏍️ EcoRide Travel Tracker",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .day-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .no-travel-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    
    .stNumberInput > div > div > input {
        background-color: #f8f9fa;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Function to calculate emissions based on transport type
def calculate_emissions_and_cost(distance, transport_type):
    """Calculate cost and emissions based on transport type and distance"""
    
    # Emission factors (grams CO2 per km)
    emission_factors = {
        "🏍️ Motorcycle/Scooter": 80,
        "🚗 Car (Petrol)": 120,
        "🚗 Car (Diesel)": 100,
        "🚌 Bus": 40,
        "🚆 Train": 30,
        "🚕 Auto Rickshaw": 90,
        "🚲 Bicycle": 0,
        "🚶 Walking": 0,
        "✈️ Flight (Domestic)": 200,
        "🛵 Electric Scooter": 20
    }
    
    # Cost factors (rupees per km)
    cost_factors = {
        "🏍️ Motorcycle/Scooter": 3.5,
        "🚗 Car (Petrol)": 6.0,
        "🚗 Car (Diesel)": 4.5,
        "🚌 Bus": 2.0,
        "🚆 Train": 1.5,
        "🚕 Auto Rickshaw": 12.0,
        "🚲 Bicycle": 0,
        "🚶 Walking": 0,
        "✈️ Flight (Domestic)": 8.0,
        "🛵 Electric Scooter": 0.5
    }

    emission = distance * emission_factors.get(transport_type, 75)
    cost = distance * cost_factors.get(transport_type, 3.5)
    
    # ✅ Return values properly
    return cost, emission
    
# Initialize session state
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'name': '',
        'age': 0,
        'vehicle': '',
        'city': '',
        'weekly_data': {}
    }

if 'current_step' not in st.session_state:
    st.session_state.current_step = 'setup'

# Header
st.markdown("""
<div class="main-header">
    <h1>🏍️ EcoRide Travel Tracker</h1>
    <p>Track your daily travels, costs, and carbon footprint with style!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for user information
with st.sidebar:
    st.header("👤 User Profile")
    
    if st.session_state.current_step == 'setup':
        st.subheader("🚀 Get Started")
        name = st.text_input("📝 Enter your name:", value=st.session_state.user_data['name'])
        age = st.number_input("🎂 Enter your age:", min_value=16, max_value=100, value=st.session_state.user_data['age'] if st.session_state.user_data['age'] > 0 else 25)
        
        # Popular vehicle models for selection
        vehicle_models = [
            "Select your primary vehicle",
            "Honda Shine 125", "Hero Splendor Plus", "Bajaj Pulsar 125",
            "TVS Apache RTR 160", "Yamaha FZ-S", "Royal Enfield Classic 350",
            "KTM Duke 200", "Honda Activa 6G", "TVS Jupiter", "Suzuki Access 125",
            "Honda City", "Maruti Swift", "Hyundai i20", "Tata Nexon",
            "Custom Vehicle"
        ]
        
        vehicle_selection = st.selectbox("🚗 Choose your primary vehicle:", vehicle_models)
        
        if vehicle_selection == "Custom Vehicle":
            vehicle = st.text_input("Enter custom vehicle model:")
        elif vehicle_selection != "Select your primary vehicle":
            vehicle = vehicle_selection
        else:
            vehicle = ""
            
        city = st.text_input("🏙️ Enter your city:", value=st.session_state.user_data['city'])
        
        if st.button("✅ Save Profile", type="primary"):
            if name and age and vehicle and city:
                st.session_state.user_data.update({
                    'name': name,
                    'age': age,
                    'vehicle': vehicle,
                    'city': city
                })
                st.session_state.current_step = 'tracking'
                st.rerun()
            else:
                st.error("Please fill in all fields!")
    
    else:
        # Display user info
        st.success(f"👋 Welcome, {st.session_state.user_data['name']}!")
        st.info(f"🚗 {st.session_state.user_data['vehicle']}")
        st.info(f"🏙️ {st.session_state.user_data['city']}")
        st.info(f"🎂 Age: {st.session_state.user_data['age']}")
        
        if st.button("🔄 Edit Profile"):
            st.session_state.current_step = 'setup'
            st.rerun()

# Main content area
if st.session_state.current_step == 'setup':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem;">
            <h2>🚀 Let's Get Started!</h2>
            <p style="font-size: 1.2em; color: #666;">
                Please complete your profile in the sidebar to begin tracking your travels and carbon footprint.
            </p>
            <div style="font-size: 4em; margin: 2rem 0;">🌍</div>
            <p style="color: #888;">Track multiple transport modes • Calculate accurate emissions • Make eco-friendly choices</p>
        </div>
        """, unsafe_allow_html=True)

else:
    # Weekly tracking interface
    st.header("📅 Weekly Travel Tracker")
    
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Create tabs for each day
    tabs = st.tabs([f"📅 {day}" for day in days_of_week])
    
    for i, (tab, day) in enumerate(zip(tabs, days_of_week)):
        with tab:
            st.subheader(f"🌟 {day} Travel Log")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                traveled = st.radio(
                    f"Did you travel on {day}?",
                    ["No", "Yes"],
                    key=f"travel_{day}",
                    index=1 if day in st.session_state.user_data['weekly_data'] and st.session_state.user_data['weekly_data'][day]['traveled'] else 0
                )
                
                if traveled == "Yes":
                    destination = st.text_input(
                        "🎯 Where did you travel?",
                        key=f"dest_{day}",
                        value=st.session_state.user_data['weekly_data'].get(day, {}).get('destination', '')
                    )
                    
                    # Transport type selection
                    transport_options = [
                        "🏍️ Motorcycle/Scooter",
                        "🚗 Car (Petrol)",
                        "🚗 Car (Diesel)", 
                        "🚌 Bus",
                        "🚆 Train",
                        "🚕 Auto Rickshaw",
                        "🚲 Bicycle",
                        "🚶 Walking",
                        "✈️ Flight (Domestic)",
                        "🛵 Electric Scooter"
                    ]
                    
                    transport_type = st.selectbox(
                        "🚀 Which transport did you use?",
                        transport_options,
                        key=f"transport_{day}",
                        index=transport_options.index(st.session_state.user_data['weekly_data'].get(day, {}).get('transport_type', transport_options[0]))
                    )
                    
                    distance = st.number_input(
                        "📏 Distance traveled (km):",
                        min_value=0.0,
                        step=0.5,
                        key=f"dist_{day}",
                        value=float(st.session_state.user_data['weekly_data'].get(day, {}).get('distance', 0))
                    )
                    
                    trip_type = st.radio(
                        "🔄 Trip Type:",
                        ["One-way", "Round-trip"],
                        key=f"trip_{day}",
                        index=0 if st.session_state.user_data['weekly_data'].get(day, {}).get('trip_type', 'One-way') == 'One-way' else 1
                    )
                    
                    # Calculate actual distance based on trip type
                    actual_distance = distance * (2 if trip_type == "Round-trip" else 1)
                    
                    if distance > 0:
                        try:
                            cost, emission = calculate_emissions_and_cost(actual_distance, transport_type)
                            # Show live calculation
                            st.info(f"💡 **Live Calculation:** {actual_distance}km × {transport_type} = ₹{cost:.2f} cost, {emission:.0f}g CO₂")
                        except Exception as e:
                            st.error(f"Error in calculation: {str(e)}")
                            cost, emission = 0.0, 0.0
                    
                    if st.button(f"💾 Save {day} Data", key=f"save_{day}"):
                        if destination and distance > 0:
                            try:
                                cost, emission = calculate_emissions_and_cost(actual_distance, transport_type)
                                
                                st.session_state.user_data['weekly_data'][day] = {
                                    'traveled': True,
                                    'destination': destination,
                                    'transport_type': transport_type,
                                    'distance': distance,
                                    'actual_distance': actual_distance,
                                    'trip_type': trip_type,
                                    'cost': cost,
                                    'emission': emission
                                }
                                st.success(f"✅ {day} data saved successfully!")
                            except Exception as e:
                                st.error(f"Error saving data: {str(e)}")
                        else:
                            st.error("Please enter destination and distance!")
                else:
                    if day in st.session_state.user_data['weekly_data']:
                        del st.session_state.user_data['weekly_data'][day]
                    st.markdown("""
                    <div class="no-travel-card">
                        <h4>🌱 Great Choice!</h4>
                        <p>You preserved money and reduced carbon emissions!</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                if day in st.session_state.user_data['weekly_data'] and st.session_state.user_data['weekly_data'][day]['traveled']:
                    data = st.session_state.user_data['weekly_data'][day]
                    # Ensure all required fields exist with defaults
                    transport_type = data.get('transport_type', '🏍️ Motorcycle/Scooter')
                    trip_type = data.get('trip_type', 'One-way')
                    actual_distance = data.get('actual_distance', data.get('distance', 0))
                    
                    st.markdown(f"""
                    <div class="day-card">
                        <h4>📊 {day} Summary</h4>
                        <p><strong>🎯 Destination:</strong> {data['destination']}</p>
                        <p><strong>🚀 Transport:</strong> {transport_type}</p>
                        <p><strong>📏 Distance:</strong> {data['distance']} km ({trip_type})</p>
                        <p><strong>📍 Total Distance:</strong> {actual_distance} km</p>
                        <p><strong>💰 Cost:</strong> ₹{data['cost']:.2f}</p>
                        <p><strong>🌫️ CO₂:</strong> {data['emission']:.0f}g</p>
                    </div>
                    """, unsafe_allow_html=True)

    # Weekly Summary Section
    if st.session_state.user_data['weekly_data']:
        st.markdown("---")
        st.header("📈 Weekly Summary & Analytics")
        
        # Calculate totals with error handling
        total_distance = 0
        total_cost = 0
        total_emission = 0
        travel_days = 0
        
        for day_data in st.session_state.user_data['weekly_data'].values():
            if day_data.get('traveled', False):
                total_distance += day_data.get('actual_distance', day_data.get('distance', 0))
                total_cost += day_data.get('cost', 0)
                total_emission += day_data.get('emission', 0)
                travel_days += 1
        
        # Transport mode analysis with error handling
        transport_usage = {}
        for day_data in st.session_state.user_data['weekly_data'].values():
            if day_data.get('traveled', False):
                transport = day_data.get('transport_type', '🏍️ Motorcycle/Scooter')
                if transport not in transport_usage:
                    transport_usage[transport] = {'distance': 0, 'cost': 0, 'emission': 0, 'trips': 0}
                transport_usage[transport]['distance'] += day_data.get('actual_distance', day_data.get('distance', 0))
                transport_usage[transport]['cost'] += day_data.get('cost', 0)
                transport_usage[transport]['emission'] += day_data.get('emission', 0)
                transport_usage[transport]['trips'] += 1
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📏 Total Distance</h3>
                <h2>{total_distance:.1f} km</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>💰 Total Cost</h3>
                <h2>₹{total_cost:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🌫️ CO₂ Emission</h3>
                <h2>{total_emission/1000:.2f} kg</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🗓️ Travel Days</h3>
                <h2>{travel_days}/7</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Daily distance chart
            chart_data = []
            for day in days_of_week:
                if day in st.session_state.user_data['weekly_data'] and st.session_state.user_data['weekly_data'][day]['traveled']:
                    chart_data.append({
                        'Day': day,
                        'Distance': st.session_state.user_data['weekly_data'][day]['actual_distance'],
                        'Cost': st.session_state.user_data['weekly_data'][day]['cost'],
                        'Emission': st.session_state.user_data['weekly_data'][day]['emission'],
                        'Transport': st.session_state.user_data['weekly_data'][day]['transport_type']
                    })
            
            if chart_data:
                df = pd.DataFrame(chart_data)
                
                fig = px.bar(df, x='Day', y='Distance', 
                           title='📏 Daily Distance Traveled',
                           color='Transport',
                           hover_data=['Cost', 'Emission'])
                fig.update_layout(showlegend=True)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if chart_data:
                # Transport mode distribution
                transport_df = pd.DataFrame.from_dict(transport_usage, orient='index')
                transport_df.reset_index(inplace=True)
                transport_df.rename(columns={'index': 'Transport'}, inplace=True)
                
                fig = px.pie(transport_df, values='distance', names='Transport',
                           title='🚀 Distance by Transport Mode')
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
        
        # Transport comparison section
        st.subheader("🚀 Transport Mode Analysis")
        if transport_usage:
            transport_df = pd.DataFrame.from_dict(transport_usage, orient='index')
            transport_df.reset_index(inplace=True)
            transport_df.rename(columns={'index': 'Transport Mode'}, inplace=True)
            
            # Display transport comparison table
            st.dataframe(
                transport_df.style.format({
                    'distance': '{:.1f} km',
                    'cost': '₹{:.2f}',
                    'emission': '{:.0f}g',
                    'trips': '{:.0f}'
                }),
                use_container_width=True
            )
            
            # Best and worst performers
            if len(transport_df) > 1:
                col1, col2 = st.columns(2)
                with col1:
                    eco_friendly = transport_df.loc[transport_df['emission'].idxmin()]
                    st.success(f"🌱 **Most Eco-Friendly:** {eco_friendly['Transport Mode']} ({eco_friendly['emission']:.0f}g CO₂)")
                
                with col2:
                    cost_effective = transport_df.loc[transport_df['cost'].idxmin()]
                    st.info(f"💰 **Most Cost-Effective:** {cost_effective['Transport Mode']} (₹{cost_effective['cost']:.2f})")
        
        # Environmental impact section
        st.subheader("🌍 Environmental Impact")
        
        trees_equivalent = total_emission / 22000  # Rough estimate: 1 tree absorbs ~22kg CO2/year
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌳 Trees needed to offset", f"{trees_equivalent:.2f}", help="Trees needed to absorb the CO₂ you generated")
        with col2:
            car_equivalent = total_emission / 120  # Average car emits ~120g CO2/km
            st.metric("🚗 Equivalent car km", f"{car_equivalent:.1f}", help="Equivalent distance if driven by car")
        with col3:
            saved_emission = (7 - travel_days) * 10 * 125  # Assuming 10km average if traveled every non-travel day
            st.metric("💚 CO₂ Saved (g)", f"{saved_emission:.0f}", help="CO₂ saved by not traveling on rest days")
        
        # Data export
        st.subheader("📤 Export Data")
        if st.button("📊 Download Weekly Report"):
            report_data = {
                'user_info': {
                    'name': st.session_state.user_data['name'],
                    'vehicle': st.session_state.user_data['vehicle'],
                    'city': st.session_state.user_data['city']
                },
                'weekly_summary': {
                    'total_distance_km': total_distance,
                    'total_cost_rs': total_cost,
                    'total_emission_g': total_emission,
                    'travel_days': travel_days
                },
                'daily_data': st.session_state.user_data['weekly_data']
            }
            
            st.download_button(
                label="📁 Download JSON Report",
                data=json.dumps(report_data, indent=2),
                file_name=f"{st.session_state.user_data['name']}_travel_report.json",
                mime="application/json"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🌱 Made with ❤️ to promote eco-friendly transportation choices</p>
    <p>💡 Tip: Consider using public transport or cycling to reduce your carbon footprint!</p>
</div>
""", unsafe_allow_html=True)