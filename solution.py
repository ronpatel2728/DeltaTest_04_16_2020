"""
"""
import pandas
from datetime import datetime, date, timedelta
import math

def getNumberofColumns(path, delimiter =","):
    data_file_delimiter = delimiter
    # The max column count a line in the file could have
    largest_column_count = 0
    # Loop the data lines
    with open(path, 'r') as temp_f:
        # Read the lines
        lines = temp_f.readlines()
        for l in lines:
            # Count the column count for the current line
            column_count = len(l.split(data_file_delimiter)) + 1

            # Set the new most column count
            largest_column_count = column_count if largest_column_count < column_count else largest_column_count
    # Close file
    temp_f.close()
    return largest_column_count

def cleanData(df):
    columnLen = len(df.columns)
    columnsNames = ['room', 'capacity', 't1', 't2']
    roomSchedule = pandas.DataFrame(columns=columnsNames)
    for i in range(2, columnLen - 1, 2):
        columns = [0, 1, i, i+1]
        dfSubSet = df.iloc[:, columns]
        dfSubSet.columns = columnsNames
        roomSchedule = roomSchedule.append(dfSubSet)
        roomSchedule = roomSchedule[roomSchedule['t1'].notnull()]

    roomSchedule["capacity"] = pandas.to_numeric(roomSchedule["capacity"])
    roomSchedule["t1"] = pandas.to_datetime(roomSchedule["t1"], format='%H:%M').dt.time
    roomSchedule["t2"] = pandas.to_datetime(roomSchedule["t2"], format='%H:%M').dt.time
    return roomSchedule

def filterRoom(df, Persons, Floor, StartTime, EndTime):
    roomDF = df.copy()
    previousFloor = Floor
    StartTime = datetime.strptime(StartTime, '%H:%M').time()
    EndTime = datetime.strptime(EndTime, '%H:%M').time()
    if EndTime <= StartTime:
        print("Invalid Start and End times")
        return None
    roomDF = roomDF[roomDF['capacity'] >= Persons]
    if len(roomDF) == 0:
        print("No rooms available for {} people".format(Persons))
        return None

    roomDF = roomDF[(roomDF['t1'] <= StartTime) & (roomDF['t2'] >= EndTime)]
    if len(roomDF) == 0:
        #print("No rooms available between {} and {}".format(StartTime, EndTime))
        #print("Looking by splitting into multiple rooms")
        timediff = datetime.combine(date.today(), EndTime) - datetime.combine(date.today(), StartTime)
        if timediff.seconds > 1800:
            interval = 1800
            SplitTime = [(StartTime, (datetime.combine(date.today(), EndTime) - timedelta(seconds=interval)).time()),
                         (((datetime.combine(date.today(), EndTime) - timedelta(seconds=interval)).time()), EndTime)]
            for i in SplitTime:
                T1 = ':'.join(str(i) for i in (str(i[0]).split(':')[:-1]))
                T2 = ':'.join(str(i) for i in (str(i[1]).split(':')[:-1]))
                filterRoom(df, Persons, previousFloor, T1, T2)
        else:
            print("Unable to find room between {} and {}".format(StartTime, EndTime))
    else:
        roomDF['Floor'] = roomDF['room'] - Floor
        roomDF['Floor'] = roomDF['Floor'].abs()
        result = roomDF.sort_values('Floor').min()
        roomNumber = str(result['room'])
        previousFloor = math.floor(result['room'])
        print("Found Room for {} people between {} and {} near floor {} -> {}".format(Persons, StartTime, EndTime, Floor, roomNumber))
        # print("Room Number is {}".format(roomNumber))
        return roomNumber


# Input
data_file = "C:/Users/pruth/Desktop/rooms.txt"

delimiter = ","
columnCount = getNumberofColumns(data_file, delimiter)
column_names = [i for i in range(0, columnCount - 1)]   # Generate column names (will be 0, 1, 2, ..., largest_column_count - 1)

# Read csv
df = pandas.read_csv(data_file, header=None, delimiter=delimiter, names=column_names)
cleanDF = cleanData(df)
filterRoom(cleanDF, 5, 8, "10:30", "11:30")
