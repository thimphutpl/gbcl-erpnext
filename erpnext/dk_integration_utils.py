import frappe
import requests
import json
import random
import json
import base64
import jwt
import string
from datetime import datetime
import datetime
from frappe.utils import flt

# @frappe.whitelist()
def dk_payment_test():
    frappe.throw('hello dk payment user')

dk_integration_setting = frappe.get_single("DK Integration Settings")

@frappe.whitelist()
def fetch_authorization_token(scope):
   
    
    # url = 'https://internal-gateway.sit.digitalkidu.bt:8082/uat/v1/cbs/connect/auth/token'
    url = dk_integration_setting.base_url + dk_integration_setting.authorization_token
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-gravitee-api-key': dk_integration_setting.x_gravitee_api_key,  # Optional
       
    }
    data = {
        'username': dk_integration_setting.user_name,
        'password': dk_integration_setting.password,
        'client_id': dk_integration_setting.client_id,
        'client_secret': dk_integration_setting.get_password('client_secret'),
        'grant_type':dk_integration_setting.grand_type,
        'source_app':dk_integration_setting.source_app,
        'scope':scope,
        'request_id':frappe.generate_hash(length=17)
    }
    token_response = requests.post(url, headers=headers, data=data)
    # frappe.throw(str(token_response.status_code))
    # if response.status_code == 200:
    #     print('Success:', response.json())
    return token_response
   

def fetch_private_key(token):
    # url = 'https://internal-gateway.sit.digitalkidu.bt:8082/uat/v1/cbs/connect/sign/key'
    url = dk_integration_setting.base_url + dk_integration_setting.fetch_key
  
    headers = {
       
        'X-gravitee-api-key': dk_integration_setting.x_gravitee_api_key,  # Optional
        'Authorization':f'bearer {token}'
       
    }
    
    data = {
            "request_id":frappe.generate_hash(length=19),
            "source_app":dk_integration_setting.source_app
        }
    # frappe.throw(str(data))
    key_response = requests.post(url, headers=headers,json=data)
    # frappe.throw(str(key_response.status_code))
    if key_response.status_code == 200:
        print('Success:', key_response.text)
        return key_response
    else:
        error_msg = f"Failed to fetch key. Status: {key_response.status_code}, Response: {key_response.text}"
        frappe.log_error(error_msg, "Key Fetch Error")
        frappe.throw(error_msg)
    # return response
    
