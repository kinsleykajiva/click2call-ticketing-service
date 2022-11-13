from fastapi import APIRouter, Request
import time
import os
import requests
from dotenv import load_dotenv
import uuid

from sqlalchemy import update, text

from databases.models import TicketTag, getDBSession
from utils.utils import accessRejectedContent, accessRejected
from routers.ticketTicketTags import get_ticket_tags, saveTicketTagDetails

load_dotenv()
router = APIRouter(
    prefix    = "/api/v1/secured/ticket/tags",
    tags      = [],
    responses = {404: accessRejectedContent, 400: accessRejectedContent},
)


@router.get("/")
async def rootq():
    return {
        "success": True,
        "message": "tickets tags are working"
    }


@router.post("/create")
async def createNewTag(request: Request):
    if request.headers.get('reject') is not None:
        if request.headers['reject'] != '':
            return accessRejected()

    userId = request.headers.get('userId')
    body   = await request.json()
    title  = body['title']

    save_result = TicketTag(title=title, )
    session     = getDBSession()
    session.add(save_result)
    session.commit()

    return {
        "success": True,
        "message": 'Saved New Ticket Tag',
        "data": {
            'tag': {
                'id': save_result.id,
            }
        }
    }


@router.post("/update")
async def updateTag(request: Request):
    if request.headers.get('reject') is not None:
        if request.headers['reject'] != '':
            return accessRejected()

    userId = request.headers.get('userId')
    body = await request.json()
    try:
        if 'id' in body and 'title' in body:
            title = body['title']
            id    = body['id']

            session     = getDBSession()
            save_result = session \
                .query(TicketTag) \
                .filter_by(id=id) \
                .first()
            save_result.title = title
            session.commit()

            return {
                "success": True,
                "message": 'Saved updated Ticket Tag'
            }
        else:
            return {
                "success": False,
                "message": 'Failed to update tag',
            }
    except Exception as e:
        print(e)
        return {
            "success": False,
            "message": "Failed to save/update"
        }


@router.post("/set-tag-to-ticket")
async def setTicketsTags(request: Request):
    userId        = request.headers.get('userId')
    companyId     = request.headers.get('companyId')
    Authorization = request.headers.get('Authorization')

    body = await request.json()
    try:
        tagId    = body['tagId']
        ticketId    = body['ticketId']
        tagTitle    = body['tagTitle']

        saveTicketTagDetails(ticketId, tagId, tagTitle)

        return {
            "success": True,
            "message": 'Saved updated Ticket Tag'
        }

    except Exception as e:
        print(e)
        return {
            "success": False,
            "message": "Failed to save/update"
        }




@router.post("/delete")
async def deleteAllTicketsTags(request: Request):
    if request.headers.get('reject') is not None:
        if request.headers['reject'] != '':
            return accessRejected()

    userId        = request.headers.get('userId')
    companyId     = request.headers.get('companyId')
    Authorization = request.headers.get('Authorization')

    body_json = await request.json()

    if 'tag_id' in body_json:
        tag_id = body_json['tag_id']
        getDBSession() \
            .query(TicketTag) \
            .filter_by(id=tag_id) \
            .delete()
        # User.query.filter(User.id == 123).delete()
        return {
            "success": True,
            "message": 'Deleted tag'
        }
    else:
        return {
            "success": False,
            "message": 'Failed to delete missing Delete Argument'
        }

@router.get("/get-ticket-tags")
async def getTicketTags(request: Request):

    params = request.query_params
    ticket_id   = params['ticket_id']
    return {
        'success':True ,
        "message":"tags for one ticket",
        'data':{
            'tags' : get_ticket_tags(int(ticket_id)),
        }
    }
@router.get("/all")
async def getAllTicketsTags(request: Request):
    if request.headers.get('reject') is not None:
        if request.headers['reject'] != '':
            return accessRejected()

    userId = request.headers.get('userId')
    companyId = request.headers.get('companyId')
    Authorization = request.headers.get('Authorization')

    params = request.query_params
    all_tags = None

    if params is not None:
        if 'tag_id' in params:
            tag_id   = params['tag_id']
            all_tags = getDBSession() \
                .query(TicketTag) \
                .filter_by(id=tag_id) \
                .all()
        elif 'tag' in params:
            tag      = params['tag']
            all_tags = getDBSession() \
                .query(TicketTag) \
                .filter_by(title=tag) \
                .all()
        else:

            all_tags = getDBSession() \
                .query(TicketTag) \
                .all()
    return {
        "success": True,
        "message": 'all tags',
        "data"   : all_tags
    }
