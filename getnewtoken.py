# import urllib.parse

# def generate_dropbox_auth_url(app_key, redirect_uri, state="12345"):
#     base_url = "https://www.dropbox.com/oauth2/authorize"
#     params = {
#         "client_id": app_key,
#         "response_type": "code",
#         "token_access_type": "offline",  # To get refresh_token
#         "redirect_uri": redirect_uri,
#         "state": 12345
#     }
#     url = f"{base_url}?{urllib.parse.urlencode(params)}"
#     print("📎 Open this URL in your browser and authorize:")
#     print(url)

# # 👉 Call the function here:
# APP_KEY = "9yzl0g2ez2uvbue"
# REDIRECT_URI = "http://localhost"

# generate_dropbox_auth_url(APP_KEY, REDIRECT_URI)




# import requests
# import base64
# import json

# APP_KEY = "9yzl0g2ez2uvbue"
# APP_SECRET = "2vmc871245bt8z5"

# # Step 1: Encode app_key:app_secret in base64
# auth_string = f"{APP_KEY}:{APP_SECRET}"
# encoded_auth = base64.b64encode(auth_string.encode()).decode()

# # Step 2: Prepare headers
# headers = {
#     "Authorization": f"Basic {encoded_auth}",
#     "Content-Type": "application/json"
# }

# # Step 3: Make the request
# url = "https://api.dropboxapi.com/2/check/app"
# response = requests.post(url, headers=headers, data=json.dumps({}))

# # Step 4: Check response
# if response.ok:
#     print("✅ App credentials are valid.")
#     print(response.json())
# else:
#     print("❌ App check failed:", response.status_code)
#     print(response.text)



# import requests
# from requests.auth import HTTPBasicAuth

# def exchange_code_for_tokens(app_key, app_secret, auth_code, redirect_uri):
#     url = "https://api.dropbox.com/oauth2/token"
#     data = {
#         "code": auth_code,
#         "grant_type": "authorization_code",
#         "redirect_uri": redirect_uri
#     }

#     auth = HTTPBasicAuth(app_key, app_secret)
#     response = requests.post(url, data=data, auth=auth)

#     if response.ok:
#         tokens = response.json()
#         print("✅ Token exchange successful!")
#         print("Access Token:", tokens["access_token"])
#         print("Refresh Token:", tokens["refresh_token"])
#         print("Expires In:", tokens["expires_in"])
#         return tokens
#     else:
#         print("❌ Failed to exchange code:", response.status_code)
#         print(response.text)
#         return None


# APP_KEY = "9yzl0g2ez2uvbue"
# APP_SECRET = "2vmc871245bt8z5"
# AUTH_CODE = "code_from_browser_redirect"
# REDIRECT_URI = "http://localhost"

# exchange_code_for_tokens(APP_KEY, APP_SECRET, AUTH_CODE, REDIRECT_URI)



import requests

APP_KEY = "i6njerp0zlda35l"
APP_SECRET = "yonvxndkvdmkhdi"
AUTHORIZATION_CODE = 'BvnkFR3KOqAAAAAAAAAA6f5jRnSKsmonuoPmjNmfbxc'

url = 'https://api.dropbox.com/oauth2/token'
auth = (APP_KEY, APP_SECRET)
data = {
    'code': AUTHORIZATION_CODE,
    'grant_type': 'authorization_code',
}

response = requests.post(url, data=data, auth=auth)
tokens = response.json()

print("✅ Access Token:", tokens.get('access_token'))
print("♻️ Refresh Token:", tokens.get('refresh_token'))



# REFRESH_TOKEN = '5dLRY8TPLCsAAAAAAAAAAf41iVwvZ56CPQayFXawSBb_ysGDH7CbTuZkp-PxBw7p'

# url = 'https://api.dropbox.com/oauth2/token'
# auth = (APP_KEY, APP_SECRET)
# data = {
#     'grant_type': 'refresh_token',
#     'refresh_token': REFRESH_TOKEN
# }

# response = requests.post(url, data=data, auth=auth)
# new_token = response.json()

# access_token = new_token.get('access_token')
# print("🆕 New Access Token:", access_token)


# headers = {
#     'Authorization': f'Bearer {access_token}',
#     'Content-Type': 'application/json'
# }

# res = requests.post('https://api.dropboxapi.com/2/users/get_current_account', headers=headers)
# print(res.json())


