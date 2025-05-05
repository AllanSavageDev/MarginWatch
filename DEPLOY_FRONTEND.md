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
