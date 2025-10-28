# MarginWatch

Python-based project for monitoring and analyzing trading margin levels.

Uses Interactive Brokers live publilshed data from the website of refernce.
Writes the margin data to a postgress table for later query analysis.

Full Docker system here with all necessary pieces in place with the standard docker-compose

# MarginWatch Command Reference

This file contains all the key commands used during your EC2/Docker-based MarginWatch setup and testing session.

---

## 🔧 Docker & Compose

```bash
# Stop all containers
docker ps -q | xargs docker stop

# Prune stopped containers
docker container prune -f

# Prune networks and volumes (careful — nukes volumes!)
docker network prune -f
docker volume prune -f

# Remove unused images (optional cleanup)
docker image prune -a -f

# Rebuild containers cleanly without destroying volumes
docker-compose down --remove-orphans
docker-compose up --build -d

# Rebuild AND nuke everything (DB included — use with caution)
docker-compose down --volumes --remove-orphans
docker builder prune -af
docker image rm marginwatch_backend || true
docker-compose up --build --force-recreate -d
```

---

## 🐳 Docker Exec

```bash
# Enter the container
docker exec -it marginwatch-backend bash

# Run the fetch script inside the container
docker exec marginwatch-backend bash fetch_IB_margin_file.sh

# Run main.py (with or without args)
docker exec marginwatch-backend python main.py
docker exec marginwatch-backend python main.py IB_margin_files/2025-05-01-00-22-28-margin_futures_fops.html

# Run your full workflow
docker exec marginwatch-backend bash run_all.sh
```

---

## 📝 Git Workflow

```bash
# Stage all changes
git add .

# Commit with a message
git commit -m "Update message here"

# Push to GitHub
git push origin main

# Pull changes on EC2
git pull origin main
```

---

## 🕓 Cron Setup (CST after timezone switch)

```bash
# Edit crontab for the current user
crontab -e

# Example cron line for 6AM and 6PM CST
0 6,18 * * * docker exec marginwatch-backend bash run_all.sh >> ~/marginwatch-cron.log 2>&1
```

---

## 🔍 Debug & Inspection

```bash
# Check what's running
docker ps

# Check if the file exists inside container
docker exec marginwatch-backend ls /app/IB_margin_files

# See script contents inside container
docker exec -it marginwatch-backend cat run_all.sh
docker exec -it marginwatch-backend cat main.py | grep nargs
```

---

## ✅ Summary

This markdown file serves as a quick reference for all the setup, debugging, and operational tasks used in the MarginWatch project on EC2 with Docker Compose.
