def daily_report_countries(country_code='sa'):
    url = "https://covid-19-data.p.rapidapi.com/country/code"

    querystring = {"format":"json","code":country_code}

    headers = {
        'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
        'x-rapidapi-key': "46345e418cmsh542642b3ab38d2fp12ab20jsne42343ea4346"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()
