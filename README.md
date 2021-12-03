# SM2T API

The SM2T RESTful API provides traffic information for OSM features suitable for integration in ORS based on the data published by [UBER movement](https://movement.uber.com/?lang=en-US). In the future, it should also provide traffic information derived from social media data.

The API is currently **under active development** and only provides dummy data.

## Installation

The SM2T API requires Python3.x and the packages listed in [requirements.txt](./requirements.txt).
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install .

```bash
python -m venv sm2t_api_env
source ./sm2t_api_env/bin/activate
pip install -r requirements.txt
```

## Usage

Start the API locally by executing

```bash
cd src/sm2t_api
python api.py
```

Send a GET request to the API by opening [http://127.0.0.1:5000/traffic/csv?bbox=8.3197,-48.9405,8.4041,49.0511](http://127.0.0.1:5000/traffic/csv?bbox=8.3197,-48.9405,8.4041,49.0511) in the browser.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GPL](https://choosealicense.com/licenses/lgpl-3.0/)
