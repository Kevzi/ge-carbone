import urllib.request, urllib.error

try:
    urllib.request.urlopen('https://ledgercarbon.org/api/v1/schema/')
except urllib.error.HTTPError as e:
    try:
        body = e.read()
    except Exception as ie:
        body = ie.partial
    with open('error.html', 'wb') as f:
        f.write(body)
except Exception as e:
    print(f'Exception: {e}')