def generate_dk_signature(private_key,account_no):
    import random
    import json
    import base64
    import datetime
    import jwt
    import string

    # Dummy RSA private key (for testing ONLY, do not use in production)
    PRIVATE_KEY_PEM = private_key
    
    def generate_nonce(length=16):
        """Generate random alphanumeric nonce of given length"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def generate_signature(request_body: dict):
        # Convert the request body to JSON string
        request_body_str = json.dumps(request_body, sort_keys=True,separators=(",", ":"))
        print(request_body_str)

    
        body_base64 = base64.b64encode(request_body_str.encode()).decode()

        # nonce = "1234567yu8"
        nonce = generate_nonce()
        print("Nonce:", nonce)
        # timestamp = "2025-05-15T11:23:45Z"
        timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=50)
        
        
        dk_signature = jwt.encode({
            "nonce": nonce,
            "timestamp": timestamp,
            "exp": expiration,
            "data": body_base64
        }, PRIVATE_KEY_PEM, algorithm="RS256")
        return dk_signature, nonce, timestamp,request_body_str
    
        currency= frappe.get_all(
            "DK Bank Payment Items",
            filters={"account_no": account_no},
            pluck="currency_code"
        )

        # Testaccount_no":"100100365856",
    sample_request_body = {
        "account_no":account_no,
        "request_id":frappe.generate_hash(length=17),
        # "request_id":'777i777778y8y',
        "source_app":dk_integration_setting.source_app,
        "product_type":dk_integration_setting.product_type
        }

    signature = generate_signature(sample_request_body)

    return signature,sample_request_body

    print("✅ Digital Signature (JWT):\n", signature)

def generate_dk_signature_transaction(private_key,doc):
    

    # Dummy RSA private key (for testing ONLY, do not use in production)
    PRIVATE_KEY_PEM = private_key
    # frappe.throw(frappe.as_json(doc))
    def generate_nonce(length=16):
        """Generate random alphanumeric nonce of given length"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    def generate_signature(request_body: dict):
        # Convert the request body to JSON string
        request_body_str = json.dumps(request_body, sort_keys=True,separators=(",", ":"))
        print(request_body_str)

    
        body_base64 = base64.b64encode(request_body_str.encode()).decode()

        # nonce = "1234567yu8"
        nonce = generate_nonce()
        print("Nonce:", nonce)
        # timestamp = "2025-05-15T11:23:45Z"
        timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=50)
        
        
        dk_signature = jwt.encode({
            "nonce": nonce,
            "timestamp": timestamp,
            "exp": expiration,
            "data": body_base64
        }, PRIVATE_KEY_PEM, algorithm="RS256")
        return dk_signature, nonce, timestamp,request_body_str
       

        # Testaccount_no":"100100365856",
    # sample_request_body = {
    #     "account_no":account_no,
    #     "request_id":frappe.generate_hash(length=17),
    #     # "request_id":'777i777778y8y',
    #     "source_app":"erp"
    #     }
    # frappe.throw(frappe.as_json(doc))
    if not doc.transaction:
        frappe.throw("No items found to process the transaction.")
    # data = frappe.db.sql('''
    #     select beneficiary_account_no, beneficiary_name,currency_code, amount, description from `tabDK Bank Payment Items`
    #     where parent = {}
    # '''.format(doc.name))
    # frappe.throw(frappe.as_json(data))
    i = doc.transaction[0]
    # frappe.throw(frappe.as_json(i))
    beneficiary_acc = i.beneficiary_account_no
    beneficiary_name = i.beneficiary_name
    currency_code = i.currency_code
    amount = i.amount
    description = doc.remarks
    beneficiary_bank = i.bank_name
    currency = i.currency_code
    fx_rate = i.fx_rate

    # frappe.throw(str(description))
        
    # if doc.salary:
    #     trans_code = dk_integration_setting.strans_code
    # else:
    #     trans_code = dk_integration_setting.nstrans_code
    if not doc.transaction_code:
        frappe.throw("Add Transaction Code")
    trans_code = frappe.db.get_value("Transaction Code",{"name":doc.transaction_code},'trans_code')
    if not beneficiary_bank:
        frappe.throw("Add Benficiary Bank in the table")
    bank_code = frappe.db.get_value("Bank",{"name":beneficiary_bank},'bank_code')
    if not bank_code:
        frappe.throw("Add Bank Code in the {} Bank".format(doc.pay_to_bank))  
    if doc.transaction_type == "Bulk DK Bank Payment":
        if currency_code == "USD":
            trans_code = "3110R"
        elif currency_code == "BTN":
            trans_code = "2400R"
        else:
            trans_code = trans_code
    
    sample_request_body = {
        "request_meta": {
        "request_id": frappe.generate_hash(length=17),
        "inquiry_id": doc.inquiry_id,
        "source_app": dk_integration_setting.source_app
        },
        "request_payload": {
        "trans_code":trans_code,
        "dr_cr": "DEBIT",
        "payer_acc": doc.bank_account_no,
        "payer_name": doc.payer_name,
        "payer_bname":"DK Bank",
        "payer_bcode":"1060",
        "beneficiary_acc": beneficiary_acc,
        "beneficiary_name": beneficiary_name,
        "beneficiary_bname": beneficiary_bank,
        "beneficiary_bcode": bank_code,
        "txn_description": description,
        "txn_purpose": "",
        "source": {
            "amount": flt(amount,2),
            "currency": currency,
            "fx_rate_to_base": flt(fx_rate,2),
            "base_currency": "BTN",
            "base_equiv_amount": flt(amount * flt(fx_rate, 2), 2)
        },
            "target": {
            "fx_rate":1,
            "amount": flt(amount,2),
            "currency": currency,
            "fx_rate_to_base": flt(fx_rate,2),
            "base_currency": "BTN",
            # "target_fx_rate ":1.0,
            "base_equiv_amount":flt(amount * flt(fx_rate, 2), 2)
        },
            "total": {
            "amount":flt(amount * flt(fx_rate, 2), 2),
            "base_currency": "BTN"
        }
        }
        }
    # frappe.throw(frappe.as_json(sample_request_body))
    

    signature = generate_signature(sample_request_body)

    return signature,sample_request_body

    print("✅ Digital Signature (JWT):\n", signature)

