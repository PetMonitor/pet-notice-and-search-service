from http import HTTPStatus
from src.main.app import app
from src.main.facebook.facebookService import FacebookPostProcessor

from src.main.constants import DATABASE_SERVER_URL, FACEBOOK_GRAPH_BASE_URL, GROUP_ID
from mock import patch


TEST_FACEBOOK_RESPONSE = {
    "data": [
        {
            "created_time": "2022-04-28T00:17:17+0000",
            "message": "Encontramos perrita perdida!! #encontrada",
            "story": "PetMonitor está en Belgrano.",
            "id": "106287571429551_368289751895997"
        },
        {
            "created_time": "2022-04-25T03:19:49+0000",
            "message": "Encontramos perro adulto perdido en parque Regatas!! Por favor difundir!! #encontrado",
            "story": "PetMonitor está en Argentina.",
            "id": "106287571429551_366554608736178"
        },
        {
            "created_time": "2022-04-24T16:19:06+0000",
            "message": "Perdimos a Maximus! Se perdió ayer por la tarde en parque las heras, por favor, lo queremos de nuevo en casa!! 🐶 🏠",
            "id": "106287571429551_366299775428328"
        },
        {
            "created_time": "2022-04-24T15:42:18+0000",
            "message": "Perrito encontrado!! Hoy al mediodía en bosques de palermo, no tiene collar!! Está bien alimentado, así que parece haberse perdido. Por favor, ayúdenos a encontrar a su familia!!",
            "story": "PetMonitor está en Belgrano.",
            "id": "106287571429551_366280065430299"
        }
    ],
    "paging": {
        "cursors": {
            "before": "QVFIUi1heEcwQ2JYY1V6dWtRNF9MWmJOTkstLTdLdFQ0R1h5TU5tQ2JNbWdUYlBwN2dlTEhOeHlBVFE2TG1yTUxySE5QbS1DZAFdRb2FnTWwweDM3OEtrcDRtOTRVQTdIZA0JIMndjTG4tcnVLVHJtcTdlLU1EUGkyaE16RnF2aE9jb0dJS0pOUWZAhUEhSSEZAyT21LSkdteE81UE9WT1JubGRsejJTOVJ2bEdhSDdZAYTNwRlA1Vi0zSGV1RGhROXVoTlZANawZDZD",
            "after": "QVFIUjNpNkJ5REtTTGxqTE5RMl9qY0J3anZAFR2RqRDNMSVBWaFZAwQ25sRXJ3Nm5qekJKV29Ed01oOFdiSF93UWZAsRzdXSk9rdjFZAVmZAGSDhqTm5TdnJKLTZAEcmNqR3lnN1k3amZAqSlhKUTgwVDk1WDVJNkRrSl9OcnFCTEgtY2JQVTdVQ2hmR3pUdVIydHhsdWE4WTQzRjBVOGU3R2U3MmZA3YmVWdGdiYUtMS1U1NzBNWVNpa1VaMGRSd0xseklNM0ZA0OAZDZD"
        }
    }
}



class FakeGet(object):
    def __init__(self, url, headers={}):
        self.url = url
        self.headers = headers
        self.status_code = 0

        if (self.url.startswith(FACEBOOK_GRAPH_BASE_URL + GROUP_ID + "/feed")):
            self.status_code = 200
            self.response = TEST_FACEBOOK_RESPONSE
        elif (self.url.startswith(FACEBOOK_GRAPH_BASE_URL  + "106287571429551_368289751895997/attachments")):
            self.status_code = 200
            self.response = { "data": {} }
        elif (self.url.startswith(FACEBOOK_GRAPH_BASE_URL +  "106287571429551_366554608736178/attachments")):
            self.status_code = 200
            self.response = { 
                "data": [{ 
                  "url": "http://imgurl",  
                  "subattachments": { 
                    "data": [{
                      "media": { "image": { "src": "http://imgsource" } },
                      "target": { "id": "123123123", "url": "http://imgurl" }
                    }] 
                  }
                }]
            }
        elif (self.url.startswith(DATABASE_SERVER_URL + "/pets/finder/facebook/posts/106287571429551_366554608736178")):
            self.status_code = 200
            self.response = { "foundPosts": [ {"postId": "106287571429551_366280065430299", "url": "http://posturl"} ], "foundPostsFromRegion": [{"postId": "106287571429551_366299775428328", "url": "http://posturl"} ] }
        else:
            self.status_code = 404
            self.response = { "error": "test route not found" }     

    def json(self):
        return self.response
    
    def raise_for_status(self):
        return

    def response(self):
        return self.response

class FakePost(object):
    def __init__(self, url, headers={}, data=''):
        self.url = url
        self.db = DATABASE_SERVER_URL
        self.data = data
        self.status_code = 0

        if (self.url == DATABASE_SERVER_URL + "/facebook/posts/processed/filter"):
            self.status_code = HTTPStatus.CREATED
            self.response = { "postIds": [ "106287571429551_368289751895997", "106287571429551_366554608736178" ] }
        elif (self.url.startswith(DATABASE_SERVER_URL + "/facebook/posts")):
            self.status_code = HTTPStatus.CREATED
            self.response = { "message": "OK" }
        elif (self.url.startswith(FACEBOOK_GRAPH_BASE_URL  + "106287571429551_368289751895997/comments")):
            self.status_code = HTTPStatus.CREATED
            self.response = { "message": "OK" }
        else:
            self.response = { "code" : 404, "message" : "Not Found" }

    def json(self):
        return self.response       

    def raise_for_status(self):
        if self.status_code != HTTPStatus.CREATED:
            raise ValueError("Database mock server returned error {}".format(self.status_code))

class FakeDelete(object):
	def __init__(self, url, headers={}):
		self.url = url
		self.db = DATABASE_SERVER_URL
		self.status_code = 0

		if (self.url.startswith(DATABASE_SERVER_URL + "/facebook/posts")):
			self.status_code = 200
			self.response = { "code" : self.status_code, "deletedCount": 1 }         
		else:
			self.response = { "code" : 404, "message" : "Not Found" }

	def json(self):
		return self.response 
           
	def raise_for_status(self):
		if self.status_code != HTTPStatus.OK:
			raise ValueError("Database mock server returned error {}".format(self.status_code))


class TestFacebookService(object):

    @patch("src.main.resources.user.requests.get", side_effect=FakeGet)
    @patch("src.main.resources.user.requests.post", side_effect=FakePost)
    @patch("src.main.resources.user.requests.delete", side_effect=FakeDelete)
    def test_get_processes_facebook_posts(self, fake_get, fake_post, fake_delete):
        response = app.test_client().get('/api/v0/facebook')
        assert response.status_code == HTTPStatus.CREATED
