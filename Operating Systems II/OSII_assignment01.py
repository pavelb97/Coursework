"""
2. Design. Outline the scheduling algorithm in pseudo-code. This will be your design for
the algorithm. You should consider all aspects related to processes and scheduling.
Your design of the algorithm must also take into account the possibility of having to
block for I/O, in which case the process will forego the rest of its time slice, or to
interrupt.

What we will need:
    - Ready queue
        - Add process
        - Remove process
        - Get process
    - Blocked Queue
        - Add Process
        - Remove process
        - Get process
    - Scheduler
        - send to ready/blocked queue
        - flush completed processes
        - send to CPU for execution
        - run idle process
    - CPU
        - execute process

class Process:
    process ID
    time for completion
    process type (normal, I/O, interrupt)
    process state (ready, blocked)

Can reuse queue structure for both blocked and ready queues - just need separate methods within scheduler.
class Queue():
    Queue = []
    head & tail & size = 0

    def addProcess(process):
        add process to end of queue

    def removeProcess:
        remove topmost process

    def getProcess:
        return topmost process

class Scheduler(process):
        process = None
        CPU = CPU()
        readyQueue = Queue()
        blockedQueue = Queue()

         addReadyProcess(process):
            add a ready process to end of ready queue

        removeReadyProcess:
            remove the topmost ready process from ready queue

        addBlockedProcess(process):
            add a blocked process to the end of blocked queue

        removeBlockedProcess:
            remove the topmost blocked process from blocked queue

        runProcess(process):
            if either queue is empty:
                run idle process
            while either queue has processes:
                process.time -= cpu time
                if process is io:
                    send to CPU
                    remove from ready queue
                    change process state
                    send to blocked queue
                if process is interrupt:
                    remove from ready queue
                    change process state
                    send to blocked queue
                    handle interrupt
                    remove from blocked queue
                    add to front of ready queue
                    send to CPU
                if process is normal:
                    send to CPU
                    if process needs more time:
                        send to ready queue
                    else:
                        flush process
                    run a blocked process

Class CPU:
    CPU time

    runProcess():
        sleep for x seconds to mimic CPU work

    runIdleProcess():
        sleep for x seconds to mimic idle process running
        check if either queue has new processes
"""

import random
import time


# Process Class -  models a process with an ID, total time it takes to execute the process, the type of process (normal,
#                   I/O operation or an interrupt), and the process state (ready, running or blocked)
#               - Contains various getter and setter methods to access and change process variables
# ._cycles represents the TOTAL no. of clock cycles it took the process to complete, including time for all other
# processes to be completed.

class Process:
    def __init__(self, pID, executionTime, type="normal", state="ready"):
        self._pID = pID
        self._exeTime = executionTime
        self._type = type.lower()
        self._state = state.lower()

        self._cycles = 0
    def __str__(self):
        return ("Process information:\n"
               "    Process ID: %s\n"
               "    Time left: %d\n"
               "    Process type: %s\n"
               "    Process state: %s" % (self._pID, self._exeTime, self._type, self._state))

    def _setState(self, newStatus):
        self._state = newStatus.lower()

    def _getState(self):
        return self._state

    def _getType(self):
        return self._type

    def _setType(self, newType):
        self._type = newType.lower()


# Queue class - Basic implementation for a FIFO queue. Resize factor = 2 x current size
#             __getQueuedProcesses()
#                   Helper method for __str__ method returns a string representation of queue with #1 being the top of
#                   the queue
#             _queueProcess(process)
#                   Queue a process object at the tail end of queue, increment tail and size. Double the size of the
#                   list if nearing the end.
#            _dequeueProcess()
#                   Pop the process at the top of the queue (head). Update tail and size.
#            _getTopProcess()
#                   Return the process at the top of the queue (head).
#
class Queue:
    def __init__(self):
        self._queue = [None] * 10
        self._head = self._tail = self._size = 0

    def __str__(self):
        queue = self.__getQueuedProcesses()
        return queue

    def __getQueuedProcesses(self):
        queueAsString = ""
        count = 1
        for i in self._queue:
            if i is None:
                continue
            else:
                queueAsString += ("%d. ID: %d Type: %s\n" % (count, i._pID, i._type))
                count += 1
        return queueAsString

    def _queueProcess(self, process):
        if self._size == len(self._queue)-1:
            self._queue.extend([None]*(self._size))
        if self._tail == self._head:
            self._queue[self._head] = process
        else:
            self._queue[self._tail] = process
        self._size += 1
        self._tail += 1

    def _dequeueProcess(self):
        self._queue.pop(self._head)
        self._tail -= 1
        self._size -= 1

    def _getTopProcess(self):
        return self._queue[self._head]