def generate_dk_signature_checkstatus(private_key,doc):
    
    # Dummy RSA private key (for testing ONLY, do not use in production)
    PRIVATE_KEY_PEM = private_key
    # frappe.throw(frappe.as_json(doc))
    def generate_nonce(length=16):
        """Generate random alphanumeric nonce of given length"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    def generate_signature(request_body: dict):
       
        # Convert the request body to JSON string
        request_body_str = json.dumps(request_body, sort_keys=True,separators=(",", ":"))
        print(request_body_str)

    
        body_base64 = base64.b64encode(request_body_str.encode()).decode()

        # nonce = "1234567yu8"
        nonce = generate_nonce()
        print("Nonce:", nonce)
        # timestamp = "2025-05-15T11:23:45Z"
        timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=50)
        
        
        dk_signature = jwt.encode({
            "nonce": nonce,
            "timestamp": timestamp,
            "exp": expiration,
            "data": body_base64
        }, PRIVATE_KEY_PEM, algorithm="RS256")
       
        return dk_signature, nonce, timestamp,request_body_str
       

        # Testaccount_no":"100100365856",
    # sample_request_body = {
    #     "account_no":account_no,
    #     "request_id":frappe.generate_hash(length=17),
    #     # "request_id":'777i777778y8y',
    #     "source_app":"erp"
    #     }
    # frappe.throw(frappe.as_json(doc))
    if not doc:
        frappe.throw("No items found to process the transaction.")
    # data = frappe.db.sql('''
    #     select beneficiary_account_no, beneficiary_name,currency_code, amount, description from `tabDK Bank Payment Items`
    #     where parent = {}
    # '''.format(doc.name))
    # frappe.throw(frappe.as_json(data))
    # i = doc.transaction[0]
    # # frappe.throw(frappe.as_json(i))
    # doc_dict = doc.as_dict()

# Now convert it to a JSON string
    # data = frappe.as_json(doc)
    data = json.loads(doc)
    transaction_id = data["transaction_no"]
    transaction_inquiry_id = data["inquiry_id"]
    transaction_status_request_id = data["transaction_status_request_id"]
    # beneficiary_acc = i.beneficiary_account_no
    # beneficiary_name = i.beneficiary_name
    # currency_code = i.currency_code
    # amount = i.amount
    # description = i.description
        
   
#frappe.generate_hash(length=17),
    # sample_request_body = {
    #     "request_id":frappe.generate_hash(length=17),
    #     "source_app":dk_integration_setting.source_app,
    #     "txn_id":transaction_id,
    #     "txn_inquiry_id":transaction_inquiry_id,
    #     "txn_status_req_id":transaction_status_request_id
    #     }

    sample_request_body = {
        
        "request_id":frappe.generate_hash(length=17),
        "source_app":dk_integration_setting.source_app,
        "txn_status_id":transaction_status_request_id

            }

    # frappe.throw(frappe.as_json(sample_request_body))
    

    signature = generate_signature(sample_request_body)

    return signature,sample_request_body

    print("✅ Digital Signature (JWT):\n", signature)


# @frappe.whitelist()
# def account_inquiry(account_no):
#     # frappe.throw(account_no)
#     token_response = fetch_authorization_token("keys:read")
#     if token_response.status_code != 200:
#         frappe.throw("Failed to fetch auth token")
   
#     if token_response.status_code == 200:
#         # frappe.throw(response.json()['response_data']['access_token'])
#         token = token_response.json()['response_data']['access_token']
#         # frappe.msgprint("Access Token Fetch Successfully")
#         private_key = fetch_private_key(token)
#         if private_key.status_code == 200:
#             # frappe.throw(private_key.text)
#             # dk_signature= generate_dk_signature(private_key.text,account_no)
#             (signature_data, request_body) = generate_dk_signature(private_key.text, account_no)
#             (jwt_token, nonce, timestamp,request_body_str) = signature_data
#             # frappe.throw(frappe.as_json(dk_signature))
#             token_response_inquiry = fetch_authorization_token("accounts:read")
            
#             token_inquiry = token_response_inquiry.json()['response_data']['access_token']

#             # frappe.throw(str(dk_time_stamp))
#             if signature_data:
#                 url = dk_integration_setting.base_url + dk_integration_setting.account_inquiry
#                 headers = {
#                     'Content-Type': 'application/json',
#                     'X-gravitee-api-key': dk_integration_setting.x_gravitee_api_key,  # Optional
#                     'Authorization':f'bearer {token_inquiry}',
#                     'DK-Timestamp':timestamp,
#                     'DK-Nonce':nonce,
#                     'DK-Signature':f'DKSignature {jwt_token}'
                
#                 }
#                 # frappe.throw(str(headers))
#                 # data = frappe.as_json(dk_signature[1])
#                 data = json.dumps(request_body)

#                 # inquiry_response = requests.post(url, headers=headers, data=data)
#                 inquiry_response = requests.post(url, headers=headers, data=request_body_str)
           
               
#                 if inquiry_response.status_code != 200:
#                     frappe.throw(f"CBS inquiry failed: {inquiry_response.text}")
                    
               
#                 # frappe.throw(frappe.as_json(inquiry_response.json()))
#                 # if inquiry_response.status_code == 200:

#                     # frappe.throw(str(inquiry_response.json()))
#                 inquiry_detail = inquiry_response.json()
#                 acc_status = inquiry_detail.get("response_data", {}).get("account_status", {}).get("acc_status_code")
#                 if acc_status in ["00","01"]:
#                     return inquiry_detail
#                 elif acc_status == "05":
#                     frappe.throw("Account is Dormant")
#                     return
#                 elif acc_status == "14":
#                     frappe.throw("Account is Closed")
#                     return
#                 else:
#                     frappe.throw(f"Account inquiry failed with status code: {acc_status}")
#                     return
                       

                 
#                     # return inquiry_detail
#                     # frappe.throw(frappe.as_json(inquiry_detail))
                   
#                 # return token_response
            

#     else:
#         frappe.throw('Could not fetch auth token')

@frappe.whitelist()
def account_inquiry(account_no):
    # frappe.throw(str(account_no))

    if not account_no:
        frappe.throw("Account number is required")

    # 1. Get auth token
    token_response = fetch_authorization_token("keys:read")
    if token_response.status_code != 200:
        frappe.throw("Failed to fetch auth token")

    token = token_response.json().get("response_data", {}).get("access_token")
    if not token:
        frappe.throw("Access token missing in response")

    # 2. Get private key
    private_key = fetch_private_key(token)
    if private_key.status_code != 200:
        frappe.throw("Failed to fetch private key")

    # 3. Generate signature
    signature_data, request_body = generate_dk_signature(private_key.text, account_no)
    jwt_token, nonce, timestamp, request_body_str = signature_data

    # 4. CBS auth token
    token_response_inquiry = fetch_authorization_token("accounts:read")
    token_inquiry = token_response_inquiry.json().get("response_data", {}).get("access_token")

    if not token_inquiry:
        frappe.throw("Failed to fetch inquiry access token")

    # 5. Call CBS API
    url = dk_integration_setting.base_url + dk_integration_setting.account_inquiry

    headers = {
        "Content-Type": "application/json",
        "X-gravitee-api-key": dk_integration_setting.x_gravitee_api_key,
        "Authorization": f"bearer {token_inquiry}",
        "DK-Timestamp": timestamp,
        "DK-Nonce": nonce,
        "DK-Signature": f"DKSignature {jwt_token}",
    }

    try:
        inquiry_response = requests.post(url, headers=headers, data=request_body_str, timeout=30)
    except Exception as e:
        frappe.throw(f"CBS connection failed: {str(e)}")

    # 6. Handle HTTP-level failure
    try:
        # response_json = inquiry_response.json()
        inquiry_detail = inquiry_response.json()
    except Exception:
        frappe.throw(f"Invalid JSON response from CBS: {inquiry_response.text}")

    # THIS is where your error comes from (4002 etc.)
    if inquiry_response.status_code != 200:
        frappe.throw(
            f"CBS inquiry failed ({inquiry_detail.get('response_code')}): "
            f"{inquiry_detail.get('response_detail')}"
        )
    

    # 7. Extract business-level status safely
    data = inquiry_detail.get("response_data") or {}
    if data.get("response_code") != "0000":

        error_details = data.get("error_details") or {}
        error_code = error_details.get("error_code")
        error_message = error_details.get("error_message")

        # 1. Handle specific CBS error codes FIRST
        if error_code == "2400":
            frappe.throw("Account not found.")

        elif error_code == "4002":
            frappe.throw("Invalid account number provided.")

        # 2. Handle known response_code cases
        elif data.get("response_code") == "2012":
            frappe.throw(error_message or "Account inquiry failed")
    

    acc_status = data.get("account_status", {}).get("acc_status_code")

    if not acc_status:
        frappe.throw("Missing account status from CBS response")

    # 8. Business rules
    if acc_status in ["00", "01"]:
        return inquiry_detail

    if acc_status == "05":
        frappe.throw("Account is Dormant. Transactions not allowed.")

    if acc_status == "14":
        frappe.throw("Account is Closed. Transaction not allowed.")

    # frappe.throw(f"Unsupported account status: {acc_status}")


@frappe.whitelist()
def intrabank_transfer(doc):

    token_response = fetch_authorization_token("keys:read")
    if token_response.status_code == 200:
        # frappe.throw(response.json()['response_data']['access_token'])
        token = token_response.json()['response_data']['access_token']
        # frappe.msgprint("Access Token Fetch Successfully")
        private_key = fetch_private_key(token)
        if private_key.status_code == 200:
            # frappe.throw(private_key.text)
            # dk_signature= generate_dk_signature(private_key.text,account_no)
            (signature_data, request_body) = generate_dk_signature_transaction(private_key.text, doc)
            (jwt_token, nonce, timestamp,request_body_str) = signature_data
            # frappe.throw(frappe.as_json(dk_signature))
            token_response_inquiry = fetch_authorization_token("transactions:write")
            # frappe.throw(frappe.as_json(token_response_inquiry.json()))
            token_inquiry = token_response_inquiry.json()['response_data']['access_token']

            # frappe.throw(str(dk_time_stamp))
            if signature_data:
                url = dk_integration_setting.base_url + dk_integration_setting.intrabank_transfer
                headers = {
                    'Content-Type': 'application/json',
                    'X-gravitee-api-key': dk_integration_setting.x_gravitee_api_key,  # Optional
                    'Authorization':f'bearer {token_inquiry}',
                    'DK-Timestamp':timestamp,
                    'DK-Nonce':nonce,
                    'DK-Signature':f'DKSignature {jwt_token}',
                    # 'Host':'internal-gateway.sit.digitalkidu.bt:8082',
                    # 'Accept':'*/*',
                    # 'Accept-Encoding':'gzip,deflate,br',
                    # 'Connection':'keep-alive'
                
                }
                # frappe.throw(str(headers))
                # data = frappe.as_json(dk_signature[1])
                # data = json.dumps(request_body)

                # inquiry_response = requests.post(url, headers=headers, data=data)
                inquiry_response = requests.post(url, headers=headers, data=request_body_str)

                # frappe.throw(frappe.as_json(inquiry_response.json()))
                # if inquiry_response.status_code == 200:
                    # frappe.throw((inquiry_response.json()))
                frappe.log_error(
                    title="Intrabank Transfer Request",
                    message=request_body_str
                )

                inquiry_detail = inquiry_response.json()
                # frappe.throw(str(inquiry_detail))
                return inquiry_detail
                    # frappe.throw(frappe.as_json(inquiry_detail))
                
                print('Success:', inquiry_response.json())
                # return token_response
            

    else:
        frappe.throw('Could not fetch auth token')

@frappe.whitelist()
def check_status_transaction(doc):
    token_response = fetch_authorization_token("keys:read")
    if token_response.status_code == 200:
        # frappe.throw(response.json()['response_data']['access_token'])
        token = token_response.json()['response_data']['access_token']
        # frappe.msgprint("Access Token Fetch Successfully")
        private_key = fetch_private_key(token)
        if private_key.status_code == 200:
            # frappe.throw(private_key.text)
            # dk_signature= generate_dk_signature(private_key.text,account_no)
            (signature_data, request_body) = generate_dk_signature_checkstatus(private_key.text, doc)
            (jwt_token, nonce, timestamp,request_body_str) = signature_data
           
            token_response_inquiry = fetch_authorization_token("transactions:read")
            #frappe.throw(frappe.as_json(token_response_inquiry.json()))
            token_inquiry = token_response_inquiry.json()['response_data']['access_token']

            # frappe.throw(str(dk_time_stamp))
            if signature_data:
                url = dk_integration_setting.base_url + dk_integration_setting.transaction_status
                headers = {
                    'Content-Type': 'application/json',
                    'X-gravitee-api-key': dk_integration_setting.x_gravitee_api_key,  # Optional
                    'Authorization':f'bearer {token_inquiry}',
                    'DK-Timestamp':timestamp,
                    'DK-Nonce':nonce,
                    'DK-Signature':f'DKSignature {jwt_token}',
                    # 'Host':'internal-gateway.sit.digitalkidu.bt:8082',
                    # 'Accept':'*/*',
                    # 'Accept-Encoding':'gzip,deflate,br',
                    # 'Connection':'keep-alive'
                
                }
                # frappe.throw(str(headers))
                # data = frappe.as_json(dk_signature[1])
                # data = json.dumps(request_body)

                # inquiry_response = requests.post(url, headers=headers, data=data)
                inquiry_response = requests.post(url, headers=headers, data=request_body_str)

                # frappe.throw(frappe.as_json(inquiry_response.json()))
                # if inquiry_response.status_code == 200:
            
                inquiry_detail = inquiry_response.json()
                return inquiry_detail
                    # frappe.throw(frappe.as_json(inquiry_detail))
                print('Success:', inquiry_response.json())
                # return token_response
            

    else:
        frappe.throw('Could not fetch auth token')

@frappe.whitelist()
def fetch_gl_turn_over(date):
   

    token_response = fetch_authorization_token("keys:read")
    if token_response.status_code == 200:
        # frappe.throw(response.json()['response_data']['access_token'])
        token = token_response.json()['response_data']['access_token']
        # frappe.msgprint("Access Token Fetch Successfully")
        private_key = fetch_private_key(token)
        if private_key.status_code == 200:
            # frappe.throw(private_key.text)
            # dk_signature= generate_dk_signature(private_key.text,account_no)
            (signature_data, request_body) = generate_glturnover_signature(private_key.text, date)
            (jwt_token, nonce, timestamp,request_body_str) = signature_data
            # frappe.throw(frappe.as_json(dk_signature))
            token_response_inquiry = fetch_authorization_token("gl_turnover:read")
            # frappe.throw(frappe.as_json(token_response_inquiry.json()))
            token_inquiry = token_response_inquiry.json()['response_data']['access_token']

            # frappe.throw(str(dk_time_stamp))
            if signature_data:
                # url = 'https://internal.digitalkidu.bt:8082/api/cbs/connect/v1/gl/turnover'
                url ='https://dk-payment-switch.uat.digitalkidu.bt:3003/api/v1/inquiry/gl/balance'
                headers = {
                    'Content-Type': 'application/json',
                    'X-gravitee-api-key': dk_integration_setting.x_gravitee_api_key,  # Optional
                    'Authorization':f'bearer {token_inquiry}',
                    'DK-Timestamp':timestamp,
                    'DK-Nonce':nonce,
                    'DK-Signature':f'DKSignature {jwt_token}',
                    # 'Host':'internal-gateway.sit.digitalkidu.bt:8082',
                    # 'Accept':'*/*',
                    # 'Accept-Encoding':'gzip,deflate,br',
                    # 'Connection':'keep-alive'
                
                }
                # frappe.throw(str(headers))
                # data = frappe.as_json(dk_signature[1])
                # data = json.dumps(request_body)

                # inquiry_response = requests.post(url, headers=headers, data=data)
                inquiry_response = requests.post(url, headers=headers, data=request_body_str)

                # frappe.throw(frappe.as_json(inquiry_response.json()))
                # if inquiry_response.status_code == 200:
                    # frappe.throw((inquiry_response.json()))
                inquiry_detail = inquiry_response.json()
                # return inquiry_detail
                frappe.throw(frappe.as_json(inquiry_detail))
                print('Success:', inquiry_response.json())
                # return token_response
                return inquiry_response

    else:
        frappe.throw('Could not fetch auth token')

def generate_glturnover_signature(private_key,date):
    

    # Dummy RSA private key (for testing ONLY, do not use in production)
    PRIVATE_KEY_PEM = private_key
    # frappe.throw(frappe.as_json(doc))
    def generate_nonce(length=16):
        """Generate random alphanumeric nonce of given length"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    def generate_signature(request_body: dict):
        # Convert the request body to JSON string
        request_body_str = json.dumps(request_body, sort_keys=True,separators=(",", ":"))
        # frappe.throw(str(request_body_str))
        print(request_body_str)

    
        body_base64 = base64.b64encode(request_body_str.encode()).decode()

        # nonce = "1234567yu8"
        nonce = generate_nonce()
        print("Nonce:", nonce)
        # timestamp = "2025-05-15T11:23:45Z"
        timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=50)
        
        
        dk_signature = jwt.encode({
            "nonce": nonce,
            "timestamp": timestamp,
            "exp": expiration,
            "data": body_base64
        }, PRIVATE_KEY_PEM, algorithm="RS256")
        return dk_signature, nonce, timestamp,request_body_str
   
        
    
        

    sample_request_body = {
        "request_id": frappe.generate_hash(length=19),
        "source_app":"SRC_APP_0101",
        "data_date":date
        }
            

    signature = generate_signature(sample_request_body)

    return signature,sample_request_body

    print("✅ Digital Signature (JWT):\n", signature)
