# import packages
from flask import Flask
import pandas as pd
import numpy as np

#create functions to pull in data from spreadsheet
def pos(col): 
  return col[col > 0].sum()
  
def neg(col): 
  return col[col < 0].sum()

def get_balance_data(data):
    
    #import data from spreadsheet
    df = pd.read_excel(data, sheet_name = 'ERCIP Obligation Ledger', header = 3, usecols=lambda x: 'Unnamed' not in x)
    df = df[['FY of Funding Action','Project #', 'P&D Funding Actions','Construction Funding Actions']]
    
    #group data by FY
    df_FY = df.groupby(by = 'FY of Funding Action')
    
    #calculate balances - apply lambda function to sum positive and negative values separately
    pd_total = df_FY['P&D Funding Actions'].agg([('spending', neg),
                              ('funding', pos)
                              ])
    c_total = df_FY['Construction Funding Actions'].agg([('spending', neg),
                              ('funding', pos)
                              ])
    #convert spending from negative to positive
    pd_total['spending'] = pd_total['spending'] * -1
    c_total['spending'] = c_total['spending'] * -1
    
    #subtract spending from funding to find balance
    pd_total['balance'] = pd_total['funding'] - pd_total['spending'] 
    c_total['balance'] = c_total['funding'] - c_total['spending'] 
    
    #rename column
    pd_total.columns = ['pd_spending','pd_funding', 'pd_balance']
    c_total.columns = ['c_spending','c_funding', 'c_balance']

    #convert dataframe to dictionary 
    pd_dict = pd_total.to_dict()
    c_dict = c_total.to_dict()
    
    #merge into one dictionary
    merged = {**pd_dict, **c_dict}

    return merged



# create the application object
app = Flask(__name__)


@app.route("/home")
def members():
    data  = get_balance_data(data = 'project_ledger.xlsx')
    return data

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)

