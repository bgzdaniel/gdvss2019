import plotly
import plotly.graph_objs as go
import pandas
import fiona

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
print(education)


mapbox_access_token = "pk.eyJ1IjoiYmd6LWRhbmllbCIsImEiOiJjandxZTFibjkxOWEyNGJsZWRiZ253OXBoIn0.vpfoIUoYkhjpn42Eb13YCg"

scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]

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

print(housing.info(verbose=True))

housing["text"] = "Adresse: " + housing["fulladdress"]\
+ "; Miete: " + housing["obj_baseRent"].astype(str)\
+ "; Wohnfläche: " + housing["obj_livingSpace"].astype(int).astype(str) + "m²"\
+ "; Zimmer: " + housing["obj_noRooms"].astype(int).astype(str)

data = [
	go.Scattermapbox(
		lon = shopping["longitude"],
		lat = shopping["latitude"],
		text = shopping["text"],
		mode = "markers",
		marker = go.scattermapbox.Marker(
			size = 10,
			color = "rgb(255, 0, 255)",
			),
		opacity = 0.4
	),
	go.Scattermapbox(
		lon = health["longitude"],
		lat = health["latitude"],
		text = health["text"],
		mode = "markers",
		marker = go.scattermapbox.Marker(
			size = 10,
			color = "rgb(0, 128, 0)",
			),
		opacity = 0.4
	),
	go.Scattermapbox(
		lon = leisure["longitude"],
		lat = leisure["latitude"],
		text = leisure["text"],
		mode = "markers",
		marker = go.scattermapbox.Marker(
			size = 10,
			color = "rgb(255, 255, 0)",
			),
		opacity = 0.4
	),
	go.Scattermapbox(
		lon = public["longitude"],
		lat = public["latitude"],
		text = public["text"],
		mode = "markers",
		marker = go.scattermapbox.Marker(
			size = 10,
			color = "rgb(128, 128, 128)",
			),
		opacity = 0.4
	),
	go.Scattermapbox(
		lon = catering["longitude"],
		lat = catering["latitude"],
		text = catering["text"],
		mode = "markers",
		marker = go.scattermapbox.Marker(
			size = 10,
			color = "rgb(0, 255, 255)",
			),
		opacity = 0.4
	),
	go.Scattermapbox(
		lon = money["longitude"],
		lat = money["latitude"],
		text = money["text"],
		mode = "markers",
		marker = go.scattermapbox.Marker(
			size = 10,
			color = "rgb(128, 128, 0)",
			),
		opacity = 0.4
	),
	go.Scattermapbox(
		lon = education["longitude"],
		lat = education["latitude"],
		text = education["text"],
		mode = "markers",
		marker = go.scattermapbox.Marker(
			size = 10,
			color = "rgb(255, 0, 0)",
			),
		opacity = 0.4
	),
	go.Scattermapbox(
		lon = housing["lng"],
		lat = housing["lat"],
		text = housing["text"],
		mode = "markers",
		marker = go.scattermapbox.Marker(
        	size = 20,
            colorscale = scl,
            cmin = 0,
            cmax = housing["obj_baseRent"].max(),
            color = housing["obj_baseRent"],
            colorbar=dict(
                title="Kaltmiete"
            ),
            opacity=1,
            reversescale = True
        )
	)]

layout = go.Layout(
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

fig = go.Figure(data=data, layout=layout)
plotly.offline.plot(fig, filename='wohnraum_mannheim.html', auto_open=True)
