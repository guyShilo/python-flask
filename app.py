from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
# setting the env to development
ENV = "dev"

# for future connection to another database on deployment
if ENV == "dev":
    app.debug = True
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://postgres:<PASSWORD>@localhost/test"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = ""
    app.debug = False

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class DataTest(db.Model):
    # Defining the model and the columns
    __tablename__ = "testing"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(100))

    # def __init__(self, name, description):
    #     self.name = name
    #     self.description = description


def handleData(stringParam, isList):
    # initiating an empty list
    listToClient = []

    def dataToObjects(list):
        # this function recieves a list from the sql server and generates a new list
        # it has to be done because sql alchemy classes has to be "serialized"
        # before they can be sent in JSON
        return [
            {"id": item.id, "name": item.name, "description": item.description}
            for item in list
        ]

    # I want this function to build both lists and dicts,
    # so if this is true, build me a list, otherwide, a dict
    if isList is True:
        # setting listToClient to the new extracted list
        listToClient.append(dataToObjects(stringParam))
        # returning it to the client
        return listToClient
    else:
        # extracting the data and building the dict
        objectToClient = {
            "id": stringParam.id,
            "name": stringParam.name,
            "description": stringParam.description,
        }
        # returning it to the client
        return objectToClient
        # if a boolean wasnt given as parameter, return the list as string.
    return str(stringParam)


def handleRequest():
    if method == "POST":
        print("request is post")
        # loads the data from the request and extracting name and description
        requestData = json.loads(request.data)
        name = requestData["name"]
        description = requestData["description"]


def returnRouteError(route, requestMethod, requestData):
    print(route, requestMethod, requestData)
    return """
        It appears you are trying to use {route} method, but you have a problem.
        The method you use is {requestMethod}.
        The data you sent is {requestData}
        """


@app.route("/", methods=["GET"])
# Defining the route, and the method.
def getData():
    if request.method == "GET":
        # if the length is not falsy, it searches by id, otherwise continue
        if len(request.args):
            parameters = request.args.to_dict()
            getByID = db.session.query(DataTest).filter_by(id=parameters["id"]).first()
            getOne = handleData(getByID, isList=False)
            return f"This is the data you queried: {json.dumps(getOne)}"
        # Queries all the data and returning it to the client
        try:
            query = DataTest.query.all()
            List = handleData(query, isList=True)
            return f"This is the data you queried: {json.dumps(List)}"
        except Exception as error:
            return str(error)

    return returnRouteError("Get", request.method, request.data)


@app.route("/", methods=["POST"])
# Defining the route, and the method.
def postData():
    if request.method == "POST":
        print("request is post")
        # loads the data from the request and extracting name and description
        requestData = json.loads(request.data)
        name = requestData["name"]
        description = requestData["description"]
        try:
            print("try")
            # if its an empty string, return an error
            if name == "" or description == "":
                print("empty string")
                return "There is a problem with your request"
            # if the name does not exist, register it.
            if db.session.query(DataTest).filter(DataTest.name == name).count() == 0:
                print("adding new one")
                dataToPost = DataTest(name=name, description=description)
                db.session.add(dataToPost)
                db.session.commit()
                # send success message to user
                return f"New data posted: {json.dumps(requestData)}"
        except Exception as error:
            print(error)
            return str(error)
    else:
        print("wrong method")
        return returnRouteError(
            route="Post", requestMethod=request.method, requestData=request.data
        )


@app.route("/", methods=["PUT"])
# Defining the route, and the method.
def updateData():
    if request.method == "PUT":
        try:
            # if the length is not falsy, it searches by id, otherwise continue
            if len(request.args):
                # converting the object to dict and extracting the id;
                parameters = request.args.to_dict()
                parameterID = parameters["id"]
                requestData = json.loads(request.data)
                # filtering by id and updates the data.
                db.session.query(DataTest).filter_by(id=parameterID).update(requestData)
                db.session.commit()
                # send success message to user
                return f"You updated {json.dumps(requestData)}"
            else:
                # if the data is empty
                return "You want to update the data, but there is no \
                arguments"
        except Exception as error:
            return str(error)
    else:
        return returnRouteError("Put", request.method, request.data)


@app.route("/", methods=["DELETE"])
# Defining the route, and the method.
def deleteData():
    if request.method == "DELETE":
        try:
            # if the length is not falsy, it searches by id, otherwise continue
            if len(request.args):
                # converting the object to dict and extracting the id;
                parameters = request.args.to_dict()
                parameterID = parameters["id"]
                # filtering by id and returns the current query.
                toBeDeleted = db.session.query(DataTest).filter_by(id=parameterID).one()
                # converting the query to readable data
                toClient = handleData(toBeDeleted, isList=False)
                # deleting the row
                db.session.delete(toBeDeleted)
                db.session.commit()
                # send success message to user
                return f"You deleted {json.dumps(toClient)}"
            else:
                return "You want to delte the data, but there is not arguments"

        except Exception as error:
            return str(error)
        return returnRouteError("Delete", request.method, request.data)


if __name__ == "__main__":
    app.run()
