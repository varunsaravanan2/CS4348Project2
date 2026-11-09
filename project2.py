import threading
import random

NUM_TELLERS = 3
NUM_CUSTOMERS = 3   # only 3 for now, changing to 50 once it all works

# lock for printing so lines from different threads don't get mixed together
print_lock = threading.Semaphore(1)

# goes up when a teller is free, customers wait on this
tellers_ready = threading.Semaphore(0)

# which tellers are free, plus a lock so two customers can't take the same one
ready_line = []
line_lock = threading.Semaphore(1)

# each teller gets its own semaphore and slot
customer_arrived = [threading.Semaphore(0) for i in range(NUM_TELLERS)]
teller_customer = [None] * NUM_TELLERS   # customer puts its id here


def say(kind, id, other, msg):
    print_lock.acquire()
    print(kind + " " + str(id) + " [" + other + "]: " + msg)
    print_lock.release()


def teller(t):
    while True:
        say("Teller", t, "", "ready to serve")

        # add this teller to the free list and signal that one is open
        line_lock.acquire()
        ready_line.append(t)
        line_lock.release()
        tellers_ready.release()

        say("Teller", t, "", "waiting for a customer")
        customer_arrived[t].acquire()

        c = teller_customer[t]
        if c is None:
            # None means main is done and wants the teller to stop
            break

        say("Teller", t, "Customer " + str(c), "serving a customer")

    say("Teller", t, "", "leaving for the day")


def customer(c):
    say("Customer", c, "", "getting in line")

    # blocks here until some teller is free
    tellers_ready.acquire()

    line_lock.acquire()
    t = ready_line.pop(0)
    line_lock.release()

    say("Customer", c, "Teller " + str(t), "selects teller")

    # write my id where the teller can see it, then wake it up
    teller_customer[t] = c
    say("Customer", c, "Teller " + str(t), "introduces itself")
    customer_arrived[t].release()


tellers = []
for t in range(NUM_TELLERS):
    tellers.append(threading.Thread(target=teller, args=(t,)))
    tellers[t].start()

customers = []
for c in range(NUM_CUSTOMERS):
    customers.append(threading.Thread(target=customer, args=(c,)))
    customers[c].start()

for c in range(NUM_CUSTOMERS):
    customers[c].join()

# customers are all done, so wake each teller up with None so it exits the loop
for t in range(NUM_TELLERS):
    tellers_ready.acquire()        # make sure the teller is waiting first
    line_lock.acquire()
    i = ready_line.pop(0)
    line_lock.release()
    teller_customer[i] = None
    customer_arrived[i].release()

for t in range(NUM_TELLERS):
    tellers[t].join()

print("The bank closes for the day.")