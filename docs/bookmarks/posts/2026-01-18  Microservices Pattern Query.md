---
title: "Microservices Pattern: Query"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://medium.com/@joudwawad/microservices-pattern-query-444d114e9a30"
author:
  - "[[Joud W. Awad]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*6WQy-of-Qhs1Co2vpzIpTg.png)

Microservices Pattern Queries

## Introduction

One of the big challenges that microservices have is how we can fetch our data from multiple resources in order to combine them and support the UI, unlike monolithic applications, microservice architecture is challenging. Queries often need to retrieve data that are ***scattered among the databases owned*** by **multiple services**. You can’t, however, use a traditional distributed query mechanism, because even if it were technically possible, it violates encapsulation.

Implementing these query operations is not as straightforward.

in this blog post, we will talk about the main ways that you can use to query data in your microservices.

There are two different patterns for implementing query operations in a microservice architecture:

- ***The API composition pattern*** — This is the simplest approach and ***should be used whenever possible***. It works by making clients of the services that own the data responsible for invoking the services and combining the results.
- ***The Command query responsibility segregation (CQRS) pattern*** — This is more powerful than the API composition pattern, but it’s also more complex. It maintains one or more view databases whose sole purpose is to support queries.

## Querying using the API composition pattern

Let us imagine that we have a requirement to create a query called ***findOrder,*** this function takes an ***orderId*** as a parameter and returns an OrderDetails object, which contains information about the order. As shown in figure, this operation is called by a frontend module, such as a mobile device or a web application, that implements the ***Order Status* view**.

The information displayed by the *Order Status* view includes basic information about the order, including its ***status, payment status, status of the order from the restaurant’s perspective, and delivery status, including its location and estimated delivery time*** if in transit.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*mnHwCzN6z8C8rHYN_Zp2sQ.png)

Implementation Flow of FindOrder Query

As you can see the data is scattered around the following services:

- **Order Service** — Basic order information, including the details and status
- **Kitchen Service** — Status of the order from the restaurant’s perspective and the estimated time it will be ready for pickup
- **Delivery Service** — The order’s delivery status, estimated delivery information, and its current location
- **Accounting Service** — The order’s payment status

Any client that needs the order details must ***ask for all of these services***.

### Overview of the API composition pattern

One way to implement query operations, such as findOrder(), that retrieve data owned by multiple services is to use the API composition pattern.

> This pattern implements a query operation by invoking the services that own the data and combining the results

The following figure shows the structure of this pattern. It has two types of participants:

- ***An API composer*** — This implements the query operation by querying the provider services.
- ***A provider service*** — This is a service that owns some of the data that the query returns.
![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*SNoRDEzkYDwVhSZ0cJ_QJg.png)

API Composer Pattern Overview

The previous image shows three provider services. The API composer implements the query by retrieving data from the provider services and combining the results.  
An API composer might be a client, such as a web application, that needs the data to render a web page. Alternatively, it might be a **service**, such as an **API gateway**, which exposes the query operation as an API endpoint.

Whether you can use this pattern to implement a particular query operation depends on several factors, including:

1. ***Data is partitioned***
2. The capabilities of the *APIs* ***exposed by the services that own the data***
3. The ***capabilities of the databases used by the services***.

For instance, even if the *Provider services* have APIs for retrieving the required data, the aggregator might need to perform an inefficient, in-memory join of large datasets. Later on, you’ll see examples of query operations that can’t be implemented using this pattern. Fortunately, though, there are many scenarios where this pattern is applicable. To see it in action, we’ll look at an example.

### Implementing the findOrder() query operation using the API composition pattern

The findOrder() query operation corresponds to a simple primary key-based equijoin query. It’s reasonable to expect that each of the *Provider services* has an API end-point for retrieving the required data by **orderId**. Consequently, the findOrder() query operation is an excellent candidate to be implemented by the API composition pattern. *The API composer invokes the four services and combines the results together.*

The following figure shows the design of the Find Order Composer.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*D9R8TNRVvezJhTUv1YnXXg.png)

Implementing findOrder() using the API composition pattern

In this example, the ***API composer is a service*** that exposes the query as a REST endpoint. The *Provider services* also implement REST APIs.

