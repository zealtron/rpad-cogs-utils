import argparse
import json
import os

from padguide.encoding import encode, decode
from padguide.extract_utils import dump_table, fix_table_name
import pymysql


def parse_args():
    parser = argparse.ArgumentParser(description="Echos PadGuide database data", add_help=False)

    inputGroup = parser.add_argument_group("Input")
    inputGroup.add_argument("--db_config", help="JSON database info")
    inputGroup.add_argument("--db_table", help="PadGuide table name")
    inputGroup.add_argument("--data_arg", help="PadGuide API data param")

    inputGroup.add_argument("--raw_file", help="Raw JSON file")

    return parser.parse_args()


def encode_data_response(data):
    output = {
        'resCode': '9000',
        'resMessage': 'OK',
        'data': encode(data),
    }
    return json.dumps(output)


def extract_tstamp(data_arg):
    decoded = decode(data_arg)
    decoded_js = json.loads(decoded)
    return int(decoded_js['TSTAMP'])


def load_file_json(file_name):
    with open(file_name) as f:
        return json.load(f)


def load_from_db(db_config, db_table, data_arg):
    connection = pymysql.connect(host=db_config['host'],
                                 user=db_config['user'],
                                 password=db_config['password'],
                                 db=db_config['db'],
                                 charset=db_config['charset'],
                                 cursorclass=pymysql.cursors.DictCursor)

    sql = 'SELECT * FROM {}'.format(db_table)
    if data_arg:
        tstamp = extract_tstamp(data_arg)
        sql += ' WHERE tstamp >= {}'.format(tstamp)
    print(sql)

    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dump_table(db_table, cursor)

    connection.close()
    return data


def main(args):
    if args.raw_file:
        data = load_file_json(args.raw_file)
    elif args.db_config and args.db_table:
        with open(args.db_config) as f:
            db_config = json.load(f)
        data = load_from_db(db_config, args.db_table, args.data_arg)
    else:
        raise RuntimeError('Incorrect arguments')

    print(encode_data_response(json.dumps(data)))


if __name__ == "__main__":
    args = parse_args()
    main(args)