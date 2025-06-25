import streamlit as st
from simple_salesforce import Salesforce
import os
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime

# Load environment variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Account Manager Workload Dashboard",
    page_icon="⚖️",
    layout="wide",
)

# Define workload thresholds
def get_workload_thresholds():
    """Return workload threshold configuration."""
    return {
        "extreme": {"min": 400, "color": "#e74c3c", "icon": "🔴", "label": "Extreme"},
        "very_high": {"min": 350, "color": "#ff6b35", "icon": "🟠", "label": "Very High"},
        "high": {"min": 200, "color": "#f39c12", "icon": "🟡", "label": "High"},
        "optimal": {"min": 100, "color": "#2ecc71", "icon": "🟢", "label": "Optimal"},
        "low": {"min": 0, "color": "#3498db", "icon": "🔵", "label": "Low"}
    }

def get_workload_category(count, thresholds):
    """Determine workload category based on policy count."""
    if count >= thresholds["extreme"]["min"]:
        return "extreme"
    elif count >= thresholds["very_high"]["min"]:
        return "very_high"
    elif count >= thresholds["high"]["min"]:
        return "high"
    elif count >= thresholds["optimal"]["min"]:
        return "optimal"
    else:
        return "low"

# Define core policy types
def get_core_policy_types():
    """Return a list of core policy types for analysis."""
    return ["Personal Auto", "Commercial Auto", "Flood", "Flood - CL", "Flood - PL", "Homeowners", "Umbrella"]

# Function to get current ISO week
def get_current_iso_week():
    """Calculate the ISO week number for the current date."""
    today = datetime.date.today()
    year, week_num, _ = today.isocalendar()
    return year, week_num

