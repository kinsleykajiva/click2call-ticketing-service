from fastapi import APIRouter, Request
import time
import os
import requests
from dotenv import load_dotenv
import uuid

from databases.models import getDBSession, Tickets, TicketLifeCycle, TicketHandlersTracking
from utils.utils import accessRejectedContent, accessRejected

load_dotenv()
router = APIRouter(
    prefix    = "/api/v1/secured/ticket/life-cycle",
    tags      = [],
    responses = {404: accessRejectedContent, 400: accessRejectedContent},
)


@router.post("/create")
async def createNew(request: Request):
    if request.headers.get('reject') is not None:
        if request.headers['reject'] != '':
            return accessRejected()

    userId       = request.headers.get('userId')
    body         = await request.form()
    total_amount = body['total_amount']

    return {}


@router.get("/")
async def rootq():
    return {
        "success": True,
        "message": "tickets lifecycle are working"
        }


@router.post("/merge-tickets")
async def mergeTicket(request: Request):
    if request.headers.get('reject') is not None:
        if request.headers['reject'] != '':
            return accessRejected()

    userId        = request.headers.get('userId')
    Authorization = request.headers.get('Authorization')
    body          = await request.form()
    ticketsIds    = body['ticketsIds']
    # create a unifier id to find the tickets or to group them

    mergeId = time.time() * 1000  # will return time long formart
    mergeId = str(mergeId).replace('.', '') + str(uuid.uuid4()).replace('-', '')  # we aim to make sure this is very unique , this will be long string

    headers = {
        "Authorization": Authorization,
        "service-key"  : 'ticketing'
    }
    postData = {
        'ticketsIds': ticketsIds,
        'mergeId'   : mergeId
    }

    responseTicket = requests.post('https://api-chat-messages.xxxxxxxxx.com/users/api/v1/secured/merge-tickets',
                                   data=postData, headers=headers) \
        if os.getenv('ENV_TYPE') is not None else \
        requests.post('http://localhost:3300/users/api/v1/secured/merge-tickets', data=postData, headers=headers)
    responseTicket = responseTicket.json()

    print('responseTicket', responseTicket)

    if responseTicket['responseTicket']:
        return {
            'success': True,
            'message': 'Merged tickets',
            'data'   : responseTicket['data'],
        }

    return {
        'success': False,
    }


@router.post("/change-status")
async def setStatus(request: Request):
    if request.headers.get('reject') is not None:
        if request.headers['reject'] != '':
            return accessRejected()
    try:
        user_id = request.headers.get('userId')
        company_id = request.headers.get('companyId')

        body_json = await request.json()
        if 'statusId' in body_json and 'ticketId' in body_json:
            status_id = body_json['statusId']
            ticket_id = body_json['ticketId']
            # get the last known status from the ticket itself than tge client.
            session = getDBSession()
            ticket = session \
                .query(Tickets) \
                .filter(Tickets.id == ticket_id) \
                .first()
            if int(ticket.statusId) == int(status_id):
                return {
                    'success': True,
                    'message': "Status Already Set",
                }
            save_result = TicketLifeCycle(oldStatusId=ticket.statusId, ticketId=ticket_id,
                                          newStatusId=status_id, savedByUserId=user_id)

            session.add(save_result)
            session.commit()

            save_result = session \
                .query(Tickets) \
                .filter_by(id=ticket.id) \
                .first()
            save_result.statusId = status_id
            session.commit()

            return {
                'success': True,
                'message': "Updated status",
            }
        else:
            return {
                'success': False,
                'message': "missing fields",
            }



    except Exception as e:
        return {
            'success': False,
        }


def _save_ticket_assignment(ticket_id, assignedToUserId, userId):
    session = getDBSession()
    save_result = TicketHandlersTracking(assignedToUserId=assignedToUserId, assignedByUserId=userId, ticketId=ticket_id)

    session.add(save_result)
    session.commit()


@router.post("/assignment-to")
async def re_assign_ticket(request: Request):
    if request.headers.get('reject') is not None:
        if request.headers['reject'] != '':
            return accessRejected()

    userId           = request.headers.get('userId')
    body             = await request.json()
    ticket_id        = body['ticket_id']
    assignedToUserId = body['assignedToUserId']
    userId           = body['userId']

    session = getDBSession()
    ticket = session \
        .query(Tickets) \
        .filter(Tickets.id == ticket_id) \
        .first()

    _save_ticket_assignment(ticket_id , assignedToUserId, ticket.createdByUserId)

    return {
        "success": True,
        "message": 'Ticket Assignment Success',
    }

