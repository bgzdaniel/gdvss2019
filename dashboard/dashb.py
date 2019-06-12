import plotly
import plotly.graph_objs as go
import pandas
import fiona
import numpy
import scipy.spatial.distance
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

mapbox_access_token = "pk.eyJ1IjoiYmd6LWRhbmllbCIsImEiOiJjandxZTFibjkxOWEyNGJsZWRiZ253OXBoIn0.vpfoIUoYkhjpn42Eb13YCg"

scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]

mannheim = (8.2693, 49.3830, 8.6850, 49.5753)
with fiona.open("/home/daniel/Daniel/GDV_project"
                "/pois+road_data/gis_osm_pois_free_1.shp") as src:
    features = list(src.filter(bbox=mannheim))
    pointsofinterest = pandas.DataFrame(
        {"id": [f["id"] for f in features],
         "longitude": [f["geometry"]["coordinates"][0] for f in features],
         "latitude": [f["geometry"]["coordinates"][1] for f in features],
         "fclass": [f["properties"]["fclass"] for f in features],
         "name": [f["properties"]["name"] for f in features]
        })
pointsofinterest["text"] = pointsofinterest["fclass"]
pointsofinterest = pointsofinterest.set_index(["fclass"])
education = pointsofinterest.loc[pointsofinterest.index.isin(["university", "school", "kindergarten", "college"])]
health = pointsofinterest.loc[pointsofinterest.index.isin(["pharmacy", "hospital", "doctors", "dentist", "veterinary"])]
leisure = pointsofinterest.loc[pointsofinterest.index.isin(["theatre", "nightclub", "cinema", "park", "playground", "dog_park", "sports_centre", "pitch", "swimming_pool", "tennis_court", "golf_course", "stadium"])]
public = pointsofinterest.loc[pointsofinterest.index.isin(["police", "fire_station", "post_box", "post_office", "library", "town_hall", "courthouse", "community_centre", "nursing_home", "arts_centre", "market_place"])]
catering = pointsofinterest.loc[pointsofinterest.index.isin(["restaurant", "fast_food", "cafe", "pub", "bar", "food_court", "biergarten"])]
shopping = pointsofinterest.loc[pointsofinterest.index.isin(["supermarket", "bakery", "kiosk", "mall", "department_store", "convenience", "clothes", "florist", "chemist", "bookshop", "butcher", "shoe_shop", "beverages", "optician", "jeweller", "gift_shop", "sports_shop", "stationery", "outdoor_shop", "toy_shop", "newsagent", "greengrocer", "beauty_shop", "video_shop", "car_dealership", "bicycle_shop", "doityourself", "furniture_shop", "computer_shop", "garden_centre", "hairdresser", "car_repair", "car_rental", "car_wash", "car_sharing", "bicycle_rental", "travel_agent", "laundry", "vending_machine", "vending_cigarette", "vending_parking"])]
money = pointsofinterest.loc[pointsofinterest.index.isin(["bank", "atm"])]
pointsofinterest.reset_index

housing_coordinates = pandas.read_csv(
    "/home/daniel/Daniel/GDV_project/wh_latlng(2).csv",
    sep=";")
housing_properties = pandas.read_csv(
    "/home/daniel/Daniel/GDV_project/wohnungsliste_19.05.2019.csv",
    sep=";")

housing = housing_properties.merge(housing_coordinates, 
    on="obj_scoutId", how="inner")
housing["lat"] = housing["lat"].apply(
    lambda x: float(x.replace(",", ".")))
housing["lng"] = housing["lng"].apply(
    lambda x: float(x.replace(",", ".")))

radial = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
pointsofinterest[["latitude", "longitude"]]) 

subset = pointsofinterest
close_by = numpy.sum(radial[:, :] < 0.01, axis = 1)
housing["score"] = close_by

housing["text"] = "Adresse: " + housing["fulladdress"]\
+ "; Miete: " + housing["obj_baseRent"].astype(str)\
+ "; Wohnfläche: " + housing["obj_livingSpace"].astype(int).astype(str) + "m²"\
+ "; Zimmer: " + housing["obj_noRooms"].astype(int).astype(str)\
+ "; Score: " + housing["score"].astype(str)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
	html.Div([
		dcc.Graph(
			id = "housing_map",
			figure = {
				"data":[
					go.Scattermapbox(
						lon = housing["lng"],
						lat = housing["lat"],
						text = housing["text"],
						customdata = housing["obj_scoutId"],
						mode = "markers",
						marker = go.scattermapbox.Marker(
        					size = 20,
            				colorscale = scl,
            				cmin = 0,
            				cmax = housing["score"].max(),
            				color = housing["score"],
            				colorbar=dict(
            				    title="Score"
            				),
            			opacity=1,
            			reversescale = True
        		))],
        		"layout": go.Layout(
						title = "Wohnraum in Mannheim",
						autosize=True,
    					hovermode='closest',
    					mapbox=go.layout.Mapbox(
        				accesstoken=mapbox_access_token,
        				bearing=0,
        				center=go.layout.mapbox.Center(
            				lat=49.48713,
            				lon=8.46624
        				),
        				pitch=0,
        				zoom=12
    					))
			})
		]),
	html.Div([
		dcc.Graph(
			id = "housing_distribution",
			figure = {
				"data": [
				go.Scatter(
					y = [500],
					x0 = "Miete",
					mode = "markers",
					marker = go.scatter.Marker(
						opacity = 1,
						size = 15)
					), {
					"type": "violin",
					"y": housing["obj_baseRent"],
					"box":{
						"visible":True
					},
					"line":{
						"color":"black"
					},
					"meanline":{
						"visible":True
					},
					"fillcolor":"#8dd3c7",
					"opacity":0.6,
					"x0":"Miete"
				}],
				"layout": {
					"title":"",
					"yaxis": {
						"zeroline": False,
					}
				}
			})])
	])

@app.callback(
	Output("housing_distribution", "figure"),
	[Input("housing_map", "hoverData")])
def update_violin(hoverData):
	housing_id = hoverData["points"][0]["customdata"]
	newRent = housing.loc[housing["obj_scoutId"] == housing_id]
	newRent = newRent.iloc[0]["obj_baseRent"]
	return {
		"data": [
				go.Scatter(
					y = [newRent],
					x0 = "Miete",
					mode = "markers",
					marker = go.scatter.Marker(
						opacity = 1,
						size = 15)
					), {
					"type": "violin",
					"y": housing["obj_baseRent"],
					"box":{
						"visible":True
					},
					"line":{
						"color":"black"
					},
					"meanline":{
						"visible":True
					},
					"fillcolor":"#8dd3c7",
					"opacity":0.6,
					"x0":"Miete"
				}],
				"layout": {
					"title":"",
					"yaxis": {
						"zeroline": False,
					}
				}
	}

@app.callback(
	Output("housing_map", "figure"),
	[Input("housing_distribution", "hoverData")])
def update_map(hoverData):
	print(hoverData)
	#location = hoverData["points"][0]["y"]
	#print(location)

if __name__ == '__main__':
    app.run_server(debug=True)
