import apache_beam as beam
from apache_beam.runners import DataflowRunner
from apache_beam.options import pipeline_options
from apache_beam.options.pipeline_options import GoogleCloudOptions, PipelineOptions
from apache_beam.io.gcp.bigquery import BigQueryDisposition, WriteToBigQuery
from apache_beam.io.gcp.pubsub import ReadFromPubSub
from apache_beam.runners import DataflowRunner
import google.auth
import json

project = google.auth.default()[1]
# PubSub topic
topic = "projects/{}/topics/forex-topic".format(project)
# BigQuery table & schema
table = "{}:forex_dataset.chfeur_daily".format(project)
schema = "date:string,eur:float" # !! Faire attention à respecter le nom des colonnes avec ceux en input dans le topic !!
# Cloud Storage bucket
bucket = "gs://forex_api_bucket"

region="us-central1"

options = PipelineOptions(
    flags={},
    streaming=True,
    project=project,
    region=region,
    staging_location="%s/staging" % bucket,
    temp_location="%s/temp" % bucket
)

p = beam.Pipeline(DataflowRunner(), options=options)

elements = (p | "Read Topic" >> ReadFromPubSub(topic=topic)
              | "To Dict" >> beam.Map(json.loads)) # Example message: {"name": "carlos", 'score': 10, 'timestamp': "2020-03-14 17:29:00.00000"}

elements | "Write To BigQuery" >> WriteToBigQuery(table=table, schema=schema,
                              create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
                              write_disposition=BigQueryDisposition.WRITE_APPEND)

pipeline = p.run()

# pipeline.cancel() # A lancer dès qu'on souhaite arrêter la pipeline