def fetch_currencies(payment_name):
    currency = frappe.db.sql("""
            SELECT currency 
            FROM `tabTransaction Code` 
            WHERE name= %s""",(payment_name), as_dict=True)[0].currency
    return currency
def fetch_exchange_rate(payment_name):
    currencies = fetch_currencies(payment_name)
    token_response = fetch_authorization_token("keys:read")
    if token_response.status_code == 200:
        # frappe.throw(response.json()['response_data']['access_token'])
        token = token_response.json()['response_data']['access_token']
        # frappe.msgprint("Access Token Fetch Successfully")
        private_key = fetch_private_key(token)
        if private_key.status_code == 200:
            # frappe.throw(private_key.text)
            # dk_signature= generate_dk_signature(private_key.text,account_no)
            (signature_data, request_body) = generate_exchange_rate_signature(private_key.text, currencies)
            (jwt_token, nonce, timestamp,request_body_str) = signature_data
            # frappe.throw(frappe.as_json(dk_signature))
            token_response_inquiry = fetch_authorization_token("fx_rate:read")
            # frappe.throw(frappe.as_json(token_response_inquiry.json()))
            token_inquiry = token_response_inquiry.json()['response_data']['access_token']

            # frappe.throw(str(dk_time_stamp))
            if signature_data:
                # url = dk_integration_setting.base_url + dk_integration_setting.exchange_rate
                url=f"{dk_integration_setting.base_url}{dk_integration_setting.exchange_rate}"
                headers = {
                    'Content-Type': 'application/json',
                    'X-gravitee-api-key': dk_integration_setting.x_gravitee_api_key,  # Optional
                    'Authorization':f'bearer {token_inquiry}',
                    'DK-Timestamp':timestamp,
                    'DK-Nonce':nonce,
                    'DK-Signature':f'DKSignature {jwt_token}',
                    # 'Host':'internal-gateway.sit.digitalkidu.bt:8082',
                    # 'Accept':'*/*',
                    # 'Accept-Encoding':'gzip,deflate,br',
                    # 'Connection':'keep-alive'
                
                }
                # frappe.throw(str(headers))
                # data = frappe.as_json(dk_signature[1])
                # data = json.dumps(request_body)

                # inquiry_response = requests.post(url, headers=headers, data=data)
                inquiry_response = requests.post(url, headers=headers, data=request_body_str)

                # frappe.throw(frappe.as_json(inquiry_response.json()))
                # if inquiry_response.status_code == 200:
                    # frappe.throw((inquiry_response.json()))
                inquiry_detail = inquiry_response.json()
                # return inquiry_detail
                # frappe.throw(frappe.as_json(inquiry_detail))
                # print('Success:', inquiry_response.json())
                # return token_response
                return inquiry_response

    else:
        frappe.throw('Could not fetch auth token')