The Find Order Composer implements a REST endpoint **GET /order/{orderId}**. It invokes the four services and joins the responses using the orderId. Each *Provider service* implements a REST endpoint that returns a response corresponding to a single aggregate.  
The OrderService retrieves its version of an Order by primary key and the other services use the orderId as a foreign key to retrieve their aggregates.

As you can see, the API composition pattern is quite simple. Let’s look at a couple of design issues you must address when applying this pattern.

### API composition design issues

When using this pattern, you have to address a couple of design issues:

- Deciding which component in your architecture is the query operation’s ***API composer***
- How to write efficient aggregation logic

Let’s look at each issue.

### Who plays the role of the API composer?

One decision that you must make is who plays the role of the query operation’s *API composer*. You have *three options*.

***The first option***, shown in the next figure, is for a *client of the services to be the API composer*.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*rxeaKKsO6f5s_-ayOskf8A.png)

Implementing API composition in a client, the Client queries the provider services to retrieve the data

A frontend client such as a web application, that implements the Order Status view and is running on the same LAN, could efficiently retrieve the order details using this pattern. However, this option is probably not practical for clients that are outside of the firewall and access services via a slower network and we will discuss this in another blog post.

***The second option***, shown in the figure, is for an *API gateway*, which implements the application’s external API, to play the role of an *API composer* for a query operation.

This option makes sense if the query operation is part of the application’s external API. Instead of routing a request to another service, the API gateway implements the API composition logic.  
This approach enables a client, such as a mobile device, that’s running outside of the firewall to efficiently retrieve data from numerous services with a single API call.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*uTTe-pQ1oohrBrfvK5W_Ug.png)

Implementing API Composition in the API Gateway, the API Gateway queries the provider services to retrieve the data, combines the results, and returns a response to the client

***The third option***, shown in the next figure, is to implement an ***API composer as a standalone service***.

**You should use this option for a query operation that’s used internally by multiple services**. This operation can also be used for externally accessible query operations whose aggregation logic is too complex to be part of an API gateway.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*YB_JI5vi56JtK7nshgLaAQ.png)

Implement a query operation used by multiple clients and services as a standalone service

### API composers should use a reactive programming model

When developing a distributed system, minimizing latency is an ever-present concern. Whenever possible, an *API composer* should call provider services in ***parallel*** in order to minimize the response time for a query operation.  
The Find Order Aggregator should, for example, invoke the four services ***concurrently*** because there are no dependencies between the calls. Sometimes, though, an *API composer* needs the result of ***one Provider service*** in order to invoke another service. In this case, it will need to invoke some — but hopefully not all — of the *provider services* sequentially.

The logic to efficiently execute a mixture of sequential and parallel service invocations can be complex. In order for an *API composer* to be maintainable as well as performant and scalable, it should use a reactive design based on Java Completable-Future’s, RxJava observables, or some other equivalent abstraction.

### The benefits and drawbacks of the API composition pattern

This pattern is a simple and intuitive way to implement query operations in a microservice architecture. But it has some drawbacks:

- Increased overhead
- Risk of reduced availability
- Lack of transactional data consistency

Let’s take a look at them.

### INCREASED OVERHEAD

One drawback of this pattern is the overhead of invoking multiple services and querying multiple databases. In a monolithic application, a client can retrieve data with a single request, which will often execute a single database query.  
In comparison, using the API composition pattern involves multiple requests and database queries. *As a result, more computing and network resources are required, increasing the cost of running the application.*

### RISK OF REDUCED AVAILABILITY

Another drawback of this pattern is reduced availability. The availability of an operation declines with the number of services that are involved. Because the implementation of a query operation involves at least three services — the *API composer* and at least two provider services — its availability will be significantly less than that of a single service. For example, if the availability of an individual service is 99.5%, then the availability of the findOrder() endpoint, which invokes four provider services, is 99.5%(4+1) = 97.5%!

There are a couple of strategies you can use to improve availability. The first strategy is for the *API composer* to return ***previously cached data when a Provider service is unavailable***.  
An *API composer* sometimes caches the data returned by a *Provider service* in order to improve performance. It can also use this cache to improve availability. If a provider is unavailable, the *API composer* can return data from the cache, though it may be potentially stale.

