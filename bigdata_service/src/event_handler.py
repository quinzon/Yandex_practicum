from bigdata_service.src.kafka import kafka_producer
from bigdata_service.src.utils import Constants


async def process_event(event_type: str, user_id: str, payload: dict) -> dict:
    await kafka_producer.start()
    await kafka_producer.send_event(event_type=event_type, user_id=user_id, payload=payload)
    return {'status': Constants.STATUS_SUCCESS, 'event_type': event_type}
