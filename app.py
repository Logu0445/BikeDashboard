import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Bike Rental Dashboard",
    page_icon="🚴",
    layout="wide"
)

# Load and prepare data
@st.cache_data
def load_data():
    # Your CSV file path
    df = pd.read_csv("train.csv")

    
    # Convert datetime
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Create time-based columns
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['weekday'] = df['datetime'].dt.weekday
    df['hour'] = df['datetime'].dt.hour
    
    # Map season values
    season_map = {1: 'spring', 2: 'summer', 3: 'fall', 4: 'winter'}
    df['season'] = df['season'].map(season_map)
    
    # Create day period
    def get_period(hour):
        if 0 <= hour < 6:
            return 'night'
        elif 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 18:
            return 'afternoon'
        else:
            return 'evening'
    
    df['day_period'] = df['hour'].apply(get_period)
    
    return df

# Load the data
try:
    df = load_data()
    st.success("✅ Data loaded successfully!")
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.stop()

# Sidebar widgets
st.sidebar.title("📊 Dashboard Controls")
st.sidebar.markdown("---")

# Widget 1: Year Filter
years = st.sidebar.multiselect(
    "Select Years:",
    options=sorted(df['year'].unique()),
    default=sorted(df['year'].unique())
)

# Widget 2: Season Filter
seasons = st.sidebar.multiselect(
    "Select Seasons:",
    options=sorted(df['season'].unique()),
    default=sorted(df['season'].unique())
)

# Widget 3: Working Day Filter
day_type = st.sidebar.selectbox(
    "Day Type:",
    options=["All Days", "Working Days Only", "Non-Working Days Only"]
)

# Apply filters
filtered_df = df.copy()
filtered_df = filtered_df[filtered_df['year'].isin(years)]
filtered_df = filtered_df[filtered_df['season'].isin(seasons)]

if day_type == "Working Days Only":
    filtered_df = filtered_df[filtered_df['workingday'] == 1]
elif day_type == "Non-Working Days Only":
    filtered_df = filtered_df[filtered_df['workingday'] == 0]

# Main dashboard
st.title("🚴 Washington D.C. Bike Rental Dashboard")
st.markdown("Analyzing hourly bike rental patterns (2011-2012)")
st.markdown("---")

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total = filtered_df['count'].sum()
    st.metric("Total Rentals", f"{total:,}")

with col2:
    avg = filtered_df['count'].mean()
    st.metric("Avg Hourly Rentals", f"{avg:.0f}")

with col3:
    peak_hour = filtered_df.groupby('hour')['count'].mean()
    peak = peak_hour.idxmax() if not peak_hour.empty else "N/A"
    st.metric("Peak Hour", f"{peak}:00")

with col4:
    season_avg = filtered_df.groupby('season')['count'].mean()
    busy_season = season_avg.idxmax() if not season_avg.empty else "N/A"
    st.metric("Busiest Season", str(busy_season).title())

st.markdown("---")

# Plot 1: Hourly Pattern
st.subheader("📈 Hourly Rental Patterns")

fig1, ax1 = plt.subplots(figsize=(10, 4))
hourly_means = filtered_df.groupby('hour')['count'].mean()
hourly_means.plot(kind='line', ax=ax1, marker='o', linewidth=2, color='steelblue')
ax1.set_xlabel('Hour of Day')
ax1.set_ylabel('Average Rentals')
ax1.set_title('Average Rentals by Hour of Day')
ax1.grid(True, alpha=0.3)
ax1.set_xticks(range(0, 24, 2))

st.pyplot(fig1)

# Plot 2: Weather Impact
st.subheader("🌤️ Weather Impact Analysis")

fig2, ax2 = plt.subplots(figsize=(8, 4))
weather_means = filtered_df.groupby('weather')['count'].mean()
colors = ['lightgreen', 'lightblue', 'orange', 'red']
weather_means.plot(kind='bar', ax=ax2, color=colors[:len(weather_means)], alpha=0.7)
ax2.set_xlabel('Weather Category')
ax2.set_ylabel('Average Rentals')
ax2.set_title('Average Rentals by Weather')
ax2.set_xticklabels(['Clear', 'Mist/Cloudy', 'Light Rain', 'Heavy Rain'][:len(weather_means)], rotation=0)

st.pyplot(fig2)

# Plot 3: Day Period Analysis
st.subheader("⏰ Rentals by Time of Day")

fig3, ax3 = plt.subplots(figsize=(8, 4))
period_order = ['night', 'morning', 'afternoon', 'evening']
period_data = filtered_df.groupby('day_period')['count'].mean().reindex(period_order)
colors = ['navy', 'dodgerblue', 'skyblue', 'lightblue']
period_data.plot(kind='bar', ax=ax3, color=colors, alpha=0.7)
ax3.set_xlabel('Time of Day')
ax3.set_ylabel('Average Rentals')
ax3.set_title('Average Rentals by Time Period')
ax3.set_xticklabels(['Night (0-6)', 'Morning (6-12)', 'Afternoon (12-18)', 'Evening (18-24)'], rotation=45)

