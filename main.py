from google.cloud import firestore
from hedera import *
from flask import *
import os

OPERATOR_ID = AccountId.fromString(os.environ["OPERATOR_ID"])
OPERATOR_KEY = PrivateKey.fromString(os.environ["OPERATOR_KEY"])
client = Client.forTestnet()
client.setOperator(OPERATOR_ID, OPERATOR_KEY)
app = Flask(__name__, template_folder="", static_folder="")

@app.route("/save/<email>")
def save(email):
    fileContents = request.files["billphoto"].read()
    fCreate = FileCreateTransaction().setKeys(OPERATOR_KEY.getPublicKey()).setContents(fileContents).setMaxTransactionFee(Hbar(1000)).execute(client)
    fId = fCreate.getReceipt(client).fileId.toString()
    db = firestore.Client()
    db.collection("bills").document().create({"name": email})
    db.collection("bills").document(email).set({"billno": request.args.get("billno"), "billtype": request.args.get("billtype", "billphoto": fId)})

@app.route("/fetch/email/<email>")
def fetch_email(email):
    return jsonify(db.collection("bills").document(email).to_dict())

@app.route("/fetch/photo/<photoid>")
def fetch_photo(photoid):
    return FileContentsQuery().setFileId(FileId.fromString(photoid)).execute(client).toStringUtf8()

app.run(host="0.0.0.0")
