# FIFA AutoBuilder
Flask API to optimise FIFA team chemistry from FUTBIN squad links.

## Setup
Clone the repository then run the following commands from the main directory to spin up the docker container:

```
docker build -t fifa-auto
docker run -d -p 5000:5000 fifa-auto
```

You should now be able to access the application at http://localhost:5000/.

## Usage

Enter a valid FUTBIN squad link e.g. https://www.futbin.com/20/squad/SQUAD_NUMBER in the text field. Then specify the number of squads you would like the optimiser to return, and tick the box if you would like the substitues bench to be factored into the optimisation.
