# -*- coding: utf-8 -*-
"""SMA_Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xGKyYK9CbAIi7Fezqpk1CrZaabKYOjRo

## **IMPORT LIBRARIES**
"""

!pip install --upgrade ta

import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np
import ta as ta

"""## **UPLOAD DATASET TO STORAGE**"""

data = pd.read_csv('indb.us.txt') 
data.head()

data.shape

data.isnull().sum()

"""As we can see, there are no NaN or null values in the dataset, and can therefore be considered a clean dataset.

## **DATA PREPROCESSING**

**COMPUTE IF THE STOCK IS MOVING UP/DOWN**
"""

def stockTrend(s):
  if (s['Close'] - s['Open'] > 0):
    return 'up'
  elif (s['Close'] - s['Open'] == 0) :
    return 'nochange'
  else:
    return 'down'

data['Class'] = data.apply(stockTrend,axis=1)

data.tail()

"""**COMPUTE VARIOUS OTHER TECHNICAL MARKERS THAT WILL BE USED**

**Force Index = ( Close - Open ) x volume**
"""

def forceindex(s):
  return (s['Close']-s['Open'])*s['Volume']

data['forceindex'] = data.apply(forceindex, axis=1)

data.head()

"""------------------------------------------------------
 
 (1)***Williams %R***---->%R = -100 * ( ( Highest High - Close) / ( Highest High - Lowest Low ) )
 

(2)***Relative Strength Indicator (RSI)***---->    RSI = 100 - (100 / (1 + RS))

(3)***The Rate of Change(ROC)***---->ROC = (Current Price / Price of n periods ago)-1.0) * 100
"""

data['WillR%' ] = ta.momentum.WilliamsRIndicator(data['High'], data['Low'], data['Close'],  fillna='true').wr()

data['RSI5'  ] = ta.momentum.RSIIndicator(data['Close'], n=5,   fillna='true').rsi()
data['RSI10' ] = ta.momentum.RSIIndicator(data['Close'], n=10,  fillna='true').rsi()
data['RSI15' ] = ta.momentum.RSIIndicator(data['Close'], n=15,  fillna='true').rsi()

data['ROC5'  ] = ta.momentum.ROCIndicator(data['Close'], n=5,   fillna='true').roc()
data['ROC10' ] = ta.momentum.ROCIndicator(data['Close'], n=10,  fillna='true').roc()

data['ATR5'  ] = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close'], n=5,  fillna='true').average_true_range()
data['ATR10' ] = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close'], n=10, fillna='true').average_true_range()

data.tail()

type(data['High'])
type(ta.momentum.WilliamsRIndicator(data['High'], data['Low'], data['Close'], 5).wr())

data.head(5)

A=data['Date']
B=data['Class']

import matplotlib.pyplot as plt
plt.scatter(A,B)
plt.ylabel('Class')
plt.xlabel('Date')
plt.show()

import seaborn as sn
df = pd.DataFrame(data,columns=['forceindex','WillR%','RSI5','RSI10','RSI15','ROC5','ROC10','ATR5','ATR10'])
corrMatrix = df.corr()
print("Co-Relation Matrix")
print (corrMatrix)
corrMatrix = df.corr()

#sn.heatmap(corrMatrix, annot=True)
#plt.show()

"""**SPLIT DATASET INTO TRAIN AND TEST SETS**"""

x_data = data[['WillR%', 'RSI5', 'RSI10', 'RSI15', 'ROC5', 'ROC10', 'ATR5', 'ATR10']]
y_data = data['Class']

x_data.tail()

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2)

"""# **ASSEMBLING MODELS**

**KNN MODEL**

First, we will create a new k-NN classifier. Next, we need to create a dictionary to store all the values we will test for ‘n_neighbors’, which is the hyperparameter we need to tune. We will test 24 different values for ‘n_neighbors’. Then we will create our grid search, inputing our k-NN classifier, our set of hyperparamters and our cross validation value.
"""

import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier

