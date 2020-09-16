import sqlite3
import re


class Processors:
    def __init__(self, pro_id):
        self.id = pro_id
        self.status = 'available'
        self.finishTime = 0
        self.taskID = None

    def handling_task(self, task_id, arrival, duration):
        self.finishTime = arrival + duration
        self.taskID = task_id
        self.status = 'unavailable'

    def release_task(self):
        self.finishTime = 0
        self.taskID = None
        self.status = 'available'


# initialize Clock
clock = 0

processors = []
busy_processor = []  # list for saving processors handling tasks
on_hold_list = []  # list for saving on-hold tasks

# initialize processors
for i in range(1, 4):
    processors.append(Processors(i))


def read_db():  # access database
    db_file = 'database.db'
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('select id,arrival,duration from simulations order by arrival')
    print('**SYSTEM INITIALISED**')

    rows = c.fetchall()
    queue = []
    for row in rows:
        queue.append(row)
    return queue


def authorizing(task_id):  # tell whether task's id is legal
    global clock
    # authorizing
    character_type_count = 0
    for regex in ['[A-Z]', '[a-z]', '[0-9]', '[-@_#*&]']:
        if re.search(regex, task_id):
            character_type_count += 1
    if character_type_count >= 3:
        #  if it is legal
        return True
    else:
        #  if not
        return False


def enter_task(task_list):
    # generate queue for tasks
    task_id, arrival, duration = task_list[0], task_list[1], task_list[2]
    if arrival >= clock:
        entering(task_id, arrival, duration)


def entering(task_id, arrival, duration):
    global clock, busy_processor

    if clock <= arrival:

        #  1. Before any action, check if any processor are assigned
        #  and append it to busy_processor list.
        for processor in processors:
            if processor.finishTime != 0:
                if processor not in busy_processor:
                    busy_processor.append(processor)

        #  2. If there are assigned processors, check if there are any task are ready to leave.
        if busy_processor:
            busy_processor.sort(key=lambda x: x.finishTime)

            #  Here we make a recursive function to travel through busy_processor list.
            def check_no_leaving_tasks():
                busy_processor.sort(key=lambda x: x.finishTime)
                not_leaving_tasks = 0
                for index, processor in enumerate(busy_processor):
                    if not_leaving_tasks == len(busy_processor):
                        break
                    elif processor.finishTime > arrival:
                        not_leaving_tasks += 1
                    #  Before the next task comes in, We check if there are any tasks are ready to leave.
                    elif processor.finishTime <= arrival:
                        clock = processor.finishTime
                        print("** {} : Task {} completed.".format(clock, processor.taskID))
                        #  If there are, let them leave one by one, in the meanwhile, let tasks in on_hold list access.
                        free = busy_processor.pop(index)
                        for processor1 in processors:  # free processor
                            if processor1 == free:
                                processor1.release_task()
                        #  While freeing processor, assign tasks in on_hold list.
                        if on_hold_list and len(busy_processor) < 3:
                            on_hold_list.sort(key=lambda x: x[1])
                            for index1, task in enumerate(on_hold_list):
                                id1, arrival1, duration1 = on_hold_list.pop(index1)
                                # for processor in processors:
                                if processor.status == 'available' and len(busy_processor) < 3:
                                    assign_task(id1, clock, duration1, processor)
                #  Once there are no task ready to leave, end recursion.
                if not_leaving_tasks < len(busy_processor):
                    return check_no_leaving_tasks()

            # Run recursive function.
            check_no_leaving_tasks()
        #  3. Let tasks enter system in order.
        clock = arrival
        entering_system(task_id, clock, duration)


def entering_system(task_id, arrival, duration):
    global clock, busy_processor
    print("** {} : Task {} with duration {} enters the system.".format(arrival, task_id, duration))
    clock = arrival
    #  Every entering tasks run through this authorizing process
    if authorizing(task_id):
        #  Authorizing succeed, read to assign task.
        print("** Task " + task_id + " accepted.")
        #  IF there are no available processors, append task in on-hold list
        if len(busy_processor) >= 3:
            print("** Task {} on hold.".format(task_id))
            # checkTaskCompleted()
            temp = task_id, arrival, duration
            if temp not in on_hold_list:
                on_hold_list.insert(0, temp)
        #  If there are available processors, assign task to the processor.
        else:
            for processor in processors:
                if processor.status == 'available':
                    assign_task(task_id, arrival, duration, processor)
                    break
    #  Authorizing failed, discard task.
    else:
        print("** Task " + task_id + " unfeasible and discarded.")


def assign_task(task_id, arrival, duration, processor):
    processor.handling_task(task_id, arrival, duration)
    clock = arrival
    print("** {} : Task {} assigned to processor {}.".format(clock, task_id, processor.id))
    # Update busy processor list right after any assignment.
    for processor in processors:
        if processor.finishTime != 0:
            if processor not in busy_processor:
                busy_processor.insert(0, processor)


def main():
    # start entering task
    global clock
    task_queue = read_db()
    for task in task_queue:
        enter_task(task)
    # Check if there are any task still in process.
    if len(busy_processor) > 0:
        busy_processor.sort(key=lambda x: x.finishTime)
        for processor in busy_processor:
            clock = processor.finishTime
            print("** {} : Task {} completed.".format(clock, processor.taskID))
    print("** {} : SIMULATION COMPLETED. **".format(clock))


if __name__ == "__main__":
    main()
