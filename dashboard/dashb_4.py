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

reset_button_count = [0]
old_y = [0]

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
with fiona.open(MARK_POIS) as src:
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
    MARK_COODRINATES,
    sep=";")
housing_properties = pandas.read_csv(
    MARK_PROPERTIES,
    sep=";")

housing = housing_properties.merge(housing_coordinates,
    on="obj_scoutId", how="inner")
housing["lat"] = housing["lat"].apply(
    lambda x: float(x.replace(",", ".")))
housing["lng"] = housing["lng"].apply(
    lambda x: float(x.replace(",", ".")))

radius = 0.002
radial = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
pointsofinterest[["latitude", "longitude"]])

subset = pointsofinterest
close_by = numpy.sum(radial[:, :] < radius, axis = 1)
#ii, jj = numpy.where(radial[:, :] < 0.001)
#in_radius = pandas.Dataframe({"housing_id": ii, "poi_id": jj})
#in_radius.loc[in_radius["housing_id"] == id, "poi_id"]
#housing["score"] = close_by

# Score for Education
radial_education = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
education[["latitude", "longitude"]])

subsetEducation = education
closeBy = numpy.sum(radial_education[:, :] < radius, axis = 1)
housing["educationScore"] = closeBy

#Score for health
radial_health = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
health[["latitude", "longitude"]])

subsetHealth = health
closeBy = numpy.sum(radial_health[:, :] < radius, axis = 1)
housing["healthScore"] = closeBy

#Score for leisure
radial_leisure = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
leisure[["latitude", "longitude"]])

subsetleisure = leisure
closeBy = numpy.sum(radial_leisure[:, :] < radius, axis = 1)
housing["leisureScore"] = closeBy

#Score for public
radial_public = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
public[["latitude", "longitude"]])

subsetPublic = public
closeBy = numpy.sum(radial_public[:, :] < radius, axis = 1)
housing["publicScore"] = closeBy

#Score for catering
radial_catering = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
catering[["latitude", "longitude"]])

subsetCatering = catering
closeBy = numpy.sum(radial_catering[:, :] < radius, axis = 1)
housing["cateringScore"] = closeBy

#Score for shopping
radial_shopping = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
shopping[["latitude", "longitude"]])

subsetShopping = shopping
closeBy = numpy.sum(radial_shopping[:, :] < radius, axis = 1)
housing["shoppingScore"] = closeBy

#Score for money
radial_money = scipy.spatial.distance.cdist(
housing[["lat", "lng"]],
money[["latitude", "longitude"]])

subsetMoney = money
closeBy = numpy.sum(radial_money[:, :] < radius, axis = 1)
housing["moneyScore"] = closeBy

housing["score"] = housing["moneyScore"]+housing["shoppingScore"]\
+ housing["cateringScore"] + housing["publicScore"]\
+ housing["leisureScore"] + housing["healthScore"]\
+ housing["educationScore"]

housing["text"] = "Adresse: " + housing["fulladdress"]\
+ "; Miete: " + housing["obj_baseRent"].astype(str)\
+ "; Wohnfläche: " + housing["obj_livingSpace"].astype(int).astype(str) + "m²"\
+ "; Zimmer: " + housing["obj_noRooms"].astype(int).astype(str)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

names = ["education_slider", "health_slider", "leisure_slider", "public_slider", "catering_slider", "shopping_slider", "money_slider"]
sliders = []
for i in range(0, 7):
	sliders.append(html.Div([
		dcc.Slider(
			id = names[i],
			min = 0,
			max = 4,
			step = 0.1,
			value = 1,
			marks = {
				0: "0",
				4: "4"
			})]))

def calculate_score(m1, m2, m3, m4, m5, m6, m7):
	new_score = housing["moneyScore"] * m7\
	+ housing["shoppingScore"] * m6\
	+ housing["cateringScore"] * m5\
	+ housing["publicScore"] * m4\
	+ housing["leisureScore"] * m3\
	+ housing["healthScore"] * m2\
	+ housing["educationScore"] * m1
	return new_score

