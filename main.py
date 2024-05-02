import logging
import json, os
from os import path
from flask import request, Response, render_template, jsonify, Flask
from flask_cors import CORS
from pywebpush import webpush, WebPushException
import random


app = Flask(__name__)
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
CORS(app, resources={r"/save/*": {"origins": "*"}, r"/send/*":{"origins":"*"}})

DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH = os.path.join(os.getcwd(),"private_key.txt")
DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH = os.path.join(os.getcwd(),"public_key.txt")

VAPID_PRIVATE_KEY = open(DER_BASE64_ENCODED_PRIVATE_KEY_FILE_PATH, "r+").readline().strip("\n")
VAPID_PUBLIC_KEY = open(DER_BASE64_ENCODED_PUBLIC_KEY_FILE_PATH, "r+").read().strip("\n")

payload =  {
        "notification":{
            "title": "KPI BBVA actualizado para el día de hoy",
            "body": "KPI BBVA Colombia",
            "vibrate_timings":[100,50,100],
            "image":"./images/BBVA_2019.png",
            "data": {
                "onActionClick": {
                    "default": {"operation": "openWindow"},
                
                }
            }
        }
}

VAPID_CLAIMS = {
"sub": "mailto:sebastian.torres.enciso@bbva.com"
}

def send_web_push(subscription_information, message_body):
    return webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=VAPID_PRIVATE_KEY,
        vapid_claims=VAPID_CLAIMS
    )



@app.route("/save/",methods=['POST'])
def save():
    token_already_exist= False

    random_index= random.randint(1,1000000)
    name_of_file = "tokenSubscription"+str(random_index)

    save_path="./tokens"
    completeName = os.path.join(save_path, name_of_file+".json")      
    tokens_directory= os.path.join('.', 'tokens')

    token = request.json.get('token')   
    tokenConversion= json.loads(token)
    tokenAuth = tokenConversion['keys']
    print("Token Auth from request to compare "+tokenAuth['auth'])
    try:
        contenido = os.listdir(tokens_directory)
    except Exception as e:
        print("Error listando archivos en la ruta directorio de tokens especificada "+e)
    for i in contenido:
        #Opening file
        contentFile = open(save_path+"/"+i,"r")
        data = json.load(contentFile)
        dataToValidate= data['keys']
        print("Token Auth from stored file to compare "+dataToValidate['auth'])
        token_already_exist =  dataToValidate['auth']  == tokenAuth['auth']
        #Closing file
        contentFile.close()
        if token_already_exist== True:
            break
        
    if(not bool(token_already_exist)):
        file = open(completeName,"w+")
        file.write(token)
        file.close()
        print("New Token client stored")
        return {"OK":200}
    else :
        print("The Token has already taken and exist by this user")
        return {"The Token has already taken and exist by this user":200}
    


@app.route("/send/", methods=["POST"])
def sendPushNotification():
    """
        POST creates a subscription
        GET returns vapid public key which clients uses to send around push notification
    """
    message = json.dumps(payload)
    save_path="./tokens"
    tokens_directory= os.path.join('.', 'tokens')
    try:
        contenido = os.listdir(tokens_directory)
    except:
        print("Error listando archivos en la ruta directorio de tokens especificada")
    for i in contenido:
        #Opening file
        contentFile = open(save_path+"/"+i,"r")
        data = json.load(contentFile)
        
        try:
            token = data
            send_web_push(token, message)
            print("Sended push message to destination")
            # return jsonify({'success':1})
        except Exception as e:
            print("error",e)
            # return jsonify({'failed':str(e)})
    return jsonify({'success':1})



if __name__ == "__main__":
    app.run(host="0.0.0.0",port=9999)