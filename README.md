# GCP forex data collect pipeline
In this project we implement a Data collection pipeline in GCP collecting forex data on the CHF/EUR pair
We have the following component :
- A Cloud Scheduler triggering the pipeline every day though an HTTP GET request
- A Containerized Flask API collecting the data from a Forex API and publishing the data to a PubSub topic
- A Cloud PubSub stream processing service collecting the data
- An ETL Apache Beam script to subscribe to our PubSub topic, transforming the data and sinking it to a BigQuery Datawarehouse (i.e. forex-pubsub-subscriber.py which is in an Apache Beam Jupyter Notebook)
- A BigQuery datawarehouse preparing views for Data visualization
- A Data visualization tool with Looker Studio
![alt text](https://github.com/rbgt/GCP_forex_data_collect_pipeline/blob/main/gcp_daily_collect_pipeline.png)

The Dockerfile containerize our application in an Image to collect the data from the Forex API and publishing it to PubSub

This pipeline is scheduled to collect the data daily from the free API : https://github.com/fawazahmed0/currency-api#readme

Credits to **![ fawazahmed0 ](https://github.com/fawazahmed0)** for this free API which made this project possible.

Main points to create the containerized app on GCP : 
1. Test the API with a Python Script 
2. Create the Flask API and use gunicorn WSGI
3. Containerize the API and make sure it listens to port 8080 on host 0.0.0.0
4. Build the image, tag it with the "gcr.io/(projectID)/(image name)"
5. Push the tagged image (goes automatically to the GCP Container registry)