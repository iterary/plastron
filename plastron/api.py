from fastapi import FastAPI
import uvicorn

app = FastAPI()


# TODO: Add an endpoint for generating schedules
# Should take in a list of course IDs and a list of filters
# And then return the result of the schedule generator
# I'd look into a POST request for this
@app.get("/")
def read_root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
