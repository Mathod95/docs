---
title: "Idea: Building the Future of DevOps Monitoring with AIOps and AWS AI"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://aws.plainenglish.io/idea-building-the-future-of-devops-monitoring-with-aiops-and-aws-ai-5b997f497cc8"
author:
  - "[[Quan Huynh]]"
---
<!-- more -->

[Sitemap](https://aws.plainenglish.io/sitemap/sitemap.xml)## [AWS in Plain English](https://aws.plainenglish.io/?source=post_page---publication_nav-35e7a49c6df5-5b997f497cc8---------------------------------------)

[![AWS in Plain English](https://miro.medium.com/v2/resize:fill:76:76/1*6EeD87OMwKk-u3ncwAOhog.png)](https://aws.plainenglish.io/?source=post_page---post_publication_sidebar-35e7a49c6df5-5b997f497cc8---------------------------------------)

New AWS, Cloud, and DevOps content every day. Follow to join our 3.5M+ monthly readers.

A proposed architecture for an intelligent system featuring a Model Context Protocol Server and custom AI agents on AWS.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*OBnY1DfFDwCbJ8CRhIdQ-A.png)

If you’re in DevOps or SRE, you know the drill: our systems are getting bigger and more complex. This means more logs, more metrics, and often, more noise. Traditional monitoring tools are great, but they can sometimes lead to “alert fatigue” — too many alerts, making it hard to see what really matters. We end up reacting to problems rather than getting ahead of them.

But what if we could make our monitoring smarter? That’s where **AIOps** comes in. Simply put, AIOps means using **Artificial Intelligence (AI)** to make IT operations, especially monitoring, much more effective.

This post outlines an **idea** we’re developing: a plan to build an AIOps system. We want to create a setup where AI doesn’t just flag issues but helps us understand them deeply and even adapts to new problems automatically. At the heart of this idea are a **Model Context Protocol (MCP) Server** and a **Versus AI Agent**, all built using powerful tools from **Amazon Web Services (AWS)**.

## Our Core Idea: A Smarter, Learning Monitoring System

Our goal isn’t just to get alerts faster. We want a system that:

- **Really Understands Problems:** It looks at an error, considers what else is happening in the system (the “context”), and then makes a smarter judgment.
- **Learns and Adapts:** When it sees new kinds of problems, it can learn how to handle them better next time, maybe even by creating new alert formats on its own.
- **Automates the Smart Stuff:** Frees up our engineers by automating some of the complex analysis and response planning.

To do this, our system will have three main parts:

1. **Versus Incident:** This is our current tool that sends out alerts. Our new AIOps system will feed it much smarter information.
2. **MCP Server (Model Context Protocol Server):** This is the new central hub of our system. Think of it as our main data gatherer and initial processor. The "Model Context Protocol" part is key: its job is to collect all the relevant background information (the "context") our AI will need to make good decisions.
3. **Versus AI Agent:** This is our new "brain," built with AI. It takes the rich information from the MCP Server, does the heavy thinking, and decides what to do.

## The Plan: Building Our AIOps System on AWS

Here’s how we’re thinking of designing this system using AWS services.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*jlPx2_60j1cB6bDJm1m_9Q.png)

### Getting the Data In (The Foundation)

Our systems generate a wealth of data from various places. We’ll primarily tap into common tools like Amazon CloudWatch for native AWS service logs and metrics, Elasticsearch (or its AWS counterpart, Amazon OpenSearch Service) where many of our applications send their detailed logs and traces, and Prometheus, a popular choice for ongoing performance numbers, known as metrics, from our applications and infrastructure.

The **MCP Server**, which we plan to run on AWS compute services like Amazon EC2 (virtual servers) or container platforms like Amazon ECS/EKS (for scalability), has several crucial jobs.

First, it will connect and collect data from all these sources. Since data arrives in many different formats, the MCP Server will then clean it up and standardize it, which is vital for our AI to understand it correctly. Before passing everything to the main AI, it will also perform some *first-pass filtering*, looking for obvious problems or known error messages to cut down on noise.

Most importantly, when it spots something interesting—an 'Event of Interest'—it will build the 'context' around it. This 'Model Context Protocol' approach means gathering related information like metrics from that time, recent code changes, or logs from connected services, giving the AI a much bigger picture to work with.

Once the MCP Server has this “Event of Interest + Rich Context” package, it needs to send it to our **Versus AI Agent**. We'll use Amazon API Gateway for this task. API Gateway acts as a reliable and secure front door for our AI Agent, efficiently managing incoming requests, security concerns, and traffic.

### The Versus AI Agent: Our AI Brain Running on AWS

The request from API Gateway will trigger AWS Lambda. Lambda is excellent for this because it’s “serverless” — our AI code runs automatically when needed, without us having to provision or manage any underlying servers. This Lambda function will be the command center for our AI Agent, orchestrating various AI capabilities.

Inside this Lambda-powered AI Agent, we’ll use a combination of AWS AI services, each chosen for its specific strengths.

- For instance, Amazon SageMaker will allow us to build and run our *own custom Machine Learning (ML) models*, perhaps trained on our company’s unique historical incident data to predict issue severity or find complex hidden patterns.
- For tasks requiring generative capabilities, like writing code for alert templates or summarizing incidents in plain English, we’ll turn to Amazon Bedrock, which provides easy access to powerful, pre-trained Foundation Models.

After its analysis, the AI Agent will produce one of two things:

1. An **alert plan**: This is a structured set of instructions for Versus Incident – what message to send, who to send it to, how critical it is, and any extra info from the AI.
2. A **new template string**: If Bedrock were asked to create a new Go template.

### Taking Action (MCP Server Gets the AI’s Instructions)

The AI Agent (Lambda) sends its output (the alert plan or the new template) back to the MCP Server through the API Gateway.

Now, the MCP Server acts on the AI’s decision:

- If it got a **new template**: It calls a special API endpoint (like `POST /api/admin/templates`) on our Versus Incident tool to add this new template to its library.
- If it got an **alert plan**: It calls the main alert API (like `POST /api/incidents`) on Versus Incident to send out a smart, context-rich alert.

## A Quick Example: How It Handles a New Error

Let’s make this more concrete. Imagine a new, never-before-seen error starts appearing in your Elasticsearch logs for a critical service. Versus Incident has never seen it before.

**1\. CP Server Sees It:** It picks up these new errors from Elasticsearch logs. It notices this is a new pattern.

**2\. MCP Gathers Context:** It also grabs related metrics from Prometheus for the database and the affected service around that time.

**3\. MCP Asks the AI:** It sends the new error data and the related metrics to the `Versus AI Agent` (via API Gateway and Lambda).

**4\. AI Agent Thinks (Lambda):**

- The Lambda code sees this is a new error type.
- It tells **Amazon SageMaker**: Here’s the data for this error. Please write a Go template for Versus Incident.

**5\. AI Agent Responds:** The Lambda sends this new template code back to the MCP Server.

**6\. MCP Updates Versus Incident:**

- The MCP Server calls the `/api/admin/templates` API on Versus Incident and gives it the new template.
- *The cool part:* Now, Versus Incident is ready! The next time *this specific* database error happens, it can use this new, AI-generated template to create a perfectly formatted, informative alert.

## Why We Think This Idea is Powerful

This isn’t just about adding AI for fun. We expect real benefits:

- **Fewer Useless Alerts:** The AI will help filter out noise and only flag things that really need attention. This means less “alert fatigue” for our teams.
- **Faster Problem Solving:** Alerts will have more context and smarter information, helping engineers figure out the root cause quicker.
- **Handles New Problems Better:** The system can learn and even create its own tools (like new alert templates) to deal with new types of issues.
- **Less Manual Work:** Automating some of the analysis and template creation saves our engineers valuable time.
- **Making Advanced AI Accessible:** Using AWS’s managed AI services means we can build these smart features without needing a huge, dedicated AI research team from day one.

## Our Plan to Get Started (From Idea to Reality)

This is a big idea, so we’ll build it in stages:

1. **First Things First:** We need to add that special API endpoint (`/api/admin/templates`) to our existing Versus Incident tool so it can accept new templates.
2. **Build the Core MCP Server on AWS:** We'll start with getting it to collect data from one or two sources (like CloudWatch). We'll also build the basic communication link (using API Gateway) to where our AI Agent will live.
3. **Create the First Version of Versus AI Agent:** We'll use AWS Lambda and start with one AI skill – for example, using Amazon Bedrock to generate templates for one common type of log data.
4. **Grow and Improve:** From there, we’ll keep adding more data sources to the MCP Server, make its context-building smarter, and add more AI skills to the AI Agent (like using SageMaker for custom predictions).

## What Do You Think of This AIOps Vision?

This is our idea for building a much smarter, more adaptive monitoring system for our DevOps world. We’re really excited about mixing our existing tools with the power of a Model Context Protocol Server and the amazing AI services available on AWS.

We believe this path can lead to systems that are not only more reliable but also less stressful to manage. But this is just our plan, our idea taking shape. What are your thoughts? Are you thinking about similar AIOps projects? Any advice or experiences you can share? We’d love to hear from you in the comments!## [Kubernetes for AI](https://a.co/d/22qG4zM?source=post_page-----5b997f497cc8---------------------------------------)

A DevOps Guide to Building Scalable AI Infrastructure on EKS.

a.co

[View original](https://a.co/d/22qG4zM?source=post_page-----5b997f497cc8---------------------------------------)

## Thank you for being a part of the community

*Before you go:*

- Be sure to **clap** and **follow** the writer ️👏 **️️**
- Follow us: [**X**](https://x.com/inPlainEngHQ) | [**LinkedIn**](https://www.linkedin.com/company/inplainenglish/) | [**YouTube**](https://www.youtube.com/@InPlainEnglish) | [**Newsletter**](https://newsletter.plainenglish.io/) | [**Podcast**](https://open.spotify.com/show/7qxylRWKhvZwMz2WuEoua0) | [**Differ**](https://differ.blog/inplainenglish) | [**Twitch**](https://twitch.tv/inplainenglish)
- [**Start your own free AI-powered blog on Differ**](https://differ.blog/) 🚀
- [**Join our content creators community on Discord**](https://discord.gg/in-plain-english-709094664682340443) 🧑🏻💻
- For more content, visit [**plainenglish.io**](https://plainenglish.io/) + [**stackademic.com**](https://stackademic.com/)

[![AWS in Plain English](https://miro.medium.com/v2/resize:fill:96:96/1*6EeD87OMwKk-u3ncwAOhog.png)](https://aws.plainenglish.io/?source=post_page---post_publication_info--5b997f497cc8---------------------------------------)

[![AWS in Plain English](https://miro.medium.com/v2/resize:fill:128:128/1*6EeD87OMwKk-u3ncwAOhog.png)](https://aws.plainenglish.io/?source=post_page---post_publication_info--5b997f497cc8---------------------------------------)

[Last published just now](https://aws.plainenglish.io/the-elasticsearch-mapping-that-reduced-our-index-size-by-75-65d22d398418?source=post_page---post_publication_info--5b997f497cc8---------------------------------------)

New AWS, Cloud, and DevOps content every day. Follow to join our 3.5M+ monthly readers.