# 11-7 8:02pm

Starting Project 1. It's three programs: a logger, an encryption program, and a driver that launches the other two and talks to them through pipes. I'm using Python with subprocess because I know Python the best and it's the most intuitive for me to write.

I went through the in-class example. cpu.py starts mem.py with Popen, sends it lines, and reads replies with readline(). mem.py flushes after every print, which I think is because output to a pipe gets buffered. Without the flush the reply would just sit in mem.py's buffer, and cpu.py would be stuck waiting on readline() forever. My driver will do the same thing but with two children. The encryption program needs stdin and stdout piped since it sends replies back, but the logger only needs stdin since it writes to a file.

This session I'm setting up git and starting encryption.py. I'll test it by hand with the spec's example (key HELLO, HELLO into OIWWC).


# 11-09 5:30pm

Got the first part working with 3 tellers and 3 customers. A customer gets in line, picks a free teller, and introduces itself, and then the teller serves it. I used a semaphore that starts at 0 and goes up every time a teller is free, so customers just wait on it until one opens up. The free tellers are kept in a list with a lock around it so two customers can't grab the same teller.

Each teller has its own semaphore that it waits on until a customer walks up. The customer writes its id into a shared slot for that teller and then releases the teller's semaphore, so the teller knows who it's serving. The order matters here, since if the customer released first the teller could read the slot before the id was in it.

One thing I had to think about was how the tellers stop. When there are no customers left, each teller is still stuck waiting for someone to walk up. So after all the customers finish, main wakes up each teller with None as the customer, and the teller sees that and leaves. I also noticed the output order changes every time I run it, which makes sense since the threads run at the same time.

Next session I'm adding the rest of the conversation (asking for the transaction, giving it, finishing, and the customer leaving).

# 11-10 10:05pm

Picking back up on project2.py. Right now the customer just introduces itself and the teller serves it, so this session I'm adding the rest of the conversation between them. The teller asks for the transaction, the customer tells it deposit/withdrawal, the teller does the transaction and tells the customer it's done. Customer leaves after.

Each of those steps needs its own semaphore for each teller, since one side has to wait for the other every time. The teller waits for the customer to arrive, then the customer waits for the teller to ask, then the teller waits for the transaction, and so on. The customer will also pick deposit or withdrawal at random and write it into a shared slot for that teller, the same way it writes its id.

I'm still keeping it at a small number of customers so the output is easy to follow. The manager and safe come next session, and the door after that.


# 11-10 11:23pm

Finished the conversation between the teller and the customer. The teller asks for the transaction, the customer gives it, the teller handles it, and then the customer leaves. I added four new semaphores for each teller, one for each step, so every step is one thread releasing and the other waiting. The customer picks deposit or withdrawal at random and writes it into a shared slot for the teller, the same way it does with its id.

At first I thought the teller could go back to ready as soon as the transaction was done. But then the next customer could pick that teller while the last one was still there, so the teller waits for its customer to leave first.

I tested it with 3 customers and then 10, and every customer left its teller and all 3 tellers stopped at the end.

Manager and safe next.

# 11-11 10:48am

Starting session 3. The teller and customer can talk to each other now, but the teller doesn't actually do anything with the transaction yet. This session I'm adding the manager and the safe, which are the shared resources the tellers have to wait their turn for.

The manager can only talk to one teller at a time, so I'm going to use a semaphore that starts at 1. The safe allows two tellers inside at once, so its semaphore starts at 2 instead. A teller only goes to the manager if the transaction is a withdrawal, and every teller goes to the safe. Both of these take time, so the teller will sleep for a random amount, 5 to 30 ms with the manager and 10 to 50 ms in the safe.

The spec also wants three lines for each resource: going to it, using it, and done with it. Plus there are two lines for every sleep, one before and one after.

# 11-11 2:23pm

Added the manager and the safe. The manager is a semaphore that starts at 1 so only one teller can talk to it at a time, and the safe starts at 2 so two tellers can be inside together. Only withdrawals go to the manager, and every transaction goes to the safe. Each one prints three lines: going to it, using it, and done with it.

One thing I had to look up was the sleep. The spec gives the times in milliseconds, but time.sleep in Python takes seconds, so I pick a random number of ms and divide it by 1000. If I had passed it in straight it would have slept for 5 to 50 whole seconds instead.

I ran it with 10 customers to make sure there were never more than two tellers in the safe or more than one with the manager at the same time. Withdrawals went to the manager first and deposits went straight to the safe.

Door and bank opening/closing next.

# 11-12 12:10pm

Starting session 4. The whole transaction works now, including the manager and safe, but customers can still walk straight in whenever they want. This session I'm adding the door and the bank opening and closing.

The door only lets two customers through at a time, so it's another semaphore that starts at 2, like the safe. Customers go through it to come in and again to leave. Before entering, each customer also waits a random 0 to 100 ms.

The bank can't open until all three tellers are ready. I'm going to keep a count of ready tellers with a lock around it, and have the last one to get ready release a semaphore that the customers are waiting on. Closing should happen after every customer has left and the tellers have stopped, which is close to what main already does.


# 11-13 9:20pm

Added the door and the bank opening and closing. The door is a semaphore that starts at 2, and customers go through it on the way in and out. Before heading to the bank, each customer waits a random 0 to 100 ms.

To open the bank, each teller adds one to a shared count when it's ready, with a lock so two tellers can't both think they're the last one. The last teller releases a semaphore once for every customer, and customers wait on it before entering. The count has to come after the teller says it's ready, or the bank could open before all three tellers were actually ready.

I tested it with 10 and 50 customers, and nobody came in before the bank opened and everyone left before it closed.

50 customers and matching the sample output next.