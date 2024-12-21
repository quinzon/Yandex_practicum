from abc import ABC, abstractmethod


class AbstractTopicConsumer(ABC):
    @property
    @abstractmethod
    def topic_name(self):
        pass

    @property
    @abstractmethod
    def table_name(self):
        pass

    @property
    @abstractmethod
    def fields(self):
        pass

    @abstractmethod
    def process_message(self, event_data):
        pass

    @abstractmethod
    def create_table_query(self):
        pass
