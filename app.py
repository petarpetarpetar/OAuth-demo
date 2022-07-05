# Importing everything needed for the flask app
from flask import Flask, redirect, render_template, request, session

# Importing everything needed for Google Ads Client
from google.ads.googleads.client import GoogleAdsClient
import google_auth_oauthlib.flow

# Importing everything needed for firebase
import firebase_admin
from firebase_admin import credentials, firestore

# Importing everything for environment variable
import os
from dotenv import load_dotenv

# Utilities that we're using:
from utils.list_all_customers import list_all_customers
from utils.get_campaigns import get_campaigns

# Load environment variables from .env file
load_dotenv()

# Flask app initialization
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# Firestore connection initialization
FIREBASE_CREDS = credentials.Certificate(os.environ.get("FIREBASE_CERT_PATH"))
firebase_admin.initialize_app(FIREBASE_CREDS)
db = firestore.client()

# Creating Oauth flow and authorization_url
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    "client_secrets.json",
    scopes=[
        "https://www.googleapis.com/auth/adwords",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ],
    redirect_uri=os.environ.get("OAUTH_REDIRECT_URI"),
)
authorization_url, state = flow.authorization_url(
    # Enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type="offline",
    # Enable incremental authorization. Recommended as a best practice.
    include_granted_scopes="true",
)


# This route acts like a proxy for authorization_url
@app.route("/consent")
def request_consent():
    return redirect(authorization_url)


# User will get redirected here after they give their consent
# Note that this endpoint will redirect to /listCustomers
# ^ It is not safe to render any html on this endpoint as it could compromise user's credentials!
@app.route("/oauth2callback")
def oauth2_callback():
    code = request.args.get("code")
    flow.fetch_token(code=code)

    sess = flow.authorized_session()
    prof_info = sess.get("https://www.googleapis.com/userinfo/v2/me").json()
    session["prof_info"] = prof_info

    db.collection("users").document(prof_info["email"]).set(
        {
            "refresh_token": flow.credentials.refresh_token,
            "token": flow.credentials.token,
        }
    )
    return redirect("/listCustomers")


@app.route("/listCustomers")
def finalise():

    doc_ref = db.collection("users").document(session["prof_info"]["email"])

    doc = doc_ref.get()

    gads = GoogleAdsClient.load_from_dict(
        {
            "developer_token": os.environ.get("DEVELOPER_TOKEN"),
            "use_proto_plus": False,
            "client_id": os.environ.get("CLIENT_ID"),
            "client_secret": os.environ.get("CLIENT_SECRET"),
            "refresh_token": doc.to_dict()["refresh_token"],
            "login_customer_id": os.environ.get("LOGIN_CUSTOMER_ID"),
        }
    )
    accessible_customers = list_all_customers(gads)

    return render_template("listCustomers.html", customers=accessible_customers)


# Home route
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/getCampaigns/<customer_id>")
def getCampaigns(customer_id):

    doc_ref = db.collection("users").document(session["prof_info"]["email"])

    doc = doc_ref.get()

    if doc.exists:
        googleads_client = GoogleAdsClient.load_from_dict(
            {
                "developer_token": os.environ.get("DEVELOPER_TOKEN"),
                "use_proto_plus": False,
                "client_id": os.environ.get("CLIENT_ID"),
                "client_secret": os.environ.get("CLIENT_SECRET"),
                "refresh_token": doc.to_dict()["refresh_token"],
            }
        )
        return get_campaigns(client=googleads_client, customer_id=customer_id)

    else:
        return "error"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
