import dash
import dash_core_components as dcc
import dash_html_components as html
from htexpr import compile
import unicodedata
from flask import Flask
import requests
import pandas as pd
import time
import chart_studio.plotly as py
import plotly.express as px
import dash_bootstrap_components as dbc
from toolz import curry
from htexpr.mappings import dbc_and_default
import dash_table

compile = curry(compile)(map_tag=dbc_and_default)


server = Flask(__name__)

def daily_report_countries(country_code='sa'):
    url = "https://covid-19-data.p.rapidapi.com/country/code"

    querystring = {"format":"json","code":country_code}

    headers = {
        'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
        'x-rapidapi-key': "46345e418cmsh542642b3ab38d2fp12ab20jsne42343ea4346"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()

def get_daily_report_countries(df_final):
    for index,row in df_countries_info[0:5].iterrows():
        country_code = row["alpha2code"]
        longitude = row["longitude"]
        latitude = row["latitude"]
        if country_code:
            df_daily_cases = daily_report_countries(country_code)
            #print(df_daily_cases)
            #input()
            if "country" in df_daily_cases[0].keys():
                country = df_daily_cases[0]["country"]
            else:
                country = "none"
            print(country)
            if "confirmed" in df_daily_cases[0].keys():
                confirmed = df_daily_cases[0]["confirmed"]
            else:
                confirmed = 0

            if "recovered" in df_daily_cases[0].keys():
                recovered = df_daily_cases[0]["recovered"]
            else:
                recovered = 0

            if "lastUpdate" in df_daily_cases[0].keys():
                update = df_daily_cases[0]["lastUpdate"]
            else:
                update = 0

            if "deaths" in df_daily_cases[0].keys():
                deaths = df_daily_cases[0]["deaths"]
            else:
                deaths = 0

            if "critical" in df_daily_cases[0].keys():
                critical = df_daily_cases[0]["critical"]
            else:
                critical = 0


            info = {'Country': country, 'Country Code': country_code,
                    'Confirmed Cases': confirmed, 'Critical Cases': critical,
                    'Recovered Cases': recovered, 'Deaths': deaths,
                    'Last Updated': update, 'Longitude': longitude,
                    'Latitude': latitude
                   }
            df_final=df_final.append(info, ignore_index = True)

        time.sleep(2)
    df_final["Confirmed Cases"]= df_final["Confirmed Cases"].astype(float)
    df_final["Recovered Cases"]= df_final["Recovered Cases"].astype(float)
    df_final["Critical Cases"]= df_final["Critical Cases"].astype(float)
    df_final["Deaths"]= df_final["Deaths"].astype(float)
    return df_final

def get_total_cases():
    url = "https://covid-19-data.p.rapidapi.com/totals"
    querystring = {"format":"json"}
    headers = {
        'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
        'x-rapidapi-key': "46345e418cmsh542642b3ab38d2fp12ab20jsne42343ea4346"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)

    df_total_stats = pd.DataFrame(response.json())
    return df_total_stats

def countries_info():
    # Make API request to get information about countries
    url = "https://covid-19-data.p.rapidapi.com/help/countries"

    querystring = {"format":"json"}

    headers = {
        'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
        'x-rapidapi-key': "46345e418cmsh542642b3ab38d2fp12ab20jsne42343ea4346"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()

def get_news():

    url = "https://covid-19-news.p.rapidapi.com/v1/covid"
    querystring = {"lang":"en","media":"True","q":"covid"}
    headers = {
        'x-rapidapi-host': "covid-19-news.p.rapidapi.com",
        'x-rapidapi-key': "46345e418cmsh542642b3ab38d2fp12ab20jsne42343ea4346"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    news = response.json()['articles']
    df_news = pd.DataFrame(news, columns= ['title','summary', 'link', 'language', 'clean_url'])
    #df_news = df_news[df_news['clean_url'] == 'cdc.gov']

    return df_news


countries_list =countries_info()
df_countries_info = pd.DataFrame(countries_list)
time.sleep(2)
columns = [ 'Country', 'Country Code',
            'Confirmed Cases', 'Critical Cases',
            'Recovered Cases', 'Deaths',
            'Last Updated', 'Longitude',
            'Latitude',
           ]
df_final = pd.DataFrame(columns = columns)
df_final=get_daily_report_countries(df_final)
df_total_stats = get_total_cases()
df_news = get_news()
print(df_news.iloc[0]['summary'],df_news.iloc[0]['link'])

mapbox_access_token = 'pk.eyJ1IjoiaGFzdHlsZSIsImEiOiJja2QwM2dtdHgwcHVhMzBwZ3F0azlpMDZtIn0.mCN0EYyBKElCkJPOO1xA7A'

color_scale = [
        "#fadc8f",
        "#f9d67a",
        "#f8d066",
        "#f8c952",
        "#f7c33d",
        "#f6bd29",
        "#f5b614",
        "#F4B000",
        "#eaa900",
        "#e0a200",
        "#dc9e00",
        ]


px.set_mapbox_access_token(mapbox_access_token)
df_final['Size'] = df_final['Confirmed Cases']**0.77

fig = px.scatter_mapbox(df_final,
                        lat="Latitude", lon="Longitude",
                        color="Confirmed Cases", size="Size",
                        hover_name="Country",
                        hover_data=["Confirmed Cases", "Recovered Cases","Critical Cases","Deaths"],
                        title= 'World-wide Covid-19 status',
                        color_continuous_scale=color_scale,
                        zoom=15)
fig.layout.update(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        # This takes away the colorbar on the right hand side of the plot
        coloraxis_showscale=False,
        mapbox_style='mapbox://styles/hastyle/ckd04vx3w0orf1irxdgxzotia',
        mapbox=dict(center=dict(lat=40.721319,lon=-73.987130), zoom=1),
        )
fig.data[0].update(hovertemplate= '<b>%{hovertext}</b><br>Confirmed Cases= %{marker.color}<br>Recovered Cases= %{customdata[1]}<br>Critical Cases= %{customdata[2]}<br>Deaths= %{customdata[3]}')

#app.layout = html.Div([
#    dcc.Graph(
#        id='confirmed-map',
#        figure=fig
#    )
#])



app = dash.Dash(__name__, external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css',
                                                '//use.fontawesome.com/releases/v5.0.7/css/all.css',
                                                '/assets/style.css'])

nav = compile("""
    <div class="main-nav col-md">
      <div class="nav-container">
      <div class="icon">
      <img src="./assets/icon.png" alt=""></img></div>
      <div class="icon">
      <img src="./assets/mail.png" alt=""></img></div>
      <div class="icon">
      <img src="./assets/stats.png" alt=""></img></div>
      </div>
    </div>
""")

content = compile("""
        <div class="main-map col-md">
          <div class="worldwide-stats">
            <div class="worldwide-title">
            <h1>الإحصاءات الإجمالية في العالم</h1>
            </div>
            <div class="worldwide-icon-container">
              <div class="worldwide-icon">
                <div class="left-icon-block">
                  <img src="./assets/spread.png" alt=""></img>
                </div>
                <div class="right-text-block">
                  <p>المصابون</p>
                  <p>{f"{df_total_stats['confirmed'][0]:,}"}</p>
                </div>
              </div>
              <div class="worldwide-icon">
                <div class="left-icon-block">
                  <img src="./assets/halloween.png" alt=""></img>
                </div>
                <div class="right-text-block">
                  <p>الوفيات</p>
                  <p>{f"{df_total_stats['deaths'][0]:,}"}</p>
                </div>
              </div>
              <div class="worldwide-icon">
                <div class="left-icon-block">
                  <img src="./assets/person.png" alt=""></img>
                </div>
                <div class="right-text-block">
                  <p>الحالات الخطرة</p>
                  <p>{f"{df_total_stats['critical'][0]:,}"}</p>
                </div>
              </div>
              <div class="worldwide-icon">
                <div class="left-icon-block">
                  <img src="./assets/spread.png" alt=""></img>
                </div>
                <div class="right-text-block">
                  <p>المتعافون</p>
                  <p>{f"{df_total_stats['recovered'][0]:,}"}</p>
                </div>
              </div>

            </div>
          </div>
          <div class="map">
          <Graph id="map" figure={fig} config={'displayModeBar': False} /> </div>
          <div class="footer">
            <span class="footer">
                Made with <i class="fa fa-heart pulse"></i> in <a target="_blank">KSA</a>
            </span>
            </div>
        </div>
""")

logo = compile("""
          <div class="logo">
          <img src="./assets/logo2.png" alt=""/></div>

""")



df_stat = df_final.copy()
df_stat = df_stat.drop(['Longitude', 'Size', 'Latitude', 'Country Code', 'Critical Cases', 'Last Updated', 'Recovered Cases'], axis=1)
stats = html.Div([html.Div([html.H1("احصائيات الدول")], className="worldwide-title"),
        html.Div(dash_table.DataTable(
                                    id='table',
                                    columns=[{"name": i, "id": i} for i in df_stat.columns],
                                    data=df_stat.to_dict('records'),
                                    editable=False,
                                    sort_action="native",
                                    sort_mode="multi",
                                    column_selectable="single",
                                    style_as_list_view=True,
                                    fixed_rows={"headers": True},
                                    fill_width=True,
                                    #style_table={
                                    #    "width": "100%",
                                    #    "height": "100vh",
                                    #},
                                    style_header={
                                        "backgroundColor": "#262A2F",
                                        "border": "#2b2b2b",
                                        "fontWeight": "bold",
                                        "font": "Lato, sans-serif",
                                        "height": "2vw",
                                    },
                                    style_cell={
                                        'textAlign': 'center',
                                        "font-size": "14px",
                                        "font-family": "Lato, sans-serif",
                                        "border-bottom": "0.01rem solid #313841",
                                        "backgroundColor": "#262A2F",
                                        "color": "#FEFEFE",
                                        "height": "2.75vw",
                                        'whiteSpace': 'normal',
                                        'height': 'auto',

                                    },
                                    style_cell_conditional=[
                                        {
                                            "if": {"column_id": "Country",},
                                            "minWidth": "3vw",
                                            "width": "3vw",
                                            "maxWidth": "3vw",
                                            "textAlign": "left"
                                        },
                                        {
                                            "if": {"column_id": "Confirmed Cases",},
                                            "color": "#F4B000",
                                            "minWidth": "3vw",
                                            "width": "3vw",
                                            "maxWidth": "3vw",
                                        },
                                        {
                                            "if": {"column_id": "Deaths",},
                                            "color": "#E55465",
                                            "minWidth": "3vw",
                                            "width": "3vw",
                                            "maxWidth": "3vw",
                                        },
                                    ],
                                    ), className="stats_table")
])
news =  html.Div([html.Div([html.H1("اخر الأخبار")], className="worldwide-title"),
        dbc.ListGroup([
                        dbc.ListGroupItem([
                            html.Div([
                                html.H6(
                                        f"{df_news.iloc[i]['title']}",
                                        className="news-txt-headline",
                                ),
                                html.P(
                                        f"source: {df_news.iloc[i]['clean_url']}.",
                                        className = "news-txt-source",
                                ),
                            ], className = "news-item-container")
                        ],  className="news-item", href=df_news.iloc[i]["link"])
                        for i in range(len(df_news))
        ], className = "news-container", flush=True, )
])

app.layout = html.Div(
                        html.Div([
                        nav.run(), content.run(),
                        html.Div([logo.run(),stats, news],className="main-stats col-md")
                        ], className='row')
                        , className="container-fluid")



# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)
