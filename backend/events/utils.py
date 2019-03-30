from flask import current_app
import requests


def get_metadata(nasa_id):
    request_response = requests.get(current_app.config['BASE_URL'] + current_app.config['META_DATA_URL'] + nasa_id)
    metadata_json = requests.get(request_response.json()['location'])
    metadata = metadata_json.json()
    return metadata


def get_media(nasa_id):
    request_response = requests.get(current_app.config['BASE_URL'] + current_app.config['MEDIA_DATA_URL'] + nasa_id)
    image_data = request_response.json()
    return image_data
