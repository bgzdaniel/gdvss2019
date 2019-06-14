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

DANIEL_POIS = "/home/daniel/Daniel/GDV_project/pois+road_data/gis_osm_pois_free_1.shp"
DANIEL_PROPERTIES = "/home/daniel/Daniel/GDV_project/wohnungsliste_19.05.2019.csv"
DANIEL_COORDINATES = "/home/daniel/Daniel/GDV_project/wh_latlng(2).csv"

MARK_POIS = "C:/Users/MarkBeckmann/PycharmProjects/gdvss2019/dashboard/pois+road_data/gis_osm_pois_free_1.shp"
MARK_PROPERTIES = "C:/Users/MarkBeckmann/PycharmProjects/gdvss2019/dashboard/wohnungsliste_19.05.2019.csv"
MARK_COODRINATES = "C:/Users/MarkBeckmann/PycharmProjects/gdvss2019/dashboard/wh_latlng(2).csv"

scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]

mannheim = (8.2693, 49.3830, 8.6850, 49.5753)
with fiona.open("C:/Users/MarkBeckmann/PycharmProjects/gdvss2019/dashboard/pois+road_data/gis_osm_pois_free_1.shp") as src:
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
    "C:/Users/MarkBeckmann/PycharmProjects/gdvss2019/dashboard/wh_latlng(2).csv",
    sep=";")
housing_properties = pandas.read_csv(
    "C:/Users/MarkBeckmann/PycharmProjects/gdvss2019/dashboard/wohnungsliste_19.05.2019.csv",
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
close_by = numpy.sum(radial[:, :] < 0.0005, axis = 1)
housing["score"] = close_by

# Score for Education
radial_education = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
education[["latitude", "longitude"]])

subsetEducation = education
closeBy = numpy.sum(radial_education[:, :] < 0.0005, axis = 1)
housing["educationScore"] = closeBy

#Score for health
radial_health = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
health[["latitude", "longitude"]])

subsetHealth = health
closeBy = numpy.sum(radial_health[:, :] < 0.0005, axis = 1)
housing["healthScore"] = closeBy

#Score for leisure
radial_leisure = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
leisure[["latitude", "longitude"]])

subsetleisure = leisure
closeBy = numpy.sum(radial_leisure[:, :] < 0.0005, axis = 1)
housing["leisureScore"] = closeBy

#Score for public
radial_public = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
public[["latitude", "longitude"]])

subsetPublic = public
closeBy = numpy.sum(radial_public[:, :] < 0.0005, axis = 1)
housing["publicScore"] = closeBy

#Score for catering
radial_catering = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
catering[["latitude", "longitude"]])

subsetCatering = catering
closeBy = numpy.sum(radial_catering[:, :] < 0.0005, axis = 1)
housing["cateringScore"] = closeBy

#Score for shopping
radial_shopping = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
shopping[["latitude", "longitude"]])

subsetShopping = shopping
closeBy = numpy.sum(radial_shopping[:, :] < 0.0005, axis = 1)
housing["shoppingScore"] = closeBy

#Score for money
radial_money = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
money[["latitude", "longitude"]])

subsetMoney = money
closeBy = numpy.sum(radial_money[:, :] < 0.0005, axis = 1)
housing["moneyScore"] = closeBy



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
			}),
		dcc.Graph(
			id = "detail_view_of_pois",
			figure = {
				"data": [
					go.Bar(
						x = ["Bildung","Gesundheit", "Freizeit", "Shopping", "Geld", "Öffentliche Gebäude", "Gastwirtschaft"],
						y = [3,4,5,6,7,8.9])
				],
				"layout" : go.Layout(
					title = "Points of Interests",
					autosize=True
				)
			}
		)
		], style={'columnCount': 2}),
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

@app.callback(
	Output("detail_view_of_pois", "figure"),
	[Input("housing_map", "clickData")])
def update_histogram(clickData):
	housing_id = clickData["points"][0]["customdata"]
	housing_loc = housing.loc[housing["obj_scoutId"] == housing_id]
	adress =  housing_loc.iloc[0]["fulladdress"]
	return {
		"data": [
			go.Bar(
				x = ["Bildung", "Gesundheit", "Freizeit", "Shopping", "Geld", "Öffentliche Gebäude", "Gastwirtschaft"],
				y = [housing_loc.iloc[0]["educationScore"], housing_loc.iloc[0]["healthScore"], housing_loc.iloc[0]["leisureScore"], housing_loc.iloc[0]["shoppingScore"],
				   housing_loc.iloc[0]["moneyScore"], housing_loc.iloc[0]["publicScore"], housing_loc.iloc[0]["cateringScore"]]
			)
		],
		"layout" : go.Layout(
					title="Points of Interests " + adress,
					autosize=True
				)
	}


if __name__ == '__main__':
    app.run_server(debug=True)
