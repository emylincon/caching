import threading

x = 0
lock = threading.Lock()

def thread_task():
    global x
    for i in range(1000000):
        lock.acquire()
        x+=1
        lock.release()


def main_task():

    t1 = threading.Thread(target=thread_task,)
    t2 = threading.Thread(target=thread_task,)
    # t1 = threading.Thread(target=thread_task,)
    # t2 = threading.Thread(target=thread_task,)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

main_task()
print(x)