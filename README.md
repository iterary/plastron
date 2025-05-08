## Plastron  [![Better Stack Badge](https://uptime.betterstack.com/status-badges/v1/monitor/1x68y.svg)](https://uptime.betterstack.com/?utm_source=status_badge) [![pytest](https://github.com/iterary/plastron/actions/workflows/python-test.yml/badge.svg)](https://github.com/iterary/plastron/actions/workflows/python-test.yml)

> **plas·tron**  
/ˈplastrən/  
the nearly flat part of a turtle's shell

![Plastron Output](./assets/plastron_output.png)

Plastron is a teensy-weensy microservice that generates optimal schedules for courses at UMD. Based on user input, it will scrape Testudo's course catalog, find suitable sections, and populate a schedule that minimizes time between classes. Made as a final project for INST326.

### Generate schedules from the command line

Install dependencies via [developer instructions](#development).

```bash
py -m plastron.schedule_generator INST335 INST314 INST311 INST327 -n 3
```

Arguments:
- `Course IDs`: List of course IDs (e.g. INST335 INST314 INST311 INST327)
- `-n` or `--num`: Number of schedules to generate (default: 1)
- `-nsg` or `--no-shady-grove`: Do not include ESG sections (default: True)
- `-nfc` or `--no-freshman-connection`: Do not include FC sections (default: True)
- `-o` or `--open-seats`: Include only sections with open seats (default: True)
- `-s` or `--earliest-start`: The earliest start time (default: 8:00am)
- `-e` or `--latest-end`: The latest end time (default: 5:00pm)

### Generate schedules via API

Deployed at: https://plastron.onrender.com/

## Development

### Get Poetry as a package manager

```bash
pip install poetry
```

### Install packages

```bash
poetry install
```

### Choose the venv interpreter

- Use CTRL/CMD + SHIFT + P
- Search for and choose `Python: Select Interpreter`
- Enter interpreter path -> Find
- Find and choose `.venv/Scripts/python.exe`

### Run the API server locally

```bash
uvicorn plastron.api:app --reload
```

You can access the development server at [http://localhost:8000/](http://localhost:8000/)

While docs are available at [http://localhost:8000/docs](http://localhost:8000/docs)

## Testing

### Unit Testing

```bash
poetry run pytest
```

### E2E Testing

Navigate to https://plastron.onrender.com/docs and run the example request bodies against each endpoint. If the service is active and in a good state, each response should return a 200 status code, along with output matching the documentation given for each endpoint.

![E2E Test](./assets/swagger.png)

Confirm that schedules are generated properly by running the command line example or hitting the `/schedules/visualized` endpoint and comparing the outputted weight against the expected weight per the formula below.

![Weight Formula](./assets/formula.png)

### Annotated Bibliography

Dijkstra, E. W. (1959). A note on two problems in connexion with graphs. *Numerische Mathematik, 1*(1), 269–271. 

- Used in project proposal as a reference for the search algorithm

Acknowledgements:

- [BetterStack](https://uptime.betterstack.com/) for providing uptime monitoring to ensure the API is always up
- [Testudo](https://app.testudo.umd.edu/soc/) for providing the course catalog
- [Maxim](https://stackoverflow.com/a/43357954) for the `str2bool` utility function
