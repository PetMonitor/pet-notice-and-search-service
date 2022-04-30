from urllib.error import HTTPError
import uuid
import requests
import json
import time
from http import HTTPStatus

from os import getenv
from datetime import datetime, timedelta
from src.main.constants import PostState

from flask_restful import Resource

DATABASE_SERVER_URL = getenv("DATABASE_SERVER_URL", "http://127.0.0.1:8000")
FACEBOOK_GRAPH_BASE_URL = getenv("FACEBOOK_GRAPH_BASE_URL", "https://graph.facebook.com/v13.0/")
FACEBOOK_BASE_URL = getenv("FACEBOOK_BASE_URL", "https://www.facebook.com/")
POST_DATE_DELETE_DELTA_DAYS = getenv("POST_DATE_DELETE_DELTA", "365")
GROUP_ID = getenv("GROUP_ID", "106287571429551")

DATE_FORMAT_STR = "%Y-%m-%dT%H:%M:%S+%f"

POST_TAG_TYPE = { 
    "#perdida" : PostState.LOST, 
    "#encontrada": PostState.FOUND,
    "#perdido" : PostState.LOST, 
    "#encontrado": PostState.FOUND  
}


class FacebookPostProcessor(Resource):

    def __init__(self):
        configFile = open('config/config.json')
        self.tokens = json.load(configFile)

    def get(self):
        self.processFacebookPosts()
        return "Successfully processed facebook posts", HTTPStatus.CREATED

    def processFacebookPosts(self):
        print("Processing facebook posts")
        
        # get feed
        petMonitorFeed = requests.get(FACEBOOK_GRAPH_BASE_URL + GROUP_ID + "/feed?access_token={}".format(self.tokens["fbUserAccessToken"]))

        if not petMonitorFeed:
            print("Attempt to retrieve Pet Monitor Facebook page feed failed. Facebook did not return response.")
            raise ValueError("Received no response from facebook page.")

        petMonitorFeed.raise_for_status()
        petMonitorFeed = petMonitorFeed.json()["data"]

        if (len(petMonitorFeed) == 0):
            print("Facebook did not return data for Pet Monitor feed.")
            return 

        # Reverse feed order, because we get newest posts first, by default.
        petMonitorFeed = petMonitorFeed[::-1]

        
        postIdsReqBody = { "postIds": [ post["id"] for post in petMonitorFeed ] }
        

        # Check if which messages have been processed before
        responseUnprocessedPosts = requests.post(DATABASE_SERVER_URL + "/facebook/posts/processed/filter", data=postIdsReqBody)
        responseUnprocessedPosts.raise_for_status()

        responseUnprocessedPosts = responseUnprocessedPosts.json()["postIds"]
        

        for post in petMonitorFeed:
            if post["id"] not in responseUnprocessedPosts:
                print("Skipping post {}. Already marked as processed.".format(post["id"]))
                continue

            if "story" in post.keys():
                print("Skipping post {}. Does not correspond to a user's post from the feed.".format(post["id"]))
                continue

            print("Processing post {} created at {}".format(post["id"], post["created_time"]))

            postMessage = post["message"]
            postMessageWords =  postMessage.split(" ")

            print("Processing post's content {} - {}".format(post["id"], postMessage))

            postType = None
            # Otherwise process message
            for hashtag in POST_TAG_TYPE.keys():
                if hashtag in postMessageWords:
                    postType = POST_TAG_TYPE[hashtag]
                    print("Processing message {}. Pet tagged as {} for this post.".format(post["id"], POST_TAG_TYPE[hashtag]))

            postAttachments = requests.get(FACEBOOK_GRAPH_BASE_URL + post["id"] + "/attachments?access_token={}".format(self.tokens["fbUserAccessToken"]))

            postAttachments = postAttachments.json()["data"]

            postImages = []

            if len(postAttachments) > 0:
                postAttachmentsData = postAttachments[0]

                if len(postAttachmentsData["subattachments"]["data"]) > 0:
                    for subattachment in postAttachmentsData["subattachments"]["data"]:
                        postImages.append(self.extractImage(subattachment))

                # when to include main attachment??
                # mainAttachmentImgSrc = self.extractImage(postAttachmentsData)

                # if mainAttachmentImgSrc not in postImages:
                #    postImages.append(mainAttachmentImgSrc)
                
            if len(postImages) == 0:
                print("Skipping post {} creation, because no image attachments were found.".format(postId))
                continue
            
            eventTimestamp = time.mktime(datetime.strptime(post["created_time"], DATE_FORMAT_STR).timetuple())

            petPost = {
                "uuid": str(uuid.uuid4()),
                "_ref": str(uuid.uuid4()),
                "postId": post["id"],
                "message": postMessage,
                "url": postAttachments[0]["url"],
                "type": str(postType),
                "eventTimestamp": eventTimestamp,
                "images": postImages,
            }


            responseCreatedPost = requests.post(DATABASE_SERVER_URL + "/facebook/posts", headers={'Content-Type': 'application/json'}, data=json.dumps(petPost))
            responseCreatedPost.raise_for_status()

            responseClosestPets = requests.get(DATABASE_SERVER_URL + "/pets/finder/facebook/posts/" + post["id"])
            # Request to get closest matches on fb page
            print("Closest matches for {} are {}".format(post["id"], str(responseClosestPets)))

            responseClosestPets.raise_for_status()
            closestPosts = responseClosestPets.json()["foundPosts"]

            if (len(closestPosts) == 0):
                print("No posts returned for post {}".format(post["id"]))
                continue


            predictedPostsResponse = "Encontramos estos posts con mascotas similares a la tuya: \n"
            newPredictionResponse = "Hay una nueva publicación con una mascota similar a la tuya: {}".format(petPost["url"])
            for closestPost in closestPosts:
                # Notify closest matches of this publication, also
                print("Notify closest match {} of this publication {}".format(closestPost, post))
                self.postReplyForComment(closestPost["postId"], newPredictionResponse)
                predictedPostsResponse += closestPost["url"] + "\n"

            # Submit response with closest matches for this post
            self.postReplyForComment(post["id"], predictedPostsResponse)
            print("Notify post {} of closest matches {}".format(post, predictedPostsResponse))
            
            
        
        delta = timedelta(days=int(POST_DATE_DELETE_DELTA_DAYS))
        beforeDate = str(datetime.today() - delta)
        self.deletePostsBeforeDate(beforeDate)

    def deletePostsBeforeDate(self, date):
        try:
            print("Deleting posts before date {}".format(str(date)))
            responseDeletedPosts = requests.delete(DATABASE_SERVER_URL + "/facebook/posts?beforeDate={}".format(str(date)))
            responseDeletedPosts.raise_for_status()
        except HTTPError as httpError:
            print("Attempting to delete facebook posts created before {} resulted in error {}".format(str(date), str(httpError)))


    def postReplyForComment(self, commentId, replyMessage):
        try:
            print("Posting reply for {}".format(commentId))
            requests.post(
                FACEBOOK_GRAPH_BASE_URL + commentId + "/comments?access_token={}".format(self.tokens["fbPageAccessToken"]),
                data={ "message": replyMessage }
            )
        except HTTPError as e:
            print(str(e))

    def extractImage(self, img):
        try:
            return { 
                "uuid": str(uuid.uuid4()),
                "src" : img["media"]["image"]["src"], 
                "photoId": img["target"]["id"], 
                "url": img["target"]["url"]  
            }
        except KeyError as e:
            print(str(e))
            return None


