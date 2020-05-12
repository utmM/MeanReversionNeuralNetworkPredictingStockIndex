# -*- coding: utf-8 -*-
'''
3. Prediction and output interpretation
       Load the model and predict the accelaration by the real stock prices.
        Prepare the market data in real. The input needs 25 close stock prices (index prices). 25 differencials form the moving average will be generated by the code. The model uses 25 differencials as input and produce 1 prediction data (accelaration). The accelaration is the direction of the stock price.
       
    (Interpretation of the predictions)
       
       The predicted accelarations has large variation or deviation, similar to the input data, so you need to get moving average of the prediction time series to get smoother the outputs. Getting average or leveling predictions is like interpretation or translation of machine language to human's to understand the deviation or angiguity of the outcome generated by AI.
        
       As you read, the data emphasis and data leveling are more important than to create more complicated neural network models.
    
'''

from __future__ import print_function
import datetime
import urllib3  # for python3
from os import path
import operator as op
from collections import namedtuple
import numpy as np
import pandas as pd
import tensorflow as tf
import sys

# <<<<< Define Constants >>>>>
T = 25 # T days moving average

# <<<<< Scraping >>>>>
def scrape_data(fileName, url):
    if path.isfile('./' + fileName):# data exist (put it in the same folder)
        print('data exists, loading...')
        return pd.read_csv('./' + fileName, header=0, index_col=0)
    else:# No data. -> sprape from sites (Caution! you need to find the sites and comply the site's scraping standard)
        csv = urllib3.PoolManager().request('GET', url)
        print('No data, Starg Scraping ...')
        with open(fileName, 'w') as f:
            f.write(str(csv.data, 'shift-jis'))
        return pd.read_csv('./' + fileName, header=0, index_col=0)

# <<<<< Calculate moving average >>>>>
def add_divergence(input_data_df):
    input_data_df = input_data_df.assign(MD=0)
    sum = float()
    for i in range(len(input_data_df)-1-T ,len(input_data_df)):
        for j in range(0, T):
            sum = sum + input_data_df.iloc[i+j-(T-1),0]
        input_data_df.iloc[i,4] = sum/T
        sum = 0
    return input_data_df

# <<<<<  Calculate the differencials　>>>>>
def add_div_divergence(input_data_df):
    input_data_df = input_data_df.assign(Div=0)
    for k in range(len(input_data_df)-1-T, len(input_data_df)):
        input_data_df.iloc[k,5] = input_data_df.iloc[k,0]/input_data_df.iloc[k,4]
    return input_data_df

# <<<<< Get input data for NN >>>>>
def get_feature_data(input_data_df):
    # ! Get rif of [NaN]s
    input_data_df = input_data_df.iloc[len(input_data_df)-T-1:len(input_data_df)-1,5]
    predictor_ndarray = input_data_df.T.values
    feature_data = np.array([predictor_ndarray]).astype('float32')
    return feature_data

# <<<<< Predict by the Model >>>>>
def predict(feature_data):
    # Load the model
    sess = tf.Session()
    saver = tf.train.import_meta_graph('model.meta')
    saver.restore(sess, tf.train.latest_checkpoint('./'))
    # Load calculation graph, weights, biasis.
    graph = tf.get_default_graph()
    weights1 = graph.get_tensor_by_name('Weights1:0')
    biases1 = graph.get_tensor_by_name('Biases1:0')
    weights2 = graph.get_tensor_by_name('Weights2:0')
    biases2 = graph.get_tensor_by_name('Biases2:0')

    hidden_layer = tf.nn.sigmoid(tf.matmul(feature_data, weights1) + biases1)
    pred_value = sess.run(tf.nn.tanh(tf.matmul(hidden_layer, weights2) + biases2))
    return pred_value


######################## The Main Function #########################
fileName = 'N225_index.csv'
#  No data. -> sprape from sites (Caution! you need to find the sites and comply the site's scraping standard)
url = 'URL:"Scraping Site"'
input_data_df = scrape_data(fileName, url)
#print('Scraped/Read CSV converted to Dataframe ->', input_data_df)
# Get closes only
#input_data_df = input_data_df.loc[:,'Close']
# Calculate T day moving average
input_data_df = add_divergence(input_data_df)
#print('input_data_df: ', input_data_df)
# Calculate the differencials
input_data_df = add_div_divergence(input_data_df)
# Get input data to NN Model
feature_data = get_feature_data(input_data_df)
print('feature_data: Differencials of the past 25 days', feature_data)
# Predict by the model
pred_value = predict(feature_data)
print('Prediction (UP/DOWN RATIO): ', pred_value)
# Please interprete the pred_value(s) such as getting moving average.


