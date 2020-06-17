import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import numpy as np
import tensorflow as tf
from tensorflow import keras
import joblib


engine = create_engine("postgres://sollsrywssgqwp:3c79a640882fb271f04b87c85e54e09c654059316404be7bcdb671cc6bf7976d@ec2-35-171-31-33.compute-1.amazonaws.com:5432/d77ns8sefglun7")
db = scoped_session(sessionmaker(bind=engine))


df_reg = pd.read_sql_query('select * from "reg_users"',con=engine)
#df_pro = pd.read_sql_query('select * from "pros"',con=engine)
#df_cheat = pd.read_sql_query('select * from "cheaters"',con=engine)

#df_pro=pd.read_csv("df3.csv")
df_reg_kill=df_reg[['playdate','kill']]
df_reg_kill.index=df_reg_kill['playdate']
df_reg_kill=df_reg_kill.drop('playdate',axis=1)
df=df_reg_kill

train_size = int(len(df) * 0.8)
test_size = len(df) - train_size
train, test = df.iloc[0:train_size], df.iloc[train_size:len(df)]

def create_dataset(X, y, time_steps=1):
    Xs, ys = [], []
    for i in range(len(X) - time_steps):
        v = X.iloc[i:(i + time_steps)].values
        Xs.append(v)        
        ys.append(y.iloc[i + time_steps])
    return np.array(Xs), np.array(ys)

time_steps = 1

# reshape to [samples, time_steps, n_features]
X_train, y_train = create_dataset(train, train.kill, time_steps)
X_test, y_test = create_dataset(test, test.kill, time_steps)


model = keras.Sequential()
model.add(keras.layers.LSTM(128, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(keras.layers.Dense(1))
model.compile(loss='mean_squared_error', optimizer=keras.optimizers.Adam(0.001))

history = model.fit(
    X_train, y_train, 
    epochs=30, 
    batch_size=16, 
    validation_split=0.1, 
    verbose=0, 
    shuffle=False
)

model_json = model.to_json()
with open("model.json", "w") as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save("model.h5")

    # reg_y_pred=y_pred
    # reg_y_test=y_test
    # reg_x_test=np.arange(len(y_train), len(y_train) + len(y_test))
    # P_reg = np.array([reg_x_test, np.squeeze(reg_y_pred)]).T



