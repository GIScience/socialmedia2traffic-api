# Social Media 2 Traffic API

The [SocialMedia2Traffic](https://heigit.org/de/new-mfund-project-start-of-socialmedia2traffic-derivation-of-traffic-information-from-social-media-data-2/) (SM2T) API provides **hourly traffic speed data** for individual OSM road features suitable for integration in [openrouteservice](https://openrouteservice.org).

At the moment, only data for Berlin is available.

## Usage

Traffic data can be queried from [https://sm2t.heigit.org/traffic/csv](https://sm2t.heigit.org/traffic/csv) using GET requests by providing a spatial bounding box in geographic coordinates (min_lon, min_lat, max_lon, max_lat).

**Example Query**

```
curl http://sm2t.heigit.org/traffic/csv?bbox=13.3472,52.499,13.4117,42.5304
```

The response is a **zip compressed CSV file** containing **hourly traffic speed in km/h** for individual OSM highway segments, e.g.

**Example Response**

```
osm_way_id,osm_start_node_id,osm_end_node_id,hour,speed
4615004,12614644,29266235,6,41.0
4615004,12614644,29266235,7,28.0
4615004,12614644,29266235,8,28.0
4615004,12614644,29266235,9,22.0
4615004,12614644,29266235,10,29.0
```

The first three columns denote **official OSM IDs**, so the respective OSM objects can be viewed on [https://www.openstreetmap.org](https://www.openstreetmap.org), e.g.
- [https://www.openstreetmap.org/way/4615004](https://openstreetmap.org/way/4615004)
- [https://www.openstreetmap.org/node/12614644](https://www.openstreetmap.org/node/12614644).

## API Setup

The API can be set up using [Docker](https://www.docker.com/):

```
cd socialmedia2traffic-api
docker compose up
```

## Contributing
If you encounter problems or bugs, please open an [issue](https://github.com/GIScience/socialmedia2traffic-api/issues).

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. Also please make sure to update tests as appropriate.

## Funding

This project was funded by the German Federal Ministry of Transport and Digital Infrastructure (BMVI) in the context of the research initiative mFUND.

<p float="left">
<img src="./img/bmdv.png" height=170 align="middle" />
<img src="./img/mfund.jpg" height=170 align="middle" />
</p>
