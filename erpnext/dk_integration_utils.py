import frappe
import requests
import json
import random
import json
import base64
import datetime
import jwt
import string
# @frappe.whitelist()
def dk_payment_test():
    frappe.throw('hello dk payment user')


@frappe.whitelist()
def fetch_authorization_token(scope):
    url = 'https://internal-gateway.sit.digitalkidu.bt:8082/uat/v1/cbs/connect/auth/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-gravitee-api-key': '98cf3639-df33-4587-9d36-dae9d2bb974c',  # Optional
       
    }
    data = {
        'username': 'admin',
        'password': 'admin123',
        'client_id': '0fefeac4-e989-46ce-8d02-92db4ed8e62e',
        'client_secret': 'GO_z/3>5!5\?75Cf<f1<r!x9h&Wf.SL$',
        'grant_type':'password',
        'scope':scope
    }
    frappe.log_error(str(scope))
    token_response = requests.post(url, headers=headers, data=data)
    # if response.status_code == 200:
    #     print('Success:', response.json())
    return token_response
    # else:
    #     print('Error:', response.status_code, response.text)

    #     return response
def fetch_private_key(token):
    url = 'https://internal-gateway.sit.digitalkidu.bt:8082/uat/v1/cbs/connect/sign/key'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-gravitee-api-key': '98cf3639-df33-4587-9d36-dae9d2bb974c',  # Optional
        'Authorization':f'bearer {token}'
       
    }
    # data = {
    #     'username': 'admin',
    #     'password': 'admin123',
    #     'client_id': '0fefeac4-e989-46ce-8d02-92db4ed8e62e',
    #     'client_secret': 'GO_z/3>5!5\?75Cf<f1<r!x9h&Wf.SL$',
    #     'grant_type':'password',
    #     'scope':scope
    # }
    key_response = requests.get(url, headers=headers)
    if key_response.status_code == 200:
        print('Success:', key_response.text)
        return key_response
    else:
        frappe.throw("Could not fetch key")
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
       

        # Testaccount_no":"100100365856",
    sample_request_body = {
        "account_no":account_no,
        "request_id":frappe.generate_hash(length=17),
        # "request_id":'777i777778y8y',
        "source_app":"erp",
        "product_type":"LCY_ACC"
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
    description = i.description
        
   

    sample_request_body = {
            "request_meta": {
            "request_id": frappe.generate_hash(length=17),
            "inquiry_id": doc.inquiry_id,
            "source_app": "ERP"
            },
            "request_payload": {
            "payer_acc": doc.bank_account_no,
            "payer_name": doc.payer_name,
            "beneficiary_acc": beneficiary_acc,
            "beneficiary_name": beneficiary_name,
            "currency_code": currency_code,
            "txn_amt": amount,
            "txn_description": description
            }
            }
    

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
    transaction_id = data["transaction_id"]
    transaction_inquiry_id = data["inquiry_id"]
    transaction_status_request_id = data["transaction_status_request_id"]
    # beneficiary_acc = i.beneficiary_account_no
    # beneficiary_name = i.beneficiary_name
    # currency_code = i.currency_code
    # amount = i.amount
    # description = i.description
        
   
#frappe.generate_hash(length=17),
    sample_request_body = {
        "request_id":frappe.generate_hash(length=17),
        "source_app":"ERP",
        "txn_id":transaction_id,
        "txn_inquiry_id":transaction_inquiry_id,
        "txn_status_req_id":transaction_status_request_id
        }

    # frappe.throw(frappe.as_json(sample_request_body))
    

    signature = generate_signature(sample_request_body)

    return signature,sample_request_body

    print("✅ Digital Signature (JWT):\n", signature)


@frappe.whitelist()
def account_inquiry(account_no):
    # frappe.throw(account_no)
    token_response = fetch_authorization_token("keys:read")
    if token_response.status_code == 200:
        # frappe.throw(response.json()['response_data']['access_token'])
        token = token_response.json()['response_data']['access_token']
        # frappe.msgprint("Access Token Fetch Successfully")
        private_key = fetch_private_key(token)
        if private_key.status_code == 200:
            # frappe.throw(private_key.text)
            # dk_signature= generate_dk_signature(private_key.text,account_no)
            (signature_data, request_body) = generate_dk_signature(private_key.text, account_no)
            (jwt_token, nonce, timestamp,request_body_str) = signature_data
            # frappe.throw(frappe.as_json(dk_signature))
            token_response_inquiry = fetch_authorization_token("accounts:read")
            # frappe.throw(frappe.as_json(token_response_inquiry.json()))
            token_inquiry = token_response_inquiry.json()['response_data']['access_token']

            # frappe.throw(str(dk_time_stamp))
            if signature_data:
                url = 'https://internal-gateway.sit.digitalkidu.bt:8082/uat/v1/cbs/connect/acc/inquiry'
                headers = {
                    'Content-Type': 'application/json',
                    'X-gravitee-api-key': '98cf3639-df33-4587-9d36-dae9d2bb974c',  # Optional
                    'Authorization':f'bearer {token_inquiry}',
                    'DK-Timestamp':timestamp,
                    'DK-Nonce':nonce,
                    'DK-Signature':f'DKSignature {jwt_token}'
                
                }
                # frappe.throw(str(headers))
                # data = frappe.as_json(dk_signature[1])
                data = json.dumps(request_body)

                # inquiry_response = requests.post(url, headers=headers, data=data)
                inquiry_response = requests.post(url, headers=headers, data=request_body_str)

                # frappe.throw(frappe.as_json(inquiry_response.json()))
                if inquiry_response.status_code == 200:
                    # frappe.throw((inquiry_response.json()))
                    inquiry_detail = inquiry_response.json()
                    return inquiry_detail
                    # frappe.throw(frappe.as_json(inquiry_detail))
                    print('Success:', inquiry_response.json())
                # return token_response
            

    else:
        frappe.throw('Could not fetch auth token')

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
                url = 'https://internal-gateway.sit.digitalkidu.bt:8082/uat/v1/cbs/connect/txn/ibt'
                headers = {
                    'Content-Type': 'application/json',
                    'X-gravitee-api-key': '98cf3639-df33-4587-9d36-dae9d2bb974c',  # Optional
                    'Authorization':f'bearer {token_inquiry}',
                    'DK-Timestamp':timestamp,
                    'DK-Nonce':nonce,
                    'DK-Signature':f'DKSignature {jwt_token}',
                    'Host':'internal-gateway.sit.digitalkidu.bt:8082',
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip,deflate,br',
                    'Connection':'keep-alive'
                
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
                url = 'https://internal-gateway.sit.digitalkidu.bt:8082/uat/v1/cbs/connect/txn/status'
                headers = {
                    'Content-Type': 'application/json',
                    'X-gravitee-api-key': '98cf3639-df33-4587-9d36-dae9d2bb974c',  # Optional
                    'Authorization':f'bearer {token_inquiry}',
                    'DK-Timestamp':timestamp,
                    'DK-Nonce':nonce,
                    'DK-Signature':f'DKSignature {jwt_token}',
                    'Host':'internal-gateway.sit.digitalkidu.bt:8082',
                    'Accept':'*/*',
                    'Accept-Encoding':'gzip,deflate,br',
                    'Connection':'keep-alive'
                
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
                return inquiry_detail
                    # frappe.throw(frappe.as_json(inquiry_detail))
                print('Success:', inquiry_response.json())
                # return token_response
            

    else:
        frappe.throw('Could not fetch auth token')

	