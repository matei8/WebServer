"""
Thread pool implementation for handling concurrent tasks.
"""

import json
import threading
from queue import Queue, Empty
from threading import Thread, Lock
import os
import multiprocessing
import logging

class ThreadPool:
    """Thread pool for managing concurrent task execution."""

    def __init__(self, logger, webserver):
        """
        Initialize the thread pool.
        
        Args:
            logger: Logger instance for logging
            webserver: Flask webserver instance
        """
        # You must implement a ThreadPool of TaskRunners
        # Your ThreadPool should check if an environment variable TP_NUM_OF_THREADS is defined
        # If the env var is defined, that is the number of threads to be used by the thread pool
        # Otherwise, you are to use what the hardware concurrency allows
        # You are free to write your implementation as you see fit, but
        # You must NOT:
        #   * create more threads than the hardware concurrency allows
        #   * recreate threads for each task
        # Note: the TP_NUM_OF_THREADS env var will be defined by the checker
        num_threads = os.getenv('TP_NUM_OF_THREADS')
        if num_threads is not None:
            self.num_threads = int(num_threads)
        else:
            self.num_threads = multiprocessing.cpu_count()

        self.tasks = Queue()
        self.threads = []
        self.shutdown_event = threading.Event()
        self.logger = logger
        self.lock = Lock()
        self.task_counter = 0
        self.job_status = {}
        self.webserver = webserver

        for _ in range(self.num_threads):
            thread = TaskRunner(self.tasks, self.shutdown_event, self.webserver)
            thread.start()
            self.threads.append(thread)

    def add_task(self, task):
        """
        Add a new task to the thread pool.
        
        Args:
            task: Task to be executed
            
        Returns:
            int: Task ID
        """
        with self.lock:
            self.task_counter += 1
            self.job_status[self.task_counter] = "running"  # Mark job as running

        if self.shutdown_event.is_set():
            self.logger.warning("ThreadPool is shutting down, cannot add new tasks")
            with open(f"results/{self.task_counter}.json", "w", encoding='utf-8') as out:
                data = {"status": "error", "reason": "shutting down"}
                out.write(json.dumps(data))
            self.job_status[self.task_counter] = "error"  # Mark job as error
            return self.task_counter

        self.logger.info("Task %d started and has been added to the queue", self.task_counter)
        self.tasks.put(task)
        return self.task_counter

    def graceful_shutdown(self):
        """Gracefully shutdown the thread pool."""
        self.logger.info("Gracefully shutting down ThreadPool...")
        self.shutdown_event.set()
        for thread in self.threads:
            thread.join(timeout=1)


class TaskRunner(Thread):
    """Thread for executing tasks from the thread pool."""

    def __init__(self, tasks, shutdown_event, webserver):
        """
        Initialize the task runner.
        
        Args:
            tasks: Queue of tasks to execute
            shutdown_event: Event for graceful shutdown
            webserver: Flask webserver instance
        """
        super().__init__()
        self.tasks = tasks
        self.shutdown_event = shutdown_event
        self.logger = logging.getLogger("TaskRunner")
        self.webserver = webserver

    def process_task(self, task):
        """
        Process a single task.
        
        Args:
            task: Task to process
            
        Returns:
            tuple: (job_id, result)
        """
        job_id, func, task_data = task
        self.logger.info("Processing task %d...", job_id)
        result = func(task_data)
        return job_id, result

    def run(self):
        """Main thread loop for processing tasks."""
        while True:
            if self.shutdown_event.is_set() and self.tasks.empty():
                return
            try:
                current_task = self.tasks.get(timeout=1)
            except Empty:
                continue

            try:
                job_id, result = self.process_task(current_task)
                output_path = f"results/{job_id}.json"
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result, f)
                self.webserver.tasks_runner.job_status[job_id] = "done"
            except (IOError, json.JSONDecodeError) as e:
                self.logger.error("Failed to process task: %s", str(e))
                if isinstance(current_task, tuple):
                    job_id = current_task[0]
                    output_path = f"results/{job_id}.json"
                    with open(output_path, 'w', encoding="utf-8") as f:
                        json.dump({"status": "error", "reason": str(e)}, f)
                    self.webserver.tasks_runner.job_status[job_id] = "error"