# Scheduler Class - models the functionality of a scheduler. CPU instantiated within the class for convenience.
#                   Contains both Ready and Blocked queues. Processes can be queued/removed manually outside of class or
#                   as needed while running.
#
#                _addReadyProcess
#                   Ready queue functionality. Adds a process to the end of the ready queue. process parameter allows for the
#                   processes to be added outside the class.
#
#               _runProcess
#                   Sends a process to the CPU if there are any processes in either queues. After a normal process is run
#                   the scheduler checks and executes a blocked processes (if there are any).

class Scheduler:
    def __init__(self):
        self._process = None
        self._CPU = CPU()

    def _addReadyProcess(self, process):
        self._CPU._readyQueue._queueProcess(process)

    def _runProcess(self):
        if (self._CPU._readyQueue._size == 0) and (self._CPU._blockedQueue._size == 0):
            self._CPU._runIdleProcess()

        while self._CPU._readyQueue._size != 0:
            self._process = self._CPU._readyQueue._getTopProcess()
            print("Process %d currently running." % self._process._pID)
            self._process._state = "running"
            self._process._cycles += 1
            self._CPU._runProcess(self._process)


            # After normal process complete check on blocked processes (for fairness)
            if self._process._type == "normal" and self._CPU._blockedQueue._size != 0:
                process = self._CPU._blockedQueue._queue[self._CPU._blockedQueue._head]
                self._CPU._removeBlockedProcess()
                process._state = "ready"
                print("Removing process %d from blocked queue." % process._pID)
                self._CPU._addReadyProcess(process)
                print("Adding process %d to ready queue." % process._pID)
            # Run idle process in no other processes are queued.
            if (self._CPU._readyQueue._size == 0) and (self._CPU._blockedQueue._size == 0):
                self._CPU._runIdleProcess()


