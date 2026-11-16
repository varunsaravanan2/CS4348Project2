# CS4348 Project 2

For this project I made a bank simulation in Python using threads. There are 3 tellers and 50 customers, and each one runs as its own thread.

- `project2.py`: the whole program. It starts the teller and customer threads and prints everything they do.
- `devlog.md`: my notes from each session.

Since they're threads, they all share the same memory, so they pass things to each other through shared variables. I used semaphores to make them take turns and wait on each other in the right order.

## Running it

It's Python so there's nothing to compile, you just need Python 3. Run this from the command line:

```
python project2.py
```

It doesn't need any arguments and finishes in about a second. It prints around 1,100 lines, so it's easier to look through if you save it to a file:

```
python project2.py > output.txt
```

## What happens

The bank opens once all 3 tellers are ready, and no customer can get in before that. Each customer picks deposit or withdrawal at random, waits 0 to 100 ms, and comes in through the door, which only lets 2 customers through at a time. Then it waits in line until a teller is free, goes to that teller, and introduces itself.

The teller asks for the transaction and the customer tells it. If it's a withdrawal, the teller goes to the manager first (only 1 teller at a time, 5 to 30 ms). Every transaction happens in the safe (2 tellers at a time, 10 to 50 ms). After that the teller tells the customer it's done, and the customer leaves the teller and goes out through the door. Once all 50 customers are gone, the tellers stop and the bank closes.

## Output

Every line uses the format from the spec:

```
THREAD_TYPE ID [THREAD_TYPE ID]: MSG
```

The brackets have the other thread in them, or are empty if there isn't one. For example:

```
Teller 0 []: ready to serve
Customer 4 [Teller 2]: selects teller
Teller 2 [Customer 4]: going to safe
```

The only lines that don't follow it are `The bank is now open.` and `The bank closes for the day.`

If you want to follow just one customer or teller, you can grep for it:

```
python project2.py | grep "Customer 4 "
python project2.py | grep "Teller 1 "
```

## Semaphores

- `tellers_ready`: counts free tellers, customers wait on it to get in line
- `line_lock`: protects the list of free tellers so two customers can't take the same one
- `customer_arrived`, `ask_transaction`, `transaction_given`, `transaction_done`, `customer_left`: one of each for every teller, one for each step of the conversation with its customer
- `manager`: starts at 1, one teller at a time
- `safe`: starts at 2, two tellers at a time
- `door`: starts at 2, two customers at a time
- `bank_open`: customers wait on it until all 3 tellers are ready
- `started_lock`: protects the count of how many tellers are ready
- `print_lock`: keeps lines from different threads from getting mixed together