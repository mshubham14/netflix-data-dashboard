#!/usr/bin/env python
# coding: utf-8

# In[ ]:

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# In[ ]:


Netflix=pd.read_csv("Netflix.csv")


# In[2]:


Netflix


# In[4]:


import pandas as pd

Netflix = pd.read_csv("Netflix.csv")

Netflix


# In[5]:


# shape is used to check the number of rows and columns in a DataFrame.
Netflix.shape


# In[6]:


# info() is used to get detailed information about a DataFrame.
# It shows the number of rows, columns, column names,
# non-null values, and data types of each column.

Netflix.info()


# In[7]:


# isnull() checks for missing (null) values in each column.
# sum() counts the total number of missing values in each column.

Netflix.isnull().sum()


# In[8]:


# describe() provides statistical summary of numerical columns.
# It shows count, mean, standard deviation, minimum, and maximum values.

Netflix.describe()


# In[9]:


# duplicated() is used to check for duplicate rows in a DataFrame.
Netflix.duplicated()


# In[10]:


# drop_duplicates() is used to remove duplicate rows from a DataFrame.
Netflix.drop_duplicates()


# In[12]:


# Convert the date_added column into Pandas datetime format.
Netflix["date_added"] = pd.to_datetime(Netflix["date_added"])


# In[13]:


# Display all column names in the Netflix DataFrame.
Netflix.columns


# In[16]:


# pd.to_datetime() converts a date column into datetime format.
Netflix["Watch_Date"] = pd.to_datetime(Netflix["Watch_Date"])


# In[17]:


# Group the data by Region and calculate the total Monthly_Revenue for each Region.
Netflix.groupby("Region")["Monthly_Revenue"].sum()


# In[19]:


get_ipython().system('pip install matplotlib')


# In[20]:


import matplotlib.pyplot as plt


# In[23]:


# Calculate total Monthly Revenue for each Region
revenue_by_region = Netflix.groupby("Region")["Monthly_Revenue"].sum()

# Create a bar chart
revenue_by_region.plot(kind="bar")

# Add chart title
plt.title("Region Wise Revenue")

# Add X-axis label
plt.xlabel("Region")

# Add Y-axis label
plt.ylabel("Monthly Revenue")

# Display the chart
plt.show()


# In[24]:


# Calculate average Rating for each Subscription Plan
rating_by_subscription = Netflix.groupby("Subscription_Plan")["Rating"].mean()

# Create a bar chart
rating_by_subscription.plot(kind="bar")

# Add chart title
plt.title("Subscription Wise Rating")

# Add X-axis label
plt.xlabel("Subscription Plan")

# Add Y-axis label
plt.ylabel("Average Rating")

# Display the chart
plt.show()


# In[26]:


# Calculate average Rating for each Subscription Plan
rating_by_subscription = Netflix.groupby("Subscription_Plan")["Rating"].mean()

# Create a pie chart
rating_by_subscription.plot(kind="pie", autopct="%1.1f%%")

# Add chart title
plt.title("Subscription Wise Rating")

# Remove Y-axis label
plt.ylabel("")

# Display the chart
plt.show()


# In[31]:


# Calculate average Rating for each Category
rating_by_category = Netflix.groupby("Category")["Rating"].mean()

# Create a pie chart
rating_by_category.plot(kind="pie", autopct="%1.1f%%")

# Add chart title
plt.title("Category Wise Rating")

# Remove Y-axis label
plt.ylabel("")

# Display the chart
plt.show()


# In[33]:


Netflix.groupby(Netflix["Watch_Date"].dt.month)["Monthly_Revenue"].sum().plot(kind="line")
plt.title("Month Wise Revenue")
plt.xlabel("Month")
plt.ylabel("Monthly Revenue")
plt.show()


# In[ ]:




