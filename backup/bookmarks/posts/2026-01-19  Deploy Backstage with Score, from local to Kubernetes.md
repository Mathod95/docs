---
title: "Deploy Backstage with Score, from local to Kubernetes"
date: 2026-01-19
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://itnext.io/deploy-backstage-with-score-45bb2d7c2d90"
author:
  - "[[Mathieu Benoit]]"
---
<!-- more -->

[Sitemap](https://itnext.io/sitemap/sitemap.xml)## [ITNEXT](https://itnext.io/?source=post_page---publication_nav-5b301f10ddcd-45bb2d7c2d90---------------------------------------)

*Update on June 27th, 2025 — A new section with the Backstage app broken down into two containers:* `*frontend*` *and* `*backend*` *has been added.*

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*TwJEg_mDCXm5gaFHxNWKHw.png)

Backstage ( CNCF Incubating ) & Score CNCF Sandbox )

In this blog post, you’ll learn how you can deploy your [Backstage](https://backstage.io/) app with [Score](https://score.dev/) to both Docker/Podman and Kubernetes.

*This will not cover what is Backstage (*[*CNCF Incubating*](https://www.cncf.io/projects/backstage/)*) nor what is Score (*[*CNCF Sandbox*](https://www.cncf.io/projects/score/)*). I’ll let the readers use these external links to get such introductions.*

I’ll walk you through a step-by-step guide illustrating different concepts for both Backstage and Score, and see how two main personas, **Developers** and **Platform Engineers**, can better collaborate to make their Backstage app deployments stronger.

- Create a sample Backstage app from scratch
- Deploy this Backstage app as a container
- Create the Score file for this Backstage app
- Deploy this Backstage app via `score-compose`
- Deploy this Backstage app via `score-k8s`
- Run this Backstage app as unprivileged
- Use PostgreSQL instead of an in-memory database
- Expose this Backstage app
- Split the `frontend` from the `backend` for the Backstage app

*Note: if you want to see a simplified documentation of this, you can visit the* [*associated page in the Score docs*](https://docs.score.dev/docs/examples/backstage/)*. Also, the source code of the Backstage app and associated container image can be found here:* [*mathieu-benoit/deploy-backstage-with-score*](https://github.com/mathieu-benoit/deploy-backstage-with-score)*.*

Let’s do it, let’s get started! 🚀

## Create a sample Backstage app

Create a [sample Backstage app](https://backstage.io/docs/getting-started/):

```rb
npx @backstage/create-app@latest
```

You’ll be prompted to supply the name of your app, let’s call it `backstage`.

Then do:

```rb
cd backstage
yarn start
```

From here you can navigate to `[http://localhost:3000/](http://localhost:3000/)` and see your first Backstage app up and running, you’ll be prompted to use an unauthenticated way for now:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*2PL-ijTyxJyUXjnoXZ9g4w.png)

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*iA446befWwa1oSK9.png)

💡At this stage, it’s using an in-memory database defined in the `app-config.yaml`:

```rb
# This is for local development only, it is not recommended to use this in production
  # The production database configuration is stored in app-config.production.yaml
  database:
    client: better-sqlite3
    connection: ':memory:'
```

✅ Nice, congrats! You have your first Backstage app running locally! 🎉

## Deploy this Backstage app as a container

Let’s now deploy this exact same Backstage app as a container.

For this we create the multi-stage build `[Dockerfile](https://backstage.io/docs/deployment/docker#multi-stage-build)` [defined here](https://backstage.io/docs/deployment/docker#multi-stage-build).

Let’s build this container image:

```rb
docker image build -t backstage .
```

*ℹ️ Note: backend and frontend are deployed as one bundled container, the size of this container image is* `*1.14GB*`*.*

Let’s run this container image:

```rb
docker run -it -p 7007:7007 backstage
```

❌ Here we will get this error:

```rb
/app/node_modules/@backstage/backend-defaults/dist/entrypoints/database/connectors/postgres.cjs.js:177
        throw new Error(
              ^

Error: Failed to connect to the database to make sure that 'backstage_plugin_app' exists, Error: connect ECONNREFUSED 127.0.0.1:5432
    at PgConnector.getClient (/app/node_modules/@backstage/backend-defaults/dist/entrypoints/database/connectors/postgres.cjs.js:177:15)
```

That’s because the container is starting with this below as defined in the `Dockerfile`:

```rb
CMD ["node", "packages/backend", "--config", "app-config.yaml", "--config", "app-config.production.yaml"]
```

Using the `app-config.production.yaml` file defining that we need a PostgreSQL database, which we don’t at this stage:

```rb
# config options: https://node-postgres.com/apis/client
  database:
    client: pg
    connection:
      host: ${POSTGRES_HOST}
      port: ${POSTGRES_PORT}
      user: ${POSTGRES_USER}
      password: ${POSTGRES_PASSWORD}
```

You can re-run the container image with this below to still use an in-memory database:

```rb
docker run -it \
    -e APP_CONFIG_backend_database_client='better-sqlite3' \
    -e APP_CONFIG_backend_database_connection=':memory:' \
    -p 7007:7007 \
    backstage
```

❌ From here you can navigate to `[http://localhost:7007/](http://localhost:7007/)` and see that you have another error `401 Unauthorized`:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*JG4TwpPWhZpTWrABinTcQw.png)

Here you will need to re-run this container by disabling the `auth` section (using `dangerouslyAllowOutsideDevelopment=true`, [**not recommended for Production**](https://backstage.io/docs/auth/guest/provider/), but that’s what we will use for now):

```rb
docker run -it \
    -e APP_CONFIG_backend_database_client='better-sqlite3' \
    -e APP_CONFIG_backend_database_connection=':memory:' \
    -e APP_CONFIG_auth_providers_guest_dangerouslyAllowOutsideDevelopment='true' \
    -p 7007:7007 \
    backstage
```

From here you can navigate to `[http://localhost:7007/](http://localhost:7007/)` and see that your Backstage app is now running successfully.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*UO2A3FLL6rnZhJGB1q77uw.png)

That’s it! Congrats! 🎉

✅ At this stage, you have a Backstage app running and deployed via its container image. And for now with an in-memory database and on non secure way to access the portal.

***⚠️ Important consideration here in terms of security. At this stage this containerized Backstage app has 86 CVEs (2 Critical, 3 High, 5 Medium and the rest in Low). Its container image size is*** `***1.14GB***`***. If you want to see how to fix these CVEs and optimize the container image size, you can follow my different updates in there:*** [***Comparing v1.0.1…v1.0.7 · mathieu-benoit/deploy-backstage-with-score***](https://github.com/mathieu-benoit/deploy-backstage-with-score/compare/v1.0.1...v1.0.7)***. The container image size is now*** `***846MB***`***,*** `***-168MB***` ***has been saved on disk. And just 4 Medium CVEs remain, 82 CVEs have been fixed! 💪***

***Friends don’t let friends run unsecure containers! 😉***

## Create the Score file for this Backstage app

Now what we want to do is describing how we want do deploy our Backstage app via Score. Score is a workload specification abstracting the **Developers** from the actual platform and environment where this workload will be deployed later. Here is how to describe what we have used so far:

```rb
apiVersion: score.dev/v1b1
metadata:
  name: backstage
containers:
  backstage:
    image: .
    variables:
      APP_CONFIG_backend_database_client: "better-sqlite3"
      APP_CONFIG_backend_database_connection: ":memory:"
      APP_CONFIG_auth_providers_guest_dangerouslyAllowOutsideDevelopment: "true"
service:
  ports:
    tcp:
      port: 7007
      targetPort: 7007
```

💡 It’s a YAML file, it’s not a Kubernetes Custom Resource and it’s not a Compose file. It’s a very basic Score file at this stage, we will iterate throughout this blog post to do more. Bear with me.

## Deploy this Backstage app via score-compose

From this Score file just defined, we now want to deploy it with Docker/Podman Compose, but we don’t want to write the Compose file ourself. For this, we will use `[score-compose](https://docs.score.dev/docs/score-implementation/score-compose/)`, a Score implementation allowing to generate a working Compose file from the Score file.

Once `[score-compose](https://docs.score.dev/docs/score-implementation/score-compose/installation/)` [installed](https://docs.score.dev/docs/score-implementation/score-compose/installation/), you can run this commands:

```rb
score-compose init

score-compose generate score.yaml \
    --build 'backstage={"context":".","tags":["backstage:local"]}' \
    --publish 7007:backstage:7007
```

This will generate a `compose.yaml` file that you can just deploy with:

```rb
docker compose up --build -d
```

✅From here you can navigate to `[http://localhost:7007/](http://localhost:7007/)` and see that your Backstage app is still running successfully. Same as before. But now deployed via `score-compose` and Docker/Podman Compose! 🎉

## Deploy this Backstage app via score-k8s

From this exact same Score file, we now want to deploy it to a Kubernetes cluster, but we don’t want to write the [Kubernetes manifests](https://backstage.io/docs/deployment/k8s) ourself. For this, we will use `[score-k8s](https://docs.score.dev/docs/score-implementation/score-k8s/)`, a Score implementation allowing to generate working Kubernetes manifests from the Score file.

Once `[score-k8s](https://docs.score.dev/docs/score-implementation/score-k8s/installation/)` [installed](https://docs.score.dev/docs/score-implementation/score-k8s/installation/), you can run this commands:

```rb
score-k8s init

score-k8s generate score.yaml \
    --image backstage:local
```

This will generate a `manifests.yaml` file that you can just deploy with:

```rb
kubectl apply -f manifests.yaml

kubectl port-forward svc/backstage 7007:7007
```

*ℹ️ Note: to run the commands above, you need to have access to a Kubernetes cluster. You can use any Kubernetes cluster, for example you can* [*use a local Kind cluster*](https://docs.score.dev/docs/how-to/score-k8s/kind-cluster/)*. And from here you can load the container image previously built to your Kind cluster like this:* `*kind load docker-image backstage:local*`.

✅From here you can navigate to `[http://localhost:7007/](http://localhost:7007/)` and see that your Backstage app is still running successfully. Same as before, but on Kubernetes now! 🎉

## What have we done so far?

➡️ **As Developer**, I have defined the information around what my Backstage app needs, and this in a Score file. I can focus on my code, and yes still run `yarn start` locally. But I now have a contract with my Platform Engineering team. They will be able to containerize my Backstage app and deploy it to their Platform based on all the information I provided in my Score file.

➡️ **As Platform Engineer**, I have now a way to abstract and standardize how we want to deploy any workloads (in this case a Backstage app) to our Platform. I can also support them for multiple Platforms, in this case Docker/Podman via Docker/Podman Compose and Kubernetes.

We saw how from this Score file we could deploy it to two platforms: Docker/Podman and Kubernetes, thanks to the respective Score implementations: `score-compose` and `score-k8s`.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*7_nWx4ILytnEyOPBiGwZVA.png)

From this layer of contract and abstraction, we can now easily iterate and add more standardization as **Platform Engineer**. Down below, we’ll see how to inject more security, expose workloads and use databases.

## Run this Backstage app as unprivileged

➡️ **As Platform Engineer**, I want to enforce that any workload runs as unprivileged. And this by seamlessly injecting the associated configurations depending on the platform where the Score files will be deployed. With both `[score-compose](https://docs.score.dev/docs/score-implementation/score-compose/patch-templates/)` and `[score-k8s](https://docs.score.dev/docs/score-implementation/score-k8s/patch-templates/)` implementations, I’m able to use the patch templates feature.

Here is how you can deploy the Score file with `score-compose` by injecting `user: 65532`, `cap_drop: ["ALL"]`, and `read_only: true` (defined [here](https://github.com/score-spec/community-patchers/blob/main/score-compose/unprivileged.tpl)):

```rb
score-compose init \
    --no-sample \
    --patch-templates https://raw.githubusercontent.com/score-spec/community-patchers/refs/heads/main/score-compose/unprivileged.tpl

score-compose generate score.yaml \
    --image ghcr.io/mathieu-benoit/backstage:latest \
    --publish 7007:backstage:7007

docker compose up -d
```

Same with `score-k8s` by injecting hardened `securityContext` (defined [here](https://github.com/score-spec/community-patchers/blob/main/score-k8s/unprivileged.tpl)):

```rb
score-k8s init \
    --no-sample \
    --patch-templates https://raw.githubusercontent.com/score-spec/community-patchers/refs/heads/main/score-k8s/unprivileged.tpl

score-k8s generate score.yaml \
    --image ghcr.io/mathieu-benoit/backstage:latest

kubectl apply -f manifests.yaml

kubectl port-forward svc/backstage 7007:7007
```

✅ In both cases, you can navigate to `[http://localhost:7007/](http://localhost:7007/)` and see that our Backstage app is still up and running. Same as before, but more secure now! 🎉

💡All of these, abstracted from the **Developers**. Good way to [shift security down to the Platform, and not left to the **Developers**](https://sched.co/1txGE).

## Use PostgreSQL instead of an in-memory database

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*zGPvsi_cNcoTiupM)

So far the Score file we have is this one below (`command` and `args` have been added from the last version we deployed earlier in this blog post, achieving the same end result):

```rb
apiVersion: score.dev/v1b1
metadata:
  name: backstage
containers:
  backstage:
    image: .
    command:
      - "node"
    args:
      - packages/backend
      - "--config"
      - app-config.yaml
      - "--config"
      - app-config.production.yaml
    variables:
      APP_CONFIG_backend_database_client: "better-sqlite3"
      APP_CONFIG_backend_database_connection: ":memory:"
      APP_CONFIG_auth_providers_guest_dangerouslyAllowOutsideDevelopment: "true"
service:
  ports:
    tcp:
      port: 7007
      targetPort: 7007
```

We are using explicitly the in-memory database provided by Backstage by supplying the `APP_CONFIG_backend_database_connection: ":memory:"` environment variable. While in the `app-config.production.yaml` it’s using the `pg` database client ([Switching Backstage from SQLite to PostgreSQL](https://backstage.io/docs/tutorials/switching-sqlite-postgres/)):

```rb
database:
    client: pg
    connection:
      host: ${POSTGRES_HOST}
      port: ${POSTGRES_PORT}
      user: ${POSTGRES_USER}
      password: ${POSTGRES_PASSWORD}
```

Let’s fix this, and update our Score file to now use PostreSQL:

```rb
apiVersion: score.dev/v1b1
metadata:
  name: backstage
containers:
  backstage:
    image: .
    command:
      - "node"
    args:
      - packages/backend
      - "--config"
      - app-config.yaml
      - "--config"
      - app-config.production.yaml
    variables:
      POSTGRES_HOST: ${resources.pg.host}
      POSTGRES_PASSWORD: ${resources.pg.password}
      POSTGRES_PORT: ${resources.pg.port}
      POSTGRES_USER: ${resources.pg.username}
      APP_CONFIG_auth_providers_guest_dangerouslyAllowOutsideDevelopment: "true"
service:
  ports:
    tcp:
      port: 7007
      targetPort: 7007
resources:
  pg:
    type: postgres-instance
```

➡️ **As Developer**, in the `resources` section I can request for a `postgres-instance` resource and can use placeholders to inject in the `variables` section the outputs of this resource when it will actually be provisioned. I’m happy here because I don’t need to worry about the technical details implementation about how to deploy PostreSQL via Docker Compose, Kubernetes, etc., someone is dealing with that for me, at deployment time.

➡️ **As Platform Engineer**, I can define the well supported resources I want to expose to the Developers, by using the Score resource provisioners. Both `score-compose` and `score-k8s` come with default provisioners that you can see [here](https://docs.score.dev/docs/score-implementation/score-compose/resources-provisioners/) and [here](https://docs.score.dev/docs/score-implementation/score-k8s/resources-provisioners/) respectively. We can see that `postres-instance` is already in there. I can author my own custom provisioners too. I can for example define a recipe for local environment, and different ones when deploying in Development, Staging or Production environments.

So let’s re-generate and re-deploy this new Score file. With `score-compose` first.

`score-compose init` is importing the default provisioners, you can list what’s available by running this command:

```rb
score-compose provisioners list
```

For example, you can see these:

```rb
+-------------------+-------+------------------+--------------------------------+--------------------------------+
|       TYPE        | CLASS |      PARAMS      |            OUTPUTS             |          DESCRIPTION           |
+-------------------+-------+------------------+--------------------------------+--------------------------------+
...
+-------------------+-------+------------------+--------------------------------+--------------------------------+
| postgres          | (any) |                  | database, host, name,          | Provisions a dedicated         |
|                   |       |                  | password, port, username       | database on a shared           |
|                   |       |                  |                                | PostgreSQL instance.           |
+-------------------+-------+------------------+--------------------------------+--------------------------------+
| postgres-instance | (any) |                  | host, password, port, username | Provisions a dedicated         |
|                   |       |                  |                                | PostgreSQL instance.           |
+-------------------+-------+------------------+--------------------------------+--------------------------------+
...
```

We are using the `postgres-instance` because Backstage needs to create different databases in this instance.

Generate the `compose.yaml` file from the Score file:

```rb
score-compose generate score.yaml \
    --image ghcr.io/mathieu-benoit/backstage:latest \
    --publish 7007:backstage:7007
```

You can see that now your next deployment just got this PostgreSQL resource:

```rb
score-compose resources list
```
```rb
+----------------------------------------+--------------------------------+
|                  UID                   |            OUTPUTS             |
+----------------------------------------+--------------------------------+
| postgres-instance.default#backstage.pg | host, password, port, username |
+----------------------------------------+--------------------------------+
```

Deploy the associated `compose.yaml` file:

```rb
docker compose up -d
```

And see now both the Backstage and the PostreSQL containers running:

```rb
CONTAINER ID   IMAGE                                             COMMAND                  CREATED         STATUS                   PORTS                                              NAMES
30513dd63c3c   deploy-backstage-with-score-backstage-backstage   "node packages/backe…"   6 minutes ago   Up 5 minutes             0.0.0.0:7007->7007/tcp, [::]:7007->7007/tcp        deploy-backstage-with-score-backstage-backstage-1
611e794cd11a   mirror.gcr.io/postgres:17-alpine                  "docker-entrypoint.s…"   6 minutes ago   Up 6 minutes (healthy)   5432/tcp                                           deploy-backstage-with-score-pg-Q10D93-1
```

Same applies now with `score-k8s`, with the exact same Score file:

```rb
score-k8s provisioners list

score-k8s generate score.yaml \
    --image ghcr.io/mathieu-benoit/backstage:latest

score-k8s resources list

kubectl apply -f manifests.yaml

kubectl get all

kubectl port-forward svc/backstage 7007:7007
```
```rb
NAME                             READY   STATUS    RESTARTS     AGE
pod/backstage-59dd9b8cfc-wth5b   1/1     Running   0            27s
pod/pg-backstage-5fa5f94b-0      1/1     Running   0            27s

NAME                            TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
service/backstage               ClusterIP   10.96.211.65   <none>        7007/TCP   29h
service/pg-backstage-5fa5f94b   ClusterIP   10.96.71.3     <none>        5432/TCP   27s

NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/backstage   1/1     1            1           29h

NAME                                   DESIRED   CURRENT   READY   AGE
replicaset.apps/backstage-59dd9b8cfc   1         1         1       27s
replicaset.apps/backstage-6dbcc8dff    0         0         0       29h
replicaset.apps/backstage-8596875bd9   0         0         0       19h
replicaset.apps/backstage-85f4674dd4   0         0         0       20h

NAME                                     READY   AGE
statefulset.apps/pg-backstage-5fa5f94b   1/1     27s
```

✅ In both cases, you can navigate to `[http://localhost:7007/](http://localhost:7007/)` and see that your Backstage app is still up and running. Same as before, but now talking to PostgreSQL! 🎉

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*DNwIsoxeKeEa0Raex8f-CQ.png)

💡In this section we were able to see how **Platform Engineers** can author concrete provisioners depending on the targeted platform, while the **Developers** just use the abstracted contract, without dealing with the technical details implementation.

## Expose this Backstage app

![](https://miro.medium.com/v2/resize:fit:640/format:webp/0*vl4bnmzCGyOh-bjJ)

So far we have used `http://localhost:3000` (with `yarn`), and `http://localhost:7007` (with `score-compose` and `score-k8s`) to expose and hit this Backstage app. If you run them in parallel, you can have conflicts with the port used, for example on `7007`.

The merge of `app-config.yaml` and `app-config.production.yaml` results with these values when starting this workload:

```rb
app:
  baseUrl: http://localhost:7007
backend:
  baseUrl: http://localhost:7007
  listen:
    port: ':7007'
  cors:
    origin: http://localhost:3000
```

❓What if we want to change either the host or the port? Do we need to manually change these `app-config.yaml` files? Which one? What will happen later in the CI/CD pipelines when this will be deployed in Development, Staging and Production environments? What about the technical details implementation: are we using an Ingress controller or Gateway API, etc.?

➡️ **As Developer**, here is how I want to describe what I need, in a generic way:

```rb
apiVersion: score.dev/v1b1
metadata:
  name: backstage
containers:
  backstage:
    image: .
    command:
      - "node"
    args:
      - packages/backend
      - "--config"
      - app-config.yaml
      - "--config"
      - app-config.production.yaml
    variables:
      POSTGRES_HOST: ${resources.pg.host}
      POSTGRES_PASSWORD: ${resources.pg.password}
      POSTGRES_PORT: ${resources.pg.port}
      POSTGRES_USER: ${resources.pg.username}
      APP_CONFIG_auth_providers_guest_dangerouslyAllowOutsideDevelopment: "true"
      APP_CONFIG_app_baseUrl: ${resources.dns.url}
      APP_CONFIG_backend_baseUrl: ${resources.dns.url}
      APP_CONFIG_backend_cors_origin: ${resources.dns.url}
service:
  ports:
    tcp:
      port: 7007
      targetPort: 7007
resources:
  pg:
    type: postgres-instance
  dns:
    type: dns
  route:
    type: route
    params:
      host: ${resources.dns.host}
      path: /
      port: 7007
```

💡In the `resources` section I am able to request a `dns` and associated `route` with the `port` and `path` to reach my workload. In the `variables` section, I override the different URLs in my config files with the `url` value generated by the `dns` resource.

```rb
score-compose init \
    --no-sample \
    --patch-templates https://raw.githubusercontent.com/score-spec/community-patchers/refs/heads/main/score-compose/unprivileged.tpl \
    --provisioners https://raw.githubusercontent.com/score-spec/community-provisioners/refs/heads/main/dns/score-compose/10-dns-with-url.provisioners.yaml
```

Generate the `compose.yaml` file from the Score file:

```rb
score-compose generate score.yaml \
    --image ghcr.io/mathieu-benoit/backstage:latest
```

*ℹ️ Note: in the* `*generate*` *command above, we don’t need anymore the* `*--publish*` *parameter.*

You can see that now your next deployment just got this `dns` resource:

```rb
score-compose resources list
```
```rb
+----------------------------------------+--------------------------------+
|                  UID                   |            OUTPUTS             |
+----------------------------------------+--------------------------------+
| dns.default#backstage.dns              | host, url                      |
+----------------------------------------+--------------------------------+
| postgres-instance.default#backstage.pg | host, password, port, username |
+----------------------------------------+--------------------------------+
| route.default#backstage.route          |                                |
+----------------------------------------+--------------------------------+
```

You can also see the actual outputs of this `dns` resource, and that now port `8080` is used:

```rb
score-compose resources get-outputs dns.default#backstage.dns
```
```rb
{
  "host": "dnsjdtv57.localhost",
  "url": "http://dnsjdtv57.localhost:8080"
}
```

Deploy the new `compose.yaml` file:

```rb
docker compose up -d
```
```rb
CONTAINER ID   IMAGE                                     COMMAND                  CREATED       STATUS                                  PORTS                                              NAMES
9b2ff62333ff   ghcr.io/mathieu-benoit/backstage:latest   "node packages/backe…"   5 hours ago   Up 5 hours                                                                                 deploy-backstage-with-score-backstage-backstage-1
4b1203acbf41   mirror.gcr.io/postgres:17-alpine          "docker-entrypoint.s…"   5 hours ago   Up 5 hours (healthy)                    5432/tcp                                           deploy-backstage-with-score-pg-mwgmNx-1
716b626ad841   mirror.gcr.io/nginx:1-alpine              "/docker-entrypoint.…"   5 hours ago   Up 5 hours                              0.0.0.0:8080->80/tcp, [::]:8080->80/tcp            deploy-backstage-with-score-routing-idouo7-1
```

✅ Navigate to `[http://dnsjdtv57.localhost:8080](http://dnsjdtv57.localhost:8080/)` and see that your Backstage app is still up and running. Same as before, running on Docker, but now exposed by a `dns` resource! 🎉

Same applies now with `score-k8s`, with the exact same Score file:

```rb
score-k8s init \
    --patch-templates https://raw.githubusercontent.com/score-spec/community-patchers/refs/heads/main/score-k8s/unprivileged.tpl \
    --provisioners https://raw.githubusercontent.com/score-spec/community-provisioners/refs/heads/main/dns/score-k8s/10-dns-with-url.provisioners.yaml

score-k8s generate score.yaml \
    --image ghcr.io/mathieu-benoit/backstage:latest

score-k8s resources list

kubectl apply -f manifests.yaml

kubectl get all,httproute
```
```rb
NAME                             READY   STATUS    RESTARTS   AGE
pod/backstage-7cfcc444bf-xt5jv   1/1     Running   0          32s
pod/pg-backstage-f8efdf15-0      1/1     Running   0          33s

NAME                            TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
service/backstage               ClusterIP   10.96.113.66    <none>        7007/TCP   33s
service/pg-backstage-f8efdf15   ClusterIP   10.96.157.102   <none>        5432/TCP   33s

NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/backstage   1/1     1            1           32s

NAME                                   DESIRED   CURRENT   READY   AGE
replicaset.apps/backstage-7cfcc444bf   1         1         1       32s

NAME                                     READY   AGE
statefulset.apps/pg-backstage-f8efdf15   1/1     33s

NAME                                                           HOSTNAMES       AGE
httproute.gateway.networking.k8s.io/route-backstage-43ebba9d   ["localhost"]   33s
```

*ℹ️ Note: we don’t need anymore the* `*kubectl port-forward*` *command.*

You can also see the actual outputs of this `dns` resource, and that now port `80` is used:

```rb
score-k8s resources get-outputs dns.default#backstage.dns
```
```rb
{
  "host": "dnsnocrke.localhost",
  "url": "http://dnsnocrke.localhost:80"
}
```

✅ Navigate to `[http://dnsnocrke.localhost:80](http://dnsnocrke.localhost/)` and see that your Backstage app is still up and running. Same as before, running in Kubernetes, but now exposed by a `dns` resource! 🎉

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*yBFiSoD-H5XiE073W3S1KA.png)

💡In this section we were able to see how **Platform Engineers** can author the way they want to implement how to exposed workloads on the targeted platform, while the **Developers** just use the abstracted contract (`dns`), without dealing with the technical details implementation.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*vvhcyg7PxvbzerI-IZrKzg.png)

## Let’s now split the frontend from the backend for the Backstage app

A good practice in terms of separation of concerns (productivity and security) is to split the Backastage app into two apps: `frontend` versus `backend`. We can easily [follow this guide to achieve this](https://backstage.io/docs/deployment/docker/#separate-frontend).

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*aFmcZZEZq-cIXVdpwEP3iQ.png)

And then we can define the two associated Score files.

`score-backend.yaml`:

```rb
apiVersion: score.dev/v1b1
metadata:
  name: backend
containers:
  backend:
    image: .
    command:
      - "node"
    args:
      - packages/backend
      - "--config"
      - app-config.yaml
      - "--config"
      - app-config.production.yaml
    variables:
      POSTGRES_HOST: ${resources.pg.host}
      POSTGRES_PASSWORD: ${resources.pg.password}
      POSTGRES_PORT: ${resources.pg.port}
      POSTGRES_USER: ${resources.pg.username}
      APP_CONFIG_auth_providers_guest_dangerouslyAllowOutsideDevelopment: "true"
      APP_CONFIG_backend_cors_origin: ${resources.dns.url}
    livenessProbe:
      httpGet:
        path: /.backstage/health/v1/liveness
        port: 7007
    readinessProbe:
      httpGet:
        path: /.backstage/health/v1/readiness
        port: 7007
service:
  ports:
    tcp:
      port: 7007
      targetPort: 7007
resources:
  pg:
    type: postgres-instance
  dns:
    type: dns
    id: dns
  route:
    type: route
    params:
      host: ${resources.dns.host}
      path: /api
      port: 7007
```

`score-frontend.yaml`:

```rb
apiVersion: score.dev/v1b1
metadata:
  name: frontend
containers:
  frontend:
    image: .
    variables:
      APP_CONFIG_app_baseUrl: ${resources.dns.url}
      APP_CONFIG_backend_baseUrl: ${resources.dns.url}
    livenessProbe:
      httpGet:
        path: /healthcheck
        port: 8080
    readinessProbe:
      httpGet:
        path: /healthcheck
        port: 8080
service:
  ports:
    tcp:
      port: 3000
      targetPort: 8080
resources:
  backend:
    type: service
  dns:
    type: dns
    id: dns
  route:
    type: route
    params:
      host: ${resources.dns.host}
      path: /
      port: 3000
```

*Note: we can see that for the* `*dns*` *in the two Score files, we are using* `*id: dns*`*, this allows to have them sharing the same* `*dns*`*.*

And then you can do with `score-compose`:

```rb
score-compose init \
    --no-sample \
    --provisioners https://raw.githubusercontent.com/score-spec/community-provisioners/refs/heads/main/service/score-compose/10-service.provisioners.yaml \
    --provisioners https://raw.githubusercontent.com/score-spec/community-provisioners/refs/heads/main/dns/score-compose/10-dns-with-url.provisioners.yaml

score-compose generate score-backend.yaml \
    --image ghcr.io/mathieu-benoit/backstage-backend:latest

score-compose generate score-frontend.yaml \
    --image ghcr.io/mathieu-benoit/backstage-frontend:latest

score-compose resources list

docker compose up -d

docker ps
```
```rb
+--------------------------------------+--------------------------------+
|                 UID                  |            OUTPUTS             |
+--------------------------------------+--------------------------------+
| dns.default#dns                      | host, url                      |
+--------------------------------------+--------------------------------+
| postgres-instance.default#backend.pg | host, password, port, username |
+--------------------------------------+--------------------------------+
| service.default#frontend.backend     | name                           |
+--------------------------------------+--------------------------------+
| route.default#backend.route          |                                |
+--------------------------------------+--------------------------------+
| route.default#frontend.route         |                                |
+--------------------------------------+--------------------------------+
```
```rb
CONTAINER ID   IMAGE                                              COMMAND                  CREATED          STATUS                   PORTS                                                 NAMES
1712a2002838   ghcr.io/mathieu-benoit/backstage-frontend:latest   "/docker-entrypoint.…"   3 minutes ago    Up 2 minutes             80/tcp                                                frontend-frontend-1
6bf734ab9179   ghcr.io/mathieu-benoit/backstage-backend:latest    "node packages/backe…"   3 minutes ago    Up 2 minutes                                                                   backend-backend-1
9a126ed0456c   mirror.gcr.io/nginx:1-alpine                       "/docker-entrypoint.…"   3 minutes ago    Up 2 minutes             0.0.0.0:8080->80/tcp, [::]:8080->80/tcp               routing-5QD6z8-1
5ec1732b6695   mirror.gcr.io/postgres:17-alpine                   "docker-entrypoint.s…"   3 minutes ago    Up 3 minutes (healthy)   5432/tcp                                              pg-glZvLw-1
```

And same with `score-k8s`:

```rb
score-k8s init \
    --provisioners https://raw.githubusercontent.com/score-spec/community-provisioners/refs/heads/main/service/score-k8s/10-service.provisioners.yaml \
    --provisioners https://raw.githubusercontent.com/score-spec/community-provisioners/refs/heads/main/dns/score-k8s/10-dns-with-url.provisioners.yaml

score-k8s generate score-backend.yaml \
    --image ghcr.io/mathieu-benoit/backstage-backend:latest

score-k8s generate score-frontend.yaml \
    --image ghcr.io/mathieu-benoit/backstage-frontend:latest

score-k8s resources list

kubectl apply -f manifests.yaml

kubectl get all,httproute
```
```rb
+--------------------------------------+--------------------------------+
|                 UID                  |            OUTPUTS             |
+--------------------------------------+--------------------------------+
| dns.default#dns                      | host, url                      |
+--------------------------------------+--------------------------------+
| postgres-instance.default#backend.pg | host, password, port, username |
+--------------------------------------+--------------------------------+
| service.default#frontend.backend     | name                           |
+--------------------------------------+--------------------------------+
| route.default#backend.route          |                                |
+--------------------------------------+--------------------------------+
| route.default#frontend.route         |                                |
+--------------------------------------+--------------------------------+
```
```rb
NAME                           READY   STATUS    RESTARTS   AGE
pod/backend-57fc5664d-4hg7l    1/1     Running   0          22s
pod/frontend-db644cf86-n9cjd   1/1     Running   0          22s
pod/pg-backend-61f0e7c1-0      1/1     Running   0          60m

NAME                          TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
service/backend               ClusterIP   10.96.183.51   <none>        7007/TCP   60m
service/frontend              ClusterIP   10.96.90.135   <none>        3000/TCP   60m
service/pg-backend-61f0e7c1   ClusterIP   10.96.45.108   <none>        5432/TCP   60m

NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/backend    1/1     1            1           60m
deployment.apps/frontend   1/1     1            1           60m

NAME                                  DESIRED   CURRENT   READY   AGE
replicaset.apps/backend-57fc5664d     1         1         1       22s
replicaset.apps/backend-64fc859b9d    0         0         0       60m
replicaset.apps/frontend-68ccb68884   0         0         0       60m
replicaset.apps/frontend-db644cf86    1         1         1       22s

NAME                                   READY   AGE
statefulset.apps/pg-backend-61f0e7c1   1/1     60m

NAME                                                          HOSTNAMES                 AGE
httproute.gateway.networking.k8s.io/route-backend-711726ce    ["dnsxmfazk.localhost"]   60m
httproute.gateway.networking.k8s.io/route-frontend-61f9e1b8   ["dnsxmfazk.localhost"]   60m
```

And that’s it! Even better now!

## That’s a wrap!

In this blog post you were able to deploy a containerized Backstage app (as one container or two) to Docker/Podman and Kubernetes, and this via Score, `score-compose ` and `score-k8s`. This Backstage app talks to PostreSQL and is exposed via a DNS. **Developers** now define what they need around their Backstage app in the Score file, it’s a contract for when it will be deployed to their Platform. On the other hand, **Platform Engineers** focus on the concrete implementation from this Score file: the platform (Docker/Podman or Kubernetes in this case) and the resource provisioners (PostreSQL and DNS in this case). Developers can now focus on their code, while Platform Engineers can focus on standardization.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*vvhcyg7PxvbzerI-IZrKzg.png)

Hope you enjoyed this one! Cheers!

## More resources about Backstage

- [Five Years In, Backstage Is Just Getting Started — The New Stack](https://thenewstack.io/five-years-in-backstage-is-just-getting-started/)
- [Introduction to Backstage: Developer Portals Made Easy (LFS142) — Linux Foundation — Education](https://training.linuxfoundation.org/training/introduction-to-backstage-developer-portals-made-easy-lfs142/)
- [Certified Backstage Associate (CBA) — Linux Foundation — Education](https://training.linuxfoundation.org/certification/certified-backstage-associate-cba/)

## More resources about Score

- [Trip report — Score at KubeCon London 2025 | Score](https://score.dev/blog/kubecon-london-2025-trip-report/)
- [Examples | Score](https://docs.score.dev/docs/examples/)
- [Generate your Backstage software catalog files with Score](https://medium.com/@mabenoit/generate-your-backstage-software-catalog-files-with-score-b62aa33e8ecc)

Solution Engineer at Docker | CNCF Ambassador | GDE Cloud

## More from Mathieu Benoit and ITNEXT

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--45bb2d7c2d90---------------------------------------)