Another strategy for improving availability is for the ***API composer to return incomplete data***. For example, imagine that Kitchen Service is temporarily unavailable. The *API Composer* for the findOrder() query operation could omit that service’s data from the response because the UI can still display useful information.

### LACK OF TRANSACTIONAL DATA CONSISTENCY

Another drawback of the API composition pattern is the lack of data consistency. A monolithic application typically executes a query operation using a single database transaction. ACID transactions — subject to the fine print about isolation levels — ensure that an application has a consistent view of the data, even if it executes multiple database queries. In contrast, the API composition pattern executes multiple database queries against multiple databases. There’s a risk, therefore, that a query operation will return inconsistent data.

For example, an Order retrieved from Order Service might be in the CANCELLED state, whereas the corresponding Ticket retrieved from Kitchen Service might not yet have been cancelled.  
The *API composer* must resolve this discrepancy, which increases the code complexity. To make matters worse, an *API composer* might not always be able to detect inconsistent data and will return it to the client.

***Despite these drawbacks, the API composition pattern is extremely useful. You can use it to implement many query operations. However, there are some query operations that can’t be efficiently implemented using this pattern. A query operation might, for example, require the API composer to perform an in-memory join of large datasets.***

## Using the CQRS pattern

Many enterprise applications use an RDBMS as the transactional system of record and a text search database, such as Elasticsearch or Solr, for text search queries. Some applications keep the databases synchronized by writing to both simultaneously. Others periodically copy data from the RDBMS to the text search engine.

Applications with this architecture leverage the strengths of multiple databases: the transactional properties of the RDBMS and the querying capabilities of the text database.

CQRS is a generalization of this kind of architecture. ***It maintains one or more view databases*** — not just text search databases — that implement one or more of the application’s queries.

### Motivations for using CQRS

The API composition pattern is a good way to implement many queries that must retrieve data from multiple services. Unfortunately, it’s only a partial solution to the problem of querying in a microservice architecture. That’s because there are multiple service queries the API composition pattern can’t implement efficiently.

We can consider the CQRS Pattern in the following situations:

1. There are also single service queries that are challenging to implement. Perhaps the service’s database doesn’t efficiently support the query.
2. Alternatively, it sometimes makes sense for a service to implement a query that retrieves data owned by a different service.

Let’s take a look at these problems, starting with a multi-service query that can’t be efficiently implemented using API composition.

### Implementing the FindOrderHistory() Query operation

The findOrderHistory() operation retrieves a consumer’s order history. It has several parameters:

- **consumerId** — Identifies the consumer
- **pagination** — Page of results to return
- **filter** — Filter criteria, including the max-age of the orders to return, an optional order status, and optional keywords that match the restaurant name and menu items

This query operation returns an OrderHistory object that contains a summary of the matching orders sorted by increasing age. It’s called by the module that implements the Order History view. This view displays a summary of each order, which includes the order number, order status, order total, and estimated delivery time.

On the surface, this operation is similar to the findOrder() query operation. The only difference is that it returns ***multiple orders instead of just one***. It may appear that the ***API composer*** only has to execute the same query against each *Provider service* and combine the results. Unfortunately, it’s not that simple.

That’s because not all services store the attributes that are used for filtering or sorting. For example, one of the findOrderHistory() operation’s filter criteria is a keyword that matches against a menu item. Only two of the services, Order Service and Kitchen Service, store an Order’s menu items. Neither Delivery Service nor Accounting Service stores the menu items, so can’t filter their data using this keyword. Similarly, neither Kitchen Service nor Delivery Service can sort by the orderCreationDate attribute.

There are two ways an *API composer* could solve this problem. One solution is for the `API composer` to do an in-memory join as shown in the following figure. It retrieves all orders for the consumer from the Delivery Service and Accounting Service and performs a join with the orders retrieved from the Order Service and Kitchen Service.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*6qL_oi9Wa1ReLAfMqZSy8A.png)

API composition can not efficiently retrieve a consumer’s orders, because some providers such as DeliveryService do not store the attributes used for filtering

