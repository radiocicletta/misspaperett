from accreditations.models import Message


def create_message(msg):

    message = Message()
    message.headers = msg.to_string()
    if msg.content_type.is_singlepart():
        message.body = msg.body
        message.content_type = msg.content_type[0]
    elif msg.content_type.is_multipart():
        for part in msg.parts:
            message.body = part.body
            message.content_type = part.content_type[0]
            if part.content_type.sub == "html":
                break

    message.message_id = msg.headers["message-id"]
    return message
