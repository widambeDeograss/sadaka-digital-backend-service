from BeemAfrica import Authorize, SMS

def pushMessage(message, phone):
    Authorize('ea6238aa30eb8eed',
                'NTA1MzEyOTIwMWE4ZjIyZmE1YmJhOGJlNDM1ZDdkNmE2NDY2ZjQ3M2Y0MjdiM2FjYjZiMjg1MjIyNDkyMjdkYQ==')
    print("=============================================================================")
    request = SMS.send_sms(
        message,
        phone,
        sender_id='BMC MAKABE'
    )

    print(request)
    return request