***The drawback of this approach is that it potentially requires the API composer to retrieve and join large datasets, which is inefficient.***

The other solution is for the *API composer* to retrieve matching orders from Order Service and Kitchen Service and then request orders from the other services by ID.

***But this is only practical if those services have a bulk fetch API.*** Requesting orders individually will likely be inefficient because of excessive network traffic.

Queries such as findOrderHistory() require the ***API composer*** to duplicate the functionality of an RDBMS’s query execution engine. On one hand, this potentially moves work from the less scalable database to the more scalable application. On the other hand, it’s less efficient. ***Also, developers should be writing business functionality, not a query execution engine.***

### A challenging single service query: findAvailableRestaurants()

As you’ve just seen, implementing queries that retrieve data from multiple services can be challenging. But even queries that are local to a single service can be difficult to implement. There are a couple of reasons why this might be the case. One is because, as discussed shortly, sometimes it’s not appropriate for the service that owns the data to implement the query. The other reason is that sometimes a service’s database (or data model) doesn’t efficiently support the query.

Consider, for example, the findAvailableRestaurants() query operation. This query finds the restaurants that are available to deliver to a given address at a given time. The heart of this query is a geospatial (location-based) search for restaurants that are within a certain distance of the delivery address. It’s a critical part of the order process and is invoked by the UI module that displays the available restaurants.

The key challenge when implementing this query operation is performing an efficient geospatial query. How you implement the findAvailableRestaurants() query depends on the capabilities of the database that stores the restaurants.

For example, it’s straightforward to implement the findAvailableRestaurants() query using either MongoDB or the Postgres and MySQL geospatial extensions. These databases support geospatial datatypes, indexes, and queries. When using one of these databases, Restaurant Service persists a Restaurant as a database record that has a location attribute. It finds the available restaurants using a geospatial query that’s optimized by a geospatial index on the location attribute.

If your application stores restaurants in some other kind of database, implementing the findAvailableRestaurant() query is more challenging. It must maintain a replica of the restaurant data in a form that’s designed to support the geospatial query.

The application could, for example, use the Geospatial Indexing Library for DynamoDB which uses a table as a geospatial index. Alternatively, the application could store a replica of the restaurant data in an entirely different type of database, a situation very similar to using a text search database for text queries.

The challenge with using replicas is keeping them up-to-date whenever the original data changes. As you’ll learn next, CQRS solves the problem of synchronizing replicas.

### The need to separate concerns

Another reason why single service queries are challenging to implement is that sometimes the service that owns the data shouldn’t be the one that implements the query.

The findAvailableRestaurants() query operation retrieves data that is owned by Restaurant Service. This service enables restaurant owners to manage their restaurant’s profile and menu items. It stores various attributes of a restaurant, including its name, address, cuisines, menu, and opening hours.

Given that this service owns the data, it makes sense, at least on the surface, for it to implement this query operation. But data ownership isn’t the only factor to consider.

You must also take into account the need to separate concerns and avoid overloading services with too many responsibilities. For example, the primary responsibility of the team that develops Restaurant Service is enabling restaurant managers to maintain their restaurants. That’s quite different from implementing a high-volume, critical query.

What’s more, if they were responsible for the findAvailableRestaurants() query operation, the team would constantly live in fear of deploying a change that prevented consumers from placing orders.

It makes sense for Restaurant Service to merely provide the restaurant data to another service that implements the findAvailableRestaurants() query operation and is most likely owned by the Order Service team. As with the findOrderHistory() query operation, and when needing to maintain geospatial index, there’s a requirement to maintain an eventually consistent replica of some data in order to implement a query. Let’s look at how to accomplish that using CQRS.

### Overview of CQRS

The examples described in this section highlighted three problems that are commonly encountered when implementing queries in a microservice architecture:

- Using the API composition pattern to retrieve data scattered across multiple services results in expensive, inefficient in-memory joins.
- The service that owns the data stores the data in a form or in a database that doesn’t efficiently support the required query.
- The need to separate concerns means that the service that owns the data isn’t the service that should implement the query operation.

The solution to all three of these problems is to use the CQRS pattern.

## CQRS separates Commands from Queries

