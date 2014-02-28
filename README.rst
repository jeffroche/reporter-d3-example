An experiment using `Reporter <http://www.reporter-app.com/>`_.

Requirements
------------

- Dropbox sync enabled in Reporter
- A Dropbox API token
- An AWS account

Installation
------------

::

  $ pip install -r requirements.txt

Set the following environmental variables::

  $ export DROPBOX_TOKEN=token
  $ export S3_BUCKET=my-bucket
  $ export AWS_ACCESS_KEY_ID=key
  $ export AWS_SECRET_ACCESS_KEY=secret_key

Usage
-----

To aggregate all the reporter JSON files into one file, run::

  $ python
  >>> import reporter
  >>> reporter.aggregate_data_to_file('path/to/local.json')

To aggregate all the reporter JSON files and upload to S3, run::

  $ python
  >>> import reporter
  >>> reporter.s3sync('file.json')

Currently only the location and weather data is extracted from the reporter JSON data but other parameters can easily be added.
