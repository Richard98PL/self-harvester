import mysql.connector as mysql

db = {}

def dbInit():
    global db
    db = mysql.connect(
        host = "",
        user = "",
        passwd = "",
        database = ""
        
    )
    cursor = db.cursor(buffered=True)
    cursor.execute("SHOW DATABASES")

    # for x in cursor:
        # print(x) 

def dbGetLogs():
    global db
    if db == {}:
        dbInit()

    print(db)
    cursor = db.cursor(buffered=True)

    cursor.execute("SELECT Id,Log FROM Logs ORDER BY Id DESC")

    result = cursor.fetchall()

    for log in result:
        print(log)

def dbInsertLog(log):
    global db
    if db == {}:
        dbInit()

    cursor = db.cursor(buffered=True)

    log = log.replace("\'",'"')
    dml = "INSERT INTO logs (log) VALUES ('" + log + "')"
    cursor.execute(dml)
    db.commit()
    print(cursor.rowcount, " records inserted.")

def getKeys():
    global db
    if db == {}:
        dbInit()

    cursor = db.cursor(buffered=True)

    cursor.execute("SELECT * from secret_keys limit 1")

    keys_json = {}

    result = cursor.fetchall()
    descriptor = 0
    for value in result:
        for tuple in value:
            # print(str(next(iter(cursor.description[descriptor]))) + 
            # ' -> ' + str(value[descriptor]))
            keys_json[str(next(iter(cursor.description[descriptor])))]  = str(value[descriptor])
            descriptor = descriptor + 1
    return keys_json
    
if __name__ == "__main__":
    # dbInsertLog('testlog')
    # dbGetLogs()
    getKeys()