def initial_map(new_housing):
	housing["score"] = new_housing
	return {
		"data":[
			go.Scattermapbox(
				lon = housing["lng"],
				lat = housing["lat"],
				text = housing["text"]\
				+ "; Score: " + housing["score"].astype(str),
				customdata = housing["obj_scoutId"],
				mode = "markers",
				marker = go.scattermapbox.Marker(
       				size = 20,
      				colorscale = scl,
       				cmin = housing["score"].min(),
       				cmax = housing["score"].max(),
           			color = housing["score"],
           			colorbar=dict(
           			    title="Number POIs"),
       			opacity=0.8,
       			reversescale = True))],
       		"layout": go.Layout(
					title = "Housing in Mannheim",
    				hovermode='closest',
    				mapbox=go.layout.Mapbox(
       				accesstoken=mapbox_access_token,
       				bearing=0,
       				center=go.layout.mapbox.Center(
           				lat=49.48713,
           				lon=8.46624
       				),
       				pitch=0,
       				zoom=12,
       				uirevision = "False"
    				))
	}

analysis = pandas.DataFrame({
    "total_rent": housing["obj_totalRent"],
    "base_rent": housing["obj_baseRent"]})

wasserturm = (49.48713, 8.46624)

dist_from_center = numpy.linalg.norm(
    housing[["lat", "lng"]] - wasserturm, axis=1)

analysis["from_center"] = dist_from_center

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
	html.Div([
html.Div([
		html.Button("Reset Map", id = "reset_button"),
		dcc.Graph(
			id = "housing_map",
			figure =
				initial_map(housing)
            )], style={"float":"left","width": "60%"}),

		html.Div([
			dcc.Graph(
				id="housing_distribution",
				figure={
					"data": [
						go.Scatter(
							y=[710],
							x0="Rent",
							mode="markers",
							marker=go.scatter.Marker(
								opacity=1,
								size=15),
							showlegend=False
						), {
							"type": "violin",
							"y": housing["obj_baseRent"],

							"box": {
								"visible": True
							},
							"line": {
								"color": "black"
							},
							"meanline": {
								"visible": True
							},
							"fillcolor": "#8dd3c7",
							"opacity": 0.6,
							"x0": "Rent",
							"points": "all",
							"jitter": 0
						}],
					"layout": {
						"showlegend": False,
						"title": "Prices",
						"yaxis": {
							"zeroline": False,
						}
					}
				})], style={"display": "inline-block","float":"left"}),
	], style={"display":"flex"}),

	html.Div([
		dcc.Markdown('''**Scaling**'''),
	], style={"width": "15em", "padding": "1em"}),
	html.Div([
		dcc.Markdown('''Education'''),
		sliders[0],
	], style={"width": "15em", "padding": "1em", "display": "inline-block"}),
	html.Div([
		dcc.Markdown('''Health'''),
		sliders[1],
	], style={"width": "15em", "padding": "1em", "display": "inline-block"}),
	html.Div([
		dcc.Markdown('''Leisure'''),
		sliders[2],
	], style={"width": "15em", "padding": "1em", "display": "inline-block"}),
	html.Div([
		dcc.Markdown('''Public Buildings'''),
		sliders[3],
	], style={"width": "15em", "padding": "1em", "display": "inline-block"}),
	html.Div([
		dcc.Markdown('''Catering'''),
		sliders[4],
	], style={"width": "15em", "padding": "1em", "display": "inline-block"}),
	html.Div([
		dcc.Markdown('''Shopping'''),
		sliders[5],
	], style={"width": "15em", "padding": "1em", "display": "inline-block"}),
	html.Div([
		dcc.Markdown('''Money'''),
		sliders[6],
	], style={"width": "15em", "padding": "1em", "display": "inline-block"}),
	html.Div([
	html.Div([
		dcc.Graph(
			id = "detail_view_of_pois",
			figure = {
				"data": [
					go.Bar(
						x = ["Education", "Leisure", "Shopping", "Money", "Public Buildings", "Catering"],
						y = [0,0,0,0,0,0,0])
				],
				"layout" : go.Layout(
					title = "POIs",
					yaxis = dict(
						tick0 = 0,
						dtick = 1)
				)
			}
		)
		], style={"display": "inline-block"}),
	html.Div([dcc.Graph(id = "current_flat")]),
	html.Div([
			dcc.Graph(
				id = "price_score_correlation",
				figure = {
					"data": [
						go.Scatter(
							x = housing["score"],
							y = housing["obj_baseRent"] / housing["obj_livingSpace"],
							mode = "markers"
						)
					],
					"layout": go.Layout(
						uirevision = "False",
						xaxis = {
							"title": "Score"
							#"range": [0, 200]
						},
						yaxis = {
							"title": "Price per m² (in Euro/m²)"
						})
				}
			)
		]),
	], style={"display":"flex"}),
	])