#create a new knn model
knn = KNeighborsClassifier()

#create a dictionary of all values we want to test for n_neighbors
params_knn = {'n_neighbors': np.arange(1, 25)}

#use gridsearch to test all values for n_neighbors
knn_gs = GridSearchCV(knn, params_knn, cv=5)

#fit model to training data
knn_gs.fit(X_train, y_train)

"""Cross-validation is when the dataset is randomly split up into ‘k’ groups. One of the groups is used as the test set and the rest are used as the training set. The model is trained on the training set and scored on the test set. Then the process is repeated until each unique group as been used as the test set.

In our case, we are using 5-fold cross validation. The dataset is split into 5 groups, and the model is trained and tested 5 separate times so each group would get a chance to be the test set. This is how we will score our model running with each hyperparamter value to see which value for ‘n_neighbors’ gives us the best score.
"""

#save best model
knn_best = knn_gs.best_estimator_

#check best n_neigbors value
print(knn_gs.best_params_)

"""Now we will save our best k-NN model to ‘knn_best’ using the ‘best_estimator_’ function and check what the best value was for ‘n_neighbors’.

**RANDOM FOREST**

The next model we will build is a random forest. A random forest is considered an ensemble model in itself, since it is a collection of decision trees combined to make a more accurate model.
"""

from sklearn.ensemble import RandomForestClassifier

#create a new random forest classifier
rf = RandomForestClassifier()

#create a dictionary of all values we want to test for n_estimators
params_rf = {'n_estimators': [50, 100, 200]}

#use gridsearch to test all values for n_estimators
rf_gs = GridSearchCV(rf, params_rf, cv=5)

#fit model to training data
rf_gs.fit(X_train, y_train)

"""We will create a new random forest classifier and set the hyperparameters we want to tune. ‘n_estimators’ is the number of trees in our random forest. Then we can run our grid search to find the optimal number of trees.

Just like before, we will save our best model and print the best ‘n_estimators’ value.
"""

#save best model
rf_best = rf_gs.best_estimator_

#check best n_estimators value
print(rf_gs.best_params_)

"""**GAUSSIAN KERNEL (SVM)**"""

from sklearn.svm import SVC

svclassifier = SVC(kernel='rbf')
svclassifier.fit(X_train, y_train)

"""# **EVALUATION OF INDIVIDUAL TRAINING ACCURACIES**"""

print('knn: {}'.format(knn_best.score(X_train, y_train)))
print('rf: {}'.format(rf_best.score(X_train, y_train)))
print('svclassifier: {}'.format(svclassifier.score(X_train, y_train)))

"""As we can say this is an overfitted model.

## **EVALUATION OF INDIVIDUAL MODEL SCORES**

Now let’s check the accuracy scores of all three of our models on our test data.
"""

print('knn: {}'.format(knn_best.score(X_test, y_test)))
print('rf: {}'.format(rf_best.score(X_test, y_test)))
print('svclassifier: {}'.format(svclassifier.score(X_test, y_test)))

"""As you can see from the output, Knn is the most accurate out of the three.

# VOTING CLASSIFIER

Now that we’ve built our three individual models, it’s time we built our voting classifier.
"""

from sklearn.ensemble import VotingClassifier

#create a dictionary of our models
estimators=[('knn', knn_best), ('rf', rf_best), ('svclassifier', svclassifier)]

#create our voting classifier, inputting our models
ensemble = VotingClassifier(estimators, voting='hard')

#fit model to training data
ensemble.fit(X_train, y_train)

#test our model on the test data
ensemble.score(X_test, y_test)

#fit model to training data
#ensemble.fit(X_train, y_train)

#test our model on the train data
#ensemble.score(X_train, y_train)

x=['KNN','RF','SVM','ENSEMBLE']
y=[73.01,71.29,70.82,73.16]

import matplotlib.pyplot as plt
import seaborn as sns
plt.bar(x,y)
plt.show

"""**Our ensemble model performed better than our individual k-NN, random forest and Gaussian SVM models!**"""