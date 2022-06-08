'''
 given an initial seed size or a specific seed in Plaintext format,
    1. evolve the seed through the NN's weights
    2. test the new output seed (using the seedTester modules)
    3. compare the output seed to the input, backprop if necessary
    4. generate a new seed
    5. repeat until new seeds do not improve stability
    6. report the maximally stable seed(s)
'''
from keras.models import Sequential
from keras.layers import Dense
from keras import optimizers


hidden_units = 100
learning_rate = 0.01
hidden_layer_act = 'tanh'
output_layer_act = 'sigmoid'
epochs = 100

model = Sequential()

model.add(Dense(hidden_units, input_dim = 8, activation=hidden_layer_act))
model.add(Dense(hidden_units, activation = hidden_layer_act))
model.add(Dense(1, activation = output_layer_act))

sgd = optimizers.SGD(lr = learning_rate)
model.compile(loss = 'binary_crossentropy', optimizer = sgd, metrics = ['acc'])

# Training

train_x = train.iloc[:, 1:9]

train_y = train.iloc[:, 9]

model.fit(train_x, train_y, epochs = no_epochs, batch_size = len(train), verbose = 2)


# Predict

predictions = model.predict(test_x)
