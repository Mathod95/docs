---
title: "Modern Load Testing for Engineering Teams with k6 and Grafana"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://blog.prateekjain.dev/modern-load-testing-for-engineering-teams-with-k6-and-grafana-4214057dff65"
author:
  - "[[Prateek Jain]]"
---
<!-- more -->

[Sitemap](https://blog.prateekjain.dev/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*yRN7pY2_Ayb0ojRzJc1WSg.png)

Load testing is an essential part of building robust, scalable applications. It allows us to simulate real-world user traffic, identify performance bottlenecks, and ensure our systems can handle peak loads without breaking a sweat.

***Friends link for non-Medium members:*** [Modern Load Testing for Engineering Teams with k6 and Grafana](https://blog.prateekjain.dev/modern-load-testing-for-engineering-teams-with-k6-and-grafana-4214057dff65?sk=eacfbfbff10ed7feb24b7c97a3f72a93)

It’s not just about testing how much traffic your app can handle. It’s about building confidence, knowing your system won’t crumble during a spike, and that your infra decisions are backed by actual data, not guesswork.

> *If you enjoy content like this, feel free to connect with me on* ***X (***[***@PrateekJainDev***](https://x.com/PrateekJainDev)***)*** *and* ***LinkedIn (***[***in/prateekjaindev***](https://www.linkedin.com/in/prateekjaindev/)***)****.*

In this guide, we’ll set up a modern, code-driven load testing workflow using **k6**, run tests from an **AWS EC2 instance**, and visualise results in **Grafana** (Cloud or self-hosted). We’ll also automate the entire flow using **GitHub Actions**, so tests can be triggered regularly or on demand.

This setup is lightweight, easy to reproduce, and doesn’t require a massive investment to get started. Whether you’re a developer trying to validate a new feature or a DevOps engineer planning for production load, this setup will help you catch issues early and plan better.

Before jumping into setup, let’s understand why load testing matters

## Why Load Testing Matters?

Before we dive into the setup, let’s take a moment to understand why load testing is so important.

Load testing simulates real-world user traffic to test how your application holds up under stress. It answers critical questions like:

- Can my app handle 1,000 users at once without crashing?
- Where are the performance choke points
- How does my system behave during a traffic spike?

The benefits are clear:

- **Avoid Downtime**: Identify and resolve issues before they impact users.
- **Optimise Performance**: Pinpoint slow APIs or resource hogs.
- **Plan Capacity**: Scale infrastructure with confidence.
- **Ship with Confidence**: Deploy knowing your app is ready for the real world.

Skipping load testing is like launching a rocket without checking the fuel, risky and likely to crash. In today’s microservices and cloud-native world, load testing isn’t a nice-to-have; it’s essential.

## Traditional Tools

Traditionally, tools like **JMeter**, **Gatling**, and **LoadRunner** ruled load testing. They’re powerful but come with baggage:

- **Steep Learning Curve**: JMeter’s XML scripting and dated UI feel like a time machine to the 90s.
- **Heavy Setup**: LoadRunner’s pricey licenses and complex infrastructure scare off smaller teams.
- **CI/CD Friction**: Integrating these into modern pipelines is often difficult and doesn’t fit well.
- **Developer-Unfriendly**: Writing tests often requires niche expertise, leaving developers on the sidelines.

These tools were built for a pre-DevOps era. Modern workflows demand something leaner, scriptable, and collaborative.

## Why k6?

[k6](https://k6.io/) is an open-source load testing tool by **Grafana Labs**, built for modern engineering teams. It’s lightweight, code-first, and designed with DevOps and developers in mind. Here’s why it’s a great fit:

- **JavaScript-Based**: Write tests in JavaScript, a language most developers already use.
- **CLI-Driven**: No bulky GUIs, just clean terminal commands and simple scripting.
- **CI/CD Native**: Works seamlessly with GitHub Actions, Jenkins, GitLab CI, and others.
- **Flexible Outputs**: Export metrics to Prometheus Remote Write, push directly to Grafana dashboards, or use other formats like JSON, InfluxDB, or CloudWatch for versatile observability.
- **Modular and Scalable**: Create reusable test scripts and scale testing with minimal setup.

k6 makes load testing as version-controlled, automated, and collaborative as your infrastructure code.

## Requirements

To follow along, you’ll need:

- An **AWS account** for an EC2 instance to run k6 tests.
- A **Grafana Cloud account** (free tier works) *or* a **self-hosted Grafana and Prometheus setup**.
- A **GitHub account** for storing test scripts and automating with GitHub Actions.

Now let’s jump into the setup

## Step 1: Set Up an EC2 Instance and Install k6

We’ll use an AWS EC2 instance to run k6 tests, ensuring consistency and isolation from your local machine.

### Launch an EC2 Instance

1. Log in to your AWS Management Console.
2. Navigate to **EC2** → **Launch Instance**.
3. Choose **Ubuntu Server 24.04 LTS** AMI.
4. Select a **t3.small** instance (fine for small tests).
5. Set up a security group allowing **SSH (port 22)** from your IP.
6. Download the private key (.pem file) for SSH.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*YXy2yReTDWdPAwl_xLOK_A.png)

7\. Connect via terminal:

```c
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@<ec2-public-ip>
```

8\. Install k6 using the official repository:

```c
sudo apt update && sudo apt install -y gnupg software-properties-common
curl -s https://dl.k6.io/key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/k6-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt update
sudo apt install k6
```

9\. Verify the installation

```c
k6 version
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*wcHjZBt7r6gfMg0x-h8gEg.png)

## Step 2: Configure Prometheus Remote Write

1. **Access Grafana Cloud**:
2. Log in to grafana.com and go to your **Cloud Portal,** and click on **Details**
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*5huAQx_jVOFr995oQBuQLQ.png)

3\. Select **Prometheus** → **Details,** and Get Connection Details:

- Copy the **Remote Write URL** (e.g., [https://prometheus-prod-01-eu-west-XX.grafana.net/api/prom/push).](https://prometheus-prod-01-eu-west-0.grafana.net/api/prom/push\).)
- Note the **Instance ID** (e.g., 12345).

4\. Now log in to Grafana Cloud Console [**https://your-username.grafana.net/**](https://prateekjaindev.grafana.net/)

5\. Go to **Administration** → **Cloud access policies,** and click on **Create access policy,** Add **metrics:write** permission and save.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*5Me7LGw0CrODDEwpchfPUw.png)

6\. Create a **token** under the policy and save it for the next step (shown once).

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*9mKxDZH8sMm1DgbVncCFDg.png)

## Step 3: Run a Sample k6 Load Test

Let’s create a k6 test to simulate traffic and push metrics to your Prometheus endpoint, with flexible output options for observability.

1. On your EC2 instance, create loadtest.js:
```c
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 5, // 5 virtual users
  duration: '15s', // Run for 15 seconds
  tags: { project: 'demo' }, // Tag for filtering
};

export default function () {
  let res = http.get('https://test.k6.io');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1); // Wait 1 second between requests
}
```

2\. Execute the following commands to run the test and send metrics to the Prometheus remote endpoint:

```c
K6_PROMETHEUS_RW_SERVER_URL="https://<your-prom-url>" \
K6_PROMETHEUS_RW_USERNAME="<your-username-or-instance-id>" \
K6_PROMETHEUS_RW_PASSWORD="<your-api-key-or-password>" \
k6 run loadtest.js --out=experimental-prometheus-rw
```
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*WGruKVzXSEoGAUTbh5qvGA.png)

> *⚠️* ***Note****:* `*experimental-prometheus-rw*` *is currently an* ***experimental feature*** *in k6. Use it with caution in production environments.For more details and the latest updates, refer to the official documentation:* [*https://grafana.com/docs/k6/latest/results-output/real-time/prometheus-remote-write/*](https://grafana.com/docs/k6/latest/results-output/real-time/prometheus-remote-write/)

## Step 4: Visualise Metrics in Grafana

1. Log in to Grafana Cloud and go to **Drilldown** → **Metrics**
2. Select **Prometheus** data source, and add filter **project = demo**
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*SUlV0pYqC1X9ltyxszMSgQ.png)

Here you can visualise test results like request rates, response times, and error percentages in real time, perfect for understanding how your system performs under load.

> **Note:*****Drilldown*** *is a new Grafana feature. If you’re using an older version, you can view the same data using the* ***Explore*** *tab.*

### Understanding k6 Metrics

Interpreting your load test results effectively requires a solid understanding of k6’s built-in metrics. Here’s a breakdown of the most important ones:

- **http\_req\_duration**: The most critical metric. It captures the total time from sending a request to receiving the full response. This includes both network latency and server processing time. It’s your go-to metric for understanding user-perceived performance.
- **http\_req\_waiting**: Also known as *Time to First Byte (TTFB)*. It measures how long the system takes to start responding. High values usually indicate backend delays.
- **http\_req\_sending** and **http\_req\_receiving**: These measure how long it takes to send the request data and receive the response data. They’re typically small unless you’re uploading/downloading large payloads or encountering network throttling.
- **http\_req\_failed**: This metric tracks the failure rate of HTTP requests. It helps you identify how resilient your system is under pressure.
- **http\_reqs**: A simple counter that tells you how many HTTP requests were made during the test. Combine this with the test duration to get the request throughput.
- **vus** and **vus\_max**: These metrics indicate how many virtual users were active (`vus`) and the maximum that were active at any point (`vus_max`). Useful when scaling your tests and analysing concurrency behaviour.
- **iteration\_duration**: Tracks how long a full iteration of the test script takes. If your test logic is complex or involves a lot of setup/teardown, this metric becomes useful.
- **checks**: Represents custom checks you define in your test (e.g., validating status codes or response content). The metric shows how many checks passed vs. failed.

You can also define **custom metrics** using `Trend`, `Counter`, `Gauge`, and `Rate` to track domain-specific behaviours in your app.

Use these to follow the **RED methodology**:

- **Rate** → `http_reqs`
- **Errors** → `http_req_failed`
- **Duration** → `http_req_duration`

For a full list of available metrics and how to use them effectively, check the official reference: [https://grafana.com/docs/k6/latest/using-k6/metrics/reference/](https://grafana.com/docs/k6/latest/using-k6/metrics/reference/)

## Step 5: Automate with GitHub Actions

Once your scripts are ready and tested, the next logical step is to automate them. This ensures consistency, saves time, and makes it easier to run tests on demand or as part of your CI/CD pipeline.

In this step, we’ll automate load testing for two microservices `project_a` and `project_b`. All the scripts will live in a single repository under `/k6-scripts`. This single-repo setup keeps things simple and centralised for this demo, though separate repos per project are also a valid approach in larger systems.

### GitHub Action Workflow

Create a new workflow file at `.github/workflows/k6-loadtest.yml`:

```c
name: Run Load Test

# Define when and how this workflow runs
on:
  workflow_dispatch:  # Allows manual triggering from GitHub UI
    inputs:
      script_name:
        description: "Choose the load test script"
        required: true
        type: choice
        default: "project_a.js"
        options:
          - project_a.js  # Basic website load test
          - project_b.js  # Website navigation test
      vu_count:
        description: "Number of virtual users"
        required: false
        type: number
        default: 10
      duration:
        description: "Test duration (e.g., 30s, 1m, 5m)"
        required: false
        type: string
        default: "1m"

jobs:
  run-load-test:
    name: Run Load Test on EC2
    runs-on: ubuntu-latest  # GitHub-hosted runner
    
    steps:
      # Step 1: Checkout the repository to access test scripts
      - name: Checkout repository
        uses: actions/checkout@v3
      
      # Step 2: Transfer the selected test script to EC2
      # Uses SCP for secure file transfer
      - name: Copy test script to EC2
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.EC2_HOST }}  # EC2 instance hostname/IP
          username: ubuntu                # Default Ubuntu username
          key: ${{ secrets.EC2_SSH_KEY }} # SSH private key for authentication
          source: k6-scripts/${{ github.event.inputs.script_name }}  # Source file in repo
          target: /home/ubuntu/k6-loadtests/  # Destination directory on EC2
          strip_components: 1  # Removes parent directory from source path
          
      # Step 3: Verify the script was transferred correctly
      # This helps with debugging any file transfer issues
      - name: Verify script transfer
        uses: appleboy/ssh-action@v0.1.10
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            echo "Verifying script exists and is accessible..."
            ls -la /home/ubuntu/k6-loadtests/${{ github.event.inputs.script_name }}
            echo -e "\nFirst 5 lines of the script:"
            head -n 5 /home/ubuntu/k6-loadtests/${{ github.event.inputs.script_name }} || true

      # Step 4: Execute the k6 load test on the EC2 instance
      # This runs the actual load test with the specified parameters
      - name: Run k6 load test
        uses: appleboy/ssh-action@v0.1.10
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            # Configure Prometheus remote write for metrics collection
            # These environment variables are used by k6's Prometheus output
            export K6_PROMETHEUS_RW_SERVER_URL="${{ secrets.K6_PROMETHEUS_URL }}"
            export K6_PROMETHEUS_RW_USERNAME="${{ secrets.K6_PROMETHEUS_ID }}"
            export K6_PROMETHEUS_RW_PASSWORD="${{ secrets.K6_PROMETHEUS_KEY }}"
            
            # Ensure the target directory exists
            mkdir -p ~/k6-loadtests
            
            # Navigate to the test directory
            cd ~/k6-loadtests
            
            # Make the script executable (in case permissions were lost in transfer)
            chmod +x ./${{ github.event.inputs.script_name }}
            
            # Display test parameters
            echo "Starting load test with ${{ github.event.inputs.vu_count }} VUs for ${{ github.event.inputs.duration }}"
            
            # Execute k6 with the specified parameters
            # --vus: Number of virtual users
            # --duration: Test duration
            # --out: Output destinations (JSON file and Prometheus)
            k6 run \
              --vus ${{ github.event.inputs.vu_count || 10 }} \
              --duration ${{ github.event.inputs.duration || '1m' }} \
              --out json=test_results_$(date +%Y%m%d_%H%M%S).json \
              --out experimental-prometheus-rw \
              ./${{ github.event.inputs.script_name }}
            
            # Confirm test completion
            echo "Load test completed successfully"