# Function to connect to Salesforce and query Insurance Policy data
# Function to connect to Salesforce and query Insurance Policy data
def connect_to_salesforce(start_date=None, end_date=None):
    """Connect to Salesforce and execute SOQL queries for Insurance Policy data."""
    try:
        # Debug: Check if environment variables are loaded
        username = os.getenv("SF_USERNAME_PRO")
        password = os.getenv("SF_PASSWORD_PRO")
        security_token = os.getenv("SF_SECURITY_TOKEN_PRO")
        
        # Add debug information
        if not username or not password or not security_token:
            st.error("❌ Missing Salesforce credentials in environment variables")
            st.info(f"Username exists: {bool(username)}, Password exists: {bool(password)}, Token exists: {bool(security_token)}")
            return pd.DataFrame()
        
        # Salesforce connection using environment variables
        sf = Salesforce(
            username=username,
            password=password,  
            security_token=security_token,
        )
        
        # Test connection
        sf.describe()
        st.success("✅ Successfully connected to Salesforce")

        # Prepare date filter for ExpirationDate
        date_filter = ""
        if start_date and end_date:
            start_date_str = start_date.strftime('%Y-%m-%dT00:00:00Z')
            end_date_str = end_date.strftime('%Y-%m-%dT23:59:59Z')
            date_filter = f"AND ExpirationDate >= {start_date_str} AND ExpirationDate <= {end_date_str}"

        # Query Account Manager information with error handling
        account_query = """
            SELECT 
                Id, 
                Name,
                Account_Manager__c,
                Account_Manager__r.Name
            FROM Account
            WHERE Account_Manager__c != null
        """

        account_manager_map = {}
        try:
            # Execute account query
            account_results = sf.query_all(account_query)
            
            # Check if results exist
            if account_results and 'records' in account_results:
                # Create a dictionary to map Account IDs to their Account Managers
                for record in account_results['records']:
                    if record:  # Check if record is not None
                        account_id = record.get('Id')
                        # Safely get the Account Manager name
                        account_manager_relation = record.get('Account_Manager__r')
                        if account_manager_relation and isinstance(account_manager_relation, dict):
                            producer_name = account_manager_relation.get('Name', 'Not Assigned')
                        else:
                            producer_name = 'Not Assigned'
                        
                        if account_id:
                            account_manager_map[account_id] = producer_name
                            
                st.info(f"📊 Found {len(account_manager_map)} accounts with account managers")
            else:
                st.warning("⚠️ No account records found or empty result set")

        except Exception as e:
            st.warning(f"⚠️ Error querying accounts: {str(e)}")
            account_manager_map = {}

        # Query Insurance Policy records with Account relationship
        policy_query = f"""
            SELECT 
                Id,
                Name,
                PolicyType,
                EffectiveDate,
                ExpirationDate,
                Status,
                NameInsuredId,
                NameInsured.Name,
                NameInsured.Account_Manager__c,
                NameInsured.Account_Manager__r.Name
            FROM InsurancePolicy
            WHERE ExpirationDate != null
            AND Status IN ('Active', 'Renewing', 'Pending Cancellation', 'Non-Renewal', 'Reinstating', 'Reinstated')
            {date_filter}
            ORDER BY ExpirationDate DESC
           
        """

        try:
            policy_results = sf.query_all(policy_query)
            
            # Check if policy results exist
            if not policy_results or 'records' not in policy_results:
                st.warning("⚠️ No insurance policy records found")
                return pd.DataFrame()
                
            if not policy_results['records']:
                st.warning("⚠️ Empty insurance policy record set")
                return pd.DataFrame()
                
            st.info(f"📊 Found {len(policy_results['records'])} insurance policies")

        except Exception as e:
            st.error(f"❌ Error querying insurance policies: {str(e)}")
            return pd.DataFrame()

        # Process results into a DataFrame with better error handling
        data = []
        for record in policy_results['records']:
            if not record:  # Skip None records
                continue
                
            try:
                policy_name = record.get('Name', 'Unknown Policy')
                policy_type = record.get('PolicyType', 'Not Specified')
                status = record.get('Status', 'Unknown')
                effective_date = record.get('EffectiveDate')
                expiration_date = record.get('ExpirationDate')
                
                # Get account information safely
                account_id = record.get('NameInsuredId')
                
                # Safe account name extraction
                name_insured = record.get('NameInsured')
                account_name = 'Unknown Account'
                if name_insured and isinstance(name_insured, dict):
                    account_name = name_insured.get('Name', 'Unknown Account')
                
                # Get account manager - try multiple sources
                account_manager = "Not Assigned"
                
                # Try from the policy relationship first
                if (name_insured and isinstance(name_insured, dict) and 
                    name_insured.get('Account_Manager__r') and 
                    isinstance(name_insured.get('Account_Manager__r'), dict)):
                    account_manager = name_insured['Account_Manager__r'].get('Name', 'Not Assigned')
                # Fallback to account_manager_map
                elif account_id and account_id in account_manager_map:
                    account_manager = account_manager_map[account_id]

                data.append({
                    'PolicyId': record.get('Id'),
                    'PolicyName': policy_name,
                    'PolicyType': policy_type,
                    'Status': status,
                    'EffectiveDate': effective_date,
                    'ExpirationDate': expiration_date,
                    'AccountId': account_id,
                    'AccountName': account_name,
                    'AccountManager': account_manager
                })
                
            except Exception as e:
                st.warning(f"⚠️ Error processing record {record.get('Id', 'Unknown')}: {str(e)}")
                continue

        # Create DataFrame
        df = pd.DataFrame(data)
        
        if df.empty:
            st.warning("⚠️ No valid policy data could be processed")
            return df
            
        # Convert dates to datetime with error handling
        try:
            df['EffectiveDate'] = pd.to_datetime(df['EffectiveDate'], errors='coerce')
            df['ExpirationDate'] = pd.to_datetime(df['ExpirationDate'], errors='coerce')
            
            # Add month columns for analysis
            df['EffectiveMonth'] = df['EffectiveDate'].dt.strftime('%Y-%m')
            df['ExpirationMonth'] = df['ExpirationDate'].dt.strftime('%Y-%m')
            
            st.success(f"✅ Successfully processed {len(df)} insurance policies")
            
        except Exception as e:
            st.error(f"❌ Error converting dates: {str(e)}")
            return pd.DataFrame()

        return df

    except Exception as e:
        st.error(f"❌ Error connecting to Salesforce: {str(e)}")
        # Add more detailed error information
        import traceback
        st.error(f"Detailed error: {traceback.format_exc()}")
        return pd.DataFrame()

