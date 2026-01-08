"""
Centrifugo client для отправки сообщений через HTTP API
"""
import requests
import json
from django.conf import settings


def publish_to_centrifugo(channel, data):
    """
    Отправляет сообщение в канал Centrifugo
    
    Args:
        channel: название канала (например, 'question:33')
        data: данные для отправки (словарь)
    
    Returns:
        bool: True если успешно, False в противном случае
    """
    try:
        url = f"{settings.CENTRIFUGO_URL}/api"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'apikey {settings.CENTRIFUGO_API_KEY}'
        }
        payload = {
            'method': 'publish',
            'params': {
                'channel': channel,
                'data': data
            }
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        return False
