import sqlite3, random

# Randomly generate 6 characters from given characters
def generateID():
    characters = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM0123456789@_#*-&"
    results = ""
    for n in range(6):
        x = random.choice(characters)
        results += x
    return(results)

# Genertate random real value from 0 to 100
def generateArrival():
    x = random.uniform(0,100)
    return(x)

# Genertate  exponential distribution of parameter 1 and round up
def generateDuration():
    x = random.expovariate(1)
    return(int(round(x + .5)))

# create class
class Simulation:
    def __init__(self, id, arrival, duration):
        self.id = id
        self.arrival = arrival
        self.duration = duration

conn = sqlite3.connect('database.db')
c = conn.cursor()

# create table
c.execute("""CREATE TABLE simulations (
            id text,
            arrival real,
            duration integer
            )""")

# define a function to add data into table
def insert_sim(sim):
    with conn:
        c.execute("INSERT INTO simulations VALUES(:id, :arrival, :duration)",
        {'id': sim.id, 'arrival': sim.arrival, 'duration': sim.duration})


# Simulate 100 data
for n in range(100):
    x = Simulation(generateID(), generateArrival(), generateDuration())
    insert_sim(x)


conn.close()
