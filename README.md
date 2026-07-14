# MPP Tools

A collection of Python tools to extract data from [Mon Petit Placement](https://www.monpetitplacement.fr) and generate a personal portfolio performance report.

![Screenshot](.resources/screen.jpg)

❤️ Made in France

## 🔒 Privacy Notice

- These scripts process and collect portfolio data locally on your machine.  
- No data is sent, shared, or transmitted to any external service.  
- All collected information is stored locally in a SQLite database.


## 📝 Overview

**MPP Tools** is composed of two main modules:

- **Extract Data**: Retrieves and stores financial data from the MPP API
- **Build Report**: Generates an HTML report from the collected data

### 📁 Project Structure

```
mpp-tools/
├── src/
│ ├── build_report/
│ └── extract_data/
├── run.sh
└── setup.sh
```

## ⚙️ Prerequisites

- Python 3.10 or higher
- Nginx (for deployment)
- Certbot (for SSL certificates)

## 🚀 Installation

Clone the repository and run the `setup.sh` script:

```bash
git clone https://github.com/dhabierre/mpp-tools.git

cd mpp-tools

git fetch --tags
git checkout 1.0.2
```

```bash
# Edit the `setup.sh` script
# Update the `BASE` variable to match your installation path

nano setup.sh

chmod +x setup.sh
./setup.sh

# Output:
# 
# 🔎 === Setup started ===
# 
# 🏗️ === Setup extract_data ===
# 🐍 Creating virtual environment...
# ⚡ Activating virtual environment...
# 📦 Checking dependencies...
# ✅ extract_data setup completed.
# 
# 🏗️ === Setup build_report ===
# 🐍 Creating virtual environment...
# ⚡ Activating virtual environment...
# 📦 Checking dependencies...
# ✅ build_report setup completed.
# 
# 🔐 Checking permissions...
# ✅ Added execute permission to run.sh
# 
# 🎉 === Installation completed successfully ===
```

Configure both modules by creating their `.env` files:

```bash
# 1. Extract Data Module
# Create the `.env` file and configure API credentials and storage paths

cp src/extract_data/.env.sample src/extract_data/.env
nano src/extract_data/.env

# 2. Build Report Module
# Create the `.env` file and configure report generation options

cp src/build_report/.env.sample src/build_report/.env
nano src/build_report/.env
```

## ▶️ Usage

### 🖥️ Manual Execution

```bash
BASE="/home/ubuntu/mpp-tools" # Change to your installation path

"$BASE/src/extract_data/venv/bin/python" "$BASE/src/extract_data/main.py"

# Output:
#
# 2026-07-10 21:29:01,668 | INFO | 🔄 [1 /6] Extracting 'Capital' data...
# 2026-07-10 21:29:01,686 | INFO | ✅ [1 /6] Data 'Capital' extracted.
# 2026-07-10 21:29:01,686 | INFO | 🔄 [2 /6] Extracting 'Capital Trends' data...
# 2026-07-10 21:29:01,722 | INFO | ✅ [2 /6] Data 'Capital Trends' extracted (1507).
# 2026-07-10 21:29:01,723 | INFO | 🔄 [3 /6] Extracting 'Products' data...
# 2026-07-10 21:29:01,850 | INFO | ✅ [3 /6] Data 'Products' extracted (56).
# 2026-07-10 21:29:01,850 | INFO | 🔄 [4 /6] Extracting 'Positions' data...
# 2026-07-10 21:29:02,232 | INFO | ✅ [4 /6] Data 'Positions' extracted (17).
# 2026-07-10 21:29:02,232 | INFO | 🔄 [5 /6] Extracting 'Product Trends' data...
# 2026-07-10 21:29:25,076 | INFO | ✅ [5 /6] Data 'Product Trends' extracted (53233).
# 2026-07-10 21:29:25,076 | INFO | 🔄 [6 /6] Extracting 'Invest Orders' data...
# 2026-07-10 21:29:26,418 | INFO | ✅ [6 /6] Data 'Invest Orders' extracted (589).
# 2026-07-10 21:29:28,255 | INFO | 🏁 Data stored (db: /home/ubuntu/mpp-tools/src/extract_data/mpp.sqlite3)

"$BASE/src/build_report/venv/bin/python" "$BASE/src/build_report/main.py"

# Output:
# 
# 2026-07-10 21:31:43,918 | INFO | 🔄 Building report...
# 2026-07-10 21:31:44,143 | INFO | ✅ Report written (path: /home/ubuntu/mpp-tools/src/build_report/wwwroot/report.html)

```

### ⏰ Scheduled Execution

This step allows you to automate script execution.

```bash
# Edit the `run.sh` script and adjust the `BASE` variable
nano run.sh
```

Execute the script to validate the setup (`.env` files, paths, etc):

```bash
chmod +x run.sh
./run.sh
ls -al logs
```

To set up the cron job:

```bash
crontab -e

# Add the following line:
# 0 10,14,20 * * * /home/ubuntu/mpp-tools/run.sh
```

## 🌐 Deployment [Optional]

### 🖥️ Server Preparation

```bash
# Create the web directory

sudo mkdir -p /var/www/mpp
sudo chown -R www-data:www-data /var/www/mpp

# Copy all resources (report.html, styles.css, ...)
cp src/build_report/wwwroot/* /var/www/mpp

# Set `DB_PATH` to /var/www/mpp/report.html
nano src/build_report/.env
```

### ⚡ Nginx Configuration

Create the Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/mpp
```

Add the following configuration:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name mpp.yourdns.org;
    root /var/www/mpp;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/mpp /etc/nginx/sites-enabled/
sudo nginx -t
sudo nginx -s reload
```

### 🔒 SSL Certificate with Certbot

```bash
sudo certbot --nginx
```

### 🚀 SSL and HTTP/2 Configuration

Edit the Nginx configuration again:

```bash
sudo nano /etc/nginx/sites-available/mpp
```

Add `http2` to the listen directives:

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2 ipv6only=on;
    # ...
}
```

Apply the changes:

```bash
sudo nginx -t
sudo nginx -s reload
sudo service nginx restart
```

### 👤 User Permissions

```bash
sudo usermod -aG www-data ubuntu
sudo chmod 775 /var/www/mpp
newgrp www-data
```

## ⚖️ License

MIT — see [LICENSE](LICENSE).
