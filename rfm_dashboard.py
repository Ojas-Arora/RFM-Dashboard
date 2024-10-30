import pandas as pd
import datetime as dt
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

# Load data
file_path = 'rfm_data.csv'  # Change this to the actual path if necessary
data = pd.read_csv(file_path)

# Convert PurchaseDate to datetime
data['PurchaseDate'] = pd.to_datetime(data['PurchaseDate'])

# Define reference date for recency calculation
reference_date = dt.datetime(2023, 7, 1)

# Calculate RFM metrics
rfm = data.groupby('CustomerID').agg({
    'PurchaseDate': lambda x: (reference_date - x.max()).days,
    'OrderID': 'count',
    'TransactionAmount': 'sum'
}).reset_index()

rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

# Filter out non-positive monetary values
rfm = rfm[rfm['Monetary'] > 0]

# Define RFM score thresholds
rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, ['1', '2', '3', '4'])
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, ['4', '3', '2', '1'])
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, ['4', '3', '2', '1'])

# Concatenate RFM score to a single RFM segment
rfm['RFM_Segment'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
rfm['RFM_Score'] = rfm[['R_Score', 'F_Score', 'M_Score']].sum(axis=1).astype(int)

# Define RFM segments
def rfm_segment(df):
    if df['RFM_Score'] >= 9:
        return 'Champions'
    elif df['RFM_Score'] >= 8:
        return 'Loyal Customers'
    elif df['RFM_Score'] >= 7:
        return 'Potential Loyalists'
    elif df['RFM_Score'] >= 6:
        return 'Recent Customers'
    elif df['RFM_Score'] >= 5:
        return 'Promising'
    elif df['RFM_Score'] >= 4:
        return 'Need Attention'
    elif df['RFM_Score'] >= 3:
        return 'At Risk'
    else:
        return 'Lost'

rfm['RFM_Segment'] = rfm.apply(rfm_segment, axis=1)

# Count of customers in each segment
segment_counts = rfm['RFM_Segment'].value_counts().reset_index()
segment_counts.columns = ['RFM_Segment', 'Count']

# Streamlit Dashboard
st.set_page_config(page_title="InsightSphere RFM", page_icon="🌐", layout="wide")

# Add custom CSS with animations
st.markdown("""
    <style>
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .stApp {
        background-image: url('https://wallpapers.com/images/high/white-color-background-ghw6e685ri75chj4.webp');
        background-size: cover;
        animation: fadeIn 2s ease-in;
    }

    .header {
        text-align: center;
    }

    .header h1 {
        font-size: 3em;
        color: #4b0082;
        animation: fadeIn 3s ease-in;
    }

    .header img {
        margin-top: -20px;
        width: 60px;
        animation: fadeIn 3s ease-in;
    }

    .segment {
        margin: 20px 0;
        text-align: center;
        color: purple;
        animation: fadeIn 3s ease-in;
    }

    .segment h3 {
        color: purple;
    }

    .segment p {
        color: purple;
    }
    .metric-container {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
        animation: fadeIn 2s ease-in;
    }

    .metric {
        text-align: center;
        background: #fff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        width: 200px;
        color: purple;
        animation: fadeIn 2s ease-in;
    }

    .metric h3 {
        color: #4b0082;
    }

    .metric p {
        font-size: 2em;
        color: black;
        margin: 0;
    }

    .plot-container {
        animation: fadeIn 3s ease-in;
    }

    .stButton>button {
        color: white !important; /* Ensure text color is always white */
        background: purple;
        width: 900px;
        padding: 10px 20px;
        border: 2px solid purple;
        border-radius: 5px;
        font-size: 1.5em;
        cursor: pointer;
        transition: background-color 0.3s ease;
        margin-left: 110px;
    }
    .center-button {
        display: flex;
        justify-content: center;
    }

    .stButton>button:hover {
        background-color: darkturquoise;
    }

    .stButton>button:active {
        background-color: darkturquoise;
    }

    .stSelectbox label {
        color: purple !important;
    }

    .stSelectbox select {
        color: purple !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class='header'>
    <h1>💡InsightSphere RFM</h1>
    <img src='https://img.icons8.com/fluency/48/000000/customer-insight.png'/>
    <p style="color:purple">Analyze your customer segments based on Recency, Frequency, and Monetary values</p>
</div>
""", unsafe_allow_html=True)

# Data Preview Button with Toggle
if 'data_preview' not in st.session_state:
    st.session_state.data_preview = False

if st.button('Data Preview'):
    st.session_state.data_preview = not st.session_state.data_preview

if st.session_state.data_preview:
    st.write(data)

# Metrics
total_customers = rfm['CustomerID'].nunique()
avg_recency = int(rfm['Recency'].mean())
avg_frequency = int(rfm['Frequency'].mean())
avg_monetary = int(rfm['Monetary'].mean())

st.markdown(f"""
<div class='metric-container'>
    <div class='metric'>
        <h3>Total Customers</h3>
        <p>{total_customers}</p>
    </div>
    <div class='metric'>
        <h3>Average Recency</h3>
        <p>{avg_recency}</p>
    </div>
    <div class='metric'>
        <h3>Average Frequency</h3>
        <p>{avg_frequency}</p>
    </div>
    <div class='metric'>
        <h3>Average Monetary Value</h3>
        <p>{avg_monetary}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Dropdown for analysis type
st.sidebar.title("Analysis Options")
analysis_type = st.sidebar.selectbox("Analyze customer segments based on RFM scores:", [
    "Comparison of RFM Segments",
    "RFM Value Segment Distribution",
    "Distribution of RFM Values within Customer Segment",
    "Correlation Matrix of RFM Values within Champions Segment"
])

# Plot based on selection
if analysis_type == "Comparison of RFM Segments":
    st.markdown("""
        <div class='segment'>
            <h3>Comparison of RFM Segments</h3>
            <p>See how many customers fall into each RFM segment.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Bar chart of segment counts
    fig_bar = px.bar(segment_counts, x='RFM_Segment', y='Count', title='Count of Customers in Each RFM Segment', color='RFM_Segment')
    fig_bar.update_layout(
    title={
        'text': 'Count of Customers in Each RFM Segment',
        'font': {'size': 24},  # Increase title font size
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
    xaxis_title={
        'text': 'RFM Segment',
        'font': {'size': 18, 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Count',
        'font': {'size': 18, 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
     legend_title={
        'text': 'RFM Segment',
        'font': {'size': 18, 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    },
    legend=dict(
        title_font=dict(size=18, family='Arial', color='black'),  # Legend title font size
        font=dict(size=16, family='Arial', color='black', weight='bold')  # Make legend text bold and increase size
    )
)
    fig_bar.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))
    fig_bar.update_xaxes(
    tickfont=dict(size=16, family='Arial', color='black', weight='bold'),
    )

     # Make the bar text bold (if necessary)
    fig_bar.update_traces(textfont=dict(size=16, family='Arial', color='black', weight='bold'))
    st.plotly_chart(fig_bar)

    # Pie chart of percentage distribution
    fig_pie = px.pie(segment_counts, values='Count', names='RFM_Segment', title='Percentage Distribution of Customers by RFM Segment')
    fig_pie.update_layout(
    title={
        'text': 'Percentage Distribution of Customers by RFM Segment',
        'font': {'size': 24, 'weight': 'bold'}  # Increase title font size and make it bold
    },
    legend_title={
        'text': 'RFM Segment',
        'font': {'size': 18, 'weight': 'bold'}  # Bold and larger size for legend title
    }
)
    fig_pie.update_traces(
    textfont=dict(size=16, family='Arial', color='black', weight='bold'),  # Bold and larger size for pie slice text
    marker=dict(line=dict(color='#000000', width=2))  # Optional: Customize the border of pie slices
)

    # Make sure "Champions" is also updated in the segment names
    fig_pie.for_each_trace(lambda t: t.update(name=t.name.title()))  # Title case for all names
    st.plotly_chart(fig_pie)

    # Histogram of RFM Scores
    fig_hist = px.histogram(rfm, x='RFM_Score', title='RFM Score Distribution', nbins=10, color='RFM_Score')
    fig_hist.update_layout(
    title={
        'text': 'RFM Score Distribution',
        'font': {'size': 24, 'weight': 'bold'}  # Increase title font size and make it bold
    },
    xaxis_title={
        'text': 'RFM Score',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Count',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
    legend_title={
        'text': 'RFM Score',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

# Update tick font sizes for axes
    fig_hist.update_xaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold for x-axis ticks
    fig_hist.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold for y-axis ticks

    # Make the bar text bold (if necessary)
    fig_hist.update_traces(textfont=dict(size=16, family='Arial', color='black', weight='bold'))
    fig_hist.update_traces(textfont=dict(size=20, family='Arial', color='black', weight='bold'))  # Adjust size for bar text
    st.plotly_chart(fig_hist)

    # Scatter plot example
    fig_scatter = px.scatter(rfm, x='Recency', y='Monetary', color='RFM_Segment', title='Scatter Plot of Recency vs Monetary')
    fig_scatter.update_layout(
    title={
        'text': 'Scatter Plot of Recency vs Monetary',
        'font': {'size': 24, 'weight': 'bold'}  # Increase title font size and make it bold
    },
    xaxis_title={
        'text': 'Recency',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Monetary',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
    legend_title={
        'text': 'RFM Segment',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

# Update tick font sizes for axes
    fig_scatter.update_xaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold for x-axis ticks
    fig_scatter.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold for y-axis ticks

    # Update marker text font sizes (if any) to be larger and bold
    fig_scatter.update_traces(marker=dict(size=10))  # Adjust marker size if needed
    fig_scatter.update_traces(textfont=dict(size=20, family='Arial', color='black', weight='bold'))  # Adjust size for point text
    st.plotly_chart(fig_scatter)

    # Box plot example
    fig_box = px.box(rfm, x='RFM_Segment', y='Monetary', color='RFM_Segment', title='Monetary Distribution by RFM Segment')
    # Update layout and formatting
    fig_box.update_layout(
    title={
        'text': 'Monetary Distribution by RFM Segment',
        'font': {'size': 24, 'weight': 'bold'}  # Increase title font size and make it bold
    },
    xaxis_title={
        'text': 'RFM Segment',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Monetary',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
    legend_title={
        'text': 'RFM Segment',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

    # Update tick font sizes for axes
    fig_box.update_xaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold for x-axis ticks
    fig_box.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold for y-axis ticks
    st.plotly_chart(fig_box)

elif analysis_type == "RFM Value Segment Distribution":
    st.markdown("""
        <div class='segment'>
            <h3>RFM Value Segment Distribution</h3>
            <p>Distribution of RFM scores among customers.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Histogram of RFM Scores
    fig_hist_rfm = px.histogram(rfm, x='RFM_Score', title='RFM Score Distribution', nbins=10, color='RFM_Score')
    fig_hist_rfm.update_layout(
    title={
        'text': 'RFM Score Distribution',
        'font': {'size': 24, 'weight': 'bold'}  # Increase title font size and make it bold
    },
    xaxis_title={
        'text': 'RFM Score',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Count',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
    legend_title={
        'text': 'RFM Score',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

    # Update tick font sizes for axes
    fig_hist_rfm.update_xaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold for x-axis ticks
    fig_hist_rfm.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold for y-axis ticks
    st.plotly_chart(fig_hist_rfm)

    # Box plot of Monetary values
    fig_box_rfm = px.box(rfm, x='RFM_Score', y='Monetary', color='RFM_Score', title='Monetary Distribution by RFM Score')
    fig_box_rfm.update_layout(
    title={
        'text': 'Monetary Distribution by RFM Score',
        'font': {'size': 24, 'weight': 'bold'}  # Increase title font size and make it bold
    },
    xaxis_title={
        'text': 'RFM Score',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Monetary Value',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
    legend_title={
        'text': 'RFM Score',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

# Update tick font sizes for axes
    fig_box_rfm.update_xaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold for x-axis ticks
    fig_box_rfm.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold for y-axis ticks
    st.plotly_chart(fig_box_rfm)

    # Scatter plot example
    fig_scatter_rfm = px.scatter(rfm, x='Frequency', y='Monetary', color='RFM_Score', title='Scatter Plot of Frequency vs Monetary')
    fig_scatter_rfm.update_layout(
    title={
        'text': 'Scatter Plot of Frequency vs Monetary',
        'font': {'size': 24, 'weight': 'bold'}  # Increase title font size and make it bold
    },
    xaxis_title={
        'text': 'Frequency',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Monetary Value',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
    legend_title={
        'text': 'RFM Score',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

# Update tick font sizes for axes
    fig_scatter_rfm.update_xaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold for x-axis ticks
    fig_scatter_rfm.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold for y-axis ticks
    st.plotly_chart(fig_scatter_rfm)

    # Pie chart example
    fig_pie_rfm = px.pie(segment_counts, values='Count', names='RFM_Segment', title='Percentage Distribution of Customers by RFM Segment')
    fig_pie_rfm.update_layout(
    title={
        'text': 'Percentage Distribution of Customers by RFM Segment',
        'font': {'size': 24, 'weight': 'bold'}  # Increase title font size and make it bold
    },
    legend_title={
        'text': 'RFM Segment',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

# Update text properties for the pie chart segments
    fig_pie_rfm.update_traces(textfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold text for pie segments
    st.plotly_chart(fig_pie_rfm)

    # Additional visualization
    fig_bar_rfm = px.bar(segment_counts, x='RFM_Segment', y='Count', title='Count of Customers in Each RFM Segment')
    fig_bar_rfm.update_layout(
    title={
        'text': 'Count of Customers in Each RFM Segment',
        'font': {'size': 24, 'weight': 'bold', 'family': 'Arial'},  # Increase title font size and make it bold
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
    xaxis_title={
        'text': 'RFM Segment',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Count',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
    legend_title={
        'text': 'RFM Segment',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

    # Update the y-axis tick font
    fig_bar_rfm.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold y-axis numbers

    # Update the bar text font
    fig_bar_rfm.update_traces(textfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold text for bars
    st.plotly_chart(fig_bar_rfm)

elif analysis_type == "Distribution of RFM Values within Customer Segment":
    st.markdown("""
        <div class='segment'>
            <h3>Distribution of RFM Values within Customer Segment</h3>
            <p>Analyze the distribution of Recency, Frequency, and Monetary values within a specific segment.</p>
        </div>
    """, unsafe_allow_html=True)
    
    segment = st.selectbox("Select RFM Segment:", rfm['RFM_Segment'].unique())
    segment_data = rfm[rfm['RFM_Segment'] == segment]
    st.markdown(f"<h4 style='color: purple;'>{segment} Segment</h4>", unsafe_allow_html=True)
   
    # Example with Recency distribution
    fig_recency = px.histogram(segment_data, x='Recency', title=f'Recency Distribution in {segment} Segment', nbins=10, color='Recency')
    fig_recency.update_layout(
    title={
        'text': f'Recency Distribution in {segment} Segment',
        'font': {'size': 24, 'weight': 'bold', 'family': 'Arial'},  # Increase title font size and make it bold
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
    xaxis_title={
        'text': 'Recency',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Count',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
    legend_title={
        'text': 'Recency',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

    # Update the x-axis tick font
    fig_recency.update_xaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold x-axis numbers

    # Update the y-axis tick font
    fig_recency.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold y-axis numbers

    # Update the bar text font
    fig_recency.update_traces(textfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold text for bars
    st.plotly_chart(fig_recency)
   
    # Example with Frequency distribution
    fig_frequency = px.histogram(segment_data, x='Frequency', title=f'Frequency Distribution in {segment} Segment', nbins=10, color='Frequency')
    fig_frequency.update_layout(
    title={
        'text': f'Frequency Distribution in {segment} Segment',
        'font': {'size': 24, 'weight': 'bold', 'family': 'Arial'},  # Increase title font size and make it bold
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
    xaxis_title={
        'text': 'Frequency',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Count',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
    legend_title={
        'text': 'Frequency',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

    # Update the x-axis tick font
    fig_frequency.update_xaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold x-axis numbers

    # Update the y-axis tick font
    fig_frequency.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold y-axis numbers

    # Update the bar text font
    fig_frequency.update_traces(textfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold text for bars
    st.plotly_chart(fig_frequency)
   
    # Example with Monetary distribution
    fig_monetary = px.histogram(segment_data, x='Monetary', title=f'Monetary Distribution in {segment} Segment', nbins=10, color='Monetary')
    fig_monetary.update_layout(
    title={
        'text': f'Monetary Distribution in {segment} Segment',
        'font': {'size': 24, 'weight': 'bold', 'family': 'Arial'},  # Increase title font size and make it bold
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
    xaxis_title={
        'text': 'Monetary',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Count',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
    legend_title={
        'text': 'Monetary',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

    # Update the x-axis tick font
    fig_monetary.update_xaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold x-axis numbers

    # Update the y-axis tick font
    fig_monetary.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold y-axis numbers

    # Update the bar text font
    fig_monetary.update_traces(textfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold text for bars
    st.plotly_chart(fig_monetary)

    # Scatter plot example
    fig_scatter = px.scatter(segment_data, x='Frequency', y='Monetary', title=f'Scatter plot of Frequency vs Monetary in {segment} Segment', color='Recency')
    fig_scatter.update_layout(
    title={
        'text': f'Scatter Plot of Frequency vs Monetary in {segment} Segment',
        'font': {'size': 24, 'weight': 'bold', 'family': 'Arial'},  # Increase title font size and make it bold
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
    xaxis_title={
        'text': 'Frequency',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Monetary',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
    legend_title={
        'text': 'Recency',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

    # Update the x-axis tick font
    fig_scatter.update_xaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold x-axis numbers

    # Update the y-axis tick font
    fig_scatter.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold y-axis numbers

    # Update the marker text font
    fig_scatter.update_traces(marker=dict(size=10), textfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold text for markers
    st.plotly_chart(fig_scatter)

    # Box plot example
    fig_box = px.box(segment_data, x='RFM_Segment', y='Monetary', color='RFM_Segment', title=f'Monetary Distribution in {segment} Segment')
    fig_box.update_layout(
    title={
        'text': f'Monetary Distribution in {segment} Segment',
        'font': {'size': 24, 'weight': 'bold', 'family': 'Arial'},  # Increase title font size and make it bold
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
    xaxis_title={
        'text': 'RFM Segment',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Monetary',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for y-axis label
    },
    legend_title={
        'text': 'RFM Segment',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

    # Update the x-axis tick font
    fig_box.update_xaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold x-axis numbers

    # Update the y-axis tick font
    fig_box.update_yaxes(tickfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold y-axis numbers

    st.plotly_chart(fig_box)

    # Additional visualization
    fig_pie_segment = px.pie(segment_counts, values='Count', names='RFM_Segment', title=f'Percentage Distribution of Customers in {segment} Segment')
    fig_pie_segment.update_layout(
    title={
        'text': f'Percentage Distribution of Customers in {segment} Segment',
        'font': {'size': 24, 'weight': 'bold', 'family': 'Arial'},  # Increase title font size and make it bold
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
    legend_title={
        'text': 'RFM Segment',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial', 'color': 'black'}  # Bold and larger size for legend title
    }
)

    # Update the text font for the pie slices
    fig_pie_segment.update_traces(textfont=dict(size=16, family='Arial', color='black', weight='bold'))  # Bold text for slice labels
    st.plotly_chart(fig_pie_segment)

elif analysis_type == "Correlation Matrix of RFM Values within Champions Segment":
    st.markdown("""
        <div class='segment'>
            <h3>Correlation Matrix of RFM Values within Champions Segment</h3>
            <p>Explore correlations between Recency, Frequency, and Monetary values within the Champions segment.</p>
        </div>
    """, unsafe_allow_html=True)
    
    champions_data = rfm[rfm['RFM_Segment'] == 'Champions']
    correlation_matrix = champions_data[['Recency', 'Frequency', 'Monetary']].corr()

    # Correlation matrix heatmap
    fig_heatmap = px.imshow(correlation_matrix, labels=dict(color="Correlation"), x=['Recency', 'Frequency', 'Monetary'], y=['Recency', 'Frequency', 'Monetary'], title='Correlation Heatmap within Champions Segment')
    fig_heatmap.update_layout(
    title={
        'text': 'Correlation Heatmap within Champions Segment',
        'font': {'size': 24, 'weight': 'bold', 'family': 'Arial'},  # Increase title font size and make it bold
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
    xaxis_title={
        'text': 'Variables',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial'}  # Bold and larger size for x-axis label
    },
    yaxis_title={
        'text': 'Variables',
        'font': {'size': 18, 'weight': 'bold', 'family': 'Arial'}  # Bold and larger size for y-axis label
    },
)
    # Update font for x and y tick labels
    fig_heatmap.update_xaxes(tickfont=dict(size=16, family='Arial', weight='bold'))  # Increase and bold x-axis tick labels
    fig_heatmap.update_yaxes(tickfont=dict(size=16, family='Arial', weight='bold'))  # Increase and bold y-axis tick labels


    # Update the font for color scale legend
    fig_heatmap.update_coloraxes(colorbar=dict(title=dict(font=dict(size=18, weight='bold', family='Arial'))))  # Bold for color bar title
    st.plotly_chart(fig_heatmap)

    # Scatter plot of Recency vs Frequency
    fig_scatter_rf = px.scatter(champions_data, x='Recency', y='Frequency', title='Scatter Plot of Recency vs Frequency in Champions Segment', color='Monetary')
    fig_scatter_rf.update_layout(
    title={
        'text': 'Scatter Plot of Recency vs Frequency in Champions Segment',
        'font': {'size': 24, 'weight': 'bold', 'family': 'Arial'},  # Increase title font size and make it bold
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
)

    # Update font for x and y axis labels
    fig_scatter_rf.update_xaxes(title_font=dict(size=18, weight='bold', family='Arial'))  # Bold and larger size for x-axis label
    fig_scatter_rf.update_yaxes(title_font=dict(size=18, weight='bold', family='Arial'))  # Bold and larger size for y-axis label

    # Update font for x and y tick labels
    fig_scatter_rf.update_xaxes(tickfont=dict(size=16, family='Arial', weight='bold'))  # Increase and bold x-axis tick labels
    fig_scatter_rf.update_yaxes(tickfont=dict(size=16, family='Arial', weight='bold'))  # Increase and bold y-axis tick labels
    st.plotly_chart(fig_scatter_rf)

    # Scatter plot of Monetary vs Frequency
    fig_scatter_fm = px.scatter(champions_data, x='Monetary', y='Frequency', title='Scatter Plot of Monetary vs Frequency in Champions Segment', color='Recency')
    fig_scatter_fm.update_layout(
    title={
        'text': 'Scatter Plot of Monetary vs Frequency in Champions Segment',
        'font': {'size': 24, 'weight': 'bold', 'family': 'Arial'},  # Increase title font size and make it bold
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
)

    # Update font for x and y axis labels
    fig_scatter_fm.update_xaxes(title_font=dict(size=18, weight='bold', family='Arial'))  # Bold and larger size for x-axis label
    fig_scatter_fm.update_yaxes(title_font=dict(size=18, weight='bold', family='Arial'))  # Bold and larger size for y-axis label

    # Update font for x and y tick labels
    fig_scatter_fm.update_xaxes(tickfont=dict(size=16, family='Arial', weight='bold'))  # Increase and bold x-axis tick labels
    fig_scatter_fm.update_yaxes(tickfont=dict(size=16, family='Arial', weight='bold'))  # Increase and bold y-axis tick labels
    st.plotly_chart(fig_scatter_fm)

    # Box plot of Monetary values
    fig_box = px.box(champions_data, x='RFM_Segment', y='Monetary', color='RFM_Segment', title='Monetary Distribution in Champions Segment')
    fig_box.update_layout(
    title={
        'text': 'Monetary Distribution in Champions Segment',
        'font': {'size': 24, 'weight': 'bold', 'family': 'Arial'},  # Increase title font size and make it bold
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
)

    # Update font for x and y axis labels
    fig_box.update_xaxes(title_font=dict(size=18, weight='bold', family='Arial'))  # Bold and larger size for x-axis label
    fig_box.update_yaxes(title_font=dict(size=18, weight='bold', family='Arial'))  # Bold and larger size for y-axis label

    # Update font for x and y tick labels
    fig_box.update_xaxes(tickfont=dict(size=16, family='Arial', weight='bold'))  # Increase and bold x-axis tick labels
    fig_box.update_yaxes(tickfont=dict(size=16, family='Arial', weight='bold'))  # Increase and bold y-axis tick labels
    st.plotly_chart(fig_box)

    # Additional visualization
    fig_bar_champions = px.bar(segment_counts, x='RFM_Segment', y='Count', title='Count of Customers in Each RFM Segment within Champions Segment', color='RFM_Segment')
    fig_bar_champions.update_layout(
    title={
        'text': 'Count of Customers in Each RFM Segment within Champions Segment',
        'font': {'size': 24, 'weight': 'bold', 'family': 'Arial'},  # Increase title font size and make it bold
        'x': 0.5,  # Center the title
        'xanchor': 'center',  # Align the title at the center
        'yanchor': 'top'  # Keeps the title anchored at the top
    },
)

    # Update font for x and y axis labels
    fig_bar_champions.update_xaxes(title_font=dict(size=18, weight='bold', family='Arial'))  # Bold and larger size for x-axis label
    fig_bar_champions.update_yaxes(title_font=dict(size=18, weight='bold', family='Arial'))  # Bold and larger size for y-axis label

    # Update font for x and y tick labels
    fig_bar_champions.update_xaxes(tickfont=dict(size=16, family='Arial', weight='bold'))  # Increase and bold x-axis tick labels
    fig_bar_champions.update_yaxes(tickfont=dict(size=16, family='Arial', weight='bold'))  # Increase and bold y-axis tick labels

    st.plotly_chart(fig_bar_champions)

# Concluding Lines
st.markdown("""
<div class='segment'>
    <h3>Thank you for using the RFM Analysis Dashboard</h3>
    <p>We hope this analysis helps you understand your customer segments better and make informed business decisions.</p>
</div>
""", unsafe_allow_html=True)