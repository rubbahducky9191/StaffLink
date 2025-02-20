import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

# Streamlit UI Configuration
st.set_page_config(page_title="Attendance Dashboard", layout="wide")

# App Title
st.title("📊 Employee Attendance Dashboard")

# Fetch Attendance Data from Supabase
def get_attendance():
    response = supabase.table("attendance_logs").select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

df = get_attendance()

# Display Attendance Data
st.subheader("Attendance Records")
st.dataframe(df)

# Attendance Form
st.subheader("Log Attendance")
employee_id = st.text_input("Employee ID")
clock_in = st.button("Clock In")
clock_out = st.button("Clock Out")

if clock_in:
    supabase.table("attendance_logs").insert({"employee_id": employee_id, "clock_in": "NOW()"}).execute()
    st.success("Clock-in recorded!")

if clock_out:
    supabase.table("attendance_logs").update({"clock_out": "NOW()"}).eq("employee_id", employee_id).execute()
    st.success("Clock-out recorded!")

# Summary Statistics
if not df.empty:
    st.subheader("Summary")
    total_employees = df["employee_id"].nunique()
    st.metric("Total Employees Logged", total_employees)

    # Convert clock-in and clock-out times to datetime
    df["clock_in"] = pd.to_datetime(df["clock_in"])
    df["clock_out"] = pd.to_datetime(df["clock_out"])
    df["Hours Worked"] = (df["clock_out"] - df["clock_in"]).dt.total_seconds() / 3600

    st.bar_chart(df.groupby("employee_id")["Hours Worked"].sum())
