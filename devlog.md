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

Picking back up on project2.py. Right now the customer just introduces itself and the teller serves it, so this session I'm adding the rest of the conversation between them. The teller asks for the transaction, the customer tells it deposit or withdrawal, the teller does the transaction and tells the customer it's done, and then the customer leaves.

Each of those steps needs its own semaphore for each teller, since one side has to wait for the other every time. The teller waits for the customer to arrive, then the customer waits for the teller to ask, then the teller waits for the transaction, and so on. The customer will also pick deposit or withdrawal at random and write it into a shared slot for that teller, the same way it writes its id.

I'm still keeping it at a small number of customers so the output is easy to follow. The manager and safe come next session, and the door after that.