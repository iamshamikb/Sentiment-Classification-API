# !pip install --upgrade pip
# !pip install pandas
# !pip install re
# !pip install string
# !pip install seaborn
# !pip install matplotlib
# !pip install textblob
# !pip install nltk
# !pip install tqdm
# !pip install spacy
# !pip install tensorflow_hub
# !pip install sklearn



import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

from IPython.display import clear_output
import re
import string
from sklearn.metrics import roc_auc_score

path=''
import sys
sys.path.append(path)
!pip install sentencepiece 
import tokenization


contractions = {
"ain't": "am not / are not",
"aren't": "are not / am not",
"can't": "cannot",
"can't've": "cannot have",
"'cause": "because",
"could've": "could have",
"couldn't": "could not",
"couldn't've": "could not have",
"didn't": "did not",
"doesn't": "does not",
"don't": "do not",
"hadn't": "had not",
"hadn't've": "had not have",
"hasn't": "has not",
"haven't": "have not",
"he'd": "he had / he would",
"he'd've": "he would have",
"he'll": "he shall / he will",
"he'll've": "he shall have / he will have",
"he's": "he has / he is",
"how'd": "how did",
"how'd'y": "how do you",
"how'll": "how will",
"how's": "how has / how is",
"i'd": "I had / I would",
"i'd've": "I would have",
"i'll": "I shall / I will",
"i'll've": "I shall have / I will have",
"i'm": "I am",
"i've": "I have",
"isn't": "is not",
"it'd": "it had / it would",
"it'd've": "it would have",
"it'll": "it shall / it will",
"it'll've": "it shall have / it will have",
"it's": "it has / it is",
"let's": "let us",
"ma'am": "madam",
"mayn't": "may not",
"might've": "might have",
"mightn't": "might not",
"mightn't've": "might not have",
"must've": "must have",
"mustn't": "must not",
"mustn't've": "must not have",
"needn't": "need not",
"needn't've": "need not have",
"o'clock": "of the clock",
"oughtn't": "ought not",
"oughtn't've": "ought not have",
"shan't": "shall not",
"sha'n't": "shall not",
"shan't've": "shall not have",
"she'd": "she had / she would",
"she'd've": "she would have",
"she'll": "she shall / she will",
"she'll've": "she shall have / she will have",
"she's": "she has / she is",
"should've": "should have",
"shouldn't": "should not",
"shouldn't've": "should not have",
"so've": "so have",
"so's": "so as / so is",
"that'd": "that would / that had",
"that'd've": "that would have",
"that's": "that has / that is",
"there'd": "there had / there would",
"there'd've": "there would have",
"there's": "there has / there is",
"they'd": "they had / they would",
"they'd've": "they would have",
"they'll": "they shall / they will",
"they'll've": "they shall have / they will have",
"they're": "they are",
"they've": "they have",
"to've": "to have",
"wasn't": "was not",
"we'd": "we had / we would",
"we'd've": "we would have",
"we'll": "we will",
"we'll've": "we will have",
"we're": "we are",
"we've": "we have",
"weren't": "were not",
"what'll": "what shall / what will",
"what'll've": "what shall have / what will have",
"what're": "what are",
"what's": "what has / what is",
"what've": "what have",
"when's": "when has / when is",
"when've": "when have",
"where'd": "where did",
"where's": "where has / where is",
"where've": "where have",
"who'll": "who shall / who will",
"who'll've": "who shall have / who will have",
"who's": "who has / who is",
"who've": "who have",
"why's": "why has / why is",
"why've": "why have",
"will've": "will have",
"won't": "will not",
"won't've": "will not have",
"would've": "would have",
"wouldn't": "would not",
"wouldn't've": "would not have",
"y'all": "you all",
"y'all'd": "you all would",
"y'all'd've": "you all would have",
"y'all're": "you all are",
"y'all've": "you all have",
"you'd": "you had / you would",
"you'd've": "you would have",
"you'll": "you shall / you will",
"you'll've": "you shall have / you will have",
"you're": "you are",
"you've": "you have"
}

def decontract(raw_html):
    for word in raw_html.split():
        if word.lower() in contractions:
            raw_html = raw_html.replace(word, contractions[word.lower()])
    return raw_html


