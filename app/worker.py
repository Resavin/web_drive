import pika
from app.logger import logger
from PIL import Image

connection = pika.BlockingConnection(
    pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)


def callback(ch, method, properties, body):
    path = body.decode()
    logger.debug(f" [x] Received {path}")
    try:
        img = Image.open(path)
        img = img.rotate(45)
        img.save(path)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.debug(" [x] Done")
    except Exception:
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        logger.debug(" [x] Image operation failed")


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue',
                      on_message_callback=callback)

logger.debug(' [*] Waiting for messages.')
channel.start_consuming()
