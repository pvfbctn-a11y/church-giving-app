import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import matplotlib.pyplot as plt

# Connect to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Read existing data from the tab named 'GivingData'
df = conn.read(worksheet="GivingData")

# Sidebar for inputs
with st.sidebar:
    st.title("Admin Entry")
    budget = st.number_input("Annual Budget ($)", value=250000)
    weekly_goal = budget / 52
    
    st.divider()
    date = st.date_input("Sunday Date")
    amount = st.number_input("Amount Received ($)", min_value=0.0)
    
    if st.button("Save to Google Sheets"):
        new_data = pd.DataFrame([{"Week Date": str(date), "Amount": amount}])
        updated_df = pd.concat([df, new_data], ignore_index=True)
        conn.update(worksheet="GivingData", data=updated_df)
        st.success("Saved!")
        st.rerun()

# Logic for the Graphic
st.title("Weekly Giving Graphic")

if not df.empty:
    total_weeks = len(df)
    ytd_actual = df["Amount"].sum()
    ytd_goal = weekly_goal * total_weeks
    diff = ytd_actual - ytd_goal

    # Generate the Chart
    fig, ax = plt.subplots(figsize=(10, 5), dpi=200)
    fig.patch.set_facecolor('#ffffff')
    
    labels = ['YTD Budget Goal', 'YTD Actual Giving']
    values = [ytd_goal, ytd_actual]
    colors = ['#dee2e6', '#28a745' if diff >= 0 else '#dc3545']

    bars = ax.barh(labels, values, color=colors, height=0.6)
    
    # Clean up the look
    ax.set_title(f"Giving Status: Week {total_weeks} of 52", fontsize=18, pad=20, fontweight='bold')
    ax.spines[['top', 'right', 'bottom', 'left']].set_visible(False)
    ax.set_xticks([])
    
    # Add currency labels to bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
                f' ${width:,.0f}', va='center', fontsize=14, fontweight='bold')

    # Footer Status Text
    status_msg = f"{'Ahead of' if diff >= 0 else 'Behind'} Budget by ${abs(diff):,.0f}"
    plt.figtext(0.5, 0.05, status_msg, ha="center", fontsize=14, fontweight='bold', color=colors[1])

    st.pyplot(fig)
    
    # Download Button
    import io
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    st.download_button(
        label="Download Graphic for Mailchimp",
        data=buf.getvalue(),
        file_name=f"Sunday_Giving_Week_{total_weeks}.png",
        mime="image/png"
    )
else:
    st.info("Add your first week of giving in the sidebar to generate the graphic!")
