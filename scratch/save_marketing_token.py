import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from utils.settings_helper import set_setting

marketing_token = "65959128dc1fd202542a36cc65600c98032826248369a6cb733fc628eee278a336b54f5929ad7bb56aae82f0d600afe0e975fe8ea8"

with app.app_context():
    success = set_setting("commpeak_api_key", marketing_token)
    if success:
        print("SUCCESS: Configured marketing stream token as commpeak_api_key in database settings!")
    else:
        print("ERROR: Failed to save to database settings.")
