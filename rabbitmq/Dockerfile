FROM rabbitmq:3.11-management

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN curl -L -o /opt/rabbitmq/plugins/rabbitmq_delayed_message_exchange-3.11.1.ez \
    https://github.com/rabbitmq/rabbitmq-delayed-message-exchange/releases/download/3.11.1/rabbitmq_delayed_message_exchange-3.11.1.ez \
    && rabbitmq-plugins enable rabbitmq_delayed_message_exchange
