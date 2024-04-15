# FILESTATUS: fully implemented but needs significant testing for efficiency, thread safety, bugfixing, overall functionality. Last updated v0.1.2-pre1
# IMPORTS ---------------------------------------------------------------------------------
from pathlib import Path
from datetime import datetime
import subprocess, streamlit as st, os, threading

# FUNCTIONS ---------------------------------------------------------------------------------

# TODO perhaps make download tasks independent of other tasks? but then you run into thread safety issues I think
# the scheduler singleton class (do i need st.cache_resource here?)
@st.cache_resource
class Scheduler:

    # THREAD SAFETY STUFF + INITIALIZATION -------------------------------------------------
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None: 
            with cls._lock:
                # Another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # constructor: set up basic attributes
    def __init__(self):
        thispath = Path(__file__).parent
        self.queuePath = os.path.join(thispath, "queue.txt")
        self.outPath = os.path.join(thispath, "completed.txt")
        self.active = False
        self.job = None
        self.command = ""
        self.lastLog = ""
        # implementation of a way to delete partially downloaded files
        self.downloaded_files = []

    # MANIPULATORS ------------------------------------------------------------------------

    # toggle active status (i.e. pause/unpause)
    def toggle(self):
        self.active = not self.active
        # begin the job loop on reactivation
        if self.active:
            self.run_next_job()

    # add a job to the queue at a potentially specified position
    def add_job(self, job, position=-1):
        # the simple one
        if position == -1:
            with open(self.queuePath, "a") as f:
                # commands are lists of strings
                f.write(' '.join(job + ["\n"]))
        # the slightly less simple one
        else:
            with open(self.queuePath, "r") as f:
                lines = f.readlines()
            lines.insert(position, job)
            with open(self.queuePath, "w") as f:
                f.writelines(lines)

    # remove a job from the queue
    def remove_job(self, position=-1):
        with open(self.queuePath, "r") as f:
            lines = f.readlines()
        lines.pop(position)
        with open(self.queuePath, "w") as f:
            f.writelines(lines)

    # clear the queue
    def clear_queue(self):
        with open(self.queuePath, "w") as f:
            f.write("")

    # clear the completed jobs
    def clear_completed(self):
        with open(self.outPath, "w") as f:
            f.write("")

    # switch the jobs at index posiiton1 and position2
    # this shouldn't actually be necessary with how we're going to run the reordering
    def rearrange_jobs(self, position1, position2):
        with open(self.queuePath, "r") as f:
            lines = f.readlines()
        lines[position1], lines[position2] = lines[position2], lines[position1]
        with open(self.queuePath, "w") as f:
            f.writelines(lines)

    # this is the implementation we'll actually use
    # write the jobs back to the queue in the order given by the positions dict
    def rearrange_all_jobs(self, positions):
        # TODO write because I don't know what the format returned by streamlit-sortables is
        pass

    # ACCESSORS ---------------------------------------------------------------------------

    # return the queue as a list[str]
    def get_queue(self):
        with open(self.queuePath, "r") as f:
            return f.readlines()

    # return the completed jobs as a list[str]
    def get_completed(self):
        with open(self.outPath, "r") as f:
            return f.readlines()
        
    # return the most recent error
    def get_log(self):
        return self.log

    # pop the next job in the queue
    def get_next_job(self):
        with open(self.queuePath, "r") as f:
            lines = f.readlines()
        if lines:
            job = lines.pop(0)
            with open(self.queuePath, "w") as f:
                f.writelines(lines)
            return job.strip().split(" ")
        return None
    
    # CONTROL FLOW ------------------------------------------------------------------------

    # the main function to run the next job in the queue
    def run_next_job(self):
        self.command = self.get_next_job()
        # if there is a job, run it
        if self.command:
            try:

                # if the job is a download task, add the file to the list of partially downloaded files
                if self.command[0] == "aria2c":
                    download_path = self.command[-4]
                    filename = self.command[-2]
                    file_path = download_path / filename
                    self.downloaded_files.append(str(file_path))

                self.job = subprocess.run(self.command, check=True)

                # log the job as completed if it works
                with open(self.outPath, "a") as f:
                    self.log = f"Task executed successfully at {self.time()}: {self.command}\n"
                    f.write(self.log)

            # log errors
            except subprocess.CalledProcessError as e:
                self.mostRecentError = f"Error in task execution: {e}"
                self.active = False

                self.clear_downloaded_files()

                # log the job as failed
                with open(self.outPath, "a") as f:
                    self.log = f"Error in task execution for task {self.command} at {self.time()}: {e}\n"
                    f.write(self.log)
 
            # automatically loop through the jobs while active but only while there are jobs
            # else you're wasting compute
            if self.active:
                self.run_next_job()
        else:
            self.active = False

    # terminate the current job while it's running
    # optional argument to retain the job in the queue or to remove it and log it
    def terminate(self, requeue=False):
        self.job.terminate()
        self.clear_downloaded_files()
        # log the job as terminated if not requeue
        if not requeue:
            with open(self.outPath, "a") as f:
                self.log = f"Terminated task {self.command} at {self.time()}\n"
                f.write(self.log)
        # if requeue, add the job back to the queue
        else:
            self.add_job(self.command, 0)

    # UTILS -------------------------------------------------------------------------------

    # return the current time for logging purposes
    def time(self):
        return datetime.now().strftime("%Y-%m-$d %H:%M:%S")

    # clear all partially downloaded files - only required for download tasks
    def clear_downloaded_files(self):
        for file_path in self.downloaded_files:
            if os.path.exists(file_path):
                os.remove(file_path)
        self.downloaded_files.clear()

# accessor for the scheduler singleton
@st.cache_resource
def get_scheduler():
    return Scheduler()

# more thread safety?
# this is a holdover from the original code where each page had its own scheduler
# that was definitely thread safe. i'm not so sure anymore lmao
# threading.Thread(target=get_scheduler, daemon=True).start()