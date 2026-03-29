from livekit.api import AccessToken
from livekit.api import VideoGrants

API_KEY = "APIrw5rrYuUcQ8x"
API_SECRET = "4wR3IfH5Yn1zFQ3VTRq7uF261mKl7H2o6tGIemt8kMt"

token = AccessToken(API_KEY, API_SECRET)
token.with_identity("assistant-user")
token.with_name("Assistant")
token.with_grants(VideoGrants(room_join=True, room="assistant-room"))

print(token.to_jwt())