***Command Query Responsibility Segregation, as the name suggests, is all about segregation, or the separation of concerns.***

As the next figure shows, it splits a persistent data model and the modules that use it into ***two parts***: **the command side** and the **query side**.

***The command side*** modules and data model implement create, update, and delete operations (abbreviated CUD — for example, HTTP POSTs, PUTs, and DELETEs).

***The query-side*** modules and data model implements queries (such as HTTP GETs). The query side keeps its data model synchronized with the command-side data model by subscribing to the events published by the command side.

> Both the non-CQRS and CQRS versions of the service have an API consisting of various CRUD operations. In a non-CQRS-based service, those operations are typically implemented by a domain model that’s mapped to a database.

For performance, a few queries might bypass the domain model and access the database directly. A single persistent data model supports both commands and queries.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*GeE7ZuoW1f8IlkPF40rnlQ.png)

Non-CQRS VS CQRS overview

In a CQRS-based service, the command-side domain model handles CRUD operations and is mapped to its own database. ***It may also handle simple queries, such as non-join, primary key-based queries.***

The ***command side publishes domain events*** whenever its data changes. These events might be published using a framework or using event sourcing.

A separate query model handles the nontrivial queries. It’s much simpler than the command side because it’s not responsible for implementing the business rules.

The query side uses whatever kind of database makes sense for the queries that it must support. The query side has event handlers that subscribe to domain events and update the database or databases.

> **There may even be multiple query models, one for each type of query.**

### CQRS & Query-Only Services

> **Not only can CQRS be applied within a service, but you can also use this pattern to define query services.**

A query service has an API consisting of only query operations — no command operations. It implements the query operations by querying a database that it keeps up-to-date by subscribing to events published by one or more other services.

A query-side service is a good way to implement a view that’s built by subscribing to events published by multiple services. This kind of view doesn’t belong to any particular service, so it makes sense **to implement it as a standalone service**.

A good example of such a service is Order History Service, which is a query service that implements the findOrderHistory() query operation. As figure shows, this service subscribes to events published by several services, including Order Service, Delivery Service, and so on.

Order History Service has event handlers that subscribe to events published by several services and update the Order History View Database.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*fUJ6BYJsz9qI_-Dp0fuMeQ.png)

CQRS implementation per service

A query service is also a good way to implement a view that replicates data owned by a single service yet because of the need to separate concerns isn’t part of that service. For example, the developers can define an Available Restaurants Service, which implements the findAvailableRestaurants() query operation described earlier. It subscribes to events published by Restaurant Service and updates a database designed for efficient geospatial queries.

> In many ways, CQRS is an event-based generalization of the popular approach of using RDBMS as the system of record and a text search engine, such as Elasticsearch, to handle text queries.

What’s different is that CQRS uses a broader range of database types — not just a text search engine. Also, CQRS query-side views are updated in near real-time by subscribing to events.

### The benefits of CQRS

CQRS has both benefits and drawbacks. The benefits are as follows:

- Enables the efficient implementation of queries in a microservice architecture
- Enables the efficient implementation of diverse queries
- Makes querying possible in an event-sourcing-based application
- Improves separation of concerns

## The drawbacks of CQRS

Even though CQRS has several benefits, it also has significant drawbacks:

- More complex architecture
- Dealing with the replication lag

## Designing CQRS views

A CQRS view module has an API consisting of one more query operation. It implements these query operations by querying a database that it maintains by subscribing to events published by one or more services. As the figure shows, a view module consists of a view database and three submodules.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*9ZNxFPdD9TALtHIX5yoE9w.png)

CQRS view module Design

- The *data access module* implements the database access logic.
- The *event handlers* and query API modules use the data access module to update and query the database.
- The *event handlers* module subscribes to events and updates the database.
- The *query API module* implements the query API.

You must make some ***important design decisions*** when developing a view module:

- You must choose a **database** and design the schema.
- When designing the data access module, you must address various issues, including ensuring that updates are idempotent and ***handling concurrent updates***.
- When implementing a new view in an existing application or changing the schema of an existing application, ***you must implement a mechanism to efficiently build or rebuild the view***.
- You must decide how to enable a client of the view to cope with the ***replication lag***, described earlier.