@app.callback(
	Output("current_flat", "figure"),
	[Input("housing_map", "clickData")])
def show_current_flat(clickData):
	if ((clickData != None) and ("customdata" in clickData["points"][0])):
		housing_id = clickData["points"][0]["customdata"]
		current_housing = housing.loc[housing["obj_scoutId"] == housing_id]
		#print("housing_id: " + str(housing_id))
		housing_pos = housing.loc[housing["obj_scoutId"] == housing_id, ["lat", "lng"]].values
		poi_pos = pointsofinterest[["latitude", "longitude"]].values
		radial = numpy.linalg.norm(housing_pos - poi_pos, axis=1)
		pois = pointsofinterest.loc[radial < radius]


	return {
		"data": [
			go.Scattermapbox(
				lat = pois["latitude"],
				lon = pois["longitude"],
				mode = "markers",
				marker = go.scattermapbox.Marker(
					size = 10,
					color = "rgb(255, 0, 0)"
				),
				text = pois["text"] + " " + pois["name"],
				showlegend=False
			),
			go.Scattermapbox(
				lat = current_housing["lat"],
				lon = current_housing["lng"],
				mode = "markers",
				marker = go.scattermapbox.Marker(
					size = 20,
           			color = "rgb(0, 0, 255)"
				),
				showlegend=False
			)
		],
		"layout": go.Layout(
				mapbox=go.layout.Mapbox(
       				accesstoken=mapbox_access_token,
       				bearing=0,
       				center=go.layout.mapbox.Center(
           				lat = current_housing["lat"].values[0],
						lon = current_housing["lng"].values[0]
       				),
       			zoom = 15
				)
			)
	}


@app.callback(
	Output("price_score_correlation", "figure"),
	[Input("education_slider", "value"),
	Input("health_slider", "value"),
	Input("leisure_slider", "value"),
	Input("public_slider", "value"),
	Input("catering_slider", "value"),
	Input("shopping_slider", "value"),
	Input("money_slider", "value")])
def update_correlation(v1, v2, v3, v4, v5, v6, v7):
	new_housing = housing.copy(True)
	new_housing["score"] = calculate_score(v1, v2, v3, v4, v5, v6, v7)
	return {
		"data": [
			go.Scatter(
				x = new_housing["score"],
				y = new_housing["obj_baseRent"] / new_housing["obj_livingSpace"],
				mode = "markers"
			)
		],
		"layout": go.Layout(
			uirevision = "False",
			xaxis = {
				"title": "Score"
				#"range": [0, 200]
			},
			yaxis = {
				"title": "Price per m² (in Euro/m²)"
			})
	}


@app.callback(
	Output("housing_distribution", "figure"),
	[Input("housing_map", "hoverData")])
