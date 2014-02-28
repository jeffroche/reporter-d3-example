from dropbox import client
import os
import json
from datetime import datetime, timedelta
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.cors import CORSConfiguration


def convert_date_to_iso(objc_date):
    """Converts date from Obj-C format to iso format
    ref: https://twitter.com/aaronpk/status/432556118275936256
    """
    d = timedelta(seconds=objc_date) + datetime(2001, 1, 1)
    return d.isoformat()


def aggregate_data(dropbox_token, reporter_folder='/Apps/Reporter-App'):
    """Combines Reporter data from all the JSON files in the folder
    """
    db = client.DropboxClient(dropbox_token)
    reporter_meta = db.metadata(reporter_folder)
    data = []
    for item in reporter_meta['contents']:
        file_name_with_extension = os.path.basename(item['path'])
        file_name, extn = os.path.splitext(file_name_with_extension)
        if not item['is_dir'] and extn == '.json':
            f = db.get_file(item['path'])
            raw = json.loads(f.read())
            for s in raw['snapshots']:
                if isinstance(s['date'], float):
                    # Reporter used to output Obj-C timestamps
                    date = convert_date_to_iso(s['date'])
                else:
                    # Now they've switched to ISO format
                    date = s['date']
                data.append({
                    'date': date,
                    'location': s['location'],
                    'weather': s['weather']})
    return data


def send_to_s3(data, aws_access_key, aws_secret_key, s3_bucket,
               file_name='data.json'):
    """Sends the reporter data to S3

    :param data: list of dicts
    :param aws_access_key:
    :param aws_secret_key:
    :param s3_bucket:
    :param file_name:
    """
    conn = S3Connection(aws_access_key, aws_secret_key)
    bucket = conn.get_bucket(s3_bucket)
    config = CORSConfiguration()
    config.add_rule('GET', '*')
    bucket.set_cors(config)
    k = Key(bucket)
    k.key = file_name
    k.set_contents_from_string(json.dumps(data))
    k.set_acl('public-read')


def aggregate_data_to_file(file,
                           dropbox_token=os.environ.get('DROPBOX_TOKEN')):
    """Aggregates the Reporter data in Dropbox to a local JSON file

    :param file: path to the local json file
    :param dropbox_token: Dropbox API token
    """
    data = aggregate_data(dropbox_token)
    f = open(file, 'w')
    f.write(json.dumps(data))


def s3sync(s3_filename, dropbox_token=os.environ.get('DROPBOX_TOKEN'),
           aws_access_key=os.environ.get('AWS_ACCESS_KEY_ID'),
           aws_secret_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
           s3_bucket=os.environ.get('S3_BUCKET')):
    """Aggregates the Reporter data in Dropbox and uploads the data to
    S3
    :param s3_filename: filename to save to on S3
    """
    data = aggregate_data(dropbox_token)
    send_to_s3(data, aws_access_key, aws_secret_key, s3_bucket,
               file_name=s3_filename)
