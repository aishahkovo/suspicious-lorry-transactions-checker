import streamlit as st
import pandas as pd
import numpy as np

st.title("🚛 Suspicious Lorry Transaction Checker")

# File upload
uploaded_file = st.file_uploader("📤 Upload your CSV file", type=["csv"])

if uploaded_file:
    # Read the uploaded file
    df = pd.read_csv(uploaded_file)

    # Filter only WB01 entries
    df = df[df['WB In'] == 'WB01']

    # Combine and parse datetime
    df['check In Full'] = df['check In'].astype(str) + ' ' + df['check In Time'].astype(str)
    df['check Out Full'] = df['check Out'].astype(str) + ' ' + df['check Out Time'].astype(str)
    df['check_in_dt'] = pd.to_datetime(df['check In Full'], errors='coerce', dayfirst=True)
    df['check_out_dt'] = pd.to_datetime(df['check Out Full'], errors='coerce', dayfirst=True)

    # Sort by check-in time
    df = df.sort_values(by='check_in_dt').reset_index(drop=True)

    # Rule 1: Check-in gap < 2 minutes
    df['check_in_diff'] = df['check_in_dt'].diff().dt.total_seconds() / 60
    df['flag_check_in_gap'] = df['check_in_diff'] < 1

    # Rule 2: Trip duration out of average range
    df['trip_duration'] = (df['check_out_dt'] - df['check_in_dt']).dt.total_seconds() / 60
    avg_duration = df['trip_duration'].mean()
    tolerance = 0.4
    lower_bound = avg_duration * (1 - tolerance)
    upper_bound = avg_duration * (1 + tolerance)
    df['flag_duration_out_of_range'] = ~df['trip_duration'].between(lower_bound, upper_bound)

    # Rule 3: BTM difference > 1500kg more than 2x per lorry
    df['btm_diff'] = df.groupby('Lorry Number')['BTM'].diff().abs()
    df['btm_flag'] = df['btm_diff'] > 1500
    btm_counts = df.groupby('Lorry Number')['btm_flag'].sum().reset_index()
    btm_counts['flag_btm_variance'] = btm_counts['btm_flag'] > 1
    df = df.merge(btm_counts[['Lorry Number', 'flag_btm_variance']], on='Lorry Number', how='left')

    # Rule 4: Accepted weight repeated
    df['prev_accepted'] = df.groupby('Lorry Number')['Accepted Weight'].shift(1)
    df['flag_repeated_weight'] = df['Accepted Weight'] == df['prev_accepted']

    # Combine all flags
    df['suspicious'] = df[[
        'flag_check_in_gap',
        'flag_duration_out_of_range',
        'flag_btm_variance',
        'flag_repeated_weight'
    ]].any(axis=1)

    # Apply specific conditions:
    flagged_df = df[
        (df['flag_check_in_gap'] == True) |
        (df['flag_duration_out_of_range'] == False) |
        (df['flag_btm_variance'] == True) |
        (df['flag_repeated_weight'] == True)
    ].copy()

    # Select required columns
    flagged_df = flagged_df[[
        'RC ID', 'SAC ID', 'Driver Name', 'Lorry Number',
        'check_in_dt', 'check_out_dt', 'BTM', 'Accepted Weight',
        'flag_check_in_gap', 'flag_duration_out_of_range',
        'flag_btm_variance', 'flag_repeated_weight'
    ]]
    # Show results
    st.subheader("📋 List of Suspicious Records Detected 📋")

    if not flagged_df.empty:
        st.dataframe(flagged_df)
        st.success(f"{len(flagged_df)} suspicious records found.")
    else:
        st.warning("No records matched the suspicious filter criteria.")

    # Prepare CSV for download
    csv = flagged_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Download Result",
        data=csv,
        file_name="suspicious_lorry_transactions.csv",
        mime='text/csv'
    )
