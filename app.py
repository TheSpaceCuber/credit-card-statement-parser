import streamlit as st
import pandas as pd
import numpy as np
from PyPDF2 import PdfReader 
import citi_operations as citi

st.title('Credit Card Statement Processor')

uploaded_file = st.file_uploader('Upload your PDF statement here')
if uploaded_file is None:
    st.warning('File not detected. Please upload a PDF file to continue')
    st.stop()

file_ext = uploaded_file.name.split('.')[-1]
if file_ext != 'pdf':
    st.warning('Uploaded file is not a PDF. Please upload a PDF file to continue')
    st.stop()

reader = PdfReader(uploaded_file) 
current_year = citi.extract_year(reader.pages)
transactions = citi.get_transactions(reader.pages)
formatted_transactions = citi.process_transactions(transactions, current_year)
masterlist = citi.get_masterlist('masterlist.csv')
df = citi.convert_transactions_to_dataframe(formatted_transactions, masterlist)

# convert df to a csv file and download it
csv = df.to_csv(index=False)
st.text('Your download is ready!')
st.download_button(label='Download CSV', data=csv, file_name='transactions.csv', mime='text/csv')
st.text('Dataframe preview:')
st.dataframe(df)