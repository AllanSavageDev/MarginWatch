# Frontend Deployment Instructions (EC2)

This builds and updates the static frontend site served by Nginx.

## Steps

0. Commit local code
    cd ~/MarginWatch

    # Add and commit changes
    git add .
    git commit -m "Finalize frontend static build setup and deployment docs"
    git push




1. SSH into the EC2 instance as `allan`

2. Navigate to the project root:

   cd ~/MarginWatch

3. Pull the latest code:

   git pull

4. Build the frontend:

   cd frontend
   npm install        # only needed after dependency changes
   npm run build      # uses output: 'export' in next.config.ts

5. Verify build output:

   ls -l out

   You should see files like `index.html`, `favicon.ico`, etc.

## Nginx Notes

- Docker Compose must include this mount:

      volumes:
        - ./frontend/out:/usr/share/nginx/html:ro

- No need to restart Nginx or the container — the files are served live from the host

## Done

You are now serving the latest frontend build via Nginx.



## rebuild the image and start the containers

    /MarginWatch$ docker-compose down
    /MarginWatch$ docker-compose up --build -d


## See whats up after rebuild and up

    allan@ip-172-31-3-128:~/MarginWatch$ docker ps
    CONTAINER ID   IMAGE                 COMMAND                  CREATED          STATUS          PORTS                                       NAMES
    f19ec004f7b9   nginx                 "/docker-entrypoint.…"   30 seconds ago   Up 29 seconds   0.0.0.0:80->80/tcp, :::80->80/tcp           marginwatch-nginx
    b6f45e9d5d7b   marginwatch_backend   "sleep infinity"         30 seconds ago   Up 30 seconds                                               marginwatch-backend
    25e62b19b156   postgres              "docker-entrypoint.s…"   31 seconds ago   Up 30 seconds   0.0.0.0:5435->5432/tcp, :::5435->5432/tcp   marginwatch-postgres