# CPU Class - mimics process execution by stalling execution using the sleep function from the time module.
#
#                _addReadyProcess
#                   Ready queue functionality. Adds a process to the end of the ready queue. process parameter allows for the
#                   processes to be added outside the class. Otherwise this method is called within the class itself when
#                   a process requires more CPU time to finish
#                       OR
#                   when a process is ready to execute after being in the blocked queue.
#
#               _removeReadyProcess
#                   Ready queue functionality. Removes the topmost process on the ready queue. Called when any kind of
#                   process is ran regardless of type or outcome.
#
#               _addBlockProcess
#                   Blocked queue functionality. Adds a process to the end of the blocked queue. process parameter allows
#                   for the processes to be added outside the class. Otherwise this method is called within the class
#                   itself whenever an I/O operation is executed and the process is sent to the blocked queue until
#                   I/O data is received
#                       OR
#                   When an interrupt occurs and the current process has to be suspended and sent to the blocked queue.
#
#               _removeBlockedProcess
#                   Blocked queue functionality. Removes the topmost process the blocked queue. Called when a blocked
#                   process is ran.
#
#               _runProcess
#                   If both queues are empty run the idle process. Checks what type of process is being run:
#                   I/O operations get sent to CPU and then to the blocked queue (the process state marked as blocked)
#                   until I/O operation completed, after I/O completed this process.
#                   Likewise for an interrupt, process state is changed to blocked, sent to the blocked queue but resumes
#                   the same process after interrupt handled. If a normal process is running it either executes and
#                   terminates as no more CPU time is needed otherwise the process is sent to the end of the ready queue,
#                   this repeats until process completion. The process clock cycle count increases for all other processes
#                   when a process is ran.
#
class CPU:
    def __init__(self):
        self._CPUProcess = None
        self._clockCycle = 100
        self._readyQueue = Queue()
        self._blockedQueue = Queue()

    def _addReadyProcess(self, process):
        self._readyQueue._queueProcess(process)

    def _removeReadyProcess(self):
        self._readyQueue._dequeueProcess()

    def _addBlockProcess(self, process):
        self._blockedQueue._queueProcess(process)

    def _removeBlockedProcess(self):
        self._blockedQueue._dequeueProcess()


    def _runProcess(self, process):
        self._CPUProcess = process
        time.sleep(1)   # mimic CPU doing work

        # CASE: I/O
        if self._CPUProcess._type == "io":
            if self._CPUProcess._exeTime <= 0:
                print("Process %d completed in %d clock cycle(s)." % (self._CPUProcess._pID, self._CPUProcess._cycles))
                self._removeReadyProcess()
            else:
                self._CPUProcess._exeTime -= self._clockCycle
                print("I/O Process. Sending to blocked queue until I/O operation completed.")
                self._CPUProcess._state = "blocked"
                self._readyQueue._dequeueProcess()
                self._addBlockProcess(self._CPUProcess)

        # CASE: INTERRUPT
        elif self._CPUProcess._type == "interrupt":
            print("Interrupt. Sending to blocked queue until handled.")
            self._CPUProcess._exeTime -= self._clockCycle
            self._CPUProcess._state = "blocked"
            self._addBlockProcess(self._CPUProcess)
            self._interruptHandler()
            self._removeBlockedProcess()
            print("Interrupt handled - resuming process.")
            self._CPUProcess._state = "running"
            self._CPUProcess._type = "normal"
        # CASE: NORMAL
        if self._CPUProcess._type == "normal":
            self._CPUProcess._exeTime -= self._clockCycle
            # CASE: IF PROCESS WILL BE COMPLETED IN CURRENT CYCLE
            if self._CPUProcess._exeTime <= 0:
                #process completed
                print("Process %d completed in %d clock cycle(s)." % (self._CPUProcess._pID, self._CPUProcess._cycles))
                self._removeReadyProcess()
            # CASE: IF MORE CPU TIME NEEDED
            else:
                #return to ready queue
                self._CPUProcess._state = "ready"
                self._removeReadyProcess()
                self._addReadyProcess(self._CPUProcess)
                print("Adding process %d to ready queue." % self._CPUProcess._pID)
            for i in self._readyQueue._queue:
                if i is None:
                    continue
                elif i._pID != self._CPUProcess._pID:
                    i._cycles += 1
            for i in self._blockedQueue._queue:
                if i is None:
                    continue
                elif i._pID != self._CPUProcess._pID:
                    i._cycles += 1
            if (self._readyQueue._size == 0) and (self._blockedQueue._size == 0):
                self._runIdleProcess()

    def _interruptHandler(self):
        time.sleep(3)   # mimic event handler

    def _runIdleProcess(self):
        while True:
            print("Idle Process - Energy Saving")     # mimic idle process
            time.sleep(5)
            if (self._readyQueue._size != 0) or (self._blockedQueue._size != 0):
                return False


if __name__ == "__main__":
    scheduler = Scheduler()
    # A test function to test random combination of process types/execution times.
    # Limits the amount of IO/ Interrupt to 4 to prevent test running too long
    def test():
        ioCount = 0
        interruptCount = 0
        exeTimeList = [100, 200, 300]
        typeList = ["normal", "io", "interrupt"]
        for i in range(0, 5):
            exeTime = random.randint(0, 2)
            proType = random.randint(0, 2)
            if proType == 1:
                ioCount += 1
            if proType == 2:
                interruptCount += 1
            if (ioCount + interruptCount) == 2:
                proType = 0
            process = Process((120 + i), exeTimeList[exeTime], typeList[proType], "ready")
            scheduler._addReadyProcess(process)

    test()
    scheduler._runProcess()
