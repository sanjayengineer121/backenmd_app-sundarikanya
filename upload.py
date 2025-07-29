import dropbox
import os
import requests
import time
import json

# APP_KEY = "9yzl0g2ez2uvbue"
# APP_SECRET = "2vmc871245bt8z5"
# REFRESH_TOKEN = "5dLRY8TPLCsAAAAAAAAAAf41iVwvZ56CPQayFXawSBb_ysGDH7CbTuZkp-PxBw7p"
# IMGBB_API_KEY = "ccc2c8268236991b9eeb435d41ae4271"

APP_KEY = "i6njerp0zlda35l"
APP_SECRET = "yonvxndkvdmkhdi"
REFRESH_TOKEN = "qKIKNKEavLEAAAAAAAAAAb6l5h8ptkRIrPG-31bif29BJYgRom8iqg9Dsp0RFzOX"
IMGBB_API_KEY = "ccc2c8268236991b9eeb435d41ae4271"
SESSION_FILE = "token_session.json"
TOKEN_EXPIRY_SECONDS = 5 * 60 * 60  # 5 hours

# === Get valid access token ===
def get_valid_access_token():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            session = json.load(f)
            token_time = session.get("generated_at", 0)
            if time.time() - token_time < TOKEN_EXPIRY_SECONDS:
                print("✅ Using cached access token.")
                return session.get("access_token")

    # Get a new access token
    url = 'https://api.dropbox.com/oauth2/token'
    auth = (APP_KEY, APP_SECRET)
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': REFRESH_TOKEN
    }

    response = requests.post(url, data=data, auth=auth)
    if response.status_code == 200:
        new_token = response.json()
        access_token = new_token.get('access_token')
        print("🆕 Refreshed Dropbox access token.")

        with open(SESSION_FILE, "w") as f:
            json.dump({
                "access_token": access_token,
                "generated_at": time.time()
            }, f, indent=2)

        return access_token
    else:
        print("❌ Failed to refresh token:", response.text)
        raise Exception("Token refresh failed")

ACCESS_TOKEN = get_valid_access_token()
print(ACCESS_TOKEN)

dbx = dropbox.Dropbox(ACCESS_TOKEN)

# === DO NOT CHANGE BELOW FUNCTIONS ===
def upload_to_root(local_file_path):
    file_name = os.path.basename(local_file_path)
    dropbox_destination = f"/{file_name}"

    with open(local_file_path, 'rb') as f:
        dbx.files_upload(f.read(), dropbox_destination, mode=dropbox.files.WriteMode.overwrite)

    # Generate shared link
    shared_link = dbx.sharing_create_shared_link_with_settings(dropbox_destination).url
    direct_link = shared_link.replace("&dl=0", "&raw=1")

    print(f"✅ Uploaded to Dropbox as: {file_name}")
    print("✅ Direct Link:", direct_link)
    return direct_link

def upload_image(image_path):
    upload_url = "https://api.imgbb.com/1/upload"
    with open(image_path, "rb") as img_file:
        payload = {"key": IMGBB_API_KEY}
        files = {"image": img_file}
        response = requests.post(upload_url, data=payload, files=files)

    if response.status_code == 200:
        data = response.json()
        print("✅ Uploaded Successfully")
        print("Image Link:", data['data']['url'])
        print("Delete Link:", data['data']['delete_url'])
        return data['data']['url']
    else:
        print("❌ Upload failed:", response.text)
        return None
