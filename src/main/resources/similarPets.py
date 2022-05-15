import requests
from http import HTTPStatus
from datetime import datetime, timedelta

from src.main.constants import DATABASE_SERVER_URL
from src.main.resources.notice import Notices

from flask_restful import request, Resource
from apscheduler.schedulers.background import BackgroundScheduler

MAX_NOTICE_SEARCH_ALERT_DAYS = 10

# Uncomment to get detailed logging for scheduler
# import logging
# logging.basicConfig()
# logging.getLogger('apscheduler').setLevel(logging.DEBUG)

searchScheduler = BackgroundScheduler()
searchScheduler.start()

class SimilarPets(Resource):
    """
    Similar pet search resource.
    """

    def get(self, noticeId):
        """
        Retrieves the pets which are near in terms of similarity to the one provided.
        """
        try:
            closestMatchesURL = DATABASE_SERVER_URL + "/pets/finder/" + noticeId
            print("Issue GET to " + closestMatchesURL)
            response = requests.get(closestMatchesURL)
            
            response.raise_for_status()
            response = response.json()

            closestNotices = response["closestMatches"]

            if len(closestNotices) <= 0:
                return "No matches found!", HTTPStatus.NOT_FOUND
            
            
            print("Got {} closest matches for notice {}".format(len(closestNotices), noticeId))

            noticesRes = Notices()
            return [ noticesRes.get(noticeId)[0] for noticeId in closestNotices ], HTTPStatus.OK

        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR  

class SimilarPetsAlerts(Resource):

    def post(self):
        """
        Schedules a new job to search for similar notices.
        If an alert has already been created for the provided user id, 
        it will be replaced.
        :noticeId the notice for which the alert will be created.
        :userId the user to whom the notice belongs.
        """
        try:
            newAlertData = request.get_json()

            noticeId = newAlertData["noticeId"]
            userId = newAlertData["userId"] 
            jobName = userId + "_noticeSearch"

            for job in searchScheduler.get_jobs():
                if job.name == jobName:
                    print("Removing job id: {} name: {}, and replacing with new alert.".format(job.id, job.name))
                    searchScheduler.remove_job(job.id)


            alertEndDateTime = datetime.now() + timedelta(days=MAX_NOTICE_SEARCH_ALERT_DAYS)
            alertEndDate = datetime.date(alertEndDateTime)

            print("Schedule alert for similar notice search for user {} and notice {}. Scheduled to end on {}".format(userId, noticeId, str(alertEndDate)))

            searchScheduler.add_job(SimilarPetsAlerts().searchSimilarNoticesAndNotify, args=[ noticeId ], trigger='cron', hour='*/2', minute=0, second=0, end_date=alertEndDate, name=jobName)
            return "OK", HTTPStatus.OK
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR  
    


    def searchSimilarNoticesAndNotify(self, noticeId):
        """
        Retrieves the pets which are near in terms of similarity to the one provided.
        """
        try:
            print("Looking for closest matches for {}".format(noticeId))
            
            closestMatchesURL = DATABASE_SERVER_URL + "/pets/finder/" + noticeId
            print("Issue GET to " + closestMatchesURL)
            response = requests.get(closestMatchesURL)
            
            response.raise_for_status()
            response = response.json()

            closestNotices = response["closestMatches"]

            if len(closestNotices) <= 0:
                return
            

            noticesRes = Notices()
            

            # TODO: send notification with result
            # [ noticesRes.get(noticeId)[0] for noticeId in closestNotices ]
            return

        except Exception as e:
            print("ERROR {}".format(e))


    def get(self):
        """
        Returns all scheduled alerts
        """
        
        try:
            scheduledJobs = []
            for job in searchScheduler.get_jobs():
                jobInfo = {
                    "id": job.id,
                    "name": job.name,
                    #"nextRunTime": job.next_run_time,
                }
                scheduledJobs.append(jobInfo)

            print("Scheduled alerts {}".format(str(scheduledJobs)))
            return { "jobs": scheduledJobs }, HTTPStatus.OK
        except Exception as e:
            print("ERROR {}".format(e))
            return str(e), HTTPStatus.INTERNAL_SERVER_ERROR  
