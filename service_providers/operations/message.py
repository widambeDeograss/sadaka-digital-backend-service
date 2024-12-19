from BeemAfrica import Authorize, SMS

def pushMessage(message, phone):
    Authorize('06f534e2fe661fad',
                'NjI1OTkzZDFhYzBiZGUyOGMzYzBkZDgzNGEwYjgzYjdmZDRmMzU1N2QxYjczZDI0YjdlYzJmNDU3MzhmMjdhNA==')
    print("=============================================================================")
    request = SMS.send_sms(
        message,
        phone,
        sender_id='JamiiConect'
    )
    print(request)
    return request