import json
import csv
from . import common


def query_db(database, sql, file, format_):
    try:
        database.connect(format_=format_)
        results = database.query(sql)

        if format_ == 'j':
            with open(file, 'w') as file:
                json.dump(results, file)

        elif format_ == 'c':
            with open(file, 'w', newline='') as csvfile:
                wr = csv.writer(csvfile, delimiter=',')
                wr.writerows(results)

        return "Success"

    except common.DatabaseError as error:
        return str(error)

    finally:
        database.close()
