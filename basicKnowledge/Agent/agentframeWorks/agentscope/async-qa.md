# Async Q&A, and the process memory model

Follow-ups to `asyncio.md`. The memory model is the part underneath “parked frames.”

## Q. What is the difference between `async for` and `await`?

`await` suspends until one `Future` finishes and gives you that one result. `async for` suspends once per item. Each resume happens when the producer hits its next `yield`.

```python
result = await self._call_model(...)            # one result, then the next line
async for event in self._func(request=request):  # one event per yield
    await event_queue.enqueue_event(a2a_message)
```

`await self._call_model(...)` parks `_reasoning_impl` on the model socket. The frame stays on the heap until that socket is readable, then continues on the next line with the response.

`async for` is how `execute` pulls `stream_query`. Each iteration calls `__anext__`, runs the generator until the next `yield`, and hands that event to `execute`. The next iteration resumes on the line after `yield`. Intermediate events are dropped. Only `RunStatus.Completed` reaches `await event_queue.enqueue_event(...)`.

From `execute`, one pull can last a long time. `stream_query` may sit inside its own `await` before it can `yield`. `execute` stays paused at `async for` for that whole wait. The waker is still the next `yield`.

Both are the same heap-frame suspend. `await` is resumed by the `Future`. `async for` is resumed by the next `yield`.

## Q. Does `await` pause the current thread until another process wakes it?

`await` parks the coroutine, the heap frame, on that line. The thread stays on the CPU and runs the event loop, which starts another ready coroutine. The thread joins the kernel sleep queue only when that ready queue is empty.

The wake is usually a packet or a timer on a file descriptor. The kernel returns from `kevent` or `epoll_wait` into this same thread. The loop matches the fd to the `Future`, then `send`s the parked frame. The frame continues on the line after `await`. The thread continues inside the loop.

Another process wakes this thread only by writing a socket or a pipe. That write becomes an fd event. The detached-server process has its own thread and its own `kevent`.

A thread that itself sleeps at the call, until some other execution wakes it, is a blocking call on a platform thread: `Socket.read()`, `Thread.sleep`, a servlet thread stuck in a model call. One request, one parked thread. `await` is many parked frames, one thread, and that thread sleeps only when none of the frames can run.

## Q. What is “many parked frames”? Compare to Java.

A frame is one function’s saved execution: its local variables and the line it stopped on. A parked frame is that record sitting on the heap, not running, waiting for the event loop to call `send` on it.

During `await self._call_model(...)`, one request freezes a chain:

```text
execute               paused at async for
  stream_query        paused at async for
    _reasoning_impl   paused at await _call_model
```

Five hundred in-flight model calls are five hundred such chains on the heap, plus five hundred sockets in one `kqueue`. One OS thread runs whichever chain is ready. The other 499 stay parked. That thread enters `kevent` only when all 500 are parked.

A Java platform thread keeps those frames on its own stack. `Socket.read()` parks the thread in the kernel. Five hundred slow calls are five hundred kernel threads, each asleep inside its own stack.

A virtual thread (Java 21) matches the Python picture. On a blocking call the JVM copies that virtual thread’s stack onto the heap and unmounts it from a carrier. Five hundred parked virtual threads are five hundred heap stacks. A handful of carrier threads run the ready ones. A carrier sleeps in `epoll_wait` when none are ready.

Python only saves the `async def` frames, and only at an `await`. A virtual thread saves the whole stack, so it can pause in the middle of an ordinary method. A plain `def` in the Python chain runs to the end on that one thread. It has no heap frame to park.

## The memory model

One process has one virtual address space. Threads in that process share it. A second process has a second address space. `subprocess.Popen` is a new space. `threading.Thread` is another stack in the same space.

```text
high addresses
  stack of thread A     grows down; one per thread
  stack of thread B
  ...
  hole
  heap                  grows up; one per process, shared by its threads
  BSS / data            globals, statics
  code                  machine instructions, read-only
low addresses
```

A stack frame is the function record for one call that is running, or waiting, on that thread. It holds the return address, the saved registers, the parameters, and the local variables whose size is known and whose lifetime is this call. When the function returns, that slot is reclaimed by moving the stack pointer. The thread’s stack is the pile of these frames for the calls it is inside right now.

The heap is for storage whose size or lifetime is not the call. `malloc` / `new`, a buffer you grow, an object another function must still see after this one returns, anything shared between threads. You free it, or a garbage collector does.

So the stack holds function information, and it also holds local variables when those locals belong to the call. The heap holds the values that must outlive the call, or that are too large, or that are shared. “Variables live on the heap” overshoots. A C `int n` inside a function is on the stack. A C `int *p = malloc(...)` puts `p` on the stack and the `int` on the heap.

Java splits the same way, one step further. Each platform thread has its own stack. The heap is shared by every thread in the process. A local `int` and a local object reference sit in the stack frame. The object from `new` sits on the heap. The stack frame stores the pointer.

CPython puts almost every Python value on the heap. The name `x` in a function is a slot that holds a pointer. The int, the list, the dict all live on the heap. The function record itself, the `PyFrameObject`, is also a heap object. The OS thread still has a C stack: that stack is the interpreter, the eval loop, and whatever C function is running. When an ordinary Python function calls another, both the C stack and the chain of Python frames grow. When it returns, both shrink.

`await` uses that split. The Python frame, with its locals and its instruction pointer, stays on the heap. The C stack unwinds back to the event loop. The thread can run a different chain, or enter `kevent`. “Many parked frames” means many of those function records are alive on the heap while only one of them occupies the thread’s C stack.

A Java platform thread cannot do this. Its function record is the stack, so parking the call parks the thread. A virtual thread can, because the JVM copies that stack onto the heap and the carrier thread’s real stack is free for someone else. Same idea as the coroutine frame: the function information of a paused call lives on the heap, and the OS stack belongs to whoever is actually running.