def update_violin(hoverData):
	if (hoverData != None and "customdata" in hoverData["points"][0]):
		housing_id = hoverData["points"][0]["customdata"]
		newRent = housing.loc[housing["obj_scoutId"] == housing_id]
		newRent = newRent.iloc[0]["obj_baseRent"]
	else:
		newRent = 100
	return {
		"data": [
				go.Scatter(
					y = [newRent],
					x0 = "Rent",
					mode = "markers",
					marker = go.scatter.Marker(
						opacity = 1,
						size = 15),
					showlegend=False
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
					"x0":"Rent",
					"points": "all",
					"jitter": 0
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
	[Input("housing_distribution", "hoverData"),
	Input("reset_button", "n_clicks"),
	Input("education_slider", "value"),
	Input("health_slider", "value"),
	Input("leisure_slider", "value"),
	Input("public_slider", "value"),
	Input("catering_slider", "value"),
	Input("shopping_slider", "value"),
	Input("money_slider", "value"),
	Input("housing_map", "clickData")])
def update_map(hoverData, n_clicks, education_value, health_value, leisure_value, public_value, catering_value, shopping_value, money_value, clickData):

	score = calculate_score(education_value, health_value, leisure_value, public_value, catering_value, shopping_value, money_value)

	if (hoverData != None and hoverData["points"][0]["y"] != old_y[0]):
		reset_button_count[0] = n_clicks

	if ((n_clicks == reset_button_count[0] or n_clicks == None) and hoverData != None):
		housing_rent = hoverData["points"][0]["y"]
		old_y[0] = hoverData["points"][0]["y"]
		new_housing = housing.loc[(housing["obj_baseRent"] > housing_rent - 75) & (housing["obj_baseRent"] < housing_rent + 75)]
	else:
		print("test")
		return initial_map(score)

	new_housing["score"] = calculate_score(education_value, health_value, leisure_value, public_value, catering_value, shopping_value, money_value)


	return {
				"data":[
					go.Scattermapbox(
						lon = new_housing["lng"],
						lat = new_housing["lat"],
						text = new_housing["text"]\
						+ "; Score: " + new_housing["score"].astype(str),
						customdata = new_housing["obj_scoutId"],
						mode = "markers",
						marker = go.scattermapbox.Marker(
        					size = 20,
            				colorscale = scl,
            				cmin = 0,
            				cmax = new_housing["score"].max(),
            				color = new_housing["score"],
            				colorbar=dict(
            				    title="Number POIs"
            				),
            			opacity=1,
            			reversescale = True
        		))],
        		"layout": go.Layout(
						title = "Housing in Mannheim",
    					hovermode='closest',
    					mapbox=go.layout.Mapbox(
        				accesstoken=mapbox_access_token,
        				bearing=0,
        				center=go.layout.mapbox.Center(
            				lat=49.48713,
            				lon=8.46624
        				),
        				pitch=0,
        				zoom=12,
        				uirevision = "False"
    					))
			}

@app.callback(
	Output("detail_view_of_pois", "figure"),
	[Input("housing_map", "clickData")])
def update_histogram(clickData):
	if (("customdata" in clickData["points"][0])):
		housing_id = clickData["points"][0]["customdata"]
		housing_loc = housing.loc[housing["obj_scoutId"] == housing_id]
		adress =  housing_loc.iloc[0]["fulladdress"]
		colors = ['#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69']
#	else:
#		housing_loc = pandas.DataFrame({"educationScore": housing["educationScore"].sum(),
#			"healthScore": housing["healthScore"].sum(),
#			})

	return {
		"data": [
			go.Bar(
				x = ["Education", "Health", "Leisure", "Shopping", "Money", "Public Buildings", "Catering"],
				y = [housing_loc.iloc[0]["educationScore"], housing_loc.iloc[0]["healthScore"], housing_loc.iloc[0]["leisureScore"], housing_loc.iloc[0]["shoppingScore"],
				   housing_loc.iloc[0]["moneyScore"], housing_loc.iloc[0]["publicScore"], housing_loc.iloc[0]["cateringScore"]],
			marker={
				'color': colors,
				'colorscale': 'Viridis'
			}
			)
		],
		"layout" : go.Layout(
					title="POIs: " + adress,
					autosize=True,
					yaxis = dict(
						tick0 = 0,
						dtick = 1,
						ticklen = 5,
						range = [0, 12])
				)
	}


if __name__ == '__main__':
	app.run_server(debug=False)
