from fastapi import APIRouter, Request
import time
import os
import requests
from dotenv import load_dotenv
import uuid

from sqlalchemy import update, text

from databases.models import TicketTag, getDBSession, TicketTicketTags, runRawSQLBindings
from utils.utils import accessRejectedContent, accessRejected

load_dotenv()
router = APIRouter(
    prefix="/api/v1/secured/ticket/ticket/tags",
    tags=[],
    responses={404: accessRejectedContent, 400: accessRejectedContent},
)


@router.get("/")
async def rootq():
    return {
        "success": True,
        "message": "tickets tags are working"
    }


def get_ticket_tags(ticketId):
    tags = runRawSQLBindings(""" 
	SELECT ticketTicketTags.id ,ticketTicketTags.ticketTagId  ,ticketsTags.title AS tag
	FROM ticketTicketTags 
	JOIN ticketsTags ON ticketsTags.id = ticketTicketTags.ticketTagId
	WHERE ticketTicketTags.ticketId = %(ticketId)s 
	""", {
        "ticketId": ticketId
    })
    tagss = []
    for row in tags:
        tagss.append({
            'tag': row.tag,
            'tagId': row.ticketTagId,
            'ticketTicketTagsId': row.id,
        })
    return tagss


def saveTicketTagDetails(ticketId, ticketTagId, ticketTagTitle):
    save_result = TicketTicketTags(ticketId=ticketId, ticketTagId=ticketTagId, ticketTagTitle=ticketTagTitle)
    session = getDBSession()
    session.add(save_result)
    session.commit()
    return {
        "success": True,
        "message": "tickets tagged"
    }
