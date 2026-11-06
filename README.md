# GCP Forex Data Collection Pipeline

![GCP](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat-square&logo=googlecloud&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9-3776AB?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Apache Beam](https://img.shields.io/badge/Apache_Beam-FF6F00?style=flat-square&logo=apache&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-669DF6?style=flat-square&logo=googlebigquery&logoColor=white)

An event-driven data pipeline on **Google Cloud Platform** that collects the **CHF/EUR exchange rate** every day, streams it through **Pub/Sub**, processes it with **Apache Beam on Dataflow** and lands it in a **BigQuery** data warehouse for reporting in **Looker Studio**.

![Pipeline architecture](gcp_daily_collect_pipeline.png)

## Architecture

| Step | Component | Role |
| --- | --- | --- |
| 1 | **Cloud Scheduler** | Triggers the pipeline once a day with an HTTP GET request |
| 2 | **Flask API** (Docker, gunicorn) | Fetches the latest CHF/EUR rate from the [currency-api](https://github.com/fawazahmed0/currency-api), keeps a history file in **Cloud Storage** and publishes the record to Pub/Sub |
| 3 | **Pub/Sub** | Decouples ingestion from processing (`forex-topic`) |
| 4 | **Apache Beam / Dataflow** | Streaming job that reads the topic, parses the JSON messages and appends them to BigQuery |
| 5 | **BigQuery** | Data warehouse (`forex_dataset.chfeur_daily`) with views prepared for reporting |
| 6 | **Looker Studio** | Dashboard on top of the BigQuery views |

## Repository structure

```
.
├── chfeur_forex_request.py     # Flask app: collect the rate, archive it in GCS, publish to Pub/Sub
├── forex-pubsub-subscriber.py  # Apache Beam streaming job: Pub/Sub → BigQuery (Dataflow runner)
├── Dockerfile                  # Container image for the Flask collector
└── gcp_daily_collect_pipeline.png
```

## Deploying

### Prerequisites

- A GCP project with Cloud Storage, Pub/Sub, Dataflow, BigQuery and Cloud Scheduler enabled
- A Cloud Storage bucket (`forex_api_bucket` in the code) and a Pub/Sub topic `forex-topic`
- The [gcloud CLI](https://cloud.google.com/sdk/docs/install) and Docker

> The project ID, bucket name and service-account key path are hard-coded in `chfeur_forex_request.py`. Update them for your own project before deploying.

### 1. Build and deploy the collector

The container listens on port `8080` on `0.0.0.0`, as Cloud Run expects.

```bash
docker build -t gcr.io/<PROJECT_ID>/forex-collector .
docker push gcr.io/<PROJECT_ID>/forex-collector
gcloud run deploy forex-collector --image gcr.io/<PROJECT_ID>/forex-collector --region <REGION>
```

### 2. Schedule the daily collection

Create a **Cloud Scheduler** job that sends a daily HTTP GET request to the service URL (`/`).
The `/reset` endpoint clears the history file kept in Cloud Storage.

### 3. Start the streaming job

```bash
python forex-pubsub-subscriber.py
```

This launches the Beam pipeline on **Dataflow**. It creates the BigQuery table `forex_dataset.chfeur_daily` (schema `date:string, eur:float`) if needed and appends every new message.

## Credits

Exchange rates come from the free [currency-api](https://github.com/fawazahmed0/currency-api) by [fawazahmed0](https://github.com/fawazahmed0).
