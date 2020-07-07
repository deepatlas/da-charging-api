da-charging-api
============
[![GitHub Stars](https://img.shields.io/github/stars/deepatlas/da-charging-api?style=social)](https://github.com/deepatlas/da-charging-api/stargazers) [![GitHub Issues](https://img.shields.io/github/issues-raw/deepatlas/da-charging-api)](https://github.com/deepatlas/da-charging-api/issues) [![GitHub Pulls](https://img.shields.io/github/issues-pr/deepatlas/da-charging-api)](https://github.com/deepatlas/da-charging-api/pulls) [![Current Version](https://img.shields.io/badge/version-1.0.0-green.svg)](https://github.com/deepatlas/da-charging-api) [![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

Restful API that provides information from multiple sources about electric vehicle charging stations in and around Germany.
## Installation
```bash
pip install git+https://github.com/deepatlas/da-charging-api.git
```
## Usage
### Python3
If you can start the api server calling the following snippet.
```bash
from charging_api import start_api
db_config = {...}
connector_config = {...}
start_api(restful_config=db_config, connector_config=connector_config, host="0.0.0.0", port=8080)
```
You can furhtermore specify a [db_config](src/charging_api/rest_api/_config.py) and [connector_config](https://github.com/deepatlas/da-charging-connectors/blob/master/src/charging_stations/connectors/_config.py).
### Docker
You can build docker containers for the API and the database:
```bash
docker build -t charging_api-db -f Dockerfile.db . 
docker build -t charging_api-rest -f Dockerfile.rest . 
```
Run containers as follows:
```bash
docker run -p 5432:5432 --detach charging_api-db
docker run -p 5432:5432 --detach charging_api-rest
```

### Docker-Compose
Start services:
```bash
docker-compose up -d
```

Stop services:
```bash
docker-compose down
```

## Run Tests
Start from Project Root:
```bash
pytest
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)