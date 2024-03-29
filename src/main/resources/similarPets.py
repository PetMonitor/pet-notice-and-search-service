import requests
from http import HTTPStatus
from datetime import datetime
from src.main.resources.notice import Notice

from flask_restful import request, Resource
from apscheduler.schedulers.background import BackgroundScheduler

from src.main.constants import DATABASE_SERVER_URL

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
            closestMatchesURL = DATABASE_SERVER_URL + "/pets/finder/" + noticeId + "?" + request.query_string.decode("utf-8")
            print("Issue GET to " + closestMatchesURL)
            response = requests.get(closestMatchesURL)
            
            response.raise_for_status()
            response = response.json()

            closestNotices = response["closestMatches"]

            if len(closestNotices) <= 0:
                return "No matches found!", HTTPStatus.NOT_FOUND
            
            
            print("Got {} closest matches for notice {}".format(closestNotices, noticeId))

            noticesRes = Notice()
            return [ noticesRes.get(closestNoticeId)[0] for closestNoticeId in closestNotices ], HTTPStatus.OK

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
            alertFrequency = newAlertData["alertFrequency"]
            alertLimitDate = newAlertData["alertLimitDate"] 
            alertLocation = newAlertData["location"]
            jobName = self.getJobName(userId)

            print("Received request to create alert! {}".format(str(newAlertData)))

            for job in searchScheduler.get_jobs():
                if job.name == jobName:
                    print("Removing job id: {} name: {}, and replacing with new alert.".format(job.id, job.name))
                    searchScheduler.remove_job(job.id)

            alertEndDate = datetime.strptime(alertLimitDate, "%Y-%m-%d")
            alertFreqExp = "*/{}".format(alertFrequency)
            
            searchScheduler.add_job(SimilarPetsAlerts().searchSimilarNoticesAndNotify, args=[ userId, noticeId, alertLocation ], trigger='cron', hour=alertFreqExp, minute=0, second=0, end_date=alertEndDate, name=jobName)
            return "OK", HTTPStatus.CREATED
        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR  
    
    def delete(self):
        try:
            requestData = request.get_json()

            userId = requestData["userId"] 
            jobName = self.getJobName(userId)

            for job in searchScheduler.get_jobs():
                print("JOB {}".format(job.name))
                if job.name == jobName:
                    print("Removing job id: {} name: {}, and replacing with new alert.".format(job.id, job.name))
                    searchScheduler.remove_job(job.id)

            return "OK", HTTPStatus.CREATED

        except Exception as e:
            print("ERROR {}".format(e))
            return e, HTTPStatus.INTERNAL_SERVER_ERROR  

    def getJobName(self, userId):
        return userId + "_noticeSearch"

    def searchSimilarNoticesAndNotify(self, userId, noticeId, location):
        """
        Retrieves the pets which are near in terms of similarity to the one provided.
        """
        try:
            print("Looking for closest matches for {}".format(noticeId))
            
            closestMatchesURL = DATABASE_SERVER_URL + "/pets/finder/" + noticeId + "?region=" + location
            print("Issue GET to " + closestMatchesURL)
            response = requests.get(closestMatchesURL)
            
            response.raise_for_status()
            closestMatchesResponse = response.json()

            closestNotices = closestMatchesResponse["closestMatches"]

            if len(closestNotices) <= 0:
                print("Running scheduled search for notice with id {}".format(noticeId))
                return closestMatchesResponse
            
            closestMatchesNotificationsURL = DATABASE_SERVER_URL + "/notifications/notices/closestMatches"
            print("Issue POST to " + closestMatchesNotificationsURL)

            notificationData = {
                "userId": userId,
                "noticeId": noticeId,
                "closestMatches": closestNotices
            }
            response = requests.post(closestMatchesNotificationsURL, notificationData)
            
            response.raise_for_status()

            return closestMatchesResponse

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


class SimilarPetsAlertsManual(Resource):

    def post(self):
        try:
            print("Run all alerts manually")
            refreshed = []
            for job in searchScheduler.get_jobs():
                searchScheduler.get_job(job_id = job.id).modify(next_run_time=datetime.now())
                refreshed.append(job.id)
            return {'number': len(searchScheduler.get_jobs()), 'list': refreshed}, HTTPStatus.OK
        except Exception as e:
            print("ERROR {}".format(e))
            return str(e), HTTPStatus.INTERNAL_SERVER_ERROR         