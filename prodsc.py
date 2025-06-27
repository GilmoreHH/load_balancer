import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os
from simple_salesforce import Salesforce
import requests
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Insurance Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Enhanced Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main > div {
        font-family: 'Inter', sans-serif;
    }
    
    /* Custom CSS Variables */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --accent-color: #06b6d4;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --dark-bg: #1f2937;
        --light-bg: #f8fafc;
        --card-bg: #ffffff;
        --border-color: #e5e7eb;
        --text-primary: #111827;
        --text-secondary: #6b7280;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Main Header */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 2rem;
        letter-spacing: -0.025em;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.875rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 2rem 0 1.5rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid var(--primary-color);
        position: relative;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-color) 0%, var(--success-color) 100%);
    }
    
    /* Modern Metric Cards */
    .metric-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-md);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--accent-color) 100%);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    /* Premium Text Metrics */
    .text-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .text-metric::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        transition: all 0.5s ease;
        opacity: 0;
    }
    
    .text-metric:hover::before {
        opacity: 1;
        top: -100%;
        left: -100%;
    }
    
    .text-metric:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
    
    .text-metric h3 {
        margin: 0;
        font-size: 2.5em;
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    .text-metric p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1em;
        opacity: 0.95;
        font-weight: 500;
    }
    
    /* Modern Sidebar */
    .sidebar .stSelectbox label, .sidebar .stMultiSelect label, 
    .sidebar .stSlider label, .sidebar .stCheckbox label {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        font-size: 0.9rem !important;
    }
    
    .sidebar .stButton button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .sidebar .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    /* Producer Tab Cards */
    .producer-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
        transition: all 0.3s ease;
        position: relative;
    }
    
    .producer-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-color);
    }
    
    .producer-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .producer-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1.2rem;
        margin-right: 1rem;
    }
    
    .producer-name {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
    }
    
    .producer-id {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0.25rem 0 0 0;
    }
    
    /* Performance Indicators */
    .performance-indicator {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .indicator-high {
        background-color: #dcfce7;
        color: #166534;
    }
    
    .indicator-medium {
        background-color: #fef3c7;
        color: #92400e;
    }
    
    .indicator-low {
        background-color: #fee2e2;
        color: #991b1b;
    }
    
    /* Chart Containers */
    .chart-container {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        margin: 1rem 0;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--light-bg);
        border-radius: 12px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white !important;
        box-shadow: var(--shadow-md);
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .text-metric {
            padding: 1.5rem;
        }
        
        .text-metric h3 {
            font-size: 2rem;
        }
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        :root {
            --card-bg: #374151;
            --light-bg: #1f2937;
            --text-primary: #f9fafb;
            --text-secondary: #d1d5db;
            --border-color: #4b5563;
        }
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
@st.cache_data
def get_stage_metadata():
    """Return stage metadata mapping."""
    return {
        'Prospect': {'category': 'Open'},
        'Qualification': {'category': 'Open'},
        'Needs Analysis': {'category': 'Open'},
        'Value Proposition': {'category': 'Open'},
        'Id. Decision Makers': {'category': 'Open'},
        'Proposal/Price Quote': {'category': 'Open'},
        'Negotiation/Review': {'category': 'Open'},
        'Closed Won': {'category': 'Won'},
        'Closed Lost': {'category': 'Lost'},
    }

@st.cache_data
def get_business_type_categories():
    """Return business type categories mapping."""
    return {
        'Auto': 'Personal Lines',
        'Home': 'Personal Lines',
        'Umbrella': 'Personal Lines',
        'General Liability': 'Commercial Lines',
        'Property': 'Commercial Lines',
        'Workers Comp': 'Commercial Lines',
        'Commercial Auto': 'Commercial Lines',
    }

def map_lob(picklist_val):
    """Map LOB picklist values to categories."""
    lob_mapping = {
        'Auto': 'Personal Auto',
        'Home': 'Personal Property',
        'Umbrella': 'Personal Umbrella',
        'General Liability': 'Commercial Liability',
        'Property': 'Commercial Property',
        'Workers Comp': 'Commercial WC',
        'Commercial Auto': 'Commercial Auto',
    }
    return lob_mapping.get(picklist_val, 'Other')

# Producer Management System
@st.cache_data
def initialize_producer_registry():
    """Initialize the producer registry with ID mapping."""
    return {
        'producers': {},
        'id_mapping': {},
        'last_updated': datetime.now()
    }

def get_account_managers_from_salesforce(sf):
    """Get account managers using the correct Account Manager query."""
    try:
        # First get the Account Manager IDs from Accounts
        account_manager_query = """
            SELECT Id, Name, InternalUserId, InternalUser.FirstName, InternalUser.LastName 
            FROM Producer 
            WHERE Id IN (
                SELECT Account_Manager__c 
                FROM Account 
                WHERE Account_Manager__c != null
            )
        """
        
        results = sf.query_all(account_manager_query)
        
        account_managers = {}
        for rec in results['records']:
            producer_id = rec['Id']
            producer_name = rec['Name']
            internal_user_id = rec.get('InternalUserId', '')
            
            # Get internal user details if available
            internal_user = rec.get('InternalUser', {})
            first_name = internal_user.get('FirstName', '') if internal_user else ''
            last_name = internal_user.get('LastName', '') if internal_user else ''
            full_internal_name = f"{first_name} {last_name}".strip() if first_name or last_name else ''
            
            account_managers[producer_id] = {
                'id': producer_id,
                'name': producer_name,
                'internal_user_id': internal_user_id,
                'internal_user_name': full_internal_name,
                'first_name': first_name,
                'last_name': last_name
            }
        
        return account_managers
        
    except Exception as e:
        st.error(f"Error fetching account managers: {e}")
        return {}

def get_producer_names(sf, producer_ids):
    """Enhanced producer name fetching with account manager data."""
    if not producer_ids:
        return {}

    # Get or initialize producer registry
    if 'producer_registry' not in st.session_state:
        st.session_state.producer_registry = initialize_producer_registry()

    # Check cache first
    registry = st.session_state.producer_registry
    cached_producers = {}
    uncached_ids = []

    for prod_id in producer_ids:
        if prod_id in registry['id_mapping']:
            cached_producers[prod_id] = registry['id_mapping'][prod_id]['name']
        else:
            uncached_ids.append(prod_id)

    # Fetch uncached producers using the account manager query
    if uncached_ids:
        # Get all account managers first
        all_account_managers = get_account_managers_from_salesforce(sf)
        
        # Filter for the ones we need
        for prod_id in uncached_ids:
            if prod_id in all_account_managers:
                manager_data = all_account_managers[prod_id]
                prod_name = manager_data['name']
                
                # Update registry with enhanced data
                registry['producers'][prod_name] = {
                    'id': prod_id,
                    'name': prod_name,
                    'internal_user_id': manager_data['internal_user_id'],
                    'internal_user_name': manager_data['internal_user_name'],
                    'first_name': manager_data['first_name'],
                    'last_name': manager_data['last_name'],
                    'performance_data': {},
                    'created_date': datetime.now(),
                    'is_account_manager': True
                }
                
                registry['id_mapping'][prod_id] = {
                    'name': prod_name,
                    'internal_user_id': manager_data['internal_user_id'],
                    'internal_user_name': manager_data['internal_user_name'],
                    'is_account_manager': True
                }
                
                cached_producers[prod_id] = prod_name

    # Update session state
    st.session_state.producer_registry = registry
    
    return cached_producers

def get_producer_performance_summary(df, producer_name):
    """Calculate performance metrics for a producer."""
    producer_data = df[df['Producer'] == producer_name]
    
    if producer_data.empty:
        return {
            'total_opportunities': 0,
            'lob_diversity': 0,
            'top_lob': 'N/A',
            'performance_level': 'low'
        }
    
    total_opps = producer_data['Count'].sum()
    lob_count = len(producer_data['LOB_Category'].unique())
    top_lob = producer_data.groupby('LOB_Category')['Count'].sum().idxmax()
    
    # Determine performance level
    if total_opps >= 50:
        performance_level = 'high'
    elif total_opps >= 20:
        performance_level = 'medium'
    else:
        performance_level = 'low'
    
    return {
        'total_opportunities': total_opps,
        'lob_diversity': lob_count,
        'top_lob': top_lob,
        'performance_level': performance_level
    }

def format_datetime_for_salesforce(dt):
    """Format datetime for Salesforce SOQL queries - always returns datetime format."""
    if dt is None:
        return None
    
    # If it's a date object, convert to datetime at start of day
    if hasattr(dt, 'date') and not hasattr(dt, 'hour'):
        dt = datetime.combine(dt, datetime.min.time())
    
    # If it's already a datetime, use as is
    elif not hasattr(dt, 'hour'):
        # It's a date object
        dt = datetime.combine(dt, datetime.min.time())
    
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'

def format_date_as_datetime_for_salesforce(dt):
    """Format date as datetime for Salesforce SOQL queries - specifically for date fields that need datetime format."""
    if dt is None:
        return None
    
    # Convert date to datetime
    if hasattr(dt, 'date') and not hasattr(dt, 'hour'):
        # It's a date object
        dt = datetime.combine(dt, datetime.min.time())
    elif not hasattr(dt, 'hour'):
        # It's a date object  
        dt = datetime.combine(dt, datetime.min.time())
    
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'

def format_end_date_as_datetime_for_salesforce(dt):
    """Format end date as datetime for Salesforce SOQL queries - end of day."""
    if dt is None:
        return None
    
    # Convert date to datetime at end of day
    if hasattr(dt, 'date') and not hasattr(dt, 'hour'):
        # It's a date object
        dt = datetime.combine(dt, datetime.max.time())
    elif not hasattr(dt, 'hour'):
        # It's a date object
        dt = datetime.combine(dt, datetime.max.time())
    
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'

# Salesforce connection functions
def get_salesforce_connection():
    """Get Salesforce connection, create if doesn't exist."""
    try:
        sf = Salesforce(
            username=os.getenv("SF_USERNAME_PRO"),
            password=os.getenv("SF_PASSWORD_PRO"),
            security_token=os.getenv("SF_SECURITY_TOKEN_PRO"),
        )
        st.session_state.sf = sf
        st.success("✅ Connected to Salesforce successfully!")
        return sf
    except Exception as e:
        st.error(f"❌ Salesforce connection failed: {str(e)}")
        st.info("Please check your environment variables: SF_USERNAME_PRO, SF_PASSWORD_PRO, SF_SECURITY_TOKEN_PRO")
        return None

def get_new_quote_requests(sf, start_date, end_date):
    """Get new quote requests data."""
    try:
        start_date_str = format_datetime_for_salesforce(start_date)
        end_date_str = format_end_date_as_datetime_for_salesforce(end_date)

        soql_query = f"""
            SELECT CreatedDate, New_Business_or_Renewal__c, Name, Id
            FROM Opportunity
            WHERE CreatedDate >= {start_date_str} AND CreatedDate <= {end_date_str}
            AND New_Business_or_Renewal__c IN ('Personal Lines - New Business', 'Commercial Lines - New Business')
        """

        results = sf.query_all(soql_query)
        return pd.DataFrame(results['records'])
    except Exception as e:
        st.error(f"Error fetching new quote requests: {str(e)}")
        return pd.DataFrame()

def get_prior_month_opportunity_status_enhanced(sf):
    """Get opportunity status for prior month with enhanced data."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        start_date_str = start_date.strftime('%Y-%m-%dT00:00:00Z')
        end_date_str = end_date.strftime('%Y-%m-%dT23:59:59Z')

        query = f"""
            SELECT StageName, COUNT(Id) oppCount
            FROM Opportunity
            WHERE CreatedDate >= {start_date_str} AND CreatedDate <= {end_date_str}
            GROUP BY StageName
        """

        results = sf.query_all(query)
        stage_metadata = get_stage_metadata()

        data = []
        total_count = sum([record['oppCount'] for record in results['records']])
        
        for record in results['records']:
            stage_name = record['StageName']
            count = record['oppCount']
            percentage = (count / total_count) * 100 if total_count > 0 else 0
            category = stage_metadata.get(stage_name, {"category": "Unknown"})["category"]

            data.append({
                'StageName': stage_name,
                'Count': count,
                'Percentage': percentage,
                'Category': category
            })

        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error fetching opportunity status: {str(e)}")
        return pd.DataFrame()
    
def create_modern_doughnut_chart(df):
    """Create a modern doughnut chart with enhanced styling."""
    if df.empty:
        return None
    
    # Modern color palette
    colors = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#84cc16', '#f97316']
    
    fig = go.Figure(data=[go.Pie(
        labels=df['StageName'],
        values=df['Count'],
        hole=0.5,
        marker=dict(
            colors=colors[:len(df)], 
            line=dict(color='#ffffff', width=3)
        ),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=12, family="Inter, sans-serif"),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text="Prior Month Opportunity Status",
            x=0.5,
            font=dict(size=18, family="Inter, sans-serif", color='#111827')
        ),
        showlegend=True,
        legend=dict(
            orientation="v", 
            yanchor="middle", 
            y=0.5, 
            xanchor="left", 
            x=1.05,
            font=dict(size=11, family="Inter, sans-serif")
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=50, l=50, r=150)
    )
    
    return fig    

def get_top_referral_sources(sf):
    """Get top 10 referral sources from prior month."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
       
        start_date_str = start_date.strftime('%Y-%m-%dT00:00:00Z')
        end_date_str = end_date.strftime('%Y-%m-%dT23:59:59Z')
       
        query = f"""
            SELECT LeadSource, COUNT(Id) oppCount
            FROM Opportunity
            WHERE CreatedDate >= {start_date_str} AND CreatedDate <= {end_date_str}
            AND LeadSource != null
            GROUP BY LeadSource
            ORDER BY COUNT(Id) DESC
            LIMIT 10
        """
       
        results = sf.query_all(query)
        return pd.DataFrame(results['records'])
    except Exception as e:
        st.error(f"Error fetching referral sources: {str(e)}")
        return pd.DataFrame()

def get_rolling_4_weeks_premium(sf, start_date=None, end_date=None):
    """Get rolling premium with optional date filter."""
    try:
        if start_date is None or end_date is None:
            # Default to last 4 weeks
            end_date = datetime.now().date()
            start_date = end_date - timedelta(weeks=4)

        # Format dates as datetime for Salesforce SOQL
        start_date_str = format_date_as_datetime_for_salesforce(start_date)
        end_date_str = format_end_date_as_datetime_for_salesforce(end_date)

        query = f"""
            SELECT PremiumAmount, EffectiveDate
            FROM InsurancePolicy
            WHERE EffectiveDate >= {start_date_str} AND EffectiveDate <= {end_date_str}
            AND PremiumAmount != null
            ORDER BY EffectiveDate
        """

        results = sf.query_all(query)
        df = pd.DataFrame(results['records'])

        if df.empty:
            return pd.DataFrame()

        # Convert EffectiveDate to datetime
        df['EffectiveDate'] = pd.to_datetime(df['EffectiveDate'])

        # Group by week
        df['week_start'] = df['EffectiveDate'].dt.to_period('W').dt.start_time
        weekly_df = df.groupby('week_start')['PremiumAmount'].sum().reset_index()
        weekly_df.columns = ['week_start', 'totalPremium']
        weekly_df['week_label'] = weekly_df['week_start'].dt.strftime('Week of %b %d')

        return weekly_df

    except Exception as e:
        st.error(f"Error fetching rolling premium with filter: {str(e)}")
        return pd.DataFrame()

def get_qtd_premium(sf, start_date=None, end_date=None):
    """Get premium with optional date filter (defaults to QTD)."""
    try:
        if start_date is None or end_date is None:
            # Default to quarter to date
            now = datetime.now()
            start_date = datetime(now.year, ((now.month - 1) // 3) * 3 + 1, 1).date()
            end_date = now.date()

        # Format dates as datetime for Salesforce SOQL
        start_date_str = format_date_as_datetime_for_salesforce(start_date)
        end_date_str = format_end_date_as_datetime_for_salesforce(end_date)

        query = f"""
            SELECT SUM(PremiumAmount) totalPremium
            FROM InsurancePolicy
            WHERE EffectiveDate >= {start_date_str} AND EffectiveDate <= {end_date_str}
            AND PremiumAmount != null
        """

        results = sf.query_all(query)
        total = results['records'][0]['totalPremium'] if results['records'] else 0
        return total or 0
    except Exception as e:
        st.error(f"Error fetching premium with filter: {str(e)}")
        return 0

def get_carrier_performance_enhanced(sf, start_date, end_date):
    """Get carrier performance with enhanced metrics and color coding."""
    try:
        # Get stage metadata
        stage_metadata = get_stage_metadata()

        # Query Carriers
        carrier_query = """
            SELECT Id, Name
            FROM Account
            WHERE Id IN (SELECT Renewing_Carrier__c FROM Opportunity WHERE Renewing_Carrier__c != null)
        """

        carrier_results = sf.query_all(carrier_query)
        carriers = {record['Id']: record['Name'] for record in carrier_results['records']}

        # Query opportunities with carrier data
        date_filter = ""
        if start_date and end_date:
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            date_filter = f"AND CloseDate >= {start_date_str} AND CloseDate <= {end_date_str}"

        query = f"""
            SELECT
                Renewing_Carrier__c,
                StageName,
                COUNT(Id) oppCount
            FROM Opportunity
            WHERE Renewing_Carrier__c != null
            {date_filter}
            GROUP BY Renewing_Carrier__c, StageName
        """

        results = sf.query_all(query)

        # Process results
        carrier_data = {}
        for record in results['records']:
            carrier_id = record['Renewing_Carrier__c']
            carrier_name = carriers.get(carrier_id, 'Unknown Carrier')
            stage = record['StageName']
            count = record['oppCount']

            if carrier_name not in carrier_data:
                carrier_data[carrier_name] = {'total': 0, 'won': 0}

            carrier_data[carrier_name]['total'] += count
            if stage == 'Closed Won':
                carrier_data[carrier_name]['won'] += count

        # Calculate close rates and rank
        data = []
        for carrier, stats in carrier_data.items():
            close_rate = (stats['won'] / stats['total']) * 100 if stats['total'] > 0 else 0
            data.append({
                'Carrier': carrier,
                'Total_Quotes': stats['total'],
                'Won_Quotes': stats['won'],
                'Close_Rate': close_rate
            })

        df = pd.DataFrame(data)
        if not df.empty:
            # Add ranking and color coding
            df = df.sort_values('Close_Rate', ascending=False).reset_index(drop=True)
            df['Rank'] = df.index + 1
            
            # Color coding based on rank
            def get_rank_color(rank, total_carriers):
                if rank <= total_carriers * 0.3:  # Top 30%
                    return '#10b981'  # Green
                elif rank <= total_carriers * 0.6:  # Middle 30%
                    return '#f59e0b'  # Amber
                else:  # Bottom 40%
                    return '#ef4444'  # Red
            
            total_carriers = len(df)
            df['Color'] = df['Rank'].apply(lambda x: get_rank_color(x, total_carriers))

        return df

    except Exception as e:
        st.error(f"Error fetching carrier performance: {e}")
        return pd.DataFrame()

def create_enhanced_sidebar():
    """Create enhanced sidebar with modern styling and comprehensive filters."""
    st.sidebar.markdown('<div class="sidebar">', unsafe_allow_html=True)
    st.sidebar.header("🎛️ Dashboard Controls")
    
    # Date range selector
    st.sidebar.subheader("📅 Date Range")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Business type filter
    st.sidebar.subheader("🏢 Business Filters")
    business_types = st.sidebar.multiselect(
        "Business Types",
        options=["Personal Lines", "Commercial Lines", "Both"],
        default=["Both"]
    )
    
    new_business_only = st.sidebar.checkbox("New Business Only", value=False)
    
    # Producer filter
    st.sidebar.subheader("👥 Producer Filters")
    show_top_producers = st.sidebar.slider("Show Top N Producers", 5, 20, 10)
    
    # Premium filters
    st.sidebar.subheader("💰 Premium Filters")
    min_premium = st.sidebar.number_input("Minimum Premium ($)", value=0, step=1000)
    max_premium = st.sidebar.number_input("Maximum Premium ($)", value=100000, step=1000)
    
    # Chart display options
    st.sidebar.subheader("📊 Display Options")
    show_percentages = st.sidebar.checkbox("Show Percentages in Charts", value=True)
    chart_theme = st.sidebar.selectbox("Chart Theme", ["plotly", "plotly_white", "plotly_dark"])
    
    # Data refresh
    st.sidebar.subheader("🔄 Data Management")
    refresh_data = st.sidebar.button("Refresh Data", type="primary")
    export_data = st.sidebar.button("Export Current View")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'business_types': business_types,
        'new_business_only': new_business_only,
        'show_top_producers': show_top_producers,
        'min_premium': min_premium,
        'max_premium': max_premium,
        'show_percentages': show_percentages,
        'chart_theme': chart_theme,
        'refresh_data': refresh_data,
        'export_data': export_data
    }

def display_modern_text_metrics(sf, filters):
    """Display modern premium metrics with enhanced styling."""
    # Rolling 4 weeks premium
    rolling_premium = get_rolling_4_weeks_premium(sf, filters['start_date'], filters['end_date'])
    total_rolling = rolling_premium['totalPremium'].sum() if not rolling_premium.empty else 0
    
    # QTD premium
    qtd_premium = get_qtd_premium(sf, filters['start_date'], filters['end_date'])
    
    # Display as modern formatted text
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="text-metric">
            <h3>${total_rolling:,.0f}</h3>
            <p>Rolling 4 Weeks Closed Premium</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="text-metric">
            <h3>${qtd_premium:,.0f}</h3>
            <p>Quarter to Date Premium</p>
        </div>
        """, unsafe_allow_html=True)

def create_overview_tab(sf, filters):
    """Create enhanced overview tab with modern styling."""
    st.markdown('<div class="section-header">Business Overview</div>', unsafe_allow_html=True)

    # Key metrics row with modern cards
    col1, col2, col3 = st.columns(3)

    with col1:
        new_quotes_df = get_new_quote_requests(sf, filters['start_date'], filters['end_date'])
        total_quotes = len(new_quotes_df)
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; font-size: 2rem; color: #6366f1;">{total_quotes}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-weight: 500;">New Quote Requests</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        referral_df = get_top_referral_sources(sf)
        top_referral_count = referral_df.iloc[0]['oppCount'] if not referral_df.empty else 0
        top_referral_source = referral_df.iloc[0]['LeadSource'] if not referral_df.empty else 'N/A'
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; font-size: 2rem; color: #10b981;">{top_referral_count}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-weight: 500;">Top Referral Source</p>
            <p style="margin: 0.25rem 0 0 0; color: #9ca3af; font-size: 0.9rem;">{top_referral_source}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        prior_month_df = get_prior_month_opportunity_status_enhanced(sf)
        if not prior_month_df.empty:
            open_opps = prior_month_df[prior_month_df['Category'] == 'Open']['Count'].sum()
        else:
            open_opps = 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; font-size: 2rem; color: #f59e0b;">{open_opps}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-weight: 500;">Open Opportunities</p>
        </div>
        """, unsafe_allow_html=True)

    # Premium Summary
    st.markdown("### 💎 Premium Summary")
    display_modern_text_metrics(sf, filters)

    # Charts row with containers
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        prior_month_df = get_prior_month_opportunity_status_enhanced(sf)
        if not prior_month_df.empty:
            fig = create_modern_doughnut_chart(prior_month_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        referral_df = get_top_referral_sources(sf)
        if not referral_df.empty:
            fig = px.bar(referral_df, 
                        x='oppCount', 
                        y='LeadSource',
                        orientation='h', 
                        title="Top 10 Referral Sources",
                        color='oppCount', 
                        color_continuous_scale='Viridis')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                title_font=dict(size=16, color='#111827'),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def create_performance_tab(sf, filters):
    """Create enhanced performance tab with modern styling."""
    st.markdown('<div class="section-header">Performance Metrics</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        rolling_premium_df = get_rolling_4_weeks_premium(sf, filters['start_date'], filters['end_date'])

        if not rolling_premium_df.empty:
            fig = px.line(rolling_premium_df, 
                         x='week_label', 
                         y='totalPremium',
                         title="Period Premium by Week",
                         line_shape='spline')
            fig.update_traces(
                line=dict(width=4, color='#6366f1'), 
                marker=dict(size=8, color='#8b5cf6')
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                title_font=dict(size=16, color='#111827'),
                xaxis_title="Week",
                yaxis_title="Premium ($)",
                yaxis_tickformat='$,.0f'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No premium data available for the selected period.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        carrier_df = get_carrier_performance_enhanced(sf, filters['start_date'], filters['end_date'])
        if not carrier_df.empty:
            fig = px.scatter(carrier_df, 
                           x='Total_Quotes', 
                           y='Close_Rate',
                           size='Won_Quotes', 
                           hover_name='Carrier',
                           color='Close_Rate',
                           color_continuous_scale='RdYlGn',
                           title="Carrier Performance Analysis")
            
            fig.update_traces(marker=dict(line=dict(width=2, color='#ffffff')))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                title_font=dict(size=16, color='#111827'),
                xaxis_title="Total Quotes",
                yaxis_title="Close Rate (%)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No carrier performance data available for the selected period.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Enhanced carrier performance table
    if not carrier_df.empty:
        st.markdown("### 🏆 Carrier Performance Ranking")
        
        carrier_display = carrier_df.copy()
        carrier_display['Close_Rate'] = carrier_display['Close_Rate'].round(1).astype(str) + '%'
        carrier_display['Performance_Tier'] = carrier_display['Rank'].apply(
            lambda x: '🥇 Top Tier' if x <= len(carrier_df) * 0.3 
            else '🥈 Mid Tier' if x <= len(carrier_df) * 0.6 
            else '🥉 Lower Tier'
        )
        
        display_cols = ['Rank', 'Carrier', 'Total_Quotes', 'Won_Quotes', 'Close_Rate', 'Performance_Tier']
        st.dataframe(
            carrier_display[display_cols].sort_values('Rank'), 
            use_container_width=True,
            hide_index=True
        )

def create_producer_card(producer_name, producer_id, performance_data, internal_user_data=None):
    """Create a modern producer card with account manager information."""
    # Get initials for avatar
    initials = ''.join([name[0].upper() for name in producer_name.split()[:2]])
    
    # Performance indicator
    perf_level = performance_data['performance_level']
    indicator_class = f"indicator-{perf_level}"
    indicator_text = f"{perf_level.title()} Performer"
    
    # Internal user information
    internal_user_info = ""
    if internal_user_data and internal_user_data.get('internal_user_name', 'N/A') != 'N/A':
        internal_user_info = f"""
        
        """
    
   

def connect_sf_and_query(sf, start_date, end_date, new_business_only):
    """Enhanced SF query with account manager tracking."""
    try:
        start_date_str = format_datetime_for_salesforce(start_date)
        end_date_str = format_end_date_as_datetime_for_salesforce(end_date)
        date_filter = f"CreatedDate >= {start_date_str} AND CreatedDate <= {end_date_str}"

        if new_business_only:
            new_business_filter = "AND New_Business_or_Renewal__c IN ('Personal Lines - New Business', 'Commercial Lines - New Business')"
        else:
            new_business_filter = ""

        # Query with Account Manager (Producer field)
        query_with_producer = f"""
            SELECT Producer__c, Type, COUNT(Id) oppCount
            FROM Opportunity
            WHERE {date_filter} {new_business_filter} AND Producer__c != null
            GROUP BY Producer__c, Type
        """
        results_with_prod = sf.query_all(query_with_producer)

        # Query without producer (fallback to Owner)
        query_without_producer = f"""
            SELECT Owner.Name, Type, COUNT(Id) oppCount
            FROM Opportunity
            WHERE {date_filter} {new_business_filter} AND Producer__c = null
            GROUP BY Owner.Name, Type
        """
        results_without_prod = sf.query_all(query_without_producer)

        # Get account manager names with enhanced registry
        producer_ids = {rec.get("Producer__c") for rec in results_with_prod["records"] if rec.get("Producer__c")}
        producer_names = get_producer_names(sf, list(producer_ids))

        producer_data = []

        # Process results with account manager
        for rec in results_with_prod["records"]:
            prod_id = rec.get("Producer__c")
            producer_name = producer_names.get(prod_id, "Account Manager Not Found")
            picklist_val = rec.get("Type", "Other")
            count_val = rec.get("oppCount", 0)
            lob_category = map_lob(picklist_val)

            # Get additional account manager info from registry
            internal_user_name = "N/A"
            internal_user_id = "N/A"
            if 'producer_registry' in st.session_state:
                registry = st.session_state.producer_registry
                if prod_id in registry['id_mapping']:
                    internal_user_name = registry['id_mapping'][prod_id].get('internal_user_name', 'N/A')
                    internal_user_id = registry['id_mapping'][prod_id].get('internal_user_id', 'N/A')

            producer_data.append({
                "Producer": producer_name,
                "Producer_ID": prod_id,
                "Internal_User_Name": internal_user_name,
                "Internal_User_ID": internal_user_id,
                "Type": picklist_val,
                "LOB_Category": lob_category,
                "Count": count_val,
                "Is_Account_Manager": True
            })

        # Process results without producer (Owner fallback)
        for rec in results_without_prod["records"]:
            owner = rec.get("Owner") or {}
            producer_name = owner.get("Name", "Owner Not Provided")
            picklist_val = rec.get("Type", "Other")
            count_val = rec.get("oppCount", 0)
            lob_category = map_lob(picklist_val)

            producer_data.append({
                "Producer": producer_name,
                "Producer_ID": "N/A",
                "Internal_User_Name": "N/A",
                "Internal_User_ID": "N/A",
                "Type": picklist_val,
                "LOB_Category": lob_category,
                "Count": count_val,
                "Is_Account_Manager": False
            })

        return pd.DataFrame(producer_data)

    except Exception as e:
        st.error(f"Error querying producer data: {str(e)}")
        return pd.DataFrame()

# Main Dashboard
def main():
    st.markdown('<h1 class="main-header">Insurance Analytics Dashboard</h1>', unsafe_allow_html=True)

    # Enhanced sidebar with modern styling
    filters = create_enhanced_sidebar()

    # Auto-connect to Salesforce
    sf = get_salesforce_connection()

    if sf is None:
        st.stop()

    # Main dashboard layout with modern tabs
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🎯 Performance", "👥 Producers"])

    with tab1:
        create_overview_tab(sf, filters)

    with tab2:
        create_performance_tab(sf, filters)

    with tab3:
        st.markdown('<div class="section-header">Producer Performance</div>', unsafe_allow_html=True)

        # Get producer data
        producer_df = connect_sf_and_query(sf, filters['start_date'], filters['end_date'], filters['new_business_only'])

        if not producer_df.empty:
            # Get unique producers
            unique_producers = producer_df['Producer'].unique()
            
            # Create producer tabs
            if len(unique_producers) > 0:
                # Limit to top performers for tabs
                producer_summary = producer_df.groupby('Producer')['Count'].sum().sort_values(ascending=False)
                top_producers = producer_summary.head(filters['show_top_producers']).index.tolist()
                
                # Create tabs for top producers
                producer_tabs = st.tabs([f"👤 {producer}" for producer in top_producers])
                
                for i, producer in enumerate(top_producers):
                    with producer_tabs[i]:
                        # Get producer ID and internal user data from registry
                        producer_id = "N/A"
                        internal_user_data = None
                        
                        if 'producer_registry' in st.session_state:
                            registry = st.session_state.producer_registry
                            if producer in registry['producers']:
                                producer_info = registry['producers'][producer]
                                producer_id = producer_info['id']
                                internal_user_data = {
                                    'internal_user_name': producer_info.get('internal_user_name', 'N/A'),
                                    'internal_user_id': producer_info.get('internal_user_id', 'N/A'),
                                    'first_name': producer_info.get('first_name', ''),
                                    'last_name': producer_info.get('last_name', '')
                                }
                        
                        # Get performance data
                        performance_data = get_producer_performance_summary(producer_df, producer)
                        
                        # Display enhanced producer card with account manager info
                        st.markdown(create_producer_card(producer, producer_id, performance_data, internal_user_data), unsafe_allow_html=True)
                        
                        # Producer-specific charts
                        producer_data = producer_df[producer_df['Producer'] == producer]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # LOB breakdown for this producer
                            lob_breakdown = producer_data.groupby('LOB_Category')['Count'].sum()
                            if not lob_breakdown.empty:
                                fig = px.pie(values=lob_breakdown.values, 
                                           names=lob_breakdown.index,
                                           title=f"{producer}'s LOB Distribution",
                                           color_discrete_sequence=px.colors.qualitative.Set3)
                                fig.update_layout(
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    font_family="Inter",
                                    title_font=dict(size=14, color='#111827')
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            # Performance by type
                            type_breakdown = producer_data.groupby('Type')['Count'].sum()
                            if not type_breakdown.empty:
                                fig = px.bar(x=type_breakdown.index, 
                                           y=type_breakdown.values,
                                           title=f"{producer}'s Performance by Type",
                                           color=type_breakdown.values,
                                           color_continuous_scale='Viridis')
                                fig.update_layout(
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    font_family="Inter",
                                    title_font=dict(size=14, color='#111827'),
                                    coloraxis_showscale=False,
                                    xaxis_title="Business Type",
                                    yaxis_title="Count"
                                )
                                st.plotly_chart(fig, use_container_width=True)

            # Enhanced producer summary table with account manager info
            st.markdown("### 📈 Account Manager Performance Summary")
            
            # Create enhanced summary with internal user information
            producer_detail = producer_df.pivot_table(
                values='Count', 
                index=['Producer', 'Producer_ID', 'Internal_User_Name', 'Is_Account_Manager'],
                columns='LOB_Category', 
                fill_value=0, 
                aggfunc='sum'
            )
            producer_detail['Total'] = producer_detail.sum(axis=1)
            producer_detail = producer_detail.sort_values('Total', ascending=False)
            
            # Reset index to show all columns
            producer_detail_display = producer_detail.reset_index()
            
            # Rename columns for better display
            display_columns = {
                'Producer': 'Account Manager Name',
                'Producer_ID': 'Account Manager ID', 
                'Internal_User_Name': 'Internal User',
                'Is_Account_Manager': 'Type'
            }
            producer_detail_display = producer_detail_display.rename(columns=display_columns)
            
            # Format the Type column
            producer_detail_display['Type'] = producer_detail_display['Type'].apply(
                lambda x: 'Account Manager' if x else 'Owner Fallback'
            )
            
            st.dataframe(producer_detail_display, use_container_width=True, hide_index=True)
            
            # Enhanced Producer Registry Status
            if 'producer_registry' in st.session_state:
                registry = st.session_state.producer_registry
                account_managers_count = sum(1 for p in registry['producers'].values() if p.get('is_account_manager', False))
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="margin: 0; font-size: 1.8rem; color: #6366f1;">{len(registry['producers'])}</h3>
                        <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-weight: 500;">Total Producers Tracked</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="margin: 0; font-size: 1.8rem; color: #10b981;">{account_managers_count}</h3>
                        <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-weight: 500;">Account Managers</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3 style="margin: 0; font-size: 1.8rem; color: #f59e0b;">{len(registry['id_mapping'])}</h3>
                        <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-weight: 500;">ID Mappings</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                **Registry Last Updated**: {registry['last_updated'].strftime('%Y-%m-%d %H:%M:%S')}
                """)
        else:
            st.info("No account manager data available for the selected period.")

if __name__ == "__main__":
    main()
