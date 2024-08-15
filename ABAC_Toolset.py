import pandas as pd
import streamlit as st

# Function to filter data based on selected attributes
def filter_data(data, cost_centers, user_departments, user_managers, user_legal_entities):
    filtered_data = data[data['User Cost Center'].isin(cost_centers)]
    if user_departments:
        filtered_data = filtered_data[filtered_data['User Department(private)'].isin(user_departments)]
    if user_managers:
        filtered_data = filtered_data[filtered_data['User Manager SID(private)'].isin(user_managers)]
    if user_legal_entities:
        filtered_data = filtered_data[filtered_data['User Legal Entity'].isin(user_legal_entities)]
    return filtered_data

# Function to generate table showing User SIDs, Entitlements, and associated attributes
def generate_entitlement_table(filtered_data, cost_centers, user_departments, user_managers, user_legal_entities):
    entitlements = filtered_data['Entitlement(private)'].unique()
    user_sids = filtered_data['User SID(private)'].unique()

    # Initialize the table with User SIDs as columns
    table = pd.DataFrame(0, index=entitlements, columns=user_sids)

    # Conditionally add additional columns for attributes
    if len(cost_centers) > 1:
        table['Cost Centers'] = ''
    if len(user_departments) > 1:
        table['User Departments'] = ''
    if len(user_managers) > 1:
        table['User Managers'] = ''
    if len(user_legal_entities) > 1:
        table['User Legal Entities'] = ''

    # Fill the table with User SIDs and associated attributes
    for entitlement in entitlements:
        entitlement_data = filtered_data[filtered_data['Entitlement(private)'] == entitlement]
        
        # Populate the User SID columns
        for sid in user_sids:
            if sid in entitlement_data['User SID(private)'].values:
                table.at[entitlement, sid] = 1
        
        # Populate the additional attribute columns if they exist
        if 'Cost Centers' in table.columns:
            associated_cost_centers = entitlement_data['User Cost Center'].astype(str).unique()
            table.at[entitlement, 'Cost Centers'] = ', '.join(associated_cost_centers)
        
        if 'User Departments' in table.columns:
            associated_departments = entitlement_data['User Department(private)'].astype(str).unique()
            table.at[entitlement, 'User Departments'] = ', '.join(associated_departments)
        
        if 'User Managers' in table.columns:
            associated_managers = entitlement_data['User Manager SID(private)'].astype(str).unique()
            table.at[entitlement, 'User Managers'] = ', '.join(associated_managers)
        
        if 'User Legal Entities' in table.columns:
            associated_legal_entities = entitlement_data['User Legal Entity'].astype(str).unique()
            table.at[entitlement, 'User Legal Entities'] = ', '.join(associated_legal_entities)

    return table

# Function to apply custom styling to the table
def highlight_policies(table):
    def highlight_row(row):
        # Separate out the columns related to User SIDs from other columns
        user_sid_columns = [col for col in table.columns if col not in ['Cost Centers', 'User Departments', 'User Managers', 'User Legal Entities']]
        
        # Determine if the entire row should be highlighted green (all SIDs have the entitlement)
        if sum(row[user_sid_columns] == 1) > 1 and all(row[user_sid_columns] == 1):
            return ['background-color: lightgreen'] * len(row)
        
        # Highlight yellow if at least half the SIDs have the entitlement
        elif sum(row[user_sid_columns] == 1) >= len(user_sid_columns) / 2:
            return ['background-color: lightyellow'] * len(row)
        
        # If any SID doesn't have the entitlement, highlight yellow as well
        elif any(row[user_sid_columns] == 0):
            return ['background-color: lightyellow'] * len(row)
        
        # Otherwise, no highlight
        else:
            return [''] * len(row)

    return table.style.apply(highlight_row, axis=1)

