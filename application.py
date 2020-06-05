import os
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from flask import Flask, request, render_template,url_for,redirect,flash, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import numpy as np
import similaritymeasures
from scipy.spatial.distance import directed_hausdorff

from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

#sys.path.append(os.path.abspath("./model"))
#from load import * 


#graph = tf.get_default_graph()

app = Flask(__name__)


model = keras.models.load_model("assets/model.h5")
#transformer = joblib.load("assets/data_transformer.joblib")


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://sollsrywssgqwp:3c79a640882fb271f04b87c85e54e09c654059316404be7bcdb671cc6bf7976d@ec2-35-171-31-33.compute-1.amazonaws.com:5432/d77ns8sefglun7")
db = scoped_session(sessionmaker(bind=engine))

#model = load_model('reg_model.h5', custom_objects={'auc': auc})

@app.route('/', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        csv_file = request.files['file']
        df = pd.read_csv(csv_file)
        
        df_kill=df[['playdate','kill']]
        df_kill.index=df_kill['playdate']
        df_kill=df_kill.drop('playdate',axis=1)
        df=df_kill

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

        y_pred = model.predict(X_test)

        in_y_pred=y_pred
        in_y_test=y_test
        in_x_test=np.arange(len(y_train), len(y_train) + len(y_test))
        P_in = np.array([in_x_test, np.squeeze(in_y_pred)]).T


        P_reg=np.array([[79.        ,  0.68125933],
       [80.        ,  0.68125933],
       [81.        ,  0.68125933],
       [82.        ,  0.68125933],
       [83.        ,  0.68125933],
       [84.        ,  0.91892499],
       [85.        ,  1.37220061],
       [86.        ,  0.68125933],
       [87.        ,  1.15134037],
       [88.        ,  1.37220061],
       [89.        ,  1.37220061],
       [90.        ,  0.68125933],
       [91.        ,  0.68125933],
       [92.        ,  0.68125933],
       [93.        ,  0.91892499],
       [94.        ,  0.68125933],
       [95.        ,  0.68125933],
       [96.        ,  0.68125933],
       [97.        ,  0.68125933]])

        P_pro=np.array([[15.        ,  3.20631218],
       [16.        ,  1.37398887],
       [17.        ,  1.90838337]])

        P_cheat=np.array([[11.        ,  5.55175591],
       [12.        ,  4.50792074]])

        # dh, ind1, ind2 = directed_hausdorff(P_reg, P_in)
        # df = similaritymeasures.frechet_dist(P_reg, P_in)
        # dtw, d = similaritymeasures.dtw(P_reg, P_in)
        # pcm = similaritymeasures.pcm(P_reg, P_in)
        # area = similaritymeasures.area_between_two_curves(P_reg, P_in)
        # cl = similaritymeasures.curve_length_measure(P_reg, P_in)
        distance, path = fastdtw(P_reg, P_in, dist=euclidean)

        # P_reg_in=[dh,df,dtw,pcm,cl,area]

        val_P_reg_in=distance

        # P_reg_cheat=[85.0860936788796,85.0860936788796,1446.7625213678207,68.78901771141983,8.231848672890777,187.4096377082169]
        # P_reg_pro=[80.00941090520637,80.00941090520637,1352.1920753596385,44.05548354039518,5.057249788685258,208.3627917431295]

        distance, path = fastdtw(P_reg, P_cheat, dist=euclidean)
        val_P_reg_cheat=distance

        distance, path = fastdtw(P_reg, P_pro, dist=euclidean)
        val_P_reg_pro=distance

        if val_P_reg_in > val_P_reg_cheat or (val_P_reg_pro < val_P_reg_in < val_P_reg_cheat):
        	message="Abnormal"
        else:
        	message="Not Abnormal" 
# all methods will return 0.0 when P and Q are the same
#print(dh, df, dtw, pcm, cl, area)


        return render_template('index.html',in_y_pred=in_y_pred,in_y_test=in_y_test,in_x_test=in_x_test,val_P_reg_cheat=val_P_reg_cheat,val_P_reg_in=val_P_reg_in,val_P_reg_pro=val_P_reg_pro,message=message)

    return """
            <form method='post' action='/' enctype='multipart/form-data'>
              Upload a csv file: <input type='file' name='file'>
              <input type='submit' value='Upload'>
            </form>
           """


@app.route('/success')
def success():
	return render_template("home.html")

if __name__ == '__main__':
    #db.create_all()
    app.run(debug=True)