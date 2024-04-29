import threading
import time
import schedule

# schedule.every(10).minutes.do(job)
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)
# schedule.every().day.at("12:42", "Europe/Amsterdam").do(job)
# schedule.every().minute.at(":17").do(job)

    

def job():
    print("I'm running on thread %s" % threading.current_thread())

def run_threaded():
    while 1:
        schedule.run_pending()
        time.sleep(1)

schedule.every().minutes.at(":08").do(job)


job_thread = threading.Thread(target=run_threaded)
job_thread.start()