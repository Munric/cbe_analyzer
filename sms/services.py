import africastalking

username = "sandbox"
api_key = "YOUR_API_KEY"

africastalking.initialize(username, api_key)

sms = africastalking.SMS

def send_sms(phone, message):
    sms.send(message, [phone])