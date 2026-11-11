import threading
import random
import time

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

# the back and forth between a teller and its customer, one step per semaphore
ask_transaction = [threading.Semaphore(0) for i in range(NUM_TELLERS)]     # teller -> customer
transaction_given = [threading.Semaphore(0) for i in range(NUM_TELLERS)]   # customer -> teller
transaction_done = [threading.Semaphore(0) for i in range(NUM_TELLERS)]    # teller -> customer
customer_left = [threading.Semaphore(0) for i in range(NUM_TELLERS)]       # customer -> teller
teller_transaction = [None] * NUM_TELLERS   # customer puts "deposit" or "withdrawal" here

# only 1 teller can talk to the manager at a time, and only 2 can be in the safe
manager = threading.Semaphore(1)
safe = threading.Semaphore(2)


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

        who = "Customer " + str(c)
        say("Teller", t, who, "serving a customer")

        # ask what they want and wait for the answer
        say("Teller", t, who, "asks for transaction")
        ask_transaction[t].release()
        transaction_given[t].acquire()

        kind = teller_transaction[t]
        say("Teller", t, who, "handling " + kind + " transaction")

        # withdrawals need the manager's ok first
        if kind == "withdrawal":
            say("Teller", t, who, "going to the manager")
            manager.acquire()
            say("Teller", t, who, "getting manager's permission")
            time.sleep(random.randint(5, 30) / 1000)
            say("Teller", t, who, "got manager's permission")
            manager.release()

        # every transaction happens in the safe
        say("Teller", t, who, "going to safe")
        safe.acquire()
        say("Teller", t, who, "enter safe")
        time.sleep(random.randint(10, 50) / 1000)
        say("Teller", t, who, "leaving safe")
        safe.release()

        say("Teller", t, who, "done with transaction")
        transaction_done[t].release()

        # wait for the customer to actually walk away before taking the next one
        say("Teller", t, who, "waiting for customer to leave")
        customer_left[t].acquire()

    say("Teller", t, "", "leaving for the day")


def customer(c):
    kind = random.choice(["deposit", "withdrawal"])
    say("Customer", c, "", "wants to perform a " + kind + " transaction")

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

    # wait for the teller to ask, then tell it what i want
    ask_transaction[t].acquire()
    teller_transaction[t] = kind
    say("Customer", c, "Teller " + str(t), "asks for " + kind + " transaction")
    transaction_given[t].release()

    # wait until the teller says it's done
    transaction_done[t].acquire()
    say("Customer", c, "Teller " + str(t), "leaves teller")
    customer_left[t].release()


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