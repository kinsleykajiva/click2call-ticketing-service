from starlette.responses import JSONResponse
import requests
import os

API_BASE_URL = 'http://localhost:8050/'

accessRejectedContent = {
	"success": False,
	'access': False,
	"message": "Access Rejected"
}


def accessRejected ():
	return JSONResponse(status_code=200, content=accessRejectedContent)


def get_ticket_conversations (isENV_TYPE, headers, ticketId):
	"""
		Will get all details or a ticket
	:param isENV_TYPE:
	:param headers:
	:param ticketId:
	:return:
	"""
	ticketId = str(ticketId)
	print(12,isENV_TYPE)
	responseTicket = requests.get('https://api-chat-messages.xxxxxxxxx.com/users/api/v1/secured/get-ticket?ticketId=' + ticketId, headers=headers) \
		if isENV_TYPE else \
		requests.get('http://localhost:3300/users/api/v1/secured/get-ticket?ticketId=' + ticketId, headers=headers)
	responseTicket = responseTicket.json()
	print(responseTicket)
	if responseTicket['success']:
		return responseTicket['data']
	return None
