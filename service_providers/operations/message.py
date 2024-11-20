from BeemAfrica import Authorize, SMS

def pushMessage(message, phone):
    Authorize('771d0353424c0189',
                'YWUwMGI2NGVlZWQyY2JlMmEwMzk0N2YwZWNjYTQzMzNlN2ZhZTJhY2VhNWU2NDNhY2E5OTI1MjEyNjNjMDgyYg==')
    print("=============================================================================")
    request = SMS.send_sms(
        message,
        phone,
        sender_id='JamiiConect'
    )
    print(request)
    return request