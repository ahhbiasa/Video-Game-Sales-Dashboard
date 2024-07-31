import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import seaborn as sns
import pandas as pd
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
from streamlit_gsheets import GSheetsConnection

# ------------------------CONFIG------------------------------
st.set_page_config(
    page_title="Video Games Sales Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    .center {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    <img src="https://www.pngmart.com/files/7/Gaming-PNG-Transparent-Image-340x279.png" class="center">
    """,
    unsafe_allow_html=True
)

# ------------------------TITLE------------------------------
st.markdown("<h1 style='text-align: center;'> Video Game Sales Dashboard</h1>",
            unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'> By Muhammad Abhyasa Santoso</h3>",
            unsafe_allow_html=True)
st.markdown("---")

# ------------------------READ DATA FUNCTION------------------------------
# Function to load data from Google Sheets
def load_data():
    conn = st.connection("gsheet", type=GSheetsConnection)
    df = conn.read(
        spreadsheet=st.secrets.gsheet_promotion["spreadsheet"],
        worksheet=st.secrets.gsheet_promotion["worksheet"]
    )
    
    # Fill null values with 0
    df_filled = df.fillna(0)
    return df_filled

# --------------------------------MAIN------------------------------------
def main():
    st.sidebar.title("Navigation")
    
    st.sidebar.markdown("Select a feature:")
    page = st.sidebar.radio("Go to", ["Home", "Data Overview", "Profile Report", "Analysis", "About"])

    if page == "Home":
        st.subheader("Welcome to the Home Page")
        st.markdown('### Goals of this dashboard')
        st.write('''
            - Understanding the contents of the dataset in the **Data Overview** section.
            - Providing a profile report of the dataset in the **Profile Report** section.
            - Providing charts for data analysis purposes in the **Analysis** section.
            - Understanding & analyzing various sales (across regions, genres, platform, etc.).
            - Understanding the results of temporal analysis of the dataset (Yearly Sales Trends & Release Year Analysis).
            - Understanding the analysis of genre and publishers and their influence.
            - Providing a Coreelation and Regression Analysis using a correlation matrix.
        ''')
        st.info("Click on the top left arrow to opne the side bar")

# --------------------------------DATA OVERVIEW------------------------------------
    elif page == "Data Overview":
        st.subheader("Data Overview")
        st.markdown('''The original dataset is from kaggle and can be accessed via the link:
                    [Video Game Sales with Ratings](https://www.kaggle.com/datasets/rush4ratio/video-game-sales-with-ratings/data?select=Video_Games_Sales_as_at_22_Dec_2016.csv).''')
        st.markdown("---")
        data = load_data()
        
        st.info("Columns NA_Sales, EU_Sales, JP_Sales, Global_Sales, and Other_Sales are in **millions of units**")

        tabs = st.tabs(["Table View", "Summary Statistics"])

        with tabs[0]:
            st.dataframe(data)

        with tabs[1]:
            st.markdown("### Summary Statistics")
            st.write(data.describe())

# --------------------------------PROFILE REPORT------------------------------------
    elif page == "Profile Report":
        if st.button("Start Profile Report"):
            st.subheader("Profile Report")
            
            # Generate Report
            pr = ProfileReport(load_data())
            
            # Display to Streamlit
            st_profile_report(pr)
        else:
            st.info("Click the **Start Profile Report** button to generate the Profile Report")

# -----------------------------------ANALYSIS---------------------------------------
    elif page == "Analysis":
        st.subheader("Data Analysis")
        data = load_data()
        
        analysis_tabs = st.tabs(["Sales Analysis", "Temporal Analysis", "Genre and Publisher Analysis", "Correlation and Regression Analysis"])

        # --------------------------------SALES ANALYSIS TAB------------------------------------
        with analysis_tabs[0]:
            st.markdown("### Sales Analysis")
            
            st.markdown("---")
            
            # -----Interactive controls-----
            publisher = st.selectbox('Select Publisher', data['Publisher'].unique())
            genres = st.multiselect('Select Genres', data['Genre'].unique(), default=data['Genre'].unique())
            min_year, max_year = int(data['Year_of_Release'].min()), int(data['Year_of_Release'].max())
            year_range = st.slider('Select Year Range', min_year, max_year, (min_year, max_year))
            
            st.markdown("---")

            # -----Filter data based on user inputs-----
            filtered_data = data[(data['Publisher'] == publisher) & (data['Genre'].isin(genres)) & 
                                (data['Year_of_Release'] >= year_range[0]) & (data['Year_of_Release'] <= year_range[1])]

            # -----Melt the data for regional sales-----
            melted_data = filtered_data.melt(
                id_vars=['Publisher'],
                value_vars=['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales'],
                var_name='Region',
                value_name='Sales'
            )

            # -----Plotting all regional sales from a publisher in a single bar chart-----
            regional_sales_sum = melted_data.groupby('Region')['Sales'].sum().reset_index()
            regional_sales_chart = alt.Chart(regional_sales_sum).mark_bar(color='cyan').encode(
                x=alt.X('Region:N', sort='-y'),
                y=alt.Y('Sales:Q', sort='-x'),
                tooltip=['Region', 'Sales']
            ).properties(
                title='Sum of Sales by Region'
            )
            st.altair_chart(regional_sales_chart, use_container_width=True)
            
            st.markdown("---")
            
            # -----Sales by Platform-----
            platform_sales = data.groupby('Platform')['Global_Sales'].sum().nlargest(10).reset_index()
            
            st.markdown("#### Sales by Platform")
            platform_sales_chart = alt.Chart(platform_sales).mark_bar(color='gold').encode(
                x=alt.X('Platform:N', sort='-y'),
                y=alt.Y('sum(Global_Sales):Q', sort='-x'),
                tooltip=['Platform', 'sum(Global_Sales)']
            ).properties(
                title='Total Sales by Platform'
            )
            st.altair_chart(platform_sales_chart, use_container_width=True)
            
            st.markdown("---")
            
            # -----Global Sales Over the Years-----
            sales_trend_chart = alt.Chart(data).mark_line(color='orange').encode(
                x='Year_of_Release:O',
                y='sum(Global_Sales):Q',
                tooltip=['Year_of_Release', 'sum(Global_Sales)']
            ).properties(
                title='Global Sales Over the Years'
            )
            st.altair_chart(sales_trend_chart, use_container_width=True)

        # --------------------------------TEMPORAL ANALYSIS TAB------------------------------------
        with analysis_tabs[1]:
            st.markdown("### Temporal Analysis")

            # -----Filtering out unrealistic years (keeping only years between 1980 and 2023)-----
            valid_years_data = data[(data['Year_of_Release'] >= 1980) & (data['Year_of_Release'] <= 2023)]

            # -----Yearly Sales Trends-----
            st.markdown("#### Yearly Sales Trends")
            yearly_sales_chart = alt.Chart(valid_years_data).mark_line(color='magenta').encode(
                x='Year_of_Release:O',
                y='sum(Global_Sales):Q',
                tooltip=['Year_of_Release', 'sum(Global_Sales)']
            ).properties(
                title='Yearly Global Sales Trends'
            )
            st.altair_chart(yearly_sales_chart, use_container_width=True)
            
            st.markdown("---")

            # -----Release Year Analysis-----
            st.markdown("#### Release Year Analysis")
            release_year_chart = alt.Chart(valid_years_data).mark_bar(color='violet').encode(
                x='Year_of_Release',
                y='count()',
                tooltip=['Year_of_Release', 'count()']
            ).properties(
                title='Number of Games Released Each Year'
            )
            st.altair_chart(release_year_chart, use_container_width=True)

        # --------------------------------GENRE AND DEVELOPER ANALYSIS TAB------------------------------------
        with analysis_tabs[2]:
            st.markdown("### Genre and Publisher Analysis")

            # -----Melt the data for regional sales and group by Genre and Region-----
            melted_data = data.melt(
                id_vars=['Genre'],
                value_vars=['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales'],
                var_name='Region',
                value_name='Sales'
            )

            # -----Calculate the sum of sales for each genre and region-----
            grouped_sales = melted_data.groupby(['Genre', 'Region'])['Sales'].sum().reset_index()

            # -----Get the top 5 genres per region-----
            top_genres_per_region = grouped_sales.groupby('Region').apply(lambda x: x.nlargest(5, 'Sales')).reset_index(drop=True)

            # -----Region selection-----
            region_options = grouped_sales['Region'].unique().tolist()
            selected_region = st.selectbox('Select a Region', region_options)

            # -----Filter data based on the selected region-----
            filtered_data = top_genres_per_region[top_genres_per_region['Region'] == selected_region]

            # -----Create a bar chart sorted by sales-----
            bar_chart = alt.Chart(filtered_data).mark_bar().encode(
                x=alt.X('Genre:N', sort=alt.EncodingSortField(field='Sales', order='descending')),
                y=alt.Y('Sales:Q'),
                color='Genre:N',
                tooltip=['Genre', 'Sales']
            ).properties(
                title=f'Top 5 Genres in {selected_region}',
                width=600
            ).configure_axis(
                labelAngle=0
            )

            st.altair_chart(bar_chart, use_container_width=True)
            
            st.markdown("---")
            
            # -----Top 5 Publishers-----
            top_publishers = data.groupby('Publisher')['Global_Sales'].sum().nlargest(5).reset_index()

            top_publishers_chart = alt.Chart(top_publishers).mark_bar(color='lightblue').encode(
                x=alt.X('Publisher:N', sort='-y'),  # ---Sort publishers based on Global_Sales in descending order---
                y=alt.Y('Global_Sales:Q', sort='-x'),  # ---Sort by Global_Sales in descending order---
                tooltip=['Publisher', 'Global_Sales']
            ).properties(
                title='Top 5 Publishers by Global Sales'
            )

            st.altair_chart(top_publishers_chart, use_container_width=True)
            
            st.markdown("---")
            
            # -----Genre Popularity-----
            genre_sales = data.groupby('Genre')['Global_Sales'].sum().nlargest(5).reset_index()
            
            st.markdown("#### Genre Popularity")
            genre_sales_chart = alt.Chart(genre_sales).mark_bar(color='steelblue').encode(
                x=alt.X('Genre:N', sort='-y'), 
                y=alt.Y('Global_Sales:Q', sort='-x'), 
                tooltip=['Genre', 'Global_Sales']
            ).properties(
                title='Global Sales by Genre'
            )
            st.altair_chart(genre_sales_chart, use_container_width=True)
            
            st.markdown("---")

            # -----Developer Performance-----
            developer_sales = data.groupby('Publisher')['Global_Sales'].sum().nlargest(5).reset_index()
            
            st.markdown("#### Developer Performance")
            developer_sales_chart = alt.Chart(developer_sales).mark_bar(color='teal').encode(
                x=alt.X('Publisher:N', sort='-y'),  
                y=alt.Y('Global_Sales:Q', sort='-x'),  
                tooltip=['Publisher', 'Global_Sales']
            ).properties(
                title='Global Sales by Developer'
            ).transform_filter(
                alt.datum.Developer != ''
            )
            st.altair_chart(developer_sales_chart, use_container_width=True)

        # --------------------------------CORRELATION AND REGRESSION TAB------------------------------------
        with analysis_tabs[3]:
            st.markdown("### Correlation and Regression Analysis")

            # -----Compute the correlation matrix-----
            corr_data = data[['Global_Sales', 'NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales', 'Year_of_Release']].corr()

            # -----Plot the correlation matrix-----
            plt.figure(figsize=(10, 8))
            sns.heatmap(corr_data, annot=True, cmap='coolwarm', fmt='.2f')
            plt.title('Correlation Matrix')
            st.pyplot(plt)
            
            st.markdown("---")

# ------------------------------------ABOUT--------------------------------------
    elif page == "About":
        st.subheader("About")
        st.write('''This dashboard is designed to facilitate data analysis on a videogame dataset. 
                 It offers a variety of charts and visualizations to help users explore and understand the data. 
                 The dashboard leverages Python libraries such as Pandas and NumPy for data manipulation and analysis, 
                 and uses Streamlit to provide interactive features for an engaging user experience. 
                 The dataset is dynamically connected via Google Sheets using the st-gsheets-connection package, 
                 ensuring that the data is always up-to-date and easily accessible.''')

if __name__ == "__main__":
    main()
