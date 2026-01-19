---
title: "Why We Replaced Kafka with gRPC for Service Communication"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@himanshusingour7/why-we-replaced-kafka-with-grpc-for-service-communication-1c946db514d4"
author:
  - "[[Himanshu Singour]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

There was a time when I thought Kafka was the answer to everything.  
Need services to talk? Kafka.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*xhTNAQo2DpN5I_A8)

There was a time when I thought Kafka was the answer to everything.  
Need services to talk? Kafka.  
Want retries? Kafka.  
Want scalability? Kafka.  
Want async communication? Kafka.  
Even for request-response type calls somehow we convinced ourselves that Kafka was the way.

But as the system grew and reality set in, we hit bottlenecks. Not with Kafka itself but with **how we were using it**. Eventually, we reached a point where we had to rethink everything.

And that’s when we made a shift. Not to REST.  
Not to WebSockets.  
But to **gRPC**.

> Now See.. what we faced, what we fixed, and what we learned along the way.

## How We Ended Up Over-Kafka’d

We were building a loan servicing platform for banks and NBFCs. Lots of moving parts:

- Loan creation
- Disbursement
- Eligibility checks
- Moratorium variations
- ROI changes
- Installment recalculations
- Notifications
- Credit Bureau reporting
- Accounting + Ledger

All broken into microservices.  
We wanted decoupling. Scalability. Loose dependencies. And Kafka felt like the glue that would hold all these services together.

We designed it like this:

- Service A does something important
- Publishes an event on Kafka
- Services B, C, D consume and react

So far so good.

But very quickly, problems started surfacing.

## Real Example: Where Kafka Made Things Shit…

Say a loan is disbursed.

The flow looks like:

- DisbursementService emits `loan_disbursed` event to Kafka
- NotificationService listens → sends SMS/email
- AccountingService listens → updates ledger
- ComplianceService listens → notifies regulator

This seems clean. Except:

- ==**What if NotificationService crashes?**== ==Kafka has no idea. The event just sits there. No alert.==
- **What if AccountingService delays consumption due to backpressure?** The ledger gets stale.
- **What if one service fails silently?** We never know unless we manually monitor logs or someone raises a ticket.
- **What if multiple retries fail?** The event lands in a dead-letter queue and is forgotten.

And the biggest one:

- ==**What if we need an immediate response?**== ==Like checking if disbursement succeeded, or if a user is eligible Kafka just doesn’t give that guarantee.==

This isn’t Kafka’s fault.  
We were simply using Kafka for **things it wasn’t built for**.

## The Moment of Clarity

It was late one evening, and a high-value customer hadn’t received a notification after their loan was disbursed.

We checked the flow:

- Disbursement → Kafka → NotificationService
- Kafka showed the event was produced
- But NotificationService was down
- No retry triggered
- No alert fired

Support team had no clue what went wrong. Neither did the customer.  
That’s when one of our devs just blurted out:

*“Why don’t we just call NotificationService directly instead of throwing it into Kafka?”*

That hit us hard.

We realized we were using Kafka as a crutch. A fancy way to feel decoupled while actually increasing **uncertainty**.

## Exploring gRPC

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*424fLfcLmJS8ok3l)

We had used gRPC before, but only lightly. This time, we decided to go deeper.

The first thing we noticed?

- It’s built on **HTTP/2** (faster, multiplexed, binary)
- It uses **Protocol Buffers (protobuf)** super efficient, small payloads
- It supports **bi-directional streaming**
- It’s **strongly typed** every call and field is contractually defined
- It supports **real-time**, **request-response**, and **streaming**
- You can generate code in **Java, Go, etc** the same `.proto` file works everywhere

We ran a small POC where LoanService used gRPC to call EligibilityService. The response came in under **10ms**.  
Simple. Fast. Clear. No brokers, no consumers, no polling.

That was enough to convince us to try replacing more flows.

## What We Replaced (and What We Didn’t)

> We started small and then went bigger.  
> how we split it:

## Moved to gRPC:

- **Loan → EligibilityService** (needs immediate response)
- **Loan → NotificationService** (retries if failed, with fallback)
- **Loan → AccountingService** (critical ledger update, rollback on failure)
- **Loan → ScheduleService** (fetches amortization schedule in real time)

## Kept Kafka for:

- **Audit Logs** (fire-and-forget, replayable)
- **Data Lake Ingestion** (send raw event data for analytics)
- **Fan-out Patterns** (1 service producing to many consumers)
- **Resilience + Buffering for async bulk workflows**

So no, we didn’t abandon Kafka.  
We just stopped forcing it into places it didn’t belong.

## Operational Benefits of Switching to gRPC

what changed after we made the switch:

### 1\. Debugging Became Easier

Kafka made debugging hell.

You’d ask: “Did the message go through?” → Check producer logs  
“Was it consumed?” → Check consumer logs  
“Did it fail?” → Check DLQ  
“Did retry work?” → Check offset and retry mechanism

With gRPC, you get a response: success or failure. That’s it.

### 2\. Latency Dropped by 70 -> 80%

Most Kafka consumers were polling every few seconds.  
Even with real-time topics, processing was delayed.  
With gRPC, it’s all synchronous responses within 10–30ms.

Perfect for eligibility checks, balance validations, and schedule preview flows.

### 3\. Less Infra to Maintain

Kafka came with Zookeeper (or now KRaft), partitions, replication, topic retention configs, consumer groups, lag monitoring, schema registry, etc.

With gRPC, there’s nothing to manage except service deployments.

Our infra team literally said:

> *“We now get fewer alerts. Kafka used to wake us up at 2 AM.*

## What We Learned

Kafka is powerful.  
But **power without clarity** leads to confusion.

We had made Kafka our default without asking *why*.  
We thought “event-driven” meant “everything should be async.”  
We confused “scalable” with “complex.”

Switching to gRPC didn’t just improve performance it made our architecture **easier to reason about**.

Today, when someone says “let’s use Kafka here,” we pause and ask:

- Do we need replayability?
- Do we need fan-out?
- Is this async or sync?
- Is real-time response critical?

If the answer is real-time + clarity + simple interaction, we go with gRPC.

## Final Words

Kafka is amazing. And it still powers a big chunk of our backend.

But it’s not a silver bullet.  
gRPC gave us the simplicity, speed, and control we were looking for in service-to-service communication.

And sometimes, the smartest move is to **use a tool for what it’s built for** and not because it’s popular.

So no hate for Kafka.

But gRPC? That was the upgrade we didn’t know we needed until we tried it.

SDE-2 @ Fintech | Full-Stack Engineer | Top 1% in Global Coding Contests (ICPC, Code Jam, Kick Start) | Strong in HLD/LLD & Distributed Systems

## More from Himanshu Singour

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--1c946db514d4---------------------------------------)