from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from py_eureka_client import eureka_client
import os

from routers import tickets, ticketLifeCycle,ticketsTags,ticketTicketTags

load_dotenv()

app = FastAPI(
	title="Ticketing service",
	description="This will handle all of the ticket related functionality",
	version="1.0.0"
)

app.include_router(tickets.router)
app.include_router(ticketLifeCycle.router)
app.include_router(ticketsTags.router)
app.include_router(ticketTicketTags.router)


@app.exception_handler(HTTPException)
async def validation_exception_handler (request, err):
	base_error_message = f"Failed to execute: {request.method}: {request.url}"
	# Change here to LOGGER
	return JSONResponse(status_code=400, content={
		"success": False,
		"status": 400,
		"message": f"{base_error_message}. Detail: {err}"
	})


@app.get("/")
async def root ():
	return {
		"success": True,
		"message": "tickets are working"}


if os.getenv('ENV_TYPE') is not None:
	print("SYSTEM::::running  in PRODUCTION")
	eureka_client.init(eureka_server=os.getenv('EUREKA_SERVER'), app_name=os.getenv('SERVICE_NAME'),
					   instance_port=int(os.getenv('PORT')), data_center_name=os.getenv('DATA_CENTER_NAME'),

					   region=os.getenv('REGION'), vip_adr=os.getenv('SERVICE_NAME'))
else:
	print("SYSTEM::::running  in local set up")
	eureka_client.init(eureka_server="http://localhost:8761/eureka/", app_name=os.getenv('SERVICE_NAME'), instance_port=int(os.getenv('PORT')), instance_host='localhost', instance_ip='172.0.0.1')

