"""
Name: Xuewen Su
CS602: SN2
Data: Boston Crime Incident Reports 2021
URL:https://python-visualization.github.io/folium/modules.html
Description:
This program is designed to help readers get insights from the dataset by creating different kinds of visualizations.
First, a bar chart and two line charts are used to display the total number of crimes counted by Month, Day of Week, and District.
Second, the program creates a shooting report by District with a pie chart to display all the Offense Type of incidents.
Third, it includes a map to show the geographic distribution of all incidents.
"""
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import folium
from folium import plugins
import plotly.graph_objects as go
from pandas.api.types import CategoricalDtype #create a new category
import base64
from PIL import Image #insert image


#Bos. Location
BOS_LATITUDE = 42.361145
BOS_LONGTITUDE = -71.057083
datafile = "bostoncrime2021_7000_sample.csv"
datafile1 ='BostonPoliceDistricts.csv'

def read_data(datafile):
    data = pd.read_csv(datafile)
    df=pd.DataFrame(data)
    if datafile=='BostonPoliceDistricts.csv':
        df = df.rename(columns={ "District": "DISTRICT"})
        df.loc['12'] = 'External'#add External to the district
    return df
def merge_data(df,df1):
    df_merge=df.merge(df1)
    return df_merge

def countMonth(df):
    Count_month=df.groupby("MONTH")["INCIDENT_NUMBER"].count().reset_index()
    Count_month.rename(columns = {"INCIDENT_NUMBER": "Count of Incidents"},
          inplace=True)
    Count_month['MONTH'] = ['Jan','Feb', 'Mar', 'Apr.','May','June']
    Count_month.plot(kind="line",title='Monthly Summary',x="MONTH",y="Count of Incidents",xlabel='Month',ylabel='Total Number of Incidents',marker='o',color='g',rot=0)
    st.pyplot(plt)
    check=st.checkbox("Check here to see more details")
    if check:
        st.table(Count_month)

def countDay(df):
    df1=df.groupby("DAY_OF_WEEK")["INCIDENT_NUMBER"].count().reset_index()
    df1.rename(columns = {"INCIDENT_NUMBER": "Count of Incidents"},
          inplace=True)
    cat_day_of_week = CategoricalDtype(
    ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
    ordered=True
)
    df1['DAY_OF_WEEK'] = df1['DAY_OF_WEEK'].astype(cat_day_of_week)
    df1_sorted=df1.sort_values('DAY_OF_WEEK')
    df1_sorted.plot(kind="line",x='DAY_OF_WEEK',title='Incidents Summary By Day of Week',ylabel='Total Number of Incidents',marker='o',color='red',rot=70)
    st.pyplot(plt)

def countDistrict(df):
    Count_district=df.groupby("District Name")["INCIDENT_NUMBER"].count().reset_index()#reset_index() resets and provides the new index to the grouped by dataframe and makes them a proper dataframe structure
    Count_district.rename(columns = {"INCIDENT_NUMBER": "Count of Incidents"},
          inplace=True)
    Sorted=Count_district.sort_values(by=['Count of Incidents'],ascending=False)
    Sorted.plot(kind="bar",x="District Name",title='Incidents Summary By District',ylabel='Total Number of Incidents',color='cyan',rot=70,fontsize=8)
    st.pyplot(plt)
    check=st.checkbox("Check here to see more details")
    if check:
        st.table(Sorted)
def shooting(Name,df_merge):
    filer_shooting=df_merge[(df_merge.SHOOTING == 1) & (df_merge['District Name'] == f'{Name}')]#filer_shooting=df.query('SHOOTING==1','District Name==District')
    count=filer_shooting.groupby("OFFENSE_DESCRIPTION")["SHOOTING"].count().reset_index()
    fig = go.Figure(data=[go.Pie(labels=count['OFFENSE_DESCRIPTION'],
                                 values=count['SHOOTING'])])
    fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=15,
                      marker=dict(line=dict(color='#000000', width=2)))

    st.plotly_chart(fig)
    details=st.button("Click Here to view incidents details")
    if details:
        st.write(filer_shooting.sort_values('OFFENSE_DESCRIPTION').astype('object'))

