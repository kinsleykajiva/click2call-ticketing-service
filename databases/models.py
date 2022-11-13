import sqlalchemy
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import DateTime, func, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
import os
import logging
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

engine = sqlalchemy.create_engine(
    "mysql+mysqldb://" + os.getenv('DB_USERNAME') + ":" + os.getenv('DB_PASSWORD') + "@" + os.getenv(
        'DB_HOST') + ":3306/" + os.getenv('DB_NAME'), pool_recycle=3600, echo=True)

Base = declarative_base()


# https://docs.sqlalchemy.org/en/14/orm/session_basics.html#querying-1-x-style

class Tickets(Base):
    __tablename__   = "tickets"
    id              = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    title           = sqlalchemy.Column(sqlalchemy.String(255), index=True, nullable=True)
    statusId        = sqlalchemy.Column(sqlalchemy.INTEGER, ForeignKey('ticketStatuses.id'))
    companyId       = sqlalchemy.Column(sqlalchemy.INTEGER)
    priorityId      = sqlalchemy.Column(sqlalchemy.INTEGER, ForeignKey("ticketPriorities.id"))
    createdByUserId = sqlalchemy.Column(sqlalchemy.INTEGER)
    dateCreated     = sqlalchemy.Column(DateTime(timezone=True), default=func.now())


class TicketStatuses(Base):
    __tablename__ = "ticketStatuses"
    id            = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    title         = sqlalchemy.Column(sqlalchemy.String(255), index=True, nullable=False)


class TicketLifeCycle(Base):
    __tablename__ = "ticketLifeCycle"
    id            = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    oldStatusId   = sqlalchemy.Column(sqlalchemy.Integer)
    newStatusId   = sqlalchemy.Column(sqlalchemy.Integer)
    savedByUserId = sqlalchemy.Column(sqlalchemy.Integer)
    ticketId      = sqlalchemy.Column(sqlalchemy.Integer)
    dateCreated   = sqlalchemy.Column(DateTime(timezone=True), default=func.now())


class TicketHandlers(Base):
    __tablename__ = "ticketHandlers"
    id            = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    userId        = sqlalchemy.Column(sqlalchemy.Integer)
    ticketId      = sqlalchemy.Column(sqlalchemy.Integer)
    savedByUserId = sqlalchemy.Column(sqlalchemy.Integer)
    dateCreated   = sqlalchemy.Column(DateTime(timezone=True), default=func.now())


class TicketTag(Base):
    __tablename__ = "ticketsTags"
    id            = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    title         = sqlalchemy.Column(sqlalchemy.String)


class TicketPriorities(Base):
    __tablename__ = "ticketPriorities"
    id            = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    title         = sqlalchemy.Column(sqlalchemy.String)


class TicketTicketTags(Base):
    __tablename__  = "ticketTicketTags"
    id             = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    ticketId       = sqlalchemy.Column(sqlalchemy.Integer)
    ticketTagId    = sqlalchemy.Column(sqlalchemy.Integer)
    ticketTagTitle = sqlalchemy.Column(sqlalchemy.String)


class TicketHandlersTracking(Base):
    __tablename__    = "ticketHandlersTracking"
    id               = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True, index=True, nullable=False)
    assignedToUserId = sqlalchemy.Column(sqlalchemy.Integer)
    assignedByUserId = sqlalchemy.Column(sqlalchemy.Integer)
    ticketId         = sqlalchemy.Column(sqlalchemy.Integer)
    dateCreated      = sqlalchemy.Column(DateTime(timezone=True), default=func.now())


def getDBSession():
    Session = sqlalchemy.orm.sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    print('Loading session')
    return session


def runRawSQL(sqlStatement):
    try:
        conx = engine.connect()
        return conx.execute(text(sqlStatement))
    except Exception as e:
        print(e)
        return None


def runRawSQLBindings(sqlStatement, params):
    try:
        conx = engine.connect()
        return conx.exec_driver_sql(sqlStatement, params)
    except Exception as e:
        print(e)
        return None


logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
