import streamlit as st
import pandas as pd
import os
import subprocess
from google.cloud import storage
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from pydub import AudioSegment
from textblob import TextBlob


import os
import pandas as pd
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from matplotlib.pyplot import specgram
import keras
from keras import regularizers
from keras.preprocessing import sequence
from keras.models import Sequential
from keras.layers import Dense, Embedding
from keras.layers import LSTM
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from keras.layers import Input, Flatten, Dropout, Activation
from keras.layers import Conv1D, MaxPooling1D, AveragePooling1D
from keras.models import Model
from keras.callbacks import ModelCheckpoint
from sklearn.metrics import confusion_matrix
from keras.utils import np_utils
from sklearn.preprocessing import LabelEncoder

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/content/gc-creds.json'

def upload_to_gcloud(bucket_name, source_file_name, destination_blob_name):
	"""Uploads a file to the bucket."""
	storage_client = storage.Client()
	bucket = storage_client.get_bucket(bucket_name)
	blob = bucket.blob(destination_blob_name)

	blob.upload_from_filename(source_file_name)

	print('File {} uploaded to {}.'.format(source_file_name, destination_blob_name))


#stop warning message
st.set_option('deprecation.showfileUploaderEncoding', False)

# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
  
# DB Management
import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data


def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data



def main():
	"""Simple Login App"""

	st.title("Discover the sentiment of your audio file!")

	menu = ["Home","Login","SignUp"]
	choice = st.sidebar.selectbox("Menu",menu)

	if choice == "Home":
		st.subheader("log in and upload you audio file now!")

	elif choice == "Login":
		st.subheader("Login Section")

		username = st.text_input("User Name")
		password = st.text_input("Password",type='password')
		if st.checkbox("Login"):
			# if password == '12345':
			create_usertable()
			hashed_pswd = make_hashes(password)

			result = login_user(username,check_hashes(password,hashed_pswd))
			if result:
				st.success("Logged In as {}".format(username))
				input_audio = st.file_uploader("Please upload mp3 audio file", type ="mp3")
				out_audio = "out_audio.ogg"
				s_out_audio = "s_out_audio.ogg"
				if input_audio is not None:
					sound = AudioSegment.from_mp3(input_audio)
					sound.export(out_audio, format="ogg", codec="libvorbis",  bitrate="48000")
					try:
						subprocess.call(["ffmpeg -i " + out_audio + " -acodec libopus -ac 1 -ar 16000 -compression_level 10 -application voip -vn " + s_out_audio],  shell=True)
					except Exception as e:
						print("couldn't create: "+str(e))
					bucket_name = 'mostafa-lebod'
					upload_to_gcloud(bucket_name, source_file_name=s_out_audio, destination_blob_name=s_out_audio)

					"""Please wait some time for accurate transcrbtion of your audio file"""

					client = speech.SpeechClient()
					audio = types.RecognitionAudio(
							uri="gs://" + bucket_name + "/" + s_out_audio)
					config = types.RecognitionConfig(
							encoding=enums.RecognitionConfig.AudioEncoding.OGG_OPUS,
							language_code='en-US',
							sample_rate_hertz=16000,
							enable_word_time_offsets=True
					)
					operation = client.long_running_recognize(config, audio)

					if not operation.done():
						print('Waiting for results...')

					result = operation.result()


					results = result.results
					
					audio_file_path = os.path.splitext(s_out_audio)[0]

					raw_text_file = open(audio_file_path + '.txt', 'w')
					for result in results:
						for alternative in result.alternatives:
							raw_text_file.write(alternative.transcript + '\n')
					raw_text_file.close() #output raw text file of transcription
					file1 = open(audio_file_path + '.txt',"r")
					testimonial = TextBlob(file1.read())
					#testimonial.sentiment
					#Sentiment(polarity=0.39166666666666666, subjectivity=0.4357142857142857)
					#testimonial.sentiment.polarity
					if testimonial.sentiment.polarity >= 0:
						st.success("The transcription of the audio suggests positive sentiment")
					else:
						st.warning("The transcription of the audio suggests negative Sentiment")
					df = pd.DataFrame(columns=['feature'])
					bookmark=0
					path = out_audio
					X, sample_rate = librosa.load(path, res_type='kaiser_fast',duration=2.5,sr=22050*2,offset=0.2)
					sample_rate = np.array(sample_rate)
					mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=13), axis=0)
					feature = mfccs
					#[float(i) for i in feature]
					#feature1=feature[:135]
					df.loc[bookmark] = [feature]
					bookmark=bookmark+1
					df_new = pd.DataFrame(df['feature'].values.tolist())
					#fill nan with 0
					df_new=df_new.fillna(0)
					X_test = np.array(df_new)
					x_testcnn= np.expand_dims(X_test, axis=2)
					model = keras.models.load_model('/content/audio_sentiment/Emotion_Voice_Detection_Model.h5')
					preds = model.predict(x_testcnn, 
                         batch_size=1, 
                         verbose=1)
					preds1=preds.argmax(axis=1)
					os.remove(audio_file_path+".ogg")
					if preds1[0]==0:
						st.warning("The tone of voice suggests negative senitment")
					elif preds1[0]==1:
						st.success("The tone of voice suggests positive senitment")
					elif preds1[0]==2:
						st.warning("The tone of voice suggests negative senitment")
					elif preds1[0]==3:
						st.success("The tone of voice suggests positive senitment")
					elif preds1[0]==4:
						st.warning("The tone of voice suggests negative senitment")
					elif preds1[0]==5:
						st.warning("The tone of voice suggests negative senitment")
					elif preds1[0]==6:
						st.success("The tone of voice suggests positive senitment")
					elif preds1[0]==7:
						st.warning("The tone of voice suggests negative senitment")
					elif preds1[0]==8:
						st.success("The tone of voice suggests positive senitment")
					elif preds1[0]==9:
						st.warning("The tone of voice suggests negative senitment")


			
			else:
				st.warning("Incorrect Username/Password")





	elif choice == "SignUp":
		st.subheader("Create New Account")
		new_user = st.text_input("Enter Username")
		new_password = st.text_input("Enter Password",type='password')

		if st.button("Signup"):
			create_usertable()
			add_userdata(new_user,make_hashes(new_password))
			st.success("You have successfully created a valid Account")
			st.info("Go to Login Menu to login")



if __name__ == '__main__':
	main()