#@st.cache(suppress_st_warning=True)
def mapping(zero_or_one,df):
    bos_map = folium.Map(location = [BOS_LATITUDE, BOS_LONGTITUDE], zoom_start = 12)
    incidents = plugins.MarkerCluster().add_to(bos_map)
    for shooting,lat, lng, label, in zip(df.SHOOTING,df.Lat, df.Long, df.OFFENSE_DESCRIPTION):
        if shooting==zero_or_one:
            folium.Marker(
                location=[lat, lng],
                icon=None,
                popup=label,
            ).add_to(incidents)
        else:
            folium.Marker(
                location=[lat, lng],
                icon=None,
                popup=label,
            ).add_to(incidents)
    bos_map.add_child(incidents)
    folium_static(bos_map)

#\Final Project\streamlit run project.py
def main():
    df=read_data(datafile)
    df1=read_data(datafile1)
    df_merge=merge_data(df,df1)
    st.sidebar.subheader("ABOUT")
    st.sidebar.write("Original data is derived from: https://data.boston.gov/")
    menu=st.sidebar.radio("Navigation",["Home Page","Dataset Preview","Summary Report","Boston Shooting Incidents","Boston Crime Map","Reference Page"])
    if menu=="Home Page":
        img = Image.open("BostonPic.webp")
        st.title("Analysis of 2021 Boston Crime Incidents")
        st.markdown("<h3 style='text-align: center; color: #DEB887;'>Xuewen Su</h3>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #E9967A;'>Bentley University</h4>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #E9967A;'>July 2021</h4>", unsafe_allow_html=True)
        st.image(img, width=700)
        st.text("(Citation:https://www.covesmart.com/blog/boston-crime-rate-is-boston-a-safe-city/)")
    if menu =="Dataset Preview":
        st.subheader("Data Preview-7000 Sample Records")
        st.write(df.astype('object'))
        coded_data = base64.b64encode(df.to_csv(index=False).encode()).decode()
        st.markdown(
            f'<a href="data:file/csv;base64,{coded_data}" download="data.csv">Download Data</a>',
            unsafe_allow_html=True
        )
    elif menu =="Summary Report":#Query 1
        st.subheader("Summary of the Crime Report")
        summary_mode = st.selectbox(
            'Summary Mode Selection: ',
            ('District Summary','Monthly Summary','Day of Week Summary')
        )
        if summary_mode =='Monthly Summary':
            st.write(f"{summary_mode} presents the total number of crime incidents happened in each month.")
            countMonth(df)
        elif summary_mode =='Day of Week Summary':
            st.write(f"{summary_mode} presents the total number of crime incidents happened in each day of week.")
            countDay(df)
        elif summary_mode =='District Summary':
            st.write(f"{summary_mode} presents the total number of crime incidents happened in each district")
            countDistrict(df_merge)
    elif menu =='Boston Shooting Incidents':#Query 2
        st.subheader("Shooting Incidents Report by District and Offense Type ")
        report_mode = st.selectbox(
            'Select ONE Boston Police District: ',
            (df_merge['District Name'].unique() )
        )
        for district in df_merge['District Name'].unique():
            if district==report_mode:
                shooting(Name=f'{district}',df_merge=df_merge)
    elif menu =='Boston Crime Map':#Query 3
        st.subheader("Map of Boston Incidents")
        selection=['ONLY Shooting Incidents','ONLY Non-shooting Incidents','Overall Incidents']
        map=st.radio("Your Selection:the map displays",
                     (selection))
        if map=='ONLY Shooting Incidents':
            mapping(1,df)
        elif map =='ONLY Non-shooting Incidents':
            mapping(0,df)
        else:
            mapping(3,df)
    elif menu=="Reference Page":
        st.title("Reference List")
        st.write('https://docs.streamlit.io/en/stable/')
        st.write('https://plotly.com/python/pie-charts/')
        st.write('https://plotly.com/python/pie-charts/')
        st.write('https://my.oschina.net/u/4678692/blog/4694741')
        st.write('https://codingfordata.com/8-simple-and-useful-streamlit-tricks-you-should-know/')
    st.sidebar.subheader('CONTACT')
    st.sidebar.write("Xuewen Su.Carol")
    st.sidebar.write("**Email**:su_xuew@bentley.edu")
    st.sidebar.write("**Connect on LinkedIn:**")
    st.sidebar.image("ImageQR.jpg", use_column_width=True)

main()
