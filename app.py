import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Automobile Data Analysis", layout="wide")

@st.cache_data
def load_automobile_data():
    df = pd.read_csv('Automobile.csv')
   
    df['horsepower'] = pd.to_numeric(df['horsepower'], errors='coerce')
    df = df.dropna(subset=['horsepower'])

    df['full_year'] = df['model_year'] + 1900
    return df

try:
    df = load_automobile_data()
except FileNotFoundError:
    st.error("The Automobile.csv file was not found. Please make sure that it is in the same folder as the script.")
    st.stop()

st.title("Dashboard for analyzing vehicle characteristics")
st.markdown("Laboratory work no.12: Advanced interactivity")

st.sidebar.header("Data Filters")

all_origins = df['origin'].unique().tolist()
selected_origins = st.sidebar.multiselect("Region of origin:", options=all_origins, default=all_origins)

all_cylinders = sorted(df['cylinders'].unique().tolist())
selected_cylinders = st.sidebar.multiselect("Number of cylinders:", options=all_cylinders, default=all_cylinders)

filtered_df = df[
    (df['origin'].isin(selected_origins)) & 
    (df['cylinders'].isin(selected_cylinders))
]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total models", len(filtered_df))
m2.metric("Average consumption (MPG)", round(filtered_df['mpg'].mean(), 1))
m3.metric("Average power (HP)", int(filtered_df['horsepower'].mean()))
m4.metric("Cf. acceleration", round(filtered_df['acceleration'].mean(), 1))

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader(" Trend: Economy (MPG) by year")
    yearly_avg = filtered_df.groupby('full_year')['mpg'].mean().reset_index()
    fig_line = px.line(yearly_avg, x='full_year', y='mpg', 
                       labels={'full_year': 'Year of manufacture', 'mpg': 'Miles per Gallon (MPG)'},
                       markers=True, title="Improved cost-effectiveness over time")
    st.plotly_chart(fig_line, use_container_width=True)

with col2:
    st.subheader(" Share of cars by region")
    fig_donut = px.pie(filtered_df, names='origin', hole=0.5, 
                       title="Distribution of models in the sample")
    st.plotly_chart(fig_donut, use_container_width=True)

st.divider()
st.subheader("Detailed analysis (Drill-down)")

drill_col1, drill_col2 = st.columns([1, 2])

with drill_col1:
    st.info("Select the region to detail the cylinder data in the graph on the right.")
    selected_drill_origin = st.selectbox("Region for Drill-down:", options=selected_origins)
    drill_data = filtered_df[filtered_df['origin'] == selected_drill_origin]

with drill_col2:
    fig_bar = px.bar(
        drill_data.groupby('cylinders').size().reset_index(name='count'),
        x='cylinders', y='count', 
        title=f"Engine configurations in the region: {selected_drill_origin}",
        labels={'cylinders': 'Cylinders', 'count': 'Number of models'},
        color='cylinders'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.subheader(" The relationship between power and acceleration")
fig_scatter = px.scatter(
    filtered_df, x='horsepower', y='acceleration', 
    color='origin', size='weight', hover_name='name',
    labels={'horsepower': 'Лошадиные силы', 'acceleration': 'Ускорение'},
    title="Power vs Acceleration (point size = car weight)"
)
st.plotly_chart(fig_scatter, use_container_width=True)

if st.checkbox("Show the data table"):
    st.dataframe(filtered_df)