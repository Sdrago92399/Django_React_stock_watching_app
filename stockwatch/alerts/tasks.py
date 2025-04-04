from celery import shared_task
from .services import AlertService

@shared_task
def check_and_process_alerts():
    """Task to check and process alerts - to be run periodically"""
    alert_service = AlertService()
    alert_service.process_alerts()