@frappe.whitelist()
def fetch_fx_rate():
   

    token_response = fetch_authorization_token("keys:read")
    if token_response.status_code == 200:
        # frappe.throw(response.json()['response_data']['access_token'])
        token = token_response.json()['response_data']['access_token']
        # frappe.msgprint("Access Token Fetch Successfully")
        private_key = fetch_private_key(token)
        if private_key.status_code == 200:
            # frappe.throw(private_key.text)
            # dk_signature= generate_dk_signature(private_key.text,account_no)
            (signature_data, request_body) = generate_fx_signature(private_key.text)
            (jwt_token, nonce, timestamp,request_body_str) = signature_data
            # frappe.throw(frappe.as_json(dk_signature))
            token_response_inquiry = fetch_authorization_token("fx_rate:read")
            # frappe.throw(frappe.as_json(token_response_inquiry.json()))
            token_inquiry = token_response_inquiry.json()['response_data']['access_token']

            # frappe.throw(str(dk_time_stamp))
            if signature_data:
                url = 'https://internal-gateway.sit.digitalkidu.bt:8082/uat/cbs/connect/v1/exchange/rate'
                headers = {
                    'Content-Type': 'application/json',
                    'X-gravitee-api-key': dk_integration_setting.x_gravitee_api_key,  # Optional
                    'Authorization':f'bearer {token_inquiry}',
                    'DK-Timestamp':timestamp,
                    'DK-Nonce':nonce,
                    'DK-Signature':f'DKSignature {jwt_token}',
                    # 'Host':'internal-gateway.sit.digitalkidu.bt:8082',
                    # 'Accept':'*/*',
                    # 'Accept-Encoding':'gzip,deflate,br',
                    # 'Connection':'keep-alive'
                
                }
                # frappe.throw(str(headers))
                # data = frappe.as_json(dk_signature[1])
                # data = json.dumps(request_body)

                # inquiry_response = requests.post(url, headers=headers, data=data)
                inquiry_response = requests.post(url, headers=headers, data=request_body_str)

                # frappe.throw(frappe.as_json(inquiry_response.json()))
                # if inquiry_response.status_code == 200:
                    # frappe.throw((inquiry_response.json()))
                inquiry_detail = inquiry_response.json()
                # return inquiry_detail
                # frappe.throw(frappe.as_json(inquiry_detail))
                # print('Success:', inquiry_response.json())
                # return token_response
                return inquiry_response

    else:
        frappe.throw('Could not fetch auth token')


