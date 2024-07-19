import pika
from PIL import Image
from app.logger import logger


def on_request(ch, method, props, body):
    path = body.decode()
    logger.debug(f" [x] Received {path}")
    try:
        img = Image.open(path)
        img = img.rotate(45)
        img.save(path)
        response = "Image processing succeeded"
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.debug(" [x] Done")
    except Exception as e:
        response = "Image processing failed"
        ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
        logger.debug(f" [x] Image operation failed: {e}")

    ch.basic_publish(
        exchange="",
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=response,
    )


task_queue = "task_queue"

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()
channel.queue_declare(queue=task_queue, durable=True)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=task_queue, on_message_callback=on_request)

logger.debug(" [*] Waiting for messages.")
channel.start_consuming()
