import os

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, Request
from sqlalchemy import join, select
from starlette.exceptions import HTTPException

from databases.models import Tickets, getDBSession, TicketStatuses, TicketHandlers, TicketPriorities, runRawSQL, \
    runRawSQLBindings
from routers.ticketTicketTags import get_ticket_tags
from utils.utils import accessRejectedContent, accessRejected, get_ticket_conversations

load_dotenv()
router = APIRouter(
    prefix="/api/v1/secured/ticket",
    tags=[],
    responses={404: accessRejectedContent, 400: accessRejectedContent},
)


@router.post("/create")
async def createNew(request: Request):
    if request.headers.get('reject') is not None:
        if request.headers['reject'] != '':
            return accessRejected()
    try:
        user_id    = request.headers.get('userId')
        company_id = request.headers.get('companyId')
        body_json  = await request.json()
        title      = body_json['title']
        title      = None if title == '' else title

        save_result = Tickets(title=title, statusId=1, createdByUserId=user_id, companyId=company_id)
        session     = getDBSession()
        session.add(save_result)
        session.commit()

        save_result2 = TicketHandlers(userId=user_id, ticketId=save_result.id, savedByUserId=user_id)
        session.add(save_result2)
        session.commit()

        return {
            "success": True,
            "message": 'Saved Ticket',
            'data'   : {
                'ticket': {
                    'id'             : save_result.id,
                    'title'          : save_result.title,
                    'statusId'       : save_result.statusId,
                    'createdByUserId': save_result.createdByUserId,
                    'companyId'      : save_result.companyId,
                    'dateCreated'    : save_result.dateCreated.strftime('%Y-%m-%d %H:%M:%S')
                },
                'ticketHandling': {
                    'id'           : save_result2.id,
                    'userId'       : save_result2.userId,
                    'ticketId'     : save_result2.ticketId,
                    'savedByUserId': save_result2.savedByUserId,
                    'dateCreated'  : save_result2.dateCreated.strftime('%Y-%m-%d %H:%M:%S'),
                },
            }
        }
    except Exception as e:
        print(e)
    return {
        "success": False,
        "message": "Failed to complete request"
    }



@router.get("/all")
async def getAllTickets(request: Request):
    if request.headers.get('reject') is not None:
        if request.headers['reject'] != '':
            return accessRejected()

    userId        = request.headers.get('userId')
    companyId     = request.headers.get('companyId')
    Authorization = request.headers.get('Authorization')
    try:
        headers = {
            "service-key": 'ticketing',
            "Authorization": Authorization
        }
        response = requests.get('https://api-app.xxxxxxxxx.com/auth/api/v1/users/users?companyId=' + companyId,
                                headers=headers) if os.getenv('ENV_TYPE') is not None \
            else requests.get('http://localhost:8050/auth/api/v1/users/users?companyId=' + companyId, headers=headers)
        response  = response.json()
        usersList = None
        if response['success'] is True:
            usersList = response['data']['users']

        tickets = runRawSQLBindings("""
            SELECT tickets.id, tickets.title, tickets.statusId , ticketStatuses.title AS statusTitle, tickets.companyId, tickets.createdByUserId, tickets.dateCreated, tickets.priorityId ,ticketPriorities.title AS priorityTitle
            FROM tickets
            JOIN ticketStatuses ON ticketStatuses.id = tickets.statusId
            JOIN ticketPriorities ON ticketPriorities.id = tickets.priorityId  
            WHERE  tickets.companyId =  %(companyId)s
        """, {
            "companyId": companyId
        })
        result = []
        for ticket in tickets:
            try:
                userObj = next(x for x in usersList if int(x["id"]) == int(ticket.createdByUserId))
            except Exception as e:
                userObj = None
            is_local = True if os.getenv('ENV_TYPE') is not None else False
            result.append({
                'id'                  : int(ticket.id),
                'ticketData'          : get_ticket_conversations(is_local, headers, ticket.id),
                'title'               : ticket.title,
                'tags'                : get_ticket_tags(int(ticket.id)),
                'priorityId'          : ticket.priorityId,
                'statusId'            : int(ticket.statusId),
                'statusTitle'         : ticket.statusTitle,
                'priorityTitle'       : ticket.priorityTitle,
                'companyId'           : int(ticket.companyId),
                'createdByUserId'     : int(ticket.createdByUserId),
                'createdByUserDetails': userObj,
                'dateCreated'         : ticket.dateCreated.strftime('%Y-%m-%d %H:%M:%S')
            })

        return {
            "success": True,
            "message": 'Getting all tickets',
            'data'   : {
                'tickets': result
            }
        }
    except Exception as e:
        print({e})

    return {
        "success": False,
        "message": "Failed to complete request"
    }


