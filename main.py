import os
from fastapi import FastAPI, Request, Response
import requests

app = FastAPI()

webhook_url = os.environ.get("WEBHOOK_URL")
masto_url = os.eviron.get("MASTODON_URL")
@app.on_event("startup")
async def startup_event():
    @app.middleware("http")
    async def log_request(request: Request, call_next):
        print(f"Received request to {request.url}")
        response = await call_next(request)
        print(f"Returning response with status code {response.status_code}")
        return response


@app.get("/")
def root():
    return Response(content="", status_code=200)


@app.post("/webhook")
async def webhook(request: Request):
    json_data = await request.json()
    if json_data["event"] == "report.created":
        account_username = json_data["object"]["account"]["username"]
        report_user = json_data["object"]["target_account"]["username"]
        category = json_data["object"]["category"]
        report_id = json_data["object"]["id"]
        comment = json_data["object"]["comment"]
        print(request.json)
        message = f':rainbow: New Report :rainbow:\n\n{report_user} has been reported for {category}\n'

        if comment:
            message += f'\nThere was a comment:\n```{comment}```\n'

        message += f'\nSubmitted by: {account_username}\nhttps://{masto_url}/admin/reports/{report_id}'
        try:
            response = requests.post(webhook_url, json={'content': message})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print("Error sending message to Discord: ", e)
            return Response(content="Error sending message to Discord", status_code=500)
    return Response(content="", status_code=200)
