# this code is heavily adapted from Jason Brownlee's
# tutorials on machinelearningmastery.com
# https://machinelearningmastery.com/convert-time-series-supervised-learning-problem-python/
# https://machinelearningmastery.com/multivariate-time-series-forecasting-lstms-keras/
# Extra comments are sprinkled throughout to demonstrate my understanding of the code.


from math import sqrt
from numpy import concatenate
from matplotlib import pyplot as plt
from pandas import read_csv
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
# the following code silences some TF error messages that I should
# probably look closer into but so far haven't been able to solve
# it needs to be called before tensorflow is added
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from keras.models import Sequential
from keras.layers import Dense, LSTM
from keras.optimizers import Adam


# convert series to supervised learning.
# the magic here is in the pandas `shift` method.
# The first tutorial linked in the header goes over it in detail. 
# It lets you add a column or columns which are the values from
# previous columns shifted up or down. This is perfect for including
# t-1 and t+1 in the same row as t.
def series_to_supervised(data, n_in=1, n_out=1):
	n_vars = data.shape[1]
	df = DataFrame(data)
	cols, names = list(), list()
	# input sequence (t-n, ... t-1)
	for i in range(n_in, 0, -1):
		cols.append(df.shift(i))
		names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
	# forecast sequence (t, t+1, ... t+n)
	for i in range(0, n_out):
		cols.append(df.shift(-i))
		if i == 0:
			names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
		else:
			names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
	# put it all together
	agg = concat(cols, axis=1)
	agg.columns = names
	# get rid of NaN
	# (i don't know ehere the NaN is coming from, but somehow it appears)
	agg.dropna(inplace=True)

	return agg
 
# load dataset
dataset = read_csv('data_cleaned.csv', header=0, index_col=0)
values = dataset.values
# ensure all data is float
values = values.astype('float32')
# normalize features
scaler = MinMaxScaler(feature_range=(0, 1))
scaled = scaler.fit_transform(values)
# frame as supervised learning
reframed = series_to_supervised(scaled, 1, 1)
# drop columns we don't want to predict (only keep Hs for time t)
reframed.drop(reframed.columns[[16, 17, 18, 19, 20, 21, 22, 23, 24,25,26,27,28,29]], axis=1, inplace=True)
# this is what our input data looks like
print("HEAD OF INPUT DATA:")
print(reframed.head())
print("")
# split into train and test sets
# We will see if it works on the last 3 days of data
values = reframed.values # get rid of first row because t-1 isn't defined yet
train = values[:-11, :]
test = values[-11:, :]
# split inputs and outputs
train_X, train_y = train[:, :-1], train[:, -1]
test_X, test_y = test[:, :-1], test[:, -1]
# reshape input to be [samples, timesteps, features] (required by LSTM)
train_X = train_X.reshape((train_X.shape[0], 1, train_X.shape[1]))
test_X = test_X.reshape((test_X.shape[0], 1, test_X.shape[1]))
# shape of train_X, train_y, test_X, test_y is now
# (1180, 1, 15) (1180,) (8, 1, 15) (8,)

# here I tried a bunch of different set-ups because I'm not entirely
# sure how to choose the correct network shape for my data.
# This is what I settled on.
# I used different activation and loss functions because they worked out
# better for my data, and added an extra LSTM layer for the fun of it.
# Changing the amount of nodes in either layer didn't have much effect.
model = Sequential()
model.add(LSTM(50,return_sequences=True, activation='relu', input_shape=(train_X.shape[1], train_X.shape[2])))
model.add(LSTM(25, activation='relu'))
model.add(Dense(1))
optimizer = Adam(clipnorm=1.0)
model.compile(loss='mse', optimizer=optimizer)
# fit network
history = model.fit(train_X, train_y, epochs=50, batch_size=5,  validation_data=(test_X, test_y), verbose=2, shuffle=False)
# plot history
plt.plot(history.history['loss'], label='train')
plt.plot(history.history['val_loss'], label='test')
plt.legend()

# the following code is taken essentially
# unchanged from Jason Brownlee's tutorial.
# (All I did was rename `yhat`` to `y_pred`
# because it's a more meaningful name to me)
# I still took the time to make sure I understand
# what everything is doing and why,
# so I left commments to demonstrate this.

# make a prediction (result is in normalized values)
y_pred = model.predict(test_X)
# reformat into original shaping
test_X = test_X.reshape((test_X.shape[0], test_X.shape[2]))
# invert scaling for forecast (undo the feature normalization)
# first, combine the predicted y with the relevant features
inv_y_pred = concatenate((y_pred, test_X[:, 1:]), axis=1)
# do the actual work of inverse scaling
inv_y_pred = scaler.inverse_transform(inv_y_pred)
# we're only interested in the y vector
inv_y_pred = inv_y_pred[:,0]
# repeat for actual values
test_y = test_y.reshape((len(test_y), 1))
inv_y = concatenate((test_y, test_X[:, 1:]), axis=1)
inv_y = scaler.inverse_transform(inv_y)
inv_y = inv_y[:,0]
# calculate RMSE (we went over the reasoning for this error in class)
rmse = sqrt(mean_squared_error(inv_y, inv_y_pred))
print("      actual               predicted")
print("========================================")
for i in range(len(test_y)):
	print(f"{inv_y[i]} -> {inv_y_pred[i]}")
print('Test RMSE: %.3f' % rmse)



# show the training graph
plt.show()