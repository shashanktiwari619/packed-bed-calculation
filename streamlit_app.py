import streamlit as st
import math

st.set_page_config(
    page_title="Packed Bed Reactor Calculator",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    .section-header {
        color: #34495E;
        border-bottom: 2px solid #3498DB;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .heat-transfer-box {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">Packed Bed Reactor Calculator</h1>', unsafe_allow_html=True)

# Input section
col1, col2 = st.columns(2)

with col1:
    st.markdown('<h3 class="section-header">Geometry Parameters</h3>', unsafe_allow_html=True)
    
    col_diameter = st.number_input(
        "Column Diameter (m)",
        min_value=0.1,
        value=1.2,
        step=0.1,
        help="Diameter of the packed bed column"
    )
    
    bed_height = st.number_input(
        "Bed Height (m)",
        min_value=0.1,
        value=5.6,
        step=0.1,
        help="Height of the packed bed"
    )
    
    pellet_diameter = st.number_input(
        "Pellet Diameter (mm)",
        min_value=0.1,
        value=10.0,
        step=0.1,
        help="Diameter of spherical pellets"
    )
    
    voidage = st.number_input(
        "Interparticle Voidage",
        min_value=0.01,
        max_value=0.99,
        value=0.3778,
        step=0.001,
        format="%.4f",
        help="Void fraction between pellets"
    )
    
    velocity = st.number_input(
        "Superficial Fluid Velocity (m/s)",
        min_value=0.001,
        value=0.146,
        step=0.01,
        format="%.3f",
        help="Fluid velocity through empty column"
    )

with col2:
    st.markdown('<h3 class="section-header">Fluid Properties</h3>', unsafe_allow_html=True)
    
    fluid_density = st.number_input(
        "Fluid Density (kg/m³)",
        min_value=0.1,
        value=36.26,
        step=1.0
    )
    
    viscosity = st.number_input(
        "Fluid Dynamic Viscosity (Pa.s)",
        min_value=1e-7,
        value=3.11e-5,
        step=1e-6,
        format="%.2e"
    )
    
    fluid_conductivity = st.number_input(
        "Fluid Thermal Conductivity (W/m.K)",
        min_value=0.001,
        value=0.05,
        step=0.01
    )
    
    fluid_heat_capacity = st.number_input(
        "Fluid Specific Heat Capacity (J/kg.K)",
        min_value=100.0,
        value=1140.1,
        step=10.0
    )
    
    st.markdown('<h3 class="section-header">Steel Properties</h3>', unsafe_allow_html=True)
    
    steel_conductivity = st.number_input(
        "Steel Thermal Conductivity (W/m.K)",
        min_value=1.0,
        value=62.3,
        step=1.0
    )
    
    steel_heat_capacity = st.number_input(
        "Steel Specific Heat Capacity (J/kg.K)",
        min_value=100.0,
        value=478.2,
        step=10.0
    )
    
    steel_density = st.number_input(
        "Steel Density (kg/m³)",
        min_value=1000.0,
        value=7750.0,
        step=100.0
    )

# Calculate button
if st.button("Calculate Results", use_container_width=True):
    try:
        # Convert pellet diameter from mm to m
        pellet_diam_m = pellet_diameter / 1000
        
        # Sphericity factor for spheres = 1
        sphericity = 1.0
        
        # Pressure Drop Calculation using Ergun Equation
        viscous_term = 150 * ((1 - voidage)**2 / (voidage**3 * (sphericity * pellet_diam_m)**2)) * viscosity * velocity
        inertial_term = 1.75 * ((1 - voidage) / (voidage**3 * (sphericity * pellet_diam_m))) * fluid_density * velocity**2
        pressure_gradient = viscous_term + inertial_term
        total_pressure_drop = pressure_gradient * bed_height
        
        # Common intermediate calculations
        Re_p = (fluid_density * velocity * pellet_diam_m) / viscosity
        Pr_f = (fluid_heat_capacity * viscosity) / fluid_conductivity

        # Wall Heat Transfer Coefficient Calculation (Li-Finlayson correlation)
        k_ratio = steel_conductivity / fluid_conductivity
        Nu_w = 0.057 * (Re_p**0.78) * (Pr_f**(1/3)) * ((col_diameter / pellet_diam_m)**0.12) * (k_ratio**0.12)
        h_w = (Nu_w * fluid_conductivity) / col_diameter

        # Particle-to-Fluid Heat Transfer Coefficient (Wakao-Kagei-Funazkri correlation)
        Nu_p = 2 + 1.1 * (Re_p**0.6) * (Pr_f**(1/3))
        h_sf = (Nu_p * fluid_conductivity) / pellet_diam_m
        
        # Display results
        st.markdown("---")
        st.markdown('<h2 class="section-header">Calculation Results</h2>', unsafe_allow_html=True)
        
        # Pressure Drop Results
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("### Pressure Drop (Ergun Equation)")
            st.markdown(f"""
            <div class="result-box">
                <p><strong>Viscous Term (Kozeny-Carman):</strong> {viscous_term:.2f} Pa·s/m</p>
                <p><strong>Inertial Term (Burke-Plummer):</strong> {inertial_term:.2f} Pa·s²/m²</p>
                <p><strong>Pressure Gradient (ΔP/L):</strong> {pressure_gradient:.2f} Pa/m</p>
                <p style='color: #21618C; font-size: 1.2em;'><strong>Total Pressure Drop (ΔP):</strong> {total_pressure_drop:.2f} Pa</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("Equation: ΔP/L = 150(1-ε)²/(ε³(φd)²) μv + 1.75(1-ε)/(ε³φd) ρv²")
        
        with col4:
            st.markdown("### Heat Transfer Coefficient")
            st.markdown(f"""
            <div class="result-box">
                <p><strong>Particle Reynolds Number (Reₚ):</strong> {Re_p:.2f}</p>
                <p><strong>Prandtl Number (Pr):</strong> {Pr_f:.3f}</p>
                <p><strong>Conductivity Ratio (kₛ/kf):</strong> {k_ratio:.2f}</p>
                <p><strong>Wall Nusselt Number (Nu_w):</strong> {Nu_w:.2f}</p>
                <p style='color: #C0392B; font-size: 1.2em;'><strong>Wall Heat Transfer Coefficient (h_w):</strong> {h_w:.2f} W/m²·K</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("Equation: Nu_w = h_wD_t/k_f = 0.057·Re_p^0.78·Pr_f^(1/3)·(D_t/d_p)^0.12·(k_s/k_f)^0.12")
         
        
        # Particle-to-Fluid Heat Transfer Results
        st.markdown("### Particle-to-Fluid Heat Transfer Coefficient")
        st.markdown(f"""
        <div class="heat-transfer-box">
            <p><strong>Particle Reynolds Number (Reₚ):</strong> {Re_p:.2f}</p>
            <p><strong>Prandtl Number (Pr):</strong> {Pr_f:.3f}</p>
            <p><strong>Particle Nusselt Number (Nu_p):</strong> {Nu_p:.2f}</p>
            <p style='color: #E67E22; font-size: 1.2em;'><strong>Particle-to-Fluid Heat Transfer Coefficient (h_sf):</strong> {h_sf:.2f} W/m²·K</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.caption("Wakao-Kagei-Funazkri Correlation: Nu_p = h_sf·d_p/k_f = 2 + 1.1·Re_p^0.6·Pr_f^(1/3)")

        
        # Summary
        st.markdown("### Summary")
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        with summary_col1:
            st.metric("Total Pressure Drop", f"{total_pressure_drop:.2f} Pa")
        with summary_col2:
            st.metric("Heat Transfer Coefficient", f"{h_w:.2f} W/m²·K")
        with summary_col3:
            st.metric("Particle-Fluid h (h_sf)", f"{h_sf:.2f} W/m²·K"

        # Comparison of heat transfer coefficients
        st.markdown("### 🔍 Heat Transfer Coefficients Comparison")
        st.info(f"""
        - **Wall Heat Transfer Coefficient (h_w)**: {h_w:.2f} W/m²·K  
          *(Heat transfer between fluid and column wall)*
        
        - **Particle-to-Fluid Heat Transfer Coefficient (h_sf)**: {h_sf:.2f} W/m²·K  
          *(Heat transfer between fluid and pellet surfaces)*
        
        **Note**: These represent different physical phenomena in the packed bed system.
        """)
            
    except Exception as e:
        st.error(f"Error in calculation: {str(e)}")
        st.info("Please check that all input values are valid and non-zero.")


# """
# # Instructions for deployment
# with st.expander("How to Deploy and Share"):
#     st.markdown("""
#     ### Deploy on Streamlit Community Cloud (Free)
    
#     1. **Save this code** as `packed_bed_calculator.py`
#     2. **Create account** at [streamlit.io/cloud](https://streamlit.io/cloud)
#     3. **Connect your GitHub** repository
#     4. **Deploy the app** - it will give you a public URL like:
#        `https://yourname-packed-bed-calculator.streamlit.app/`
    
#     ### Required packages:
#     ```bash
#     pip install streamlit
#     ```
    
#     ### Run locally:
#     ```bash
#     streamlit run packed_bed_calculator.py
#     ```
    
#     Then share the generated URL with others! 
#     """)

# # Footer
# st.markdown("---")
# st.caption("Developed for Packed Bed Reactor Calculations | Uses Ergun Equation and Li-Finlayson Correlation")

# """
