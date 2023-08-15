# gcp-advisor

## Introduction
This project helps Google Cloud customers check whether their projects have hidden dangers and what can be optimized in terms of security, cost, reliability, performance, and operational excellence, so as to achieve stable and reliable business.

## How to setup
1. Git clone this repo in your Google Cloud Cloud Shell.
2. Install the required Python dependencies with following command:
```
pip install -r requirements.txt
```

## Try it out
1. Run gcp advisor

make sure you have permission to do this
```
chmod +x bin/gcp-advisor
./bin/gcp-advisor --projects project_1_id,project_2_id
```
2. check result
```
cat check_result.csv
```
<img width="702" alt="image" src="https://github.com/hellof20/gcp-advisor/assets/8756642/cdd1a397-3cac-4498-bb18-d1f546771bf7">