Let’s look at each of these issues.

### Choosing a view datastore

A key design decision is the choice of database and the design of the schema. The primary purpose of the database and the data model is to efficiently implement the view module’s query operations. It’s the characteristics of those queries that are the primary consideration when selecting a database.  
*However, the database must also efficiently implement the update operations performed by the event handlers*.

**SUPPORTING UPDATE OPERATIONS**

Besides efficiently implementing queries, the view data model must also efficiently implement the ***update operations executed by the event handlers***.

Usually, an event handler will ***update or delete a record*** in the view database using its **primary key.**

Sometimes, though, it will need to update or delete a record using the equivalent of a foreign key. Consider, for instance, the event handlers for Delivery events. If there is a ***one-to-one*** correspondence between a Delivery and an Order, then Delivery.id might be the same as Order.id. If it is, then Delivery event handlers can easily update the order’s database record.

But suppose a Delivery has its own primary key or there is a one-to-many relationship between an Order and a Delivery. Some Delivery events, such as the DeliveryCreated event, will contain the orderId. But other events, such as a DeliveryPickedUp event, might not. In this scenario, an event handler for DeliveryPickedUp will need to update the order’s record using the deliveryId as the equivalent of a foreign key.

### Data access module design

The event handlers and the query API module don’t access the datastore directly. Instead, they use the data access module, which consists of a data access object (DAO) and its helper classes. The DAO has several responsibilities. It implements the update operations invoked by the event handlers and the query operations invoked by the query module.  
The DAO maps between the data types used by the higher-level code and the database API. It also must handle ***concurrent updates*** and ensure that updates are idempotent.

Let’s look at these issues, starting with how to handle concurrent updates.

**HANDLING CONCURRENCY**

Sometimes a DAO must handle the possibility of multiple concurrent updates to the same database record. If a view subscribes to events published by a single aggregate type, there won’t be any concurrency issues. That’s because events published by a particular aggregate instance are processed ***sequentially***.

As a result, a record corresponding to an aggregate instance won’t be updated concurrently. But if a view subscribes to events published by ***multiple aggregate types*,** then it’s possible that multiple events handlers update the same record simultaneously.

For example, an event handler for an Order event might be invoked at the same time as an event handler for a Delivery event for the same order. Both event handlers then simultaneously invoke the DAO to update the database record for that Order.

> A DAO must be written in a way that ensures that this situation is handled correctly. It must not allow one update to overwrite another. If a DAO implements updates by reading a record and then writing the updated record, it must use either pessimistic or optimistic locking.

**IDEMPOTENT EVENT HANDLERS**

An event handler may be invoked with the same event more than once. This is generally not a problem if a query-side event handler is **idempotent**. An event handler is idempotent if handling duplicate events results in the correct outcome. **In the worst case, the view datastore will temporarily be out-of-date.**

For example, an event handler that maintains the Order History view might be invoked with the (admittedly improbable) sequence of events shown in Figure: `DeliveryPickedUp, DeliveryDelivered, DeliveryPickedUp, and DeliveryDelivered`.

After delivering the **DeliveryPickedUp** and **DeliveryDelivered** events the first time, ***the message broker, perhaps because of a network error, starts delivering the events from an earlier point in time,*** and so redelivers **DeliveryPickedUp** and **DeliveryDelivered**.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*3Y_hZia_eyZ2HCIT0p7idg.png)

Order events received in a timely manner

After the event handler processes the second **DeliveryPickedUp** event, the Order History view temporarily contains the out-of-date state of the Order until the **DeliveryDelivered** is processed. If this behavior is undesirable, then the event handler should detect and discard duplicate events, like a non-idempotent event handler.

> An event handler isn’t idempotent if duplicate events result in an incorrect out-come.

For example, an event handler that increments the balance of a bank account isn’t idempotent. A non-idempotent event handler must detect and discard duplicate events by recording the IDs of events that it has processed in the view datastore. *In order to be reliable, the event handler must record the event ID and update the datastore atomically.*

How to do this depends on the type of database. If the view database store is an SQL database, the event handler could insert processed events into a **PROCESSED\_EVENTS** table as part of the transaction that updates the view. But if the view datastore is a NoSQL database that has a limited transaction model, the event handler must save the event in the datastore “record” (for example, a MongoDB document or DynamoDB table item) that it updates.