def fun(X):
    tf.keras.backend.clear_session()
    max_seq_length = mymaxlen = 170
    input_word_ids = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name="input_word_ids")
    input_mask = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name="input_mask")
    segment_ids = tf.keras.layers.Input(shape=(max_seq_length,), dtype=tf.int32, name="segment_ids")

    bert_layer = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/1", trainable=False)
    pooled_output, sequence_output = bert_layer([input_word_ids, input_mask, segment_ids])

    bert_model = Model(inputs=[input_word_ids, input_mask, segment_ids], outputs=pooled_output)

    vocab_file = bert_layer.resolved_object.vocab_file.asset_path.numpy()
    do_lower_case = bert_layer.resolved_object.do_lower_case.numpy()
    tokenizer = tokenization.FullTokenizer(vocab_file, do_lower_case)
    
    print('Tokeninzing...')
    X_t = []
    X_m = []
    X_s = []
    mymaxlen = 170
    fornulls = []
    for i in range(mymaxlen-2):
            fornulls.append('[PAD]')

    for i in range(len(X)):
        if len(X)==1:
            tokens = tokenizer.tokenize(X[0])
        else:
            tokens = tokenizer.tokenize(X.values[i])
        
        if len(tokens)>=(mymaxlen-2):
            tokens = tokens[0:(mymaxlen-2)]
            tokens = ['[CLS]', *tokens, '[SEP]']
            only_token = len(tokens)  
        else:
            tokens = ['[CLS]', *tokens, '[SEP]'] 
            only_token = len(tokens) 
            gap = max_seq_length-only_token
            for j in range(gap):
                tokens.append('[PAD]')

        if np.asarray(tokenizer.convert_tokens_to_ids(tokens)) is not None:
            X_t.append(np.asarray(tokenizer.convert_tokens_to_ids(tokens)))
        else :
            X_t.append(np.asarray(tokenizer.convert_tokens_to_ids(['[CLS]', *fornulls, '[SEP]'])))

        if (np.asarray([1]*len(tokens)+[0]*(max_seq_length-len(tokens)))) is not None:
            X_m.append(np.asarray([1]*(only_token)+[0]*(max_seq_length-only_token)))
        else :
            X_m.append(np.asarray([1]*len(fornulls)+[0]*(max_seq_length-len(fornulls))))
        X_s.append(np.asarray([0]*max_seq_length))

    X_t = np.asarray(X_t)
    X_m = np.asarray(X_m)
    X_s = np.asarray(X_s)
    return bert_model, X_t, X_m, X_s

def auc_score(y_true, y_pred):
    return tf.py_function(roc_auc_score,(y_true,y_pred),tf.double) 

def simple_preprocessing_function(text):
    text = re.sub('@\S*\s','',text+str(' '))      # Removing @VirginAmerica and likes of that
    text = re.sub('http:\S*\s','',text+str(' '))  # Remove hyperlinks
    text = decontract(text)                       # Decontractions
    text = re.sub("[^-9A-Za-z ]", " " , text)     # Remove punctuations and special charaters
    text = re.sub(' +', ' ', text)                # Remove extra spaces
    text = "".join([i.lower() for i in text if i not in string.punctuation])  # To lower case
    return text

def prediction_function(text):
        print('Will need 10 seconds in Paperspace GPU, 2 min in Colab GPU...')
        print('Cleaning the text...')
        text = [simple_preprocessing_function(text)]
        
        print('Making BERT Ready...')
        bert_model, Xn_test_tokens, Xn_test_mask, Xn_test_segment = fun(text)
        print('BERT is making predictions...')
        cl=bert_model.predict([Xn_test_tokens, Xn_test_mask, Xn_test_segment])
        
        print('Loading the additional Neural Network...')
        nnmodel = tf.keras.models.load_model("bert_model2.hdf5", compile=False)
        nnmodel.compile(loss='binary_crossentropy', optimizer=Adam(), metrics=['accuracy', auc_score])
         
        print('Making final predictions...')                      # 0 Negetive ,1 Positive
        predictions = nnmodel.predict(cl)[0]
        clear_output()
        
        # print(round(predictions[0], 4), '% Negetive. ', round(predictions[1], 4), '% Positive.')
        result = str(text[0]) + '::: is :::'+str(round(predictions[0], 4))+ ' % Negetive. '+ str(round(predictions[1], 4))+ ' % Positive.   Verdict- '

        if nnmodel.predict(cl).argmax(axis=-1) == 0:
            print('It is a Negetive Review.')
            return result+'Negetive Review'
        else:
            print('It is a Positive Review.')
            return result+'Positive Review'
        print('-------------------------------------------')

####################### Flask ############################
!pip install flask-ngrok

from flask_ngrok import run_with_ngrok
from flask import Flask, request, render_template, jsonify
app = Flask(__name__)
run_with_ngrok(app)

@app.route('/', methods=['GET', 'POST'])
def check_sentiment():
    if request.method == 'POST':
        verdict = prediction_function(request.form['input_text'])
        # verdict = request.form['input_text']
        return jsonify(verdict)
    return render_template('trial.html')

app.run()