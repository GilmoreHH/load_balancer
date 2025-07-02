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


# Modern Enhanced Custom CSS with Asymmetrical Cards and Producer-specific styling
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
   
    /* Modern Metric Cards with Asymmetrical Heights */
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
   
    .metric-card:nth-child(1) { min-height: 120px; }
    .metric-card:nth-child(2) { min-height: 140px; }
    .metric-card:nth-child(3) { min-height: 160px; }
    .metric-card:nth-child(4) { min-height: 130px; }
    .metric-card:nth-child(5) { min-height: 150px; }
    .metric-card:nth-child(6) { min-height: 125px; }
   
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
   
    /* Premium Text Metrics with Asymmetrical Heights */
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
   
    .text-metric:nth-child(1) { min-height: 180px; }
    .text-metric:nth-child(2) { min-height: 200px; }
    .text-metric:nth-child(3) { min-height: 220px; }
   
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
   
    /* Producer-specific gradient overview cards */
    .producer-overview-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        min-height: 200px;
    }
   
    .producer-overview-card::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(-45deg);
        transition: all 0.5s ease;
        opacity: 0;
    }
   
    .producer-overview-card:hover::before {
        opacity: 1;
        top: -100%;
        right: -100%;
    }
   
    .producer-overview-card:hover {
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
   
    .producer-overview-card h2 {
        margin: 0 0 1rem 0;
        font-size: 2.2em;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
   
    .producer-metric {
        display: inline-block;
        margin: 0.5rem 1rem 0.5rem 0;
        padding: 0.5rem 1rem;
        background: rgba(255,255,255,0.2);
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
   
    .producer-metric-value {
        font-size: 1.8em;
        font-weight: 700;
        display: block;
    }
   
    .producer-metric-label {
        font-size: 0.9em;
        opacity: 0.9;
        display: block;
    }
   
    /* Specialty sections with enhanced styling */
    .specialty-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        box-shadow: var(--shadow-lg);
        position: relative;
        overflow: hidden;
    }
   
    .specialty-section h3 {
        margin: 0 0 1rem 0;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
   
    .specialty-item {
        background: rgba(255,255,255,0.2);
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        backdrop-filter: blur(10px);
    }
   
    .specialty-name {
        font-weight: 500;
    }
   
    .specialty-value {
        font-weight: 700;
        font-size: 1.1em;
    }
   
    /* Performance containers with asymmetrical heights */
    .performance-container {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
   
    .performance-container:nth-child(odd) { min-height: 400px; }
    .performance-container:nth-child(even) { min-height: 450px; }
   
    .performance-container:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
   
    /* Chart Containers with Asymmetrical Heights */
    .chart-container {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
   
    .chart-container:nth-child(odd) { min-height: 450px; }
    .chart-container:nth-child(even) { min-height: 500px; }
   
    .chart-container:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
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
   
    /* Producer tab styling */
    .producer-tab {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
   
    /* Debug info styling */
    .debug-info {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
        color: #6b7280;
    }
   
    /* Recent policies table styling */
    .recent-policies {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
    }
   
    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
       
        .text-metric, .producer-overview-card {
            padding: 1.5rem;
            min-height: auto;
        }
       
        .text-metric h3, .producer-overview-card h2 {
            font-size: 2rem;
        }
        
        .producer-metric {
            display: block;
            margin: 0.5rem 0;
        }
        
        .chart-container, .performance-container {
            min-height: auto;
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


def get_available_producers(sf):
    """Get all available producers from Salesforce."""
    try:
        producer_query = """
            SELECT Name
            FROM Producer
            ORDER BY Name
        """
        
        producer_results = sf.query_all(producer_query)
        producer_names = [record['Name'] for record in producer_results['records']]
        return producer_names
        
    except Exception as e:
        st.error(f"Error fetching producers: {str(e)}")
        return []


def get_producer_ids_from_names(sf, producer_names):
    """Convert producer names to Producer record IDs for lookup field filtering."""
    try:
        if not producer_names:
            return []
       
        # Create a safe query string for producer names
        name_conditions = []
        for name in producer_names:
            # Escape single quotes in names
            safe_name = name.replace("'", "\\'")
            name_conditions.append(f"Name = '{safe_name}'")
       
        producer_query = f"""
            SELECT Id, Name
            FROM Producer
            WHERE {' OR '.join(name_conditions)}
        """
       
        producer_results = sf.query_all(producer_query)
        producer_ids = [record['Id'] for record in producer_results['records']]
       
        return producer_ids
       
    except Exception as e:
        st.error(f"Error fetching producer IDs: {str(e)}")
        return []


def get_insurance_policy_data(sf, start_date, end_date, producer_filter=None):
    """Get Insurance Policy data with optional producer filtering."""
    try:
        start_date_str = format_date_as_datetime_for_salesforce(start_date)
        end_date_str = format_end_date_as_datetime_for_salesforce(end_date)
       
        # Base filters matching the Salesforce report
        base_filters = [
            f"EffectiveDate >= {start_date_str}",
            f"EffectiveDate <= {end_date_str}",
            "Status = 'Active'",
            "Business_Type_Reporting__c = 'New Business'"
        ]
       
        # Producer filter - handle both Producer and Producer_2__c fields
        producer_where_clause = ""
        if producer_filter and len(producer_filter) > 0:
            # First, get Producer IDs from Producer names
            producer_ids = get_producer_ids_from_names(sf, producer_filter)
           
            if producer_ids:
                producer_conditions = []
                for producer_id in producer_ids:
                    # Check both ProducerId and Producer_2__c custom lookup fields using IDs
                    producer_conditions.append(f"(ProducerId = '{producer_id}' OR Producer_2__c = '{producer_id}')")
                producer_where_clause = f"AND ({' OR '.join(producer_conditions)})"
            else:
                # If no producer IDs found, also try name-based filtering as fallback
                name_conditions = []
                for name in producer_filter:
                    safe_name = name.replace("'", "\\'")
                    name_conditions.append(f"(Producer.Name = '{safe_name}' OR Producer_2__r.Name = '{safe_name}')")
                if name_conditions:
                    producer_where_clause = f"AND ({' OR '.join(name_conditions)})"
        
        # Get Insurance Policy data
        policy_query = f"""
            SELECT
                Id,
                Name,
                PolicyName,
                ProducerId,
                Producer.Name,
                Producer_2__c,
                Producer_2__r.Name,
                PolicyType,
                WritingCarrierAccount.Name,
                Total_Policy_Premium__c,
                PremiumAmount,
                TaxesSurcharges,
                EffectiveDate,
                NameInsuredId,
                NameInsured.Name
            FROM InsurancePolicy
            WHERE {' AND '.join(base_filters)}
            {producer_where_clause}
            ORDER BY EffectiveDate DESC
        """
       
        policy_results = sf.query_all(policy_query)
        policy_df = pd.DataFrame(policy_results['records'])
       
        if policy_df.empty:
            return pd.DataFrame()
       
        # Clean up the policy data
        policy_df = policy_df.drop('attributes', axis=1, errors='ignore')
       
        # Handle nested fields safely - improved version
        def safe_get_nested_field(row, field_path):
            try:
                if '.' in field_path:
                    parts = field_path.split('.')
                    current = row
                    for part in parts:
                        if isinstance(current, dict) and part in current:
                            current = current[part]
                        else:
                            return ''
                    return current if current is not None else ''
                else:
                    return row.get(field_path, '') if row.get(field_path) is not None else ''
            except:
                return ''
       
        # Create column mappings
        policy_df['PolicyNumber'] = policy_df['Name']
        policy_df['PolicyName'] = policy_df['PolicyName']
       
        # Producer Identifier - improved logic to handle different data structures
        def get_producer_name(row):
            # Try Producer.Name first
            producer_name = safe_get_nested_field(row, 'Producer.Name')
            if producer_name:
                return producer_name
                
            # Try Producer_2__r.Name
            producer2_name = safe_get_nested_field(row, 'Producer_2__r.Name')
            if producer2_name:
                return producer2_name
                
            # Try direct access to nested structures
            if isinstance(row.get('Producer'), dict) and row.get('Producer', {}).get('Name'):
                return row['Producer']['Name']
                
            if isinstance(row.get('Producer_2__r'), dict) and row.get('Producer_2__r', {}).get('Name'):
                return row['Producer_2__r']['Name']
                
            return 'Unknown Producer'
        
        policy_df['ProducerIdentifier'] = policy_df.apply(get_producer_name, axis=1)
       
        policy_df['PolicyType'] = policy_df['PolicyType']
       
        # Writing Carrier Account Name
        policy_df['WritingCarrierName'] = policy_df.apply(lambda row:
            safe_get_nested_field(row, 'WritingCarrierAccount.Name'), axis=1)
       
        policy_df['TotalPolicyPremium'] = policy_df['Total_Policy_Premium__c']
       
        # Account Name
        policy_df['AccountName'] = policy_df.apply(lambda row:
            safe_get_nested_field(row, 'NameInsured.Name'), axis=1)
       
        # Convert dates
        policy_df['EffectiveDate'] = pd.to_datetime(policy_df['EffectiveDate'])
       
        # Convert premiums to numeric
        policy_df['PremiumAmount'] = pd.to_numeric(policy_df['PremiumAmount'], errors='coerce').fillna(0)
        policy_df['TaxesSurcharges'] = pd.to_numeric(policy_df['TaxesSurcharges'], errors='coerce').fillna(0)
        policy_df['TotalPolicyPremium'] = pd.to_numeric(policy_df['TotalPolicyPremium'], errors='coerce')
       
        # If TotalPolicyPremium is null, calculate it
        policy_df['TotalPolicyPremium'] = policy_df['TotalPolicyPremium'].fillna(
            policy_df['PremiumAmount'] + policy_df['TaxesSurcharges']
        )
       
        # Select final columns to return
        final_columns = [
            'PolicyNumber', 'PolicyName', 'ProducerIdentifier', 'PolicyType',
            'WritingCarrierName', 'TotalPolicyPremium', 'PremiumAmount',
            'TaxesSurcharges', 'EffectiveDate', 'AccountName', 'NameInsuredId'
        ]
       
        return policy_df[final_columns]
       
    except Exception as e:
        st.error(f"Error fetching insurance policy data: {str(e)}")
        return pd.DataFrame()


def get_external_referrer_data(sf, start_date, end_date, producer_filter=None):
    """Get external referrer data with optional producer filtering."""
    try:
        start_date_str = format_date_as_datetime_for_salesforce(start_date)
        end_date_str = format_end_date_as_datetime_for_salesforce(end_date)
       
        # Base filters
        base_filters = [
            f"EffectiveDate >= {start_date_str}",
            f"EffectiveDate <= {end_date_str}",
            "Status = 'Active'",
            "Business_Type_Reporting__c = 'New Business'",
            "NameInsuredId != null"
        ]
        
        # Producer filter
        producer_where_clause = ""
        if producer_filter and len(producer_filter) > 0:
            producer_ids = get_producer_ids_from_names(sf, producer_filter)
            if producer_ids:
                producer_conditions = []
                for producer_id in producer_ids:
                    producer_conditions.append(f"(ProducerId = '{producer_id}' OR Producer_2__c = '{producer_id}')")
                producer_where_clause = f"AND ({' OR '.join(producer_conditions)})"
       
        # Get policies with optional producer filtering
        policy_query = f"""
            SELECT
                Id,
                NameInsuredId
            FROM InsurancePolicy
            WHERE {' AND '.join(base_filters)}
            {producer_where_clause}
        """
       
        policy_results = sf.query_all(policy_query)
        if not policy_results['records']:
            return pd.DataFrame()
       
        policy_df = pd.DataFrame(policy_results['records'])
        account_ids = policy_df['NameInsuredId'].dropna().unique().tolist()
       
        if not account_ids:
            return pd.DataFrame()
       
        # Get Account data with external referrers
        account_sources = [
            'Boat Dealer', 'Employee Referral', 'Existing Client',
            'Financial Advisor / Estate Planner', 'Friend or Relative',
            'Influencer', 'Inspector', 'Lender', 'MM Lead', 'Marina',
            'Organically Prospected', 'Other', 'Other Insurance Agent', 'Realtor'
        ]
        account_source_list = ','.join([f"'{source}'" for source in account_sources])
       
        # Split account IDs into chunks
        account_chunks = [account_ids[i:i+200] for i in range(0, len(account_ids), 200)]
        account_data = []
       
        for chunk in account_chunks:
            account_ids_str = ','.join([f"'{acc_id}'" for acc_id in chunk])
           
            account_query = f"""
                SELECT
                    Id,
                    FinServ__ReferredByContact__r.Name
                FROM Account
                WHERE Id IN ({account_ids_str})
                AND FinServ__ReferredByContact__c != null
                AND AccountSource IN ({account_source_list})
            """
           
            account_results = sf.query_all(account_query)
            if account_results['records']:
                account_data.extend(account_results['records'])
       
        if not account_data:
            return pd.DataFrame()
       
        # Create referrer DataFrame
        referrer_data = []
        for record in account_data:
            if record.get('FinServ__ReferredByContact__r') and record['FinServ__ReferredByContact__r'].get('Name'):
                referrer_name = record['FinServ__ReferredByContact__r']['Name']
                referrer_data.append({
                    'AccountId': record['Id'],
                    'ReferredByContactName': referrer_name
                })
       
        if not referrer_data:
            return pd.DataFrame()
       
        referrer_df = pd.DataFrame(referrer_data)
        return referrer_df
       
    except Exception as e:
        st.error(f"Error fetching external referrer data: {str(e)}")
        return pd.DataFrame()


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


def get_top_external_referrers(referrer_df):
    """Get top 10 external referrers from external referrer data."""
    if referrer_df.empty:
        return pd.DataFrame()
   
    try:
        # Get external referrer counts
        external_referrer_counts = referrer_df['ReferredByContactName'].value_counts().head(10)
       
        if external_referrer_counts.empty:
            return pd.DataFrame()
       
        # Convert to DataFrame format
        referrer_data = []
        for referrer_name, count in external_referrer_counts.items():
            referrer_data.append({
                'ExternalReferrer': referrer_name,
                'PolicyCount': count
            })
       
        result_df = pd.DataFrame(referrer_data)
        return result_df
       
    except Exception as e:
        st.error(f"Error processing external referrers: {str(e)}")
        return pd.DataFrame()


def get_carrier_performance_enhanced(sf, start_date, end_date):
    """Get carrier performance with enhanced metrics and color coding."""
    try:
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


def get_producer_performance_data(sf, producer_name, start_date, end_date):
    """Get comprehensive performance data for a specific producer."""
    try:
        # Get policy data for this specific producer
        policy_df = get_insurance_policy_data(sf, start_date, end_date, [producer_name])
        
        if policy_df.empty:
            return None
            
        # Filter to ensure we only get data for this producer
        producer_policy_df = policy_df[policy_df['ProducerIdentifier'] == producer_name].copy()
        
        if producer_policy_df.empty:
            return None
        
        # Calculate key metrics
        total_policies = len(producer_policy_df)
        total_premium = producer_policy_df['TotalPolicyPremium'].sum()
        avg_premium = producer_policy_df['TotalPolicyPremium'].mean()
        
        # Policy type analysis
        policy_types = producer_policy_df['PolicyType'].value_counts()
        
        # Premium by policy type (for specialty analysis)
        premium_by_type = producer_policy_df.groupby('PolicyType')['TotalPolicyPremium'].sum().sort_values(ascending=False)
        
        # Recent policies (last 10)
        recent_policies = producer_policy_df.nlargest(10, 'EffectiveDate')[
            ['PolicyNumber', 'PolicyName', 'PolicyType', 'TotalPolicyPremium', 'EffectiveDate', 'AccountName']
        ].copy()
        
        # Weekly trend data
        producer_policy_df['week_start'] = producer_policy_df['EffectiveDate'].dt.to_period('W').dt.start_time
        weekly_premium = producer_policy_df.groupby('week_start')['TotalPolicyPremium'].sum().reset_index()
        weekly_premium['week_label'] = weekly_premium['week_start'].dt.strftime('Week of %b %d')
        
        # Business performance trends (top policy types)
        top_policy_types = policy_types.head(5).index.tolist()
        trend_data = []
        
        for policy_type in top_policy_types:
            type_data = producer_policy_df[producer_policy_df['PolicyType'] == policy_type]
            if not type_data.empty:
                type_weekly = type_data.groupby('week_start')['TotalPolicyPremium'].sum().reset_index()
                type_weekly['PolicyType'] = policy_type
                trend_data.append(type_weekly)
        
        trend_df = pd.concat(trend_data, ignore_index=True) if trend_data else pd.DataFrame()
        
        # Least active business types (bottom 5 with at least 1 policy)
        least_active_types = policy_types.tail(5)
        
        return {
            'total_policies': total_policies,
            'total_premium': total_premium,
            'avg_premium': avg_premium,
            'policy_types': policy_types,
            'premium_by_type': premium_by_type,
            'recent_policies': recent_policies,
            'weekly_premium': weekly_premium,
            'trend_data': trend_df,
            'least_active_types': least_active_types,
            'policy_df': producer_policy_df
        }
        
    except Exception as e:
        st.error(f"Error fetching producer performance data: {str(e)}")
        return None


def create_producer_overview_card(producer_name, producer_data):
    """Create modern gradient overview card for producer."""
    if not producer_data:
        return
        
    st.markdown(f"""
    <div class="producer-overview-card">
        <h2>🎯 {producer_name}</h2>
        <div style="display: flex; flex-wrap: wrap; gap: 1rem;">
            <div class="producer-metric">
                <span class="producer-metric-value">{producer_data['total_policies']:,}</span>
                <span class="producer-metric-label">Total Policies</span>
            </div>
            <div class="producer-metric">
                <span class="producer-metric-value">${producer_data['total_premium']:,.0f}</span>
                <span class="producer-metric-label">Total Premium</span>
            </div>
            <div class="producer-metric">
                <span class="producer-metric-value">${producer_data['avg_premium']:,.0f}</span>
                <span class="producer-metric-label">Average Premium</span>
            </div>
            <div class="producer-metric">
                <span class="producer-metric-value">{len(producer_data['policy_types']):,}</span>
                <span class="producer-metric-label">Policy Types</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_policy_type_donut_chart(policy_types, title="Policy Type Distribution"):
    """Create policy type distribution donut chart with percentages."""
    if policy_types.empty:
        return None
        
    colors = ['#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#84cc16', '#f97316']
    
    fig = go.Figure(data=[go.Pie(
        labels=policy_types.index,
        values=policy_types.values,
        hole=0.5,
        marker=dict(
            colors=colors[:len(policy_types)],
            line=dict(color='#ffffff', width=3)
        ),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=11, family="Inter, sans-serif"),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, family="Inter, sans-serif", color='#111827')
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(size=10, family="Inter, sans-serif")
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=50, l=50, r=150),
        height=400
    )
    
    return fig


def create_premium_specialty_donut_chart(premium_by_type, title="Premium by Specialty"):
    """Create premium specialty donut chart."""
    if premium_by_type.empty:
        return None
        
    colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
    
    fig = go.Figure(data=[go.Pie(
        labels=premium_by_type.index,
        values=premium_by_type.values,
        hole=0.5,
        marker=dict(
            colors=colors[:len(premium_by_type)],
            line=dict(color='#ffffff', width=3)
        ),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=11, family="Inter, sans-serif"),
        hovertemplate='<b>%{label}</b><br>Premium: $%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text=title,
            x=0.5,
            font=dict(size=16, family="Inter, sans-serif", color='#111827')
        ),
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05,
            font=dict(size=10, family="Inter, sans-serif")
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=50, b=50, l=50, r=150),
        height=400
    )
    
    return fig


def create_specialty_section(premium_by_type):
    """Create top specialties section with premium breakdown."""
    if premium_by_type.empty:
        return
        
    st.markdown("""
    <div class="specialty-section">
        <h3>🏆 Top Specialties by Premium</h3>
    """, unsafe_allow_html=True)
    
    for specialty, premium in premium_by_type.head(5).items():
        percentage = (premium / premium_by_type.sum()) * 100
        st.markdown(f"""
        <div class="specialty-item">
            <span class="specialty-name">{specialty}</span>
            <span class="specialty-value">${premium:,.0f} ({percentage:.1f}%)</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def create_business_performance_trends_chart(trend_df):
    """Create business performance trends line chart for top policy types."""
    if trend_df.empty:
        return None
        
    fig = px.line(trend_df, 
                  x='week_start', 
                  y='TotalPolicyPremium',
                  color='PolicyType',
                  title="Business Performance Trends (Top Policy Types)",
                  line_shape='spline')
    
    fig.update_traces(line=dict(width=3), marker=dict(size=6))
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Inter",
        title_font=dict(size=16, color='#111827'),
        xaxis_title="Week",
        yaxis_title="Premium ($)",
        yaxis_tickformat='$,.0f',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=400
    )
    
    return fig


def create_least_active_chart(least_active_types):
    """Create least active business types bar chart."""
    if least_active_types.empty:
        return None
        
    fig = px.bar(x=least_active_types.values,
                 y=least_active_types.index,
                 orientation='h',
                 title="Least Active Business Types",
                 color=least_active_types.values,
                 color_continuous_scale='Reds')
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Inter",
        title_font=dict(size=16, color='#111827'),
        coloraxis_showscale=False,
        xaxis_title="Policy Count",
        yaxis_title="Policy Type",
        height=300
    )
    
    return fig


def create_individual_producer_tab(sf, producer_name, filters):
    """Create comprehensive individual producer tab."""
    st.markdown(f'<div class="section-header">📊 {producer_name} Performance Dashboard</div>', unsafe_allow_html=True)
    
    # Get producer performance data
    producer_data = get_producer_performance_data(sf, producer_name, filters['start_date'], filters['end_date'])
    
    if not producer_data:
        st.warning(f"No data available for {producer_name} in the selected date range.")
        return
    
    # Producer overview card
    create_producer_overview_card(producer_name, producer_data)
    
    # First row: Policy type distribution and Premium specialty
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="performance-container">', unsafe_allow_html=True)
        fig = create_policy_type_donut_chart(producer_data['policy_types'])
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="performance-container">', unsafe_allow_html=True)
        fig = create_premium_specialty_donut_chart(producer_data['premium_by_type'])
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Top specialties section
    create_specialty_section(producer_data['premium_by_type'])
    
    # Second row: Business performance trends and Least active types
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="performance-container">', unsafe_allow_html=True)
        if not producer_data['trend_data'].empty:
            fig = create_business_performance_trends_chart(producer_data['trend_data'])
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient data for trend analysis")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="performance-container">', unsafe_allow_html=True)
        fig = create_least_active_chart(producer_data['least_active_types'])
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent policies table
    st.markdown("### 📋 Recent Policies")
    st.markdown('<div class="recent-policies">', unsafe_allow_html=True)
    
    # Format the recent policies data for display
    recent_display = producer_data['recent_policies'].copy()
    recent_display['TotalPolicyPremium'] = recent_display['TotalPolicyPremium'].apply(lambda x: f"${x:,.0f}")
    recent_display['EffectiveDate'] = recent_display['EffectiveDate'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        recent_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            'PolicyNumber': 'Policy #',
            'PolicyName': 'Policy Name',
            'PolicyType': 'Type',
            'TotalPolicyPremium': 'Premium',
            'EffectiveDate': 'Effective Date',
            'AccountName': 'Account'
        }
    )
    
    st.markdown('</div>', unsafe_allow_html=True)


def create_enhanced_sidebar(sf):
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
   
    # Producer selection
    st.sidebar.subheader("👥 Producer Selection")
    available_producers = get_available_producers(sf)
    selected_producers = st.sidebar.multiselect(
        "Select Producers",
        options=available_producers,
        default=[]
    )
   
    # Debug information
    if available_producers:
        st.sidebar.markdown('<div class="debug-info">', unsafe_allow_html=True)
        st.sidebar.write(f"**Debug Info:**")
        st.sidebar.write(f"Total available producers: {len(available_producers)}")
        if selected_producers:
            st.sidebar.write(f"Selected producers: {len(selected_producers)}")
            for prod in selected_producers[:5]:  # Show first 5
                st.sidebar.write(f"  • {prod}")
            if len(selected_producers) > 5:
                st.sidebar.write(f"  • ... and {len(selected_producers) - 5} more")
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
   
    # Business type filter
    st.sidebar.subheader("🏢 Business Filters")
    business_types = st.sidebar.multiselect(
        "Business Types",
        options=["Personal Lines", "Commercial Lines", "Both"],
        default=["Both"]
    )
   
    new_business_only = st.sidebar.checkbox("New Business Only", value=True)
   
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
        'selected_producers': selected_producers,
        'business_types': business_types,
        'new_business_only': new_business_only,
        'min_premium': min_premium,
        'max_premium': max_premium,
        'show_percentages': show_percentages,
        'chart_theme': chart_theme,
        'refresh_data': refresh_data,
        'export_data': export_data
    }


def display_modern_text_metrics(df):
    """Display modern premium metrics with enhanced styling."""
    if df.empty:
        total_premium = 0
        policy_count = 0
        avg_premium = 0
    else:
        total_premium = df['TotalPolicyPremium'].sum()
        policy_count = len(df)
        avg_premium = df['TotalPolicyPremium'].mean()
   
    # Display as modern formatted text
    col1, col2, col3 = st.columns(3)
   
    with col1:
        st.markdown(f"""
        <div class="text-metric">
            <h3>${total_premium:,.0f}</h3>
            <p>Total Premium Written</p>
        </div>
        """, unsafe_allow_html=True)
   
    with col2:
        st.markdown(f"""
        <div class="text-metric">
            <h3>{policy_count:,}</h3>
            <p>Policies Issued</p>
        </div>
        """, unsafe_allow_html=True)
   
    with col3:
        st.markdown(f"""
        <div class="text-metric">
            <h3>${avg_premium:,.0f}</h3>
            <p>Average Premium</p>
        </div>
        """, unsafe_allow_html=True)


def create_overview_tab(sf, filters):
    """Create enhanced overview tab with modern styling."""
    st.markdown('<div class="section-header">Business Overview</div>', unsafe_allow_html=True)

    # Get insurance policy data with optional producer filtering
    selected_producers = filters['selected_producers']
    policy_df = get_insurance_policy_data(sf, filters['start_date'], filters['end_date'], selected_producers)
    
    # Get external referrer data with same filtering
    referrer_df = get_external_referrer_data(sf, filters['start_date'], filters['end_date'], selected_producers)

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
        external_referrers = get_top_external_referrers(referrer_df)
        if not external_referrers.empty:
            top_referrer_count = external_referrers.iloc[0]['PolicyCount']
            top_referrer_name = external_referrers.iloc[0]['ExternalReferrer']
        else:
            top_referrer_count = 0
            top_referrer_name = 'N/A'
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; font-size: 2rem; color: #10b981;">{top_referrer_count}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-weight: 500;">Top External Referrer</p>
            <p style="margin: 0.25rem 0 0 0; color: #9ca3af; font-size: 0.9rem;">{top_referrer_name}</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        carrier_df = get_carrier_performance_enhanced(sf, filters['start_date'], filters['end_date'])
        if not carrier_df.empty:
            top_carrier = carrier_df.iloc[0]['Carrier']
            top_close_rate = carrier_df.iloc[0]['Close_Rate']
        else:
            top_carrier = 'N/A'
            top_close_rate = 0
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; font-size: 2rem; color: #8b5cf6;">{top_close_rate:.1f}%</h3>
            <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-weight: 500;">Top Carrier Close Rate</p>
            <p style="margin: 0.25rem 0 0 0; color: #9ca3af; font-size: 0.9rem;">{top_carrier}</p>
        </div>
        """, unsafe_allow_html=True)

    # Only show Premium Summary if there's policy data
    if not policy_df.empty:
        st.markdown("### 💎 Premium Summary")
        display_modern_text_metrics(policy_df)

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
            # Only show external referrer chart if there's referrer data
            if not referrer_df.empty:
                external_referrers = get_top_external_referrers(referrer_df)
                if not external_referrers.empty:
                    fig = px.bar(
                        external_referrers,
                        x='PolicyCount',
                        y='ExternalReferrer',
                        orientation='h',
                        title="Top 10 External Referrers",
                        color='PolicyCount',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_family="Inter",
                        title_font=dict(size=16, color='#111827'),
                        coloraxis_showscale=False,
                        xaxis_title="Policy Count",
                        yaxis_title="External Referrer"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No external referrer data available.")
            else:
                st.info("No external referrer data available.")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        if selected_producers:
            st.info(f"No policy data available for selected producers: {', '.join(selected_producers)}")
        else:
            st.info("No policy data available for the selected period. Please select producers from the sidebar.")


def create_performance_tab(sf, filters):
    """Create enhanced performance tab with modern styling."""
    st.markdown('<div class="section-header">Performance Metrics</div>', unsafe_allow_html=True)

    # Get insurance policy data with optional producer filtering
    selected_producers = filters['selected_producers']
    policy_df = get_insurance_policy_data(sf, filters['start_date'], filters['end_date'], selected_producers)

    if not policy_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            # Weekly premium trend
            policy_df['week_start'] = policy_df['EffectiveDate'].dt.to_period('W').dt.start_time
            weekly_premium = policy_df.groupby('week_start')['TotalPolicyPremium'].sum().reset_index()
            weekly_premium['week_label'] = weekly_premium['week_start'].dt.strftime('Week of %b %d')

            fig = px.line(weekly_premium,
                         x='week_label',
                         y='TotalPolicyPremium',
                         title="Weekly Premium Trend",
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
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            # Enhanced carrier performance with close rates
            carrier_df = get_carrier_performance_enhanced(sf, filters['start_date'], filters['end_date'])
            
            if not carrier_df.empty:
                # Create scatter plot with carrier performance data
                fig = px.scatter(carrier_df,
                               x='Total_Quotes',
                               y='Close_Rate',
                               size='Won_Quotes',
                               hover_name='Carrier',
                               color='Close_Rate',
                               color_continuous_scale='RdYlGn',
                               title="Carrier Performance: Close Rate vs Volume",
                               hover_data={
                                   'Total_Quotes': True,
                                   'Won_Quotes': True,
                                   'Close_Rate': ':.1f%'
                               })
                
                fig.update_traces(marker=dict(line=dict(width=2, color='#ffffff')))
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_family="Inter",
                    title_font=dict(size=16, color='#111827'),
                    xaxis_title="Total Quotes",
                    yaxis_title="Close Rate (%)",
                    yaxis_tickformat='.1f',
                    coloraxis_colorbar=dict(title="Close Rate (%)")
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No carrier performance data available for the selected period.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Enhanced carrier performance table
        if not carrier_df.empty:
            st.markdown("### 🏆 Carrier Performance Ranking (Based on Close Rates)")
            
            # Format the dataframe for display
            display_df = carrier_df.copy()
            display_df['Close_Rate_Display'] = display_df['Close_Rate'].apply(lambda x: f"{x:.1f}%")
            
            # Add performance tier based on close rate
            display_df['Performance_Tier'] = display_df['Rank'].apply(
                lambda x: '🥇 Top Performer' if x <= len(display_df) * 0.3
                else '🥈 Average Performer' if x <= len(display_df) * 0.6
                else '🥉 Needs Improvement'
            )
            
            # Select and reorder columns for display
            display_cols = ['Rank', 'Carrier', 'Total_Quotes', 'Won_Quotes', 'Close_Rate_Display', 'Performance_Tier']
            column_names = ['Rank', 'Carrier', 'Total Quotes', 'Won Quotes', 'Close Rate', 'Performance Tier']
            
            styled_df = display_df[display_cols].copy()
            styled_df.columns = column_names
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True
            )
        
        # Writing Carrier Summary
        st.markdown("### 📈 Writing Carrier Summary (Policy Volume)")
        
        # Writing carrier performance from policy data
        carrier_summary = policy_df.groupby('WritingCarrierName').agg({
            'TotalPolicyPremium': ['count', 'sum', 'mean']
        }).round(0)
        
        carrier_summary.columns = ['Policy_Count', 'Total_Premium', 'Average_Premium']
        carrier_summary = carrier_summary.reset_index()
        carrier_summary = carrier_summary.sort_values('Total_Premium', ascending=False)
        carrier_summary['Rank'] = range(1, len(carrier_summary) + 1)
        
        # Add performance tier
        total_carriers = len(carrier_summary)
        carrier_summary['Performance_Tier'] = carrier_summary['Rank'].apply(
            lambda x: '🥇 Top Volume' if x <= total_carriers * 0.3
            else '🥈 Mid Volume' if x <= total_carriers * 0.6
            else '🥉 Lower Volume'
        )
        
        # Format premium columns
        carrier_summary['Total_Premium'] = carrier_summary['Total_Premium'].apply(lambda x: f"${x:,.0f}")
        carrier_summary['Average_Premium'] = carrier_summary['Average_Premium'].apply(lambda x: f"${x:,.0f}")
        
        display_cols = ['Rank', 'WritingCarrierName', 'Policy_Count', 'Total_Premium', 'Average_Premium', 'Performance_Tier']
        column_names = ['Rank', 'Writing Carrier', 'Policy Count', 'Total Premium', 'Average Premium', 'Performance Tier']
        
        styled_df = carrier_summary[display_cols].copy()
        styled_df.columns = column_names
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        if selected_producers:
            st.info(f"No policy data available for selected producers: {', '.join(selected_producers)}")
        else:
            st.info("No policy data available for the selected period. Please select producers from the sidebar.")


def create_producer_performance_tab(sf, filters):
    """Create producer performance tab with optional producer filtering."""
    st.markdown('<div class="section-header">Producer Performance</div>', unsafe_allow_html=True)

    # Get insurance policy data with optional producer filtering
    selected_producers = filters['selected_producers']
    policy_df = get_insurance_policy_data(sf, filters['start_date'], filters['end_date'], selected_producers)

    if not policy_df.empty:
        # Producer Performance Summary
        if selected_producers:
            st.markdown(f"### 👨‍💼 Selected Producer Performance ({len(selected_producers)} producers)")
        else:
            st.markdown("### 👨‍💼 All Producer Performance")
        
        # Get producer performance data
        producer_performance = policy_df.groupby('ProducerIdentifier').agg({
            'TotalPolicyPremium': ['count', 'sum', 'mean'],
            'PolicyType': 'nunique'
        }).round(0)
        
        producer_performance.columns = ['Policies', 'Total_Premium', 'Avg_Premium', 'Policy_Types']
        producer_performance = producer_performance.reset_index()
        producer_performance = producer_performance.sort_values('Total_Premium', ascending=False)
        producer_performance['Rank'] = range(1, len(producer_performance) + 1)
        
        # Add performance tier
        total_producers = len(producer_performance)
        producer_performance['Performance_Tier'] = producer_performance['Rank'].apply(
            lambda x: '🥇 Top Producer' if x <= total_producers * 0.2
            else '🥈 High Producer' if x <= total_producers * 0.4
            else '🥉 Average Producer' if x <= total_producers * 0.6
            else '📈 Developing Producer'
        )
        
        # Format premium columns
        producer_performance['Total_Premium'] = producer_performance['Total_Premium'].apply(lambda x: f"${x:,.0f}")
        producer_performance['Avg_Premium'] = producer_performance['Avg_Premium'].apply(lambda x: f"${x:,.0f}")
        
        # Display the table
        st.dataframe(
            producer_performance,
            use_container_width=True,
            hide_index=True
        )
        
        # Producer charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            # Top 10 producers by premium
            top_producers = policy_df.groupby('ProducerIdentifier')['TotalPolicyPremium'].sum().nlargest(10).reset_index()
            
            fig = px.bar(top_producers,
                        x='TotalPolicyPremium',
                        y='ProducerIdentifier',
                        orientation='h',
                        title="Top 10 Producers by Premium",
                        color='TotalPolicyPremium',
                        color_continuous_scale='Blues')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                title_font=dict(size=16, color='#111827'),
                coloraxis_showscale=False,
                xaxis_title="Total Premium ($)",
                yaxis_title="Producer",
                xaxis_tickformat='$,.0f'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            # Policy type distribution
            policy_type_dist = policy_df['PolicyType'].value_counts()
            
            title_suffix = f" (Selected Producers)" if selected_producers else " (All Producers)"
            fig = px.pie(values=policy_type_dist.values,
                        names=policy_type_dist.index,
                        title=f"Policy Type Distribution{title_suffix}",
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family="Inter",
                title_font=dict(size=16, color='#111827')
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        if selected_producers:
            st.info(f"No policy data available for selected producers: {', '.join(selected_producers)}")
        else:
            st.info("No policy data available for the selected period. Please select producers from the sidebar.")


# Main Dashboard
def main():
    st.markdown('<h1 class="main-header">Insurance Analytics Dashboard</h1>', unsafe_allow_html=True)

    # Auto-connect to Salesforce first
    sf = get_salesforce_connection()

    if sf is None:
        st.stop()

    # Enhanced sidebar with modern styling (pass sf for producer list)
    filters = create_enhanced_sidebar(sf)

    # Create dynamic tabs based on selected producers
    tab_names = ["📊 Overview", "🎯 Performance", "👥 Producer Performance"]
    
    # Add individual producer tabs if producers are selected
    selected_producers = filters['selected_producers']
    if selected_producers:
        for producer in selected_producers:
            tab_names.append(f"👤 {producer}")

    # Create tabs dynamically
    tabs = st.tabs(tab_names)

    # Overview Tab
    with tabs[0]:
        create_overview_tab(sf, filters)

    # Performance Tab
    with tabs[1]:
        create_performance_tab(sf, filters)

    # Producer Performance Tab
    with tabs[2]:
        create_producer_performance_tab(sf, filters)

    # Individual Producer Tabs
    if selected_producers:
        for i, producer in enumerate(selected_producers, start=3):
            with tabs[i]:
                create_individual_producer_tab(sf, producer, filters)


if __name__ == "__main__":
    main()


