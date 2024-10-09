Recently, I attended the JuaraGCP class on Cloud Infrastructure. I chose this course as part of continuing my learning path toward earning the Google Cloud Machine Learning Engineer Certification. To make it more 'hands-on', I created a mini web project called 'Image Search,' where users can search for images in a database with similar features.

The frameworks used are:
1. **Weaviate** ㅡ used as both a vector database and a search engine. I vectorize my images using the img2vec-neural module, which is a Weaviate module that converts images to vectors. \
   Note: I'm using the ResNet50 model with Keras. However, when running it on my local PC, I use ResNet50 with Torch. The results with ResNet50 and Torch are excellent. Since ResNet50 with Torch is quite large (around 7GB) and requires a GPU, it wasn’t compatible when I deployed it on a Compute Engine instance with only 8GB of CPU memory and no GPU. Therefore, for the web app deployment, I switched to ResNet50 with Keras.
2. **FastAPI** ㅡ used as backend.
3. **React.js** ㅡ used as frontend.
4. **Postgres** ㅡ used as database for logging.

Here are the steps:
1. After building the code, first ensure you're logged into gcloud via the CLI. Set the project you want to use.
```
# login
gcloud auth login

# see the list of projects
gcloud projects list

# set the project
gcloud config set project PROJECT_ID

# to view the current configuration details
gcloud config list
```
2. Create an instance in **Compute Engine** and run both Weaviate and the PostgreSQL database.
3. Don’t forget to configure the **firewall** rules for the Weaviate and PostgreSQL database ports so they can be accessed by your program.
4. Set up the database configuration in your code.
5. Create a cluster in **Kubernetes Engine**:
```
# create a cluster
gcloud container clusters create-auto CLUSTER_NAME --location=LOCATION --project=PROJECT_ID --service-account=SERVICE_ACCOUNT_EMAIL
```
6. CreateCreate a GitHub workflow. Wait until everything is done. To verify if the program has been deployed:
```
kubectl get pods
```
If the status is RUNNING, the deployment is complete.

7. Repeat the above steps for both the backend and frontend (code frontend can be access: [frontend](https://github.com/rzkamalia/image-search-fe)).
8. After that, set up ingress so that your app can be accessed from outside the network:
```
# set up ingress
kubectl apply -f ingress-config.yaml
```
To verify that ingress has been set up:
```
kubectl get ingress
```
Wait up to 15 minutes, then access the host in the ADDRESS field.
