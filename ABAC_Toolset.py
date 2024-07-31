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

# Function to generate table showing User SIDs and their access to each entitlement
def generate_entitlement_table(filtered_data):
    entitlements = filtered_data['Entitlement(private)'].unique()
    user_sids = filtered_data['User SID(private)'].unique()
    
    table = pd.DataFrame(0, index=entitlements, columns=user_sids)
    
    for sid in user_sids:
        user_entitlements = filtered_data[filtered_data['User SID(private)'] == sid]['Entitlement(private)']
        table.loc[user_entitlements, sid] = 1
    
    return table

# Function to apply custom styling to the table
def highlight_policies(table):
    def highlight_row(row):
        if sum(row == 1) > 1 and all(row[row == 1]):
            return ['background-color: lightgreen'] * len(row)
        elif sum(row == 1) >= len(row) / 2:
            return ['background-color: lightyellow'] * len(row)
        else:
            return [''] * len(row)
    return table.style.apply(highlight_row, axis=1)

# Function to identify policies
def identify_policies(entitlement_table, cost_centers, user_departments, user_managers, user_legal_entities):
    policies = []
    for entitlement, row in entitlement_table.iterrows():
        if sum(row == 1) > 1:
            policies.append({
                "Entitlement": entitlement,
                "Cost Centers": cost_centers,
                "User Departments": user_departments,
                "User Managers": user_managers,
                "User Legal Entities": user_legal_entities
            })
    return policies

# Streamlit interface
st.title("Automated ABAC Policy Detection")

st.sidebar.title("Upload Dataset")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# Add custom CSS to adjust margins and layout
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
        display: block;
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
                    entitlement_table = generate_entitlement_table(filtered_data)
                    
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