# Function to identify policies based on entitlement table and selected attributes
def identify_policies(entitlement_table, cost_centers, user_departments, user_managers, user_legal_entities):
    policies = []
    user_sid_columns = entitlement_table.columns.difference(['Cost Centers', 'User Departments', 'User Managers', 'User Legal Entities'])

    for entitlement in entitlement_table.index:
        row = entitlement_table.loc[entitlement, user_sid_columns]
        
        if all(row == 1) and len(user_sid_columns[row == 1]) > 1:  # Ensure all values are 1 and more than 1 User SID
            
            # Extract relevant attributes from the table for the current entitlement
            associated_cost_centers = entitlement_table.at[entitlement, 'Cost Centers'] if 'Cost Centers' in entitlement_table.columns else cost_centers
            associated_departments = entitlement_table.at[entitlement, 'User Departments'] if 'User Departments' in entitlement_table.columns else user_departments
            associated_managers = entitlement_table.at[entitlement, 'User Managers'] if 'User Managers' in entitlement_table.columns else user_managers
            associated_legal_entities = entitlement_table.at[entitlement, 'User Legal Entities'] if 'User Legal Entities' in entitlement_table.columns else user_legal_entities
            
            # Ensure the extracted attributes are lists
            if isinstance(associated_cost_centers, str):
                associated_cost_centers = associated_cost_centers.split(', ')
            if isinstance(associated_departments, str):
                associated_departments = associated_departments.split(', ')
            if isinstance(associated_managers, str):
                associated_managers = associated_managers.split(', ')
            if isinstance(associated_legal_entities, str):
                associated_legal_entities = associated_legal_entities.split(', ')
            
            # Create policy profile using the filtered attributes
            policy_profile = {
                'Entitlement': entitlement,
                'Cost Centers': associated_cost_centers,
                'User Departments': associated_departments,
                'User Managers': associated_managers,
                'User Legal Entities': associated_legal_entities
            }
            policies.append(policy_profile)

    return policies


# Streamlit interface
st.title("Automated ABAC Policy Detection")

st.sidebar.title("Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# Add custom CSS to adjust margins and layout, including making the table only vertically scrollable
st.markdown(
    """
    <style>
    .reportview-container .main .block-container{
        padding-top: 20px;
        padding-right: 50px;
        padding-left: 50px;
        padding-bottom: 20px;
    }
    .dataframe-container {
        overflow-y: scroll;
        max-height: 500px;
        max-width: 100%;
        width: 100%;
        display: block;
    }
    table.dataframe {
        width: 100%;
        table-layout: fixed;
    }
    table.dataframe th, table.dataframe td {
        word-wrap: break-word;
        overflow-wrap: break-word;
        text-align: center;
    }
    .policy-section {
        margin-top: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    
    st.sidebar.title("Select Attributes")
    selected_cost_centers = st.sidebar.multiselect("Cost Center", data['User Cost Center'].unique())
    
    if selected_cost_centers:
        departments = data[data['User Cost Center'].isin(selected_cost_centers)]['User Department(private)'].unique()
        selected_user_departments = st.sidebar.multiselect("User Department", departments)
        
        if selected_user_departments:
            managers = data[(data['User Cost Center'].isin(selected_cost_centers)) & 
                            (data['User Department(private)'].isin(selected_user_departments))]['User Manager SID(private)'].unique()
            selected_user_managers = st.sidebar.multiselect("User Manager SID", managers)
            
            if selected_user_managers:
                legal_entities = data[(data['User Cost Center'].isin(selected_cost_centers)) & 
                                      (data['User Department(private)'].isin(selected_user_departments)) & 
                                      (data['User Manager SID(private)'].isin(selected_user_managers))]['User Legal Entity'].unique()
                selected_user_legal_entities = st.sidebar.multiselect("User Legal Entity", legal_entities)
                
                if st.sidebar.button("Execute"):
                    filtered_data = filter_data(data, selected_cost_centers, selected_user_departments, selected_user_managers, selected_user_legal_entities)
                    entitlement_table = generate_entitlement_table(filtered_data, selected_cost_centers, selected_user_departments, selected_user_managers, selected_user_legal_entities)
                    
                    styled_table = highlight_policies(entitlement_table)
                    st.write("User SID and Entitlements:")
                    
                    # Use custom HTML to embed the styled table in a scrollable container
                    st.markdown(f'<div class="dataframe-container">{styled_table.to_html()}</div>', unsafe_allow_html=True)
                    
                    policies = identify_policies(entitlement_table, selected_cost_centers, selected_user_departments, selected_user_managers, selected_user_legal_entities)
                    
                    st.markdown('<div class="policy-section">', unsafe_allow_html=True)
                    st.write("Policies Identified from Dataset and Chosen Attributes:")
                    if policies:
                        for idx, policy in enumerate(policies, 1):
                            st.markdown(f"**Policy {idx}**")
                            st.markdown(f"**Entitlement:** {policy['Entitlement']}")
                            st.markdown(f"**Policy Profile:**")
                            st.markdown(f"Cost Centers - {', '.join(map(str, policy['Cost Centers']))}")
                            if policy['User Departments']:
                                st.markdown(f"User Departments - {', '.join(map(str, policy['User Departments']))}")
                            if policy['User Managers']:
                                st.markdown(f"User Managers - {', '.join(map(str, policy['User Managers']))}")
                            if policy['User Legal Entities']:
                                st.markdown(f"User Legal Entities - {', '.join(map(str, policy['User Legal Entities']))}")
                            st.markdown("---")
                    else:
                        st.markdown("No common access patterns found for the selected attributes.")
                    st.markdown('</div>', unsafe_allow_html=True)