@router.get("/ticket")
async def getTicket(request: Request):
    if request.headers.get('reject') is not None:
        if request.headers['reject'] != '':
            return accessRejected()

    user_id       = request.headers.get('userId')
    company_id    = request.headers.get('companyId')
    authorization = request.headers.get('Authorization')
    params        = request.query_params
    ticket_id     = params['ticketId']
    try:
        headers = {
            "Authorization": authorization,
            "service-key": 'ticketing'
        }
        response = requests.get('https://api-app.xxxxxxxxx.com/auth/api/v1/users/users?companyId=' + company_id,
                                headers=headers) \
            if os.getenv('ENV_TYPE') is not None else \
            requests.get('http://localhost:8050/auth/api/v1/users/users?companyId=' + company_id, headers=headers)
        response  = response.json()
        usersList = None

        if response['success'] is True:
            usersList = response['data']['users']

        response_ticket_conversations = requests.get(
            'https://api-chat-messages.xxxxxxxxx.com/api/v1/secured/ticket-conversations?ticketId=' + ticket_id,
            headers=headers) \
            if os.getenv('ENV_TYPE') is not None else \
            requests.get('http://localhost:3300/api/v1/secured/ticket-conversations?ticketId=' + ticket_id,
                         headers=headers)
        response_ticket_conversations = response_ticket_conversations.json()

        tickets = getDBSession().query(Tickets, TicketStatuses) \
            .join(TicketStatuses).filter(Tickets.id == ticket_id) \
            .all()

        tickets_handlers = getDBSession().query(TicketHandlers).filter_by(ticketId=ticket_id).all()

        result = []
        result_tickets_handles = []

        for ticket, ticketstatuse in tickets:
            try:
                userObj = next(x for x in usersList if x["id"] == ticket.createdByUserId)
            except Exception as e:
                userObj = None  # user was either removed from the database   or the user was edited manually

            for handles in tickets_handlers:
                if ticket.id == handles.ticketId:
                    result_tickets_handles.append({
                        'handlersId'   : handles.id,
                        'ticketId'     : handles.ticketId,
                        'savedByUserId': handles.savedByUserId,
                        'dateCreated'  : handles.dateCreated.strftime('%Y-%m-%d %H:%M:%S'),
                    })

            result.append({
                'ticketId'            : ticket.id,
                'tickets_handlers'    : result_tickets_handles,
                'chats'               : response_ticket_conversations['data']['conversations'],
                'customer'            : response_ticket_conversations['data']['customer'],
                'title'               : ticket.title,
                'statusId'            : ticket.statusId,
                'statusTitle'         : ticketstatuse.title,
                'companyId'           : ticket.companyId,
                'createdByUserId'     : ticket.createdByUserId,
                'createdByUserDetails': userObj,
                'dateCreated'         : ticket.dateCreated.strftime('%Y-%m-%d %H:%M:%S')
            })
            result_tickets_handles = []  # reset this list before the next iteration

        return {
            "success": True,
            "message": 'Getting ticket',
            'data'   : {
                'tickets': result
            }
        }
    except Exception as e:
        print({e})
    return {
        "success": False,
        "message": "Failed to complete request"
    }
