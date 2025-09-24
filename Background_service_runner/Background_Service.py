import time
import threading
import logging
from datetime import datetime

class BackgroundRunner:
    def __init__(self, interval_seconds, target_function, *args, **kwargs):
        self.interval = interval_seconds
        self.target_function = target_function
        self.args = args
        self.kwargs = kwargs
        self._stop_event = threading.Event()
        self.thread = None
        self.is_running = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _run(self):
        self.logger.info(f"Background runner started at {datetime.now()}")
        while not self._stop_event.is_set():
            try:
                self.logger.info(f"Executing {self.target_function.__name__} at {datetime.now()}")
                self.target_function(*self.args, **self.kwargs)
            except Exception as e:
                self.logger.error(f"Error in background task: {e}")
            
            # Wait for interval or stop signal
            self._stop_event.wait(self.interval)

    def start(self):
        if not self.is_running:
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            self.is_running = True
            self.logger.info("Background runner started")

    def stop(self):
        if self.is_running:
            self._stop_event.set()
            self.thread.join()
            self.is_running = False
            self.logger.info("Background runner stopped")

# Example log processing functions
def fetch_logs(a):
    print(f"Fetching logs at {datetime.now()}",a)
    # Your log fetching logic here

def process_logs():
    print(f"Processing logs at {datetime.now()}")
    # Your log processing logic here

def classify_logs():
    print(f"Classifying logs at {datetime.now()}")
    # Your log classification logic here

# Usage
if __name__ == "__main__":
    # Run log fetching every 3 seconds
    fetch_runner = BackgroundRunner(3, fetch_logs,2)
    
    # Run log processing every 6 seconds
    process_runner = BackgroundRunner(6, process_logs)
    
    # Run log classification every 12 seconds
    classify_runner = BackgroundRunner(12, classify_logs)
    
    # Start all runners
    fetch_runner.start()
    process_runner.start()
    classify_runner.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all runners...")
        fetch_runner.stop()
        process_runner.stop()
        classify_runner.stop()
