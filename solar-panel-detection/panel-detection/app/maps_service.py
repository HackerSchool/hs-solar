import requests
from io import BytesIO


class MapsService:
    def __init__(self, api_key: str):
        if api_key == "":
            raise KeyError("Missing Google Cloud API Key")
        self.__api_key = api_key

    def get_image(self, lat: float, long: float) -> BytesIO:
        r = requests.get(
            f"https://maps.googleapis.com/maps/api/staticmap?center={lat},{long}&zoom=20&size=416x416&maptype=satellite&key={self.__api_key}"
        )
        r.raise_for_status()

        content_type = r.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            raise ValueError(
                f"Expected image from Google Maps response, got '{content_type}'"
            )

        return BytesIO(r.content)