def generate_exchange_rate_signature(private_key,currencies):
    

    # Dummy RSA private key (for testing ONLY, do not use in production)
    PRIVATE_KEY_PEM = private_key
    # frappe.throw(frappe.as_json(doc))
    def generate_nonce(length=16):
        """Generate random alphanumeric nonce of given length"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    def generate_signature(request_body: dict):
        # Convert the request body to JSON string
        request_body_str = json.dumps(request_body, sort_keys=True,separators=(",", ":"))
        print(request_body_str)

    
        body_base64 = base64.b64encode(request_body_str.encode()).decode()

        # nonce = "1234567yu8"
        nonce = generate_nonce()
        print("Nonce:", nonce)
        # timestamp = "2025-05-15T11:23:45Z"
        timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=50)
        
        
        dk_signature = jwt.encode({
            "nonce": nonce,
            "timestamp": timestamp,
            "exp": expiration,
            "data": body_base64
        }, PRIVATE_KEY_PEM, algorithm="RS256")
        return dk_signature, nonce, timestamp,request_body_str
   
        
    sample_request_body =  {
                "request_id":frappe.generate_hash(length=19),
                "source_app":"SRC_APP_0201",
                "currencies":currencies
                }
            

    signature = generate_signature(sample_request_body)

    return signature,sample_request_body

    print("✅ Digital Signature (JWT):\n", signature)

def generate_fx_signature(private_key):
    

    # Dummy RSA private key (for testing ONLY, do not use in production)
    PRIVATE_KEY_PEM = private_key
    # frappe.throw(frappe.as_json(doc))
    def generate_nonce(length=16):
        """Generate random alphanumeric nonce of given length"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    def generate_signature(request_body: dict):
        # Convert the request body to JSON string
        request_body_str = json.dumps(request_body, sort_keys=True,separators=(",", ":"))
        print(request_body_str)

    
        body_base64 = base64.b64encode(request_body_str.encode()).decode()

        # nonce = "1234567yu8"
        nonce = generate_nonce()
        print("Nonce:", nonce)
        # timestamp = "2025-05-15T11:23:45Z"
        timestamp = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=50)
        
        
        dk_signature = jwt.encode({
            "nonce": nonce,
            "timestamp": timestamp,
            "exp": expiration,
            "data": body_base64
        }, PRIVATE_KEY_PEM, algorithm="RS256")
        return dk_signature, nonce, timestamp,request_body_str
   
        
    
        

    sample_request_body =  {
                "request_id":frappe.generate_hash(length=19),
                "source_app":"SRC_APP_0201",
                "currencies":["all"]
                }
            

    signature = generate_signature(sample_request_body)

    return signature,sample_request_body

    print("✅ Digital Signature (JWT):\n", signature)


#ORO BANK GL INTEGRATION WITH ERP BEGINS HERE

def fetch_gl_oro_bank(date,currency):
    url = dk_integration_setting.oro_endpoint
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d")  # input format: "2024-02-01"

    # Start of the day
    from_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    # End of the day
    end_date = date.replace(hour=23, minute=59, second=59, microsecond=0)

    # Format as ISO8601 with Z
    from_date_str = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "from": from_date_str,
        "to": end_date_str,
        "currency": currency
    }

    

    # Authorization token
    headers = {
        "Authorization": "Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzMTE5NSIsImV4cCI6MTc5MDUzODc0NSwiaWF0IjoxNzU0NTM4NzQ1LCJqdGkiOiIxNDgzNDcifQ.oY1Xxxzh5tJyTEZ0bvXoXjsTvjgqap-4frH5ep3hpACtQsrUOdnzxFSlJJ8EGggv6y2kYxHrNTvENmkGM8GU_w",
        "Content-Type": "application/json"
    }

    # Send GET request
    response = requests.get(url, params=params, headers=headers)

    # Check response
    if response.status_code == 200:
        data = response.json()  # parse JSON response
        return data
        print(data)
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(response.text)
        frappe.throw("Could not fetch the ORO Bank GL")