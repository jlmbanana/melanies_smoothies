# Import python packages
import streamlit as st
import requests  #NEW FOR API CONNECT
import pandas as pd



from snowflake.snowpark.functions import col, when_matched
#Commented out for SniS---
#from snowflake.snowpark.context import get_active_session

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

#Add a text box for customer to enter their name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

#Added these lines for SNIS (the connection)-------
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

#Uncomment below line to see the dataframe:
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Convert the snowpark df to pandas df, so we can use the LOC function
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

#Put a multiselect widget on app
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)
###############################################################
# Test if anything is in the list. If list NOT NULL, write it
    #Create string to hold fruits
    # iterate through ingredients and concat each fruit into the string.
    # Build the SQL insert statement
##################################################################
if ingredients_list:
    
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
       ingredients_string += fruit_chosen + ' '
       
       #Code is getting row wwhere fruit_chosen equals what is in FRUIT_NAME column. Then get the value of Search_ON & save into variable
       search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
       # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        #Add subheader to output
       st.subheader(fruit_chosen + ' Nutrition Information')
       
        #API info: 
       smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
       sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    #SQL insert statement
    my_insert_statement = """insert into smoothies.public.orders(ingredients, NAME_ON_ORDER)
        values ('""" + ingredients_string + """', '"""+name_on_order+"""')"""

    # st.write(my_insert_statement)
    # st.stop()

    #Add in insert button to for customer to submit their order
    time_to_insert = st.button('Submit Order')

    #If result from 'submit order' holds information, add information to table.
    if time_to_insert:
        session.sql(my_insert_statement).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")

