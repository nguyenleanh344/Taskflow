# TaskFlow API

TaskFlow API is a project, task, comment, and project-member management backend built with FastAPI, PostgreSQL, Redis, and async SQLAlchemy.

## Requirements

- Python 3.12+
- Docker Desktop
- Docker Compose

## Run Locally

Create a virtual environment and install the dependencies:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Start PostgreSQL and Redis:

```powershell
docker compose up -d postgres redis
```

Start the API:

```powershell
python -m uvicorn app.main:app --reload
```

The API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Code Quality and Tests

```powershell
ruff check .
ruff format --check .
pytest -q
```

Run tests with coverage:

```powershell
pytest -q tests --ignore=tests/integration --cov=app --cov-report=term-missing --cov-report=xml:coverage.xml
```

## Build the Docker Image

```powershell
docker build -t taskflow-api:latest .
```

## CI with Jenkins

The `Jenkinsfile` defines a pipeline that automatically:

1. Installs the dependencies.
2. Runs Ruff and measures test coverage.
3. Runs unit tests and integration tests with PostgreSQL and Redis.
4. Builds the Docker image.
5. Pushes the image to Docker Hub.

The Jenkins job can use Poll SCM or a GitHub webhook to build automatically when a new commit is pushed to the `main` branch.

### Run Jenkins Locally with Docker

Build the custom Jenkins image. It includes Python, Docker CLI, and Docker Compose:

```powershell
docker build -t taskflow-jenkins:latest -f docker/jenkins/Dockerfile .
```

Create the Jenkins container and persist its jobs and plugins using the `jenkins_home` volume:

```powershell
docker run -d --name jenkins --user root --restart unless-stopped `
  -p 8080:8080 -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  -v /var/run/docker.sock:/var/run/docker.sock `
  taskflow-jenkins:latest
```

Verify the tools inside Jenkins:

```powershell
docker exec jenkins python3 --version
docker exec jenkins docker --version
docker exec jenkins docker compose version
```

Open Jenkins at `http://localhost:8080` and create a Pipeline job with:

- Definition: `Pipeline script from SCM`
- SCM: `Git`
- Repository: `https://github.com/nguyenleanh344/Taskflow.git`
- Branch: `*/main`
- Script Path: `Jenkinsfile`

To push images to Docker Hub, create a Jenkins credential with type `Username with password`:

- ID: `dockerhub-creds`
- Username: your Docker Hub username
- Password: a Docker Hub access token with `Read & Write` permission

Never commit passwords, access tokens, or the `.env` file to Git.

## Local Kubernetes Deployment with Minikube

The Kubernetes manifests are located in the `k8s/` directory. Docker Desktop, `kubectl`, and Minikube are required.

Start the cluster:

```powershell
minikube start --driver=docker
kubectl config use-context minikube
kubectl get nodes
```

Deploy the resources in this order:

```powershell
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
```

Check the resources:

```powershell
kubectl get pods -n taskflow
kubectl get deployments -n taskflow
kubectl get services -n taskflow
kubectl rollout status deployment/taskflow-api -n taskflow
```

Open the API Swagger page:

```powershell
minikube service taskflow-api -n taskflow --url
```

Keep this terminal open, copy the returned URL, and append `/docs`, for example:

```text
http://127.0.0.1:56809/docs
```

Alternatively, use port forwarding:

```powershell
kubectl port-forward service/taskflow-api 8000:8000 -n taskflow
```

Then open `http://localhost:8000/docs`.

Scale the API to multiple Pods:

```powershell
kubectl scale deployment taskflow-api --replicas=3 -n taskflow
kubectl get pods -n taskflow
```

## Prometheus Monitoring

The API exposes Prometheus metrics at `/metrics`. The Kubernetes setup includes a Prometheus Deployment that scrapes the API through the `taskflow-api` Service.

Apply the Prometheus resources after deploying the API:

```powershell
kubectl apply -f k8s/prometheus-config.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl get pods -n taskflow
```

Open the Prometheus UI:

```powershell
minikube service prometheus -n taskflow --url
```

In Prometheus, open **Status > Target health** and verify that the `taskflow-api` target is `UP`. You can also query metrics such as `http_requests_total`.

In the current Minikube setup, PostgreSQL and Redis use `emptyDir`, so their data is lost when the Pods are deleted. This configuration is intended for learning; production should use PersistentVolumes or managed PostgreSQL and Redis services.
