# netdata-ml-apps

App is available to play with it at: https://andrewm4894-netdata-ml-apps-home-uvftgr.streamlit.app/

## Running locally

```bash
# clone repo
gh repo clone andrewm4894/netdata-ml-apps

# cd into repo
cd netdata-ml-apps

# make python env
python3 -m venv venv

# activate env
source venv/bin/activate

# install requirements
pip install -r requirements.txt

# run app
streamlit run Home.py
```

## Running on Docker

### Build image

```bash
docker build -t netdata-ml-apps .
```

### Run container

```bash
# run via docker locally
docker run -p 8501:8501 netdata-ml-apps
```

```bash
# pull image and run via docker
docker run -d --network="host" --name=netdata-ml-apps \
  -p 8501:8501 \
  --restart unless-stopped \
  andrewm4894/netdata-ml-apps:latest
```

### Docker push

```bash
docker tag netdata-ml-apps:latest andrewm4894/netdata-ml-apps:latest
docker push andrewm4894/netdata-ml-apps:latest
```
