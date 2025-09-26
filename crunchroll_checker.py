import requests
import uuid
import random

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 10; SM-G988N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-A715F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36",
]

def get_random_user_agent():
    return random.choice(USER_AGENTS)

def crunchyroll_login(username, password, proxy=None):
    session = requests.Session()
    if proxy:
        session.proxies.update({
            "http": proxy,
            "https": proxy,
        })

    device_id = str(uuid.uuid4())
    user_agent = get_random_user_agent()

    headers_token = {
        "Host": "www.crunchyroll.com",
        "Authorization": "Basic ZDBxbWtqaGdiaGwwbWRqeDY4bmY6ZzVoYUgzOWZad1J1YWNFWk1jb0F5cFFGVk8yTnNicnQ=",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": user_agent,
    }

    data_token = {
        "username": username,
        "password": password,
        "grant_type": "password",
        "scope": "offline_access",
        "device_id": device_id,
        "device_name": "SM-G988N",
        "device_type": "samsung SM-G9810"
    }

    try:
        response_token = session.post(
            "https://beta-api.crunchyroll.com/auth/v1/token",
            headers=headers_token,
            data=data_token,
            timeout=15
        )
        if response_token.status_code == 403:
            return {"error": "Access forbidden (403). Try using a proxy or check your IP."}
        response_token.raise_for_status()
        token_json = response_token.json()
    except Exception as e:
        return {"error": f"Token request failed: {e}"}

    access_token = token_json.get("access_token")
    if not access_token:
        return {"error": "Invalid credentials or missing access token."}

    headers_auth = {
        "Authorization": f"Bearer {access_token}",
        "Connection": "Keep-Alive",
        "Host": "beta-api.crunchyroll.com",
        "User-Agent": user_agent,
    }

    try:
        response_me = session.get(
            "https://beta-api.crunchyroll.com/accounts/v1/me",
            headers=headers_auth,
            timeout=15
        )
        response_me.raise_for_status()
        me_json = response_me.json()
    except Exception as e:
        return {"error": f"Account info request failed: {e}"}

    email_verified = me_json.get("email_verified", False)
    created_at = me_json.get("created", "")
    external_id = me_json.get("external_id", "")

    if not external_id:
        return {"error": "External ID not found in account info."}

    try:
        url_products = f"https://beta-api.crunchyroll.com/subs/v1/subscriptions/{external_id}/products"
        response_products = session.get(url_products, headers=headers_auth, timeout=15)
        response_products.raise_for_status()
        products_json = response_products.json()
    except Exception as e:
        return {"error": f"Subscription products request failed: {e}"}

    plan = ""
    currency = ""
    subscribable = ""
    free_trial = ""
    if isinstance(products_json, list) and products_json:
        product = products_json[0]
        plan = product.get("sku", "")
        currency = product.get("currency_code", "")
        subscribable = str(product.get("is_subscribable", ""))
        free_trial = str(product.get("active_free_trial", ""))

    try:
        url_sub = f"https://beta-api.crunchyroll.com/subs/v1/subscriptions/{external_id}"
        response_sub = session.get(url_sub, headers=headers_auth, timeout=15)
        response_sub.raise_for_status()
        sub_json = response_sub.json()
    except Exception as e:
        return {"error": f"Subscription details request failed: {e}"}

    expiry = sub_json.get("next_renewal_date", "")
    is_cancelled = sub_json.get("is_cancelled", False)

    if is_cancelled:
        status = "EXPIRED"
    elif subscribable.lower() == "false":
        status = "FREE"
    else:
        status = "ACTIVE"

    return {
        "Email Verified": email_verified,
        "Account Creation Date": created_at,
        "Plan": plan,
        "Currency": currency,
        "Subscribable": subscribable,
        "Free Trials": free_trial,
        "Expiry": expiry,
        "Status": status,
    }

def load_list_from_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines
    except FileNotFoundError:
        return []