# Streamlit UI
st.title("⚖️ Account Manager Workload Dashboard")
st.markdown("*Insurance Policy Distribution & Workload Analysis*")

# Get current date and ISO week information
today = datetime.datetime.today()
iso_year, iso_week = get_current_iso_week()

# Display current date
st.info(f"📅 Today: {today.strftime('%A, %B %d, %Y')} | Week {iso_week} of {iso_year}")

# Sidebar for user interaction
st.sidebar.header("🎛️ Dashboard Controls")

# Threshold configuration
thresholds = get_workload_thresholds()
st.sidebar.markdown("### ⚖️ Workload Thresholds")
st.sidebar.info(f"""
**Current Thresholds:**
- {thresholds['extreme']['icon']} Extreme: ≥{thresholds['extreme']['min']} policies
- {thresholds['very_high']['icon']} Very High: ≥{thresholds['very_high']['min']} policies  
- {thresholds['high']['icon']} High: ≥{thresholds['high']['min']} policies
- {thresholds['optimal']['icon']} Optimal: ≥{thresholds['optimal']['min']} policies
- {thresholds['low']['icon']} Low: <{thresholds['optimal']['min']} policies
""")

# Date range selection
st.sidebar.subheader("📅 Date Range Selection")
date_range_type = st.sidebar.radio(
    "Select Date Range Type (by Expiration Date)",
    ["Predefined", "Custom"]
)

# Date range logic
if date_range_type == "Predefined":
    time_period = st.sidebar.selectbox(
        "Select Time Period",
        options=["Next 30 Days", "Next 60 Days", "Next 90 Days", "Current Quarter", "Next Quarter", "Current Year"],
        index=0
    )
    
    # Determine dates based on selection
    if time_period == "Next 30 Days":
        start_date = today.date()
        end_date = today.date() + datetime.timedelta(days=30)
    elif time_period == "Next 60 Days":
        start_date = today.date()
        end_date = today.date() + datetime.timedelta(days=60)
    elif time_period == "Next 90 Days":
        start_date = today.date()
        end_date = today.date() + datetime.timedelta(days=90)
    elif time_period == "Current Quarter":
        current_quarter = (today.month - 1) // 3 + 1
        start_date = datetime.date(today.year, (current_quarter - 1) * 3 + 1, 1)
        if current_quarter == 4:
            end_date = datetime.date(today.year, 12, 31)
        else:
            end_date = datetime.date(today.year, current_quarter * 3 + 1, 1) - datetime.timedelta(days=1)
    elif time_period == "Next Quarter":
        current_quarter = (today.month - 1) // 3 + 1
        next_quarter = current_quarter + 1 if current_quarter < 4 else 1
        next_year = today.year if current_quarter < 4 else today.year + 1
        start_date = datetime.date(next_year, (next_quarter - 1) * 3 + 1, 1)
        if next_quarter == 4:
            end_date = datetime.date(next_year, 12, 31)
        else:
            end_date = datetime.date(next_year, next_quarter * 3 + 1, 1) - datetime.timedelta(days=1)
    else:  # Current Year
        start_date = datetime.date(today.year, 1, 1)
        end_date = datetime.date(today.year, 12, 31)
else:
    # Custom date range
    start_date = st.sidebar.date_input(
        "Start Date (Expiration)", 
        value=today.date(),
        min_value=datetime.date(2020, 1, 1)
    )
    end_date = st.sidebar.date_input(
        "End Date (Expiration)", 
        value=today.date() + datetime.timedelta(days=90),
        min_value=start_date
    )

    # Validate dates
    if start_date > end_date:
        st.sidebar.error("Start date must be before or equal to end date.")
        start_date, end_date = end_date, start_date



# View options
view_by = st.sidebar.radio(
    "📊 View Breakdown By",
    ["Workload Overview", "Policy Type Analysis", "Account Manager Details", "Expiration Timeline"]
)

# Additional options
show_data_table = st.sidebar.checkbox("📋 Show Data Tables", value=True)
show_core_lines_only = st.sidebar.checkbox("🎯 Focus on Core Lines Only", value=False)

# Fetch data
with st.spinner('🔄 Fetching policy data from Salesforce...'):
    df = connect_to_salesforce(start_date, end_date)