st.pyplot(fig3)

# Plot 4: Working vs Non-Working
st.subheader("🏢 Working vs Non-Working Day Patterns")

fig4, ax4 = plt.subplots(figsize=(10, 4))

# Create two columns for side-by-side display
col_left, col_right = st.columns(2)

with col_left:
    # Bar plot version
    fig4a, ax4a = plt.subplots(figsize=(8, 4))
    sns.barplot(data=filtered_df, x='day_period', y='count', hue='workingday',
                order=['night', 'morning', 'afternoon', 'evening'], ax=ax4a)
    ax4a.set_xlabel('Time of Day')
    ax4a.set_ylabel('Average Rentals')
    ax4a.set_title('Working vs Non-Working: Bar Chart')
    ax4a.legend(title='Day Type', labels=['Non-Working', 'Working'])
    st.pyplot(fig4a)

with col_right:
    # Line plot version
    fig4b, ax4b = plt.subplots(figsize=(8, 4))
    working_means = filtered_df[filtered_df['workingday'] == 1].groupby('hour')['count'].mean()
    nonworking_means = filtered_df[filtered_df['workingday'] == 0].groupby('hour')['count'].mean()
    
    ax4b.plot(working_means.index, working_means.values, label='Working Days', linewidth=2, color='darkgreen')
    ax4b.plot(nonworking_means.index, nonworking_means.values, label='Non-Working Days', linewidth=2, color='darkorange')
    ax4b.set_xlabel('Hour of Day')
    ax4b.set_ylabel('Average Rentals')
    ax4b.set_title('Working vs Non-Working: Line Chart')
    ax4b.legend()
    ax4b.grid(True, alpha=0.3)
    ax4b.set_xticks(range(0, 24, 2))
    st.pyplot(fig4b)

# Plot 5: Correlation Heatmap
st.subheader("🔗 Variable Correlations")

fig5, ax5 = plt.subplots(figsize=(10, 6))
numeric_cols = ['temp', 'atemp', 'humidity', 'windspeed', 'casual', 'registered', 'count']
corr_matrix = filtered_df[numeric_cols].corr()
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", 
            mask=mask, ax=ax5, center=0, square=True)
ax5.set_title('Correlation Matrix of Numerical Variables')

st.pyplot(fig5)

# Plot 6: Seasonal Analysis
st.subheader("🍂 Seasonal Patterns")

fig6, axes = plt.subplots(2, 2, figsize=(12, 8))
seasons_list = ['spring', 'summer', 'fall', 'winter']
colors = ['lightgreen', 'gold', 'orange', 'lightblue']

for idx, season in enumerate(seasons_list):
    row = idx // 2
    col = idx % 2
    
    season_data = filtered_df[filtered_df['season'] == season]
    if not season_data.empty:
        hourly_means = season_data.groupby('hour')['count'].mean()
        axes[row, col].plot(hourly_means.index, hourly_means.values, 
                           marker='o', linewidth=2, color=colors[idx])
    
    axes[row, col].set_title(f'Season: {season.title()}')
    axes[row, col].set_xlabel('Hour of Day')
    axes[row, col].set_ylabel('Mean Rentals')
    axes[row, col].grid(True, alpha=0.3)
    axes[row, col].set_xticks(range(0, 24, 4))

plt.tight_layout()
st.pyplot(fig6)

# Insights
st.markdown("---")
st.subheader("💡 Key Insights")

col_insight1, col_insight2 = st.columns(2)

with col_insight1:
    st.write("**📊 From Analysis:**")
    st.write("• Peak rental hours: 8 AM and 5-6 PM (commute times)")
    st.write("• Clear weather (Category 1) has highest rentals")
    st.write("• Afternoon period has highest average rentals")
    st.write("• Fall is typically the busiest season")

with col_insight2:
    st.write("**👥 User Behavior:**")
    st.write("• Registered users prefer working days")
    st.write("• Casual users prefer weekends and holidays")
    st.write("• Temperature shows strongest correlation with rentals")
    st.write("• Different hourly patterns for working vs non-working days")

# Data summary
with st.expander("📋 View Data Summary"):
    st.write(f"**Total records in filter:** {len(filtered_df):,}")
    st.write(f"**Date range:** {filtered_df['datetime'].min().date()} to {filtered_df['datetime'].max().date()}")
    st.write("**Basic statistics:**")
    st.dataframe(filtered_df[['temp', 'atemp', 'humidity', 'windspeed', 'count']].describe())

# Footer
st.markdown("---")

st.markdown("Dashboard created for Bike Rental Analysis | Data: Washington D.C. 2011-2012")


