import tensorflow as tf
import numpy as np
import pandas as pd
import math
from matplotlib import pyplot as plt
#print('Tensorflow version:', tf.__version__)
#print('Is using GPU?', tf.test.is_gpu_available())


##Data Collection
dataset = pd.read_csv("/home/gopi/Desktop/TATAGLOBAL.csv")
dataset.head()
dataset.tail()

data = dataset.reset_index()['Close']
print(data)

data.shape
"""
##Visualization of stock price
plt.title("given dataset")
plt.xlabel("No.of.closing price")
plt.ylabel("closing price ")
plt.plot(data)
plt.show()
"""

##Min Max Scalar, because LSTM is sensitive to scale of the data 
##where we transferring our data to 0 & 1

from sklearn.preprocessing import MinMaxScaler
scaler=MinMaxScaler(feature_range=(0,1))
data=scaler.fit_transform(np.array(data).reshape(-1,1))
#this line same ia above line
#data=scaler.fit_transform(data.values.reshape(-1,1))
print(data)

##splitting dataset into train and test split
training_size=int(len(data)*0.65)
test_size=len(data)-training_size
train_data,test_data=data[0:training_size,:],data[training_size:len(data),:1]
print("training data",train_data)
print(train_data.shape)
#print("testing data",test_data)
print(test_data.shape)

#Preprocess the data into x_train,y_train,x_test,y_test by using timestamp method
# convert an array of values into a dataset matrix
def create_dataset(dataset, time_step=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-time_step-1):
		a = dataset[i:(i+time_step), 0]   ###i=0, 0,1,2,3-----99   100 
		dataX.append(a)
		dataY.append(dataset[i + time_step, 0])
	return np.array(dataX) , np.array(dataY)

# reshape into X=t,t+1,t+2,t+3 and Y=t+4
time_step = 100
x_train, y_train = create_dataset(train_data, time_step)
x_test, y_test = create_dataset(test_data, time_step)
#print(x_train.shape)

# reshape input to be [samples, time steps, features] which is required for LSTM
x_train =x_train.reshape(x_train.shape[0],x_train.shape[1] , 1)
x_test = x_test.reshape(x_test.shape[0],x_test.shape[1] , 1)
#print(x_train)

###Create the Stacked LSTM model
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM


model=Sequential()
model.add(LSTM(50,return_sequences=True,input_shape=(100,1)))
model.add(LSTM(50,return_sequences=True))
model.add(LSTM(50))
model.add(Dense(1))
model.compile(loss='mean_squared_error',optimizer='adam')

model.summary()
model.fit(x_train,y_train)

#model.fit(x_train,y_train,validation_data=(x_test,y_test),epochs=20,batch_size=64,verbose=1)

##Prediction
### Lets Do the prediction and check performance metrics
train_predict=model.predict(x_train)
test_predict=model.predict(x_test)

##Transformback to original form
train_predict=scaler.inverse_transform(train_predict)
test_predict=scaler.inverse_transform(test_predict)


### Calculate RMSE performance metrics
from sklearn.metrics import mean_squared_error
##Train Data RMSE
math.sqrt(mean_squared_error(y_train,train_predict))
### Test Data RMSE
math.sqrt(mean_squared_error(y_test,test_predict))


"""
### Plotting 
# shift train predictions for plotting
look_back=100
trainPredictPlot = np.empty_like(data)
trainPredictPlot[:, :] = np.nan
trainPredictPlot[look_back:len(train_predict)+look_back, :] = train_predict
# shift test predictions for plotting
testPredictPlot = np.empty_like(data)
testPredictPlot[:, :] = np.nan
testPredictPlot[len(train_predict)+(look_back*2)+1:len(data)-1, :] = test_predict
# plot baseline and predictions
plt.plot(scaler.inverse_transform(data))
plt.plot(trainPredictPlot)
plt.plot(testPredictPlot)
plt.show()
"""
##Prediction of future price

##Taking a last 100 data from test data
x_input=test_data[340:].reshape(1,-1)
x_input.shape

#Coverting into list and taking all the value
temp_input=list(x_input)
temp_input=temp_input[0].tolist()


## Prediction for next 30 days
from numpy import array

lst_output=[]
n_steps=100
i=0
while(i<30):
    
    if(len(temp_input)>100):
        #print(temp_input)
        x_input=np.array(temp_input[1:])
        print("{} day input {}".format(i,x_input))
        x_input=x_input.reshape(1,-1)
        #x_input = x_input.reshape((1, n_steps, 1))
        #print(x_input)
        yhat = model.predict(x_input, verbose=0)
        print("{} day output {}".format(i,yhat))
        temp_input.extend(yhat[0].tolist())
        temp_input=temp_input[1:]
        #print(temp_input)
        lst_output.extend(yhat.tolist())
        i=i+1
    else:
        #x_input = x_input.reshape((1, n_steps,1))
        yhat = model.predict(x_input, verbose=0)
        print(yhat[0])
        temp_input.extend(yhat[0].tolist())
        print(len(temp_input))
        lst_output.extend(yhat.tolist())
        i=i+1
    
print(lst_output)

"""
##Plotting the result
day_new=np.arange(1,101)
day_pred=np.arange(101,131)

plt.plot(day_new,scaler.inverse_transform(data[1157:]))
plt.plot(day_pred,scaler.inverse_transform(lst_output))


result=data.tolist()
result.extend(lst_output)
plt.plot(result[1000:])

result=scaler.inverse_transform(result).tolist()

plt.plot(result)
"""