if not df.empty:
    # Filter for core lines if requested
    if show_core_lines_only:
        core_types = get_core_policy_types()
        df = df[df['PolicyType'].isin(core_types)]
        st.info(f"🎯 Showing core policy types only: {', '.join(core_types)}")

    # Display reporting period
    st.subheader("📊 Reporting Period")
    st.info(f"**Expiration Date Range:** {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}")

    # Overall summary metrics
    st.subheader("📈 Policy Portfolio Summary")
    col1, col2, col3, col4 = st.columns(4)

    total_policies = len(df)
    active_policies = len(df[df['Status'] == 'Active'])
    unique_accounts = df['AccountId'].nunique()
    unique_managers = df['AccountManager'].nunique()

    with col1:
        st.metric("Total Policies", f"{total_policies:,}")
    with col2:
        st.metric("Active Policies", f"{active_policies:,}")
    with col3:
        st.metric("Unique Accounts", f"{unique_accounts:,}")
    with col4:
        st.metric("Account Managers", f"{unique_managers:,}")

    # Workload Overview
    if view_by == "Workload Overview":
        st.header("⚖️ Account Manager Workload Distribution")

        # Calculate workload by account manager
        workload_df = df.groupby('AccountManager').agg({
            'PolicyId': 'count',
            'PolicyType': lambda x: ', '.join(x.value_counts().head(3).index.tolist())
        }).reset_index()
        workload_df.columns = ['AccountManager', 'PolicyCount', 'TopPolicyTypes']

        # Add workload categories
        workload_df['WorkloadCategory'] = workload_df['PolicyCount'].apply(
            lambda x: get_workload_category(x, thresholds)
        )
        workload_df['CategoryColor'] = workload_df['WorkloadCategory'].apply(
            lambda x: thresholds[x]['color']
        )
        workload_df['CategoryIcon'] = workload_df['WorkloadCategory'].apply(
            lambda x: thresholds[x]['icon']
        )

        # Sort by policy count
        workload_df = workload_df.sort_values('PolicyCount', ascending=False)

        # Workload distribution chart
        fig = px.bar(
            workload_df.head(15),
            x="AccountManager",
            y="PolicyCount",
            color="WorkloadCategory",
            title="Policy Workload by Account Manager (Top 15)",
            color_discrete_map={
                "extreme": thresholds["extreme"]["color"],
                "very_high": thresholds["very_high"]["color"],
                "high": thresholds["high"]["color"],
                "optimal": thresholds["optimal"]["color"],
                "low": thresholds["low"]["color"]
            },
            text="PolicyCount"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            xaxis_title="Account Manager",
            yaxis_title="Number of Policies",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)

        # Workload category distribution
        st.subheader("📊 Workload Category Distribution")
        category_counts = workload_df['WorkloadCategory'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart of workload categories
            fig = px.pie(
                values=category_counts.values,
                names=[thresholds[cat]['label'] for cat in category_counts.index],
                title="Account Managers by Workload Category",
                color_discrete_map={
                    thresholds[cat]['label']: thresholds[cat]['color'] 
                    for cat in category_counts.index
                }
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Summary statistics
            st.markdown("### 📊 Workload Statistics")
            avg_workload = workload_df['PolicyCount'].mean()
            median_workload = workload_df['PolicyCount'].median()
            max_workload = workload_df['PolicyCount'].max()
            min_workload = workload_df['PolicyCount'].min()

            st.metric("Average Workload", f"{avg_workload:.1f} policies")
            st.metric("Median Workload", f"{median_workload:.0f} policies")
            st.metric("Highest Workload", f"{max_workload:,} policies")
            st.metric("Lowest Workload", f"{min_workload:,} policies")

        # Show workload table
        if show_data_table:
            st.subheader("📋 Detailed Workload Breakdown")
            display_df = workload_df.copy()
            display_df['Category'] = display_df['CategoryIcon'] + ' ' + display_df['WorkloadCategory'].apply(lambda x: thresholds[x]['label'])
            display_df = display_df[['AccountManager', 'PolicyCount', 'Category', 'TopPolicyTypes']]
            display_df.columns = ['Account Manager', 'Policy Count', 'Workload Level', 'Top Policy Types']
            st.dataframe(display_df, use_container_width=True)

    # Policy Type Analysis
    elif view_by == "Policy Type Analysis":
        st.header("📊 Policy Type Distribution")

        # Policy type breakdown
        type_counts = df['PolicyType'].value_counts().reset_index()
        type_counts.columns = ['PolicyType', 'Count']

        # Bar chart
        fig = px.bar(
            type_counts.head(10),
            x="PolicyType",
            y="Count",
            title="Policy Count by Type (Top 10)",
            color="Count",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(xaxis_title="Policy Type", yaxis_title="Number of Policies")
        st.plotly_chart(fig, use_container_width=True)

        # Policy type by account manager heatmap
        st.subheader("🔥 Policy Type Distribution by Account Manager")
        
        # Create cross-tabulation
        cross_tab = pd.crosstab(df['AccountManager'], df['PolicyType'])
        
        # Get top managers and types for visualization
        top_managers = cross_tab.sum(axis=1).nlargest(10).index
        top_types = cross_tab.sum(axis=0).nlargest(8).index
        
        filtered_cross_tab = cross_tab.loc[top_managers, top_types]

        fig = px.imshow(
            filtered_cross_tab,
            text_auto=True,
            aspect="auto",
            title="Policy Count Heatmap: Top Account Managers vs Top Policy Types",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(
            xaxis_title="Policy Type",
            yaxis_title="Account Manager"
        )
        st.plotly_chart(fig, use_container_width=True)

        if show_data_table:
            st.subheader("📋 Policy Type Summary")
            st.dataframe(type_counts, use_container_width=True)

    # Account Manager Details
    elif view_by == "Account Manager Details":
        st.header("👥 Account Manager Performance Details")

        # Account manager selection
        manager_list = sorted(df['AccountManager'].unique())
        selected_managers = st.multiselect(
            "Select Account Managers to Compare",
            options=manager_list,
            default=manager_list[:5] if len(manager_list) >= 5 else manager_list
        )

        if selected_managers:
            filtered_df = df[df['AccountManager'].isin(selected_managers)]

            # Manager comparison metrics
            manager_stats = filtered_df.groupby('AccountManager').agg({
                'PolicyId': 'count',
                'PolicyType': 'nunique',
                'AccountId': 'nunique',
                'ExpirationDate': ['min', 'max']
            }).round(2)

            manager_stats.columns = [
                'Total Policies', 'Policy Types', 'Unique Accounts', 
                'Earliest Expiration', 'Latest Expiration'
            ]

            # Comparison chart
            fig = px.bar(
                manager_stats.reset_index(),
                x="AccountManager",
                y="Total Policies",
                title="Policy Count Comparison - Selected Account Managers",
                color="Total Policies",
                color_continuous_scale="Plasma"
            )
            fig.update_layout(xaxis_title="Account Manager", yaxis_title="Number of Policies")
            st.plotly_chart(fig, use_container_width=True)

            if show_data_table:
                st.subheader("📋 Manager Comparison Table")
                st.dataframe(manager_stats, use_container_width=True)

    # Expiration Timeline
    elif view_by == "Expiration Timeline":
        st.header("📅 Policy Expiration Timeline")

        # Monthly expiration analysis
        monthly_exp = df.groupby('ExpirationMonth').agg({
            'PolicyId': 'count',
            'AccountManager': 'nunique'
        }).reset_index()
        monthly_exp.columns = ['Month', 'Policies Expiring', 'Account Managers Affected']

        # Line chart for expiration timeline
        fig = px.line(
            monthly_exp,
            x="Month",
            y="Policies Expiring",
            title="Monthly Policy Expiration Timeline",
            markers=True,
            color_discrete_sequence=["#e74c3c"]
        )
        fig.update_layout(xaxis_title="Month", yaxis_title="Number of Policies Expiring")
        st.plotly_chart(fig, use_container_width=True)

        # Stacked bar chart by manager and month
        if len(df['AccountManager'].unique()) <= 15:  # Only show if manageable number
            monthly_by_manager = df.groupby(['ExpirationMonth', 'AccountManager']).size().reset_index(name='Count')
            
            fig = px.bar(
                monthly_by_manager,
                x="ExpirationMonth",
                y="Count",
                color="AccountManager",
                title="Monthly Expiration Distribution by Account Manager",
                barmode="stack"
            )
            fig.update_layout(xaxis_title="Month", yaxis_title="Number of Policies")
            st.plotly_chart(fig, use_container_width=True)

        if show_data_table:
            st.subheader("📋 Monthly Expiration Summary")
            st.dataframe(monthly_exp, use_container_width=True)

    # Core Lines Workload Analysis (similar to original)
    if show_core_lines_only or st.checkbox("🎯 Show Core Lines Workload Analysis"):
        st.header("🎯 Core Lines Workload Analysis")
        st.info("Core Lines: Auto, Flood, Homeowners, Umbrella")

        core_lines = get_core_policy_types()
        df_core = df[df['PolicyType'].isin(core_lines)]

        if not df_core.empty:
            # Apply weighting: Flood-CL and Flood-PL = 0.5, others = 1.0
            df_core_workload = df_core.copy()
            df_core_workload['WeightedCount'] = df_core_workload['PolicyType'].apply(
            lambda x: 0.5 if x in ['Flood', 'Flood - CL', 'Flood - PL'] else 1.0
        )


            # Group by Account Manager and Policy Type
            workload_summary = df_core_workload.groupby(['AccountManager', 'PolicyType']).agg({
                'PolicyId': 'count',
                'WeightedCount': 'first'
            }).rename(columns={'PolicyId': 'Count'})

            # Apply the weighting
            workload_summary['WeightedCount'] = workload_summary['Count'] * workload_summary['WeightedCount']
            workload_summary = workload_summary.reset_index()

            # Calculate totals per account manager
            manager_totals = workload_summary.groupby('AccountManager').agg({
                'Count': 'sum',
                'WeightedCount': 'sum'
            }).reset_index()
            manager_totals = manager_totals.sort_values('WeightedCount', ascending=False)

            # Visualization
            fig = px.bar(
                manager_totals.head(15),
                x="AccountManager",
                y="WeightedCount",
                title="Core Lines Weighted Workload by Account Manager (Flood - CL/Flood - PL = 0.5 weight)",
                color="WeightedCount",
                color_continuous_scale="Viridis"
            )
            fig.update_layout(xaxis_title="Account Manager", yaxis_title="Weighted Policy Count")
            st.plotly_chart(fig, use_container_width=True)

            # Detailed breakdown
            if show_data_table:
                st.subheader("📊 Core Lines Workload Summary")
                
                # Show aggregated manager totals
                manager_display = manager_totals.copy()
                manager_display['Workload Reduction'] = manager_display['Count'] - manager_display['WeightedCount']
                manager_display.columns = ['Account Manager', 'Total Policies', 'Weighted Total', 'Workload Reduction']
                st.dataframe(manager_display, use_container_width=True)
                
                # Show detailed breakdown by policy type
                st.subheader("📋 Detailed Policy Type Breakdown")
                policy_breakdown = workload_summary.pivot_table(
                    index='AccountManager', 
                    columns='PolicyType', 
                    values='Count', 
                    fill_value=0
                ).reset_index()
                
                # Add total column
                policy_breakdown['Total'] = policy_breakdown.iloc[:, 1:].sum(axis=1)
                policy_breakdown = policy_breakdown.sort_values('Total', ascending=False)
                
                st.dataframe(policy_breakdown, use_container_width=True)
    
    st.info("📊 **Example:** If a manager has 200 Flood - CL + 200 Auto policies → Weighted Total = 350 (200×0.5 + 200×1.0)")

    # Show full raw data option
    with st.expander("🔍 View Raw Policy Data", expanded=False):
        st.dataframe(df, use_container_width=True)

else:
    st.warning("⚠️ No policy data available for the selected date range. Please adjust your filters or check your Salesforce connection.")
    st.info("""
    **Troubleshooting Tips:**
    - Verify your Salesforce credentials in the .env file
    - Check if the date range contains policies with expiration dates
    - Ensure the InsurancePolicy object is accessible in your Salesforce org
    - Verify the Account_Manager__c field exists on the Account object
    """)
