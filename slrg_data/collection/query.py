import json
import csv
from . import common


def query_db(database, sql, out_file, format_):
    try:
        database.connect(format_=format_)
        results = database.query(sql)

        if format_ == 'j':
            with open(out_file, 'w') as file:
                json.dump(results, file)

        elif format_ == 'c':
            with open(out_file, 'w', newline='') as csvfile:
                wr = csv.writer(csvfile, delimiter=',')
                wr.writerows(results)

        return "Successfully wrote to " + out_file

    except common.DatabaseError as error:
        return str(error)

    finally:
        database.close()
