
#Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched
import pandas as pd




# Image URLs
image_url_left = "https://media.licdn.com/dms/image/D4E12AQF-BvR3QRs9gw/article-cover_image-shrink_720_1280/0/1656343174665?e=2147483647&v=beta&t=T3dP2OU7Tbws3Ap79YdaIIYX1st1UqSW1TeKVdH6L48"
image_url_center = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSkM0Emsq4_Gz6ZqhBstMmUDwDeogsSd0zcQQ&s"
image_url_right = "https://www.uptoplay.net/imagescropped/diemsnoticesicon128.jpg.webp"

# Layout using Streamlit columns
col1, col2, col3 = st.columns([1, 2, 1])  # Adjust the proportions of the columns

# Display the left image in the first column with circular styling
with col1:
    st.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center;">
        <img src="{image_url_left}" alt="Left Image" style="width:150px; height:150px; border-radius: 50%;">
    </div>
    """, unsafe_allow_html=True)

# Display the center collab image in the second column
with col2:
    st.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center;">
        <img src="{image_url_center}" alt="Collab Logo" style="width:150px; height:150px; border-radius: 50%;">
    </div>
    """, unsafe_allow_html=True)

    # Attractive heading for B.Tech CA-II Submission
    st.title("🎓 **DIEMS B.Tech CA-II Submission Checking** 🎓")
    st.write("Enhancing Knowledge Through Collaboration")

# Display the right image in the third column with circular styling
with col3:
    st.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center;">
        <img src="{image_url_right}" alt="DIEMS Logo" style="width:150px; height:150px; border-radius: 50%;">
    </div>
    """, unsafe_allow_html=True)

# # Display the text in the center column
# with col2:
#     st.title("DIEMS B.Tech CA-II Submission Checking")
# st.write("Assignment Completed or Marks given.")

# -- assignment_checking
cnx = st.connection("snowflake")
session = cnx.session()

# Load the submission table data where assignment is not checked
my_dataframe = session.table("DIEMS_CA.PUBLIC.submission").filter(col("assignment_checked") == 0).collect()

# Convert the collected data to a Pandas DataFrame for Streamlit UI
df = pd.DataFrame(my_dataframe)

# Check if the DataFrame is empty and handle appropriately
if df.empty:
    st.write("No assignments to check.")
else:
    # Display the editable data
    editable_df = st.data_editor(df)

    submitted = st.button("Submit")

    if submitted:
        # Check if the DataFrame is empty (after editing)
        if editable_df.empty:
            st.write("No data to submit.")
        else:
            og_dataset = session.table("DIEMS_CA.PUBLIC.submission")
            
            # Create a Snowflake DataFrame from the editable DataFrame
            edited_dataset = session.create_dataframe(editable_df)

            try:
                og_dataset.merge(
                    edited_dataset, 
                    (og_dataset['SUB_UID'] == edited_dataset['SUB_UID']),
                    [
                        when_matched().update({
                            'ASSIGNMENT_CHECKED': edited_dataset['ASSIGNMENT_CHECKED'],  
                            'MARKS': edited_dataset['MARKS']  
                        })
                    ]
                )
                st.success('Data successfully submitted and updated.', icon='👍')
                
                # Re-query the data after submission to reflect changes
                my_dataframe = session.table("DIEMS_CA.PUBLIC.submission").filter(col("assignment_checked") == 0).collect()
                df = pd.DataFrame(my_dataframe)  # Update the DataFrame

                if df.empty:
                    st.write("No more assignments left to check.")
                else:
                    st.data_editor(df)  # Refresh the UI with updated data

            except Exception as e:
                st.write("Something went wrong:", e)



