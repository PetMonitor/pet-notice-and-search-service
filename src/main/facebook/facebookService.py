import uuid
import requests
import json
import time
from http import HTTPStatus
from urllib.error import HTTPError
from datetime import datetime, timedelta
from src.main.constants import PostState, DATABASE_SERVER_URL, FACEBOOK_GRAPH_BASE_URL, POST_DATE_DELETE_DELTA_DAYS, GROUP_ID, FB_PAGE_ACCESS_TOKEN, FB_USER_ACCESS_TOKEN

from flask_restful import Resource

from apscheduler.schedulers.background import BackgroundScheduler


DATE_FORMAT_STR = "%Y-%m-%dT%H:%M:%S+%f"

POST_TAG_TYPE = {
    "#perdida": PostState.LOST,
    "#encontrada": PostState.FOUND,
    "#perdido": PostState.LOST,
    "#encontrado": PostState.FOUND  
}


class FacebookPostProcessor(Resource):

    def get(self):
        self.processFacebookPosts()
        return "Successfully processed facebook posts", HTTPStatus.CREATED

    def processFacebookPosts(self):
        print("Processing facebook posts")

        # get feed
        petMonitorFeed = requests.get(FACEBOOK_GRAPH_BASE_URL + GROUP_ID + "/feed?fields=place,message&access_token={}".format(FB_USER_ACCESS_TOKEN))

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
            postMessageWords = postMessage.split(" ")

            print("Processing post's content {} - {}".format(post["id"], postMessage))

            postType = None
            # Otherwise process message
            for word in postMessageWords.lower():
                if word in POST_TAG_TYPE:
                    postType = POST_TAG_TYPE[word]
                    print("Processing message {}. Pet tagged as {} for this post.".format(post["id"], POST_TAG_TYPE[word]))

            postAttachments = requests.get(FACEBOOK_GRAPH_BASE_URL + post["id"] + "/attachments?access_token={}".format(FB_USER_ACCESS_TOKEN))

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
                print("Skipping post {} creation, because no image attachments were found.")
                continue
            
            eventTimestamp = time.mktime(datetime.strptime(post["created_time"], DATE_FORMAT_STR).timetuple())
            place = post["place"]
            if place and ("location" in place) and ("city" in place["location"]):
                postLocation = place["location"]["city"]
            else:
                postLocation = None

            petPost = {
                "uuid": str(uuid.uuid4()),
                "_ref": str(uuid.uuid4()),
                "postId": post["id"],
                "message": postMessage,
                "url": postAttachments[0]["url"],
                "type": str(postType),
                "eventTimestamp": eventTimestamp,
                "images": postImages,
                "location": postLocation
            }

            responseCreatedPost = requests.post(DATABASE_SERVER_URL + "/facebook/posts", headers={'Content-Type': 'application/json'}, data=json.dumps(petPost))
            responseCreatedPost.raise_for_status()

            regionFilter = "?region=" + postLocation if postLocation else ""
            responseClosestPets = requests.get(DATABASE_SERVER_URL + "/pets/finder/facebook/posts/" + post["id"] + regionFilter)
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
                FACEBOOK_GRAPH_BASE_URL + commentId + "/comments?access_token={}".format(FB_PAGE_ACCESS_TOKEN),
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


sched = BackgroundScheduler()
facebookProcessor = FacebookPostProcessor()

try:
    print("Scheduling task facebook processor...")
    sched.add_job(facebookProcessor.processFacebookPosts, 'interval', hours=24)
    sched.start()
except (KeyboardInterrupt, SystemExit):
    sched.shutdown()