It’s important to note that the event handler doesn’t need to record the ID of every event. If events have a *monotonically increasing ID,* then each record only needs to store the max(eventId) that’s received from a given aggregate instance.

Furthermore, if the record corresponds to a single aggregate instance, then the event handler only needs to record max(eventId). Only records that represent joins of events from multiple aggregates must contain a map from **\[aggregate type, aggregate id\]** to max(eventId).

**ENABLING A CLIENT APPLICATION TO USE AN EVENTUALLY CONSISTENT VIEW**

As I said earlier, one issue with using CQRS is that a client that updates the command side and then immediately executes a query might not see its own update. The view is eventually consistent because of the unavoidable latency of the messaging infrastructure. The command and query module APIs can enable the client to detect an inconsistency using the following approach. A command-side operation returns a token containing the ID of the published event to the client.

The client then passes the token to a query operation, which returns an error if the view hasn’t been updated by that event. A view module can implement this mechanism using the duplicate event-detection mechanism.

there are more ways to handle this kind of issue that are out of the scope of this blog post, you can refer to this post for more information about how to handle eventual consistency in distributed systems

[https://medium.com/ssense-tech/handling-eventual-consistency-with-distributed-system-9235687ea5b3](https://medium.com/ssense-tech/handling-eventual-consistency-with-distributed-system-9235687ea5b3)

### Adding and updating CQRS views

CQRS views will be added and updated throughout the lifetime of an application. Sometimes you need to add a new view to support a new query. ***At other times you might need to re-create a view because the schema has changed or you need to fix a bug in code that updates the view***.

Adding and updating views is conceptually quite simple. To create a new view, you develop the query-side module, set up the datastore, and deploy the service. The query side module’s event handlers process all the events, and eventually, the view will be up-to-date.  
Similarly, updating an existing view is also conceptually simple: you change the event handlers and rebuild the view from scratch. The problem, however, is that this approach is unlikely to work in practice. Let’s look at the issues.

**BUILD CQRS VIEWS USING ARCHIVED EVENTS**

One problem is that message brokers can’t store messages indefinitely. Traditional message brokers such as RabbitMQ delete a message once it’s been processed by a consumer. Even more modern brokers such as Apache Kafka, which retain messages for a configurable retention period, aren’t intended to store events indefinitely. *As a result, a view can’t be built by only reading all the needed events from the message broker*.

**Instead, an application must also read older events that have been archived in**, for example, AWS S3. You can do this by using a scalable big data technology such as Apache Spark.

**BUILD CQRS VIEWS INCREMENTALLY**

Another problem with view creation is that the time and resources required to process all events keep growing over time. Eventually, view creation will become too slow and expensive. The solution is to use a two-step incremental algorithm.

- The first step periodically computes a snapshot of each aggregate instance based on its previous snapshot and events that have occurred since that snapshot was created.
- The second step creates a view using the snapshots and any subsequent events.

## Conclusion

Implementing seemingly simple operations like queries can be significantly more challenging in distributed systems than in traditional monolithic architectures. Throughout this blog post, we have explored various methods for implementing queries within a microservices architecture, specifically focusing on the Composition API and CQRS patterns.

We began by examining the limitations of the Composition API, followed by a discussion on the CQRS pattern as an alternative approach for handling more complex queries. We concluded by addressing the challenges associated with CQRS and proposing solutions to mitigate these difficulties.

In real-world scenarios, it is crucial to thoroughly understand the specific requirements of your queries to select the most appropriate implementation pattern. By carefully considering these factors, you can ensure that your chosen method will effectively meet your system’s needs.

## References

- [Microservices Patterns — Chris Richardson](https://microservices.io/patterns/microservices.html)
- [Building Microservices: Designing Fine-Grained Systems 2nd Edition — Sam Newman](https://www.amazon.com.au/Building-Microservices-Second-Sam-Newman/dp/1492034029)

AWS Community Builder, Principal Software Engineer, and Solutions Architect with 11+ years in backend, AWS, DevOps, AI, and machine learning.