```

### GitHub Secrets

Go to your repo’s **Settings → Secrets → Actions** and add the following:

- `EC2_HOST`: Public IP of the EC2 instance
- `EC2_SSH_KEY`: Private SSH key for login
- `K6_PROMETHEUS_URL`: Prometheus Remote Write endpoint (Push URL)
- `K6_PROMETHEUS_ID`: Your Prometheus username or instance ID
- `K6_PROMETHEUS_KEY`: API key or token

### Run the Pipeline

Once the workflow and test scripts are pushed:

- Head over to **GitHub → Actions**
- Select the **Run Load Test** workflow
- Pick a script from the dropdown and trigger the run
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*EpcCkggBcDbPRkPfeHuFRA.png)

With this, your load tests are now just a few clicks away, version-controlled, reproducible, and fully automated.

## Step 6: Create Grafana Dashboards for Each Project

Create dashboards for each project to track metrics.

1. Go to **Dashboards** → **New Dashboard** → **Add Panel**.
2. Select **Prometheus** data source.
3. You can then select from the available k6 metrics and apply filters (like `project="project_a"`) to create custom panels that visualise specific aspects of your load test.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*929DTsn4KIIvpZ0iCVyG2g.png)

4\. You can add multiple panels to your dashboard to build a dedicated view for your project, making it easy to track and analyse load test data over time.

## Wrapping Up

This load testing pipeline is a game-changer:

- **Centralised Testing**: A single EC2 instance handles all load test executions, reducing infrastructure sprawl and simplifying management.
- **Automated Workflow**: GitHub Actions lets QA or DevOps teams trigger tests on demand with dynamic inputs like script name, virtual users, and duration, no manual SSH or setup required.
- **Flexible Observability**: k6 metrics can be exported to Prometheus and visualised in Grafana. You can also switch to JSON, InfluxDB, or CloudWatch, depending on what your team uses.
- **Actionable Insights**: With project-specific tagging and custom dashboards, you can monitor performance trends across services and periods, all in one place.

You can keep expanding this by:

- Creating a **dedicated Grafana dashboard** for each project using multiple panels.
- Adding alerts for response time spikes or failure rates.
- Automating daily/weekly runs to track regression performance.

Whether you go with **Grafana Cloud** for a hosted solution or a **self-hosted Prometheus + Grafana** combo for more control, this setup brings **developer-first load testing** into your workflow.

I love how well k6’s JavaScript scripting, GitHub Actions’ dynamic inputs, and Prometheus-based observability fit into modern DevOps. If you’re on AWS, EC2 is a solid starting point, but this can easily be adapted to GCP, Azure, or even Kubernetes for more scalable needs.

You can find the GitHub Actions workflow configuration and sample load test scripts in this repository: [**https://github.com/prateekjaindev/k6-server**](https://github.com/prateekjaindev/k6-server)

For more updates, tips, and DevOps content, follow me on  
X ([@PrateekJainDev](https://x.com/PrateekJainDev)) and LinkedIn ([in/prateekjaindev](https://x.com/PrateekJainDev))

Happy Testing 🚀

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*hQC7RAxkL8FG-HGX.gif)

## Thank you for being a part of the community

*Before you go:*

- Be sure to **clap** and **follow** the writer ️👏 **️️**
- Follow us: [**X**](https://x.com/inPlainEngHQ) | [**LinkedIn**](https://www.linkedin.com/company/inplainenglish/) | [**YouTube**](https://www.youtube.com/@InPlainEnglish) | [**Newsletter**](https://newsletter.plainenglish.io/) | [**Podcast**](https://open.spotify.com/show/7qxylRWKhvZwMz2WuEoua0) | [**Twitch**](https://twitch.tv/inplainenglish)
- [**Start your own free AI-powered blog on Differ**](https://differ.blog/) 🚀
- [**Join our content creators community on Discord**](https://discord.gg/in-plain-english-709094664682340443) 🧑🏻💻
- For more content, visit [**plainenglish.io**](https://plainenglish.io/) + [**stackademic.com**](https://stackademic.com/)

DevSecOps Architect at Tech Alchemy. Writing about DevOps, cloud security, scalable infra, and engineering workflows. More about me: [prateekjain.dev](http://prateekjain.dev/)

## More from Prateek Jain

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--4214057dff65---------------------------------------)