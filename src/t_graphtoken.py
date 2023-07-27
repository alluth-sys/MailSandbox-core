import msal

def getToken():

    config = {
        "client_id": "ff9050b9-ddad-4b30-b158-26b93bb7a296",
        "authority": "https://login.microsoftonline.com/common",
        "redirect_uri": "http://localhost",
        "scope": ["https://graph.microsoft.com/.default"],
    }

    app = msal.PublicClientApplication(config['client_id'], authority=config['authority'])

    result = None
    accounts = app.get_accounts()

    if accounts:
        chosen_account = accounts[0]
        result = app.acquire_token_silent(config['scope'], account=chosen_account)

    if not result:
        result = app.acquire_token_interactive(config['scope'])

    if 'access_token' in result:
        print(result['access_token'])
    else:
        print(result.get('error'))
        print(result.get('error_description'))
        print(result.get('correlation_id'))
    return result['access_token']