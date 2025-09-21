import json
import os
import time
from kafka import KafkaProducer
# from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler

TOPIC = os.getenv("KAFKA_TOPIC", "customer_conversation")
DIRECTORY = "/app/data"

producer = KafkaProducer(
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092"),
    max_request_size=int(os.getenv("KAFKA_MAX_MESSAGE_SIZE")),
    value_serializer=lambda v: v.encode("utf-8"),
)

class FileHandler(FileSystemEventHandler):
    def process_file(self, path):
        filename = os.path.basename(path)
        print(f"Processing file: {filename}")
        try:
            with open(path, "r") as f:
                # print(f.read())
                data = f.read()

                producer.send(TOPIC, value=data)
                print(f"Sent file {filename}")
            producer.flush()
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    def on_created(self, event):
        print(f"Created file {event.src_path}, {event.is_directory}")
        if not event.is_directory:
            self.process_file(event.src_path)

if __name__ == "__main__":
    print(f"Watching directory {DIRECTORY} for new files...")
    os.makedirs(DIRECTORY, exist_ok=True)

    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, DIRECTORY, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
