from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api
from flask_restful.reqparse import RequestParser
from uuid import uuid4

import db

app = Flask(__name__, static_folder="../email-app/build", static_url_path='/')

def get_document_by_receiverEmailAddress(receiverEmailAddress):
    documents = db.db.users.find( {"receiverEmailAddress": receiverEmailAddress }, {'_id': False} )
    output = {} 
    i = 0
    for document in documents: 
        output[i] = document 
        i += 1
    
    if not output:
        return False
    
    return output

def update_sender_receiver_new_email(emailContent, uniqueID):
    sender_new_email_data = {
        "id": uniqueID.time_low,
        "date": emailContent['date'],
        "time": emailContent['time'],
        "receiverEmailAddress": emailContent['receiverEmailAddress'],
        "subject": emailContent['subject'],
        "messageContent": emailContent['messageContent']
    }

    receiver_new_email_data = {
        "id": uniqueID.time_low,
        "date": emailContent['date'],
        "time": emailContent['time'],
        "senderEmailAddress": emailContent['senderEmailAddress'],
        "subject": emailContent['subject'],
        "messageContent": emailContent['messageContent']
    }

    update_sender = db.db.users.update({"receiverEmailAddress": emailContent['senderEmailAddress']}, {'$push': {'sent': sender_new_email_data}})
    update_receiver = db.db.users.update({"receiverEmailAddress": emailContent['receiverEmailAddress']}, {'$push': {'inbox': receiver_new_email_data}})
    
    if not update_sender["updatedExisting"] or not update_receiver["updatedExisting"]:
        return False
    
    return True

def generate_unique_id():
    id = uuid4()
    print ("The random id using uuid4() is : ") 
    print (id)

    return id

@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route("/api/email-list")
def emailList():
    receiverEmailAddress = request.args["receiverEmailAddress"]
    result = get_document_by_receiverEmailAddress(receiverEmailAddress)
    
    if not result:
        return {"msg": "no user with that email address"}, 204
    
    return jsonify(result[0]["inbox"]), 200

@app.route("/api/email/<int:messageId>/<string:receiverEmailAddress>")
def specEmail(messageId, receiverEmailAddress):
    result = get_document_by_receiverEmailAddress(receiverEmailAddress)

    if not result:
        return {"msg": "no user with that email address"}, 204

    for x in result[0]["inbox"]:
        if x["id"] == messageId:
            return x, 200
    
    return {"msg": "couldnt find message"}, 204

@app.route("/api/spec-email-sent/<int:messageId>/<string:receiverEmailAddress>")
def specEmailSent(messageId, receiverEmailAddress):
    result = get_document_by_receiverEmailAddress(receiverEmailAddress)

    if not result:
        return {"msg": "no user with that email address"}, 204

    for x in result[0]["sent"]:
        if x["id"] == messageId:
            return x, 200
    
    return {"msg": "couldnt find message"}, 204

@app.route("/api/sent-email-list")
def sentEmailList():
    receiverEmailAddress = request.args["receiverEmailAddress"]
    result = get_document_by_receiverEmailAddress(receiverEmailAddress)
    if not result:
        return {"msg": "no user with that email address"}, 204
    
    return jsonify(result[0]["sent"]), 200

@app.route("/api/composeNewEmail", methods=["POST"])
def composeNewEmail():
    body = request.get_json()

    is_receiver_exist = get_document_by_receiverEmailAddress(body["receiverEmailAddress"])
    is_sender_exist = get_document_by_receiverEmailAddress(body["senderEmailAddress"])
    
    if not is_receiver_exist or not is_sender_exist:
        return {"msg": "couldnt send email proparly"}, 204

    unique_id = generate_unique_id()

    result = update_sender_receiver_new_email(body, unique_id)
    if not result:
        return {"msg": "couldnt send email proparly"}
    
    return jsonify(body), 200

@app.route("/api/deleteEmail", methods=["DELETE"])
def deleteEmail():
    req_data = request.get_json()
    is_receiver_exist = get_document_by_receiverEmailAddress(req_data["receiverEmailAddress"])
    if not is_receiver_exist:
        res = make_response(jsonify({"err": "Member not found"}), 404)
        return res
    
    updated_inbox = db.db.users.update({"receiverEmailAddress": req_data['receiverEmailAddress']}, {'$pull': {'inbox': {"id": req_data["id"]}}})
    res = make_response(jsonify({}), 204)
    return res

@app.route("/api/deleteSentEmail", methods=["DELETE"])
def deleteSentEmail():
    req_data = request.get_json()
    is_account_exist = get_document_by_receiverEmailAddress(req_data["receiverEmailAddress"])
    if not is_account_exist:
        res = make_response(jsonify({"err": "Member not found"}), 404)
        return res
    
    updated_sent = db.db.users.update({"receiverEmailAddress": req_data['receiverEmailAddress']}, {'$pull': {'sent': {"id": req_data["id"]}}})
    res = make_response(jsonify({}), 204)
    return res

