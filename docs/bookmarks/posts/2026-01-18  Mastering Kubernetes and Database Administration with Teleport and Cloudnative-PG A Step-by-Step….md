---
title: "Mastering Kubernetes and Database Administration with Teleport and Cloudnative-PG: A Step-by-Step…"
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - "untagged"
source: "https://mirakl.tech/mastering-kubernetes-and-database-administration-with-teleport-and-cloudnative-pg-a-step-by-step-f768f1c614de"
author:
  - "[[Mirakl Labs]]"
---
<!-- more -->

[Sitemap](https://mirakl.tech/sitemap/sitemap.xml)## [Mirakl Tech Blog](https://mirakl.tech/?source=post_page---publication_nav-46f311b0d17c-f768f1c614de---------------------------------------)

[![Mirakl Tech Blog](https://miro.medium.com/v2/resize:fill:76:76/1*iqi4nkVqH5XcBsWowi0bEw.jpeg)](https://mirakl.tech/?source=post_page---post_publication_sidebar-46f311b0d17c-f768f1c614de---------------------------------------)

Deep dives with members of the Mirakl engineering, product and data teams who are at the forefront of the enterprise marketplace revolution.

*By* [*Thomas Loubiou*](https://www.linkedin.com/in/thomas-loubiou/)*, Site Reliability Engineer at Mirakl*

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*vjnfySvE8GuLnbQxFpcezQ.jpeg)

At Mirakl, we have chosen to use [Teleport](https://goteleport.com/) as our primary method of accessing all our infrastructure. This includes SSH access to our servers, Kubernetes clusters, and PostgreSQL databases. Initially, we were using a combination of self-hosted and cloud-managed PostgreSQL databases that were well integrated with Teleport. However, we recently made the decision to migrate to [Cloudnative-PG](https://cloudnative-pg.io/), a Kubernetes operator specifically designed for managing PostgreSQL databases on Kubernetes.

Cloudnative-PG, or CNPG for short, offers a variety of features. It allows us to create primary and standby databases, and it also provides a connection-pooler for managing connections to the databases.

In this article, we will discuss how we integrated Cloudnative-PG with Teleport, and the challenges we encountered during the process. Our ultimate goal is to develop a self-contained Helm chart that can create PostgreSQL high-availability clusters using CNPG, while automatically registering them in our Teleport cluster.

## Seamless Integration of Teleport with PostgreSQL

In Teleport’s perspective, integrating a CNPG database is as straightforward as integrating a self-hosted PostgreSQL database. The process of integrating a self-hosted PostgreSQL database with Teleport is pretty easy. It is based on mTLS ([mutual TLS authentication](https://en.wikipedia.org/wiki/Mutual_authentication)), where both the client and server authenticate each other using certificates. Here is an overview of the integration steps:

- The Teleport Agent establishes a connection with the PostgreSQL database using its client certificate, and it verifies the server certificate using the designated Certificate Authority (CA).
- The PostgreSQL database validates the certificate provided by the Teleport Agent using the configured CA. Additionally, it cross-checks that the database user corresponds to the certificate user.

Below, you will find a helpful diagram that illustrates the integration process:

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*C_SQiqjJZiBc6O0OzXtGbw.png)

It is worth noting that Teleport Proxy generates an internal certificate to connect with the database, allowing it to decrypt the traffic and log user requests. If you’d like to explore further details, take a look at the Teleport database architecture [documentation](https://goteleport.com/docs/database-access/architecture/).

## Mapping Teleport Users to PostgreSQL Users

When a Teleport user connects to a PostgreSQL database, it will use a PostgreSQL user, not its own username. A single Teleport user may be allowed to use multiple PostgreSQL users (we could imagine users with read-only access, admin, etc…).

The mapping of Teleport user <-> PostgreSQL user is done on the [Teleport Roles](https://goteleport.com/docs/reference/resources/#role) attached to the user (a Teleport user may have multiple roles).

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*gzFalzTP1Cg8WaCf5-I7XA.png)

Let’s say we want to provide two PostgreSQL users to our Teleport users, `teleport_user_read` that has read-only access to the database and `teleport_user_write` that has read/write access to the database.

We can first create a Teleport role and associate it to our Teleport user. The role will only target the database that we will provision using CNPG, so we will use a label to target them. We decided to put the following label on our databases later: `provisioned_by: cloudnative-pg`.

```c
tctl create -f <<EOF
---
kind: role
version: v6
metadata:
  name: database_access
spec:
  allow:
    db_labels:
      provisioned_by: cloudnative-pg  # Target cloudnative-pg databases
    db_names:
      - '*'  # Allow to connect to any database inside the instance
    db_users:  # Allow to impersonate those users
      - teleport_user_read
      - teleport_user_write
EOF
```

Now we can update our Teleport user to add the role. If you use a local Teleport user, you can use the `tctl` command (adapt to your needs):

```c
tctl auth update teleport_user 
--set-roles=database_access,OTHER_ROLES
```

We can now create the PostgreSQL database and add Teleport users to the database.

It is important to note that although Teleport introduced the capability to dynamically provision PostgreSQL users with the release of v13.1.0, we have decided not to utilize this feature for now. As it is still relatively new, we prefer to maintain greater control over the users we create within our databases.

## Streamlining CNPG Database Creation

Next, let’s create our CNPG database using a new [Helm](https://helm.sh/) chart. The chart we will write will have prerequisites that you have a CNPG operator already deployed in your Kubernetes cluster. To install the Cloudnative-PG operator, you can follow the [official documentation](https://cloudnative-pg.io/documentation/1.21/installation_upgrade/#installation-on-kubernetes). I will assume you have a working operator in the rest of this article.

Here is the structure we will have for our chart:

├── Chart.yaml  
├── values.yaml  
├── templates/  
│ ├── cluster.yaml  
│ ├── users-secrets.yaml

Start with a simple `Chart.yaml`:

```c
# file: Chart.yaml
---
apiVersion: v2
name: cnpg-database
description: A Helm chart for CNPG database
type: application
version: 0.1.0
```

Now we can create the `templates/cluster.yaml` file that will contain our CNPG cluster definition. Let’s start with a simple definition:

```c
# file: templates/cluster.yaml
---
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: {{ .Values.dbName }}
spec:
  description: "PostgreSQL Cluster that integrates with Teleport"
  imageName: {{ .Values.image.name}}:{{ .Values.image.tag }}
  instances: {{ .Values.instancesCount }}
  bootstrap:
    initdb: #  Setup the database.
      database: {{ .Values.database.name }}
      owner: {{ .Values.database.owner }}
      localeCollate: en_US.UTF-8
      localeCtype: en_US.UTF-8
      encoding: UTF-8
      secret:
        name: {{ .Values.dbName }}-owner-user
  storage:
    size: "{{ .Values.storage.pgData.sizeGb }}Gi"
  walStorage:
    size: "{{ .Values.storage.wal.sizeGb }}Gi"

  resources:
    {{- toYaml .Values.resources | nindent 4 }}

  postgresql:
    parameters:
      {{- toYaml .Values.pgParameters | nindent  6 }}
```

And the corresponding `templates/users-secrets.yaml`

```c
# file: templates/users-secrets.yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Values.dbName }}-owner-user
data:
  username: {{ .Values.database.owner | b64enc }}
  password: {{ .Values.database.ownerPassword | b64enc }}
```

And finally the `values.yaml` file:

```c
# file: values.yaml
---
# -- The name of the database.
dbName: cnpg-postgres
database:
  # -- The name of the PostgreSQL database to create.
  name: database1
  # -- The name of the PostgreSQL user that will own the database.
  owner: app_user
  # -- The password of the PostgreSQL user that will own the database.
  ownerPassword: "password"

# -- The number of instances to create for the database.
instances: 2
image:
  # -- The name of the image to use for the database.
  name: ghcr.io/cloudnative-pg/postgresql
  # -- The tag of the image to use for the database.
  tag: 13.6
storage:
  pgData:
    # -- The size of the persistent volume that will be created for the database.
    sizeGb: 10
  wal:
    # -- The size of the persistent volume that will be created for the WAL.
    sizeGb: 10
# -- Postgres parameters, see <https://cloudnative-pg.io/documentation/1.21/postgresql_conf/> and <https://www.postgresql.org/docs/current/runtime-config.html>.
pgParameters: {}
# -- Resources to allocate to the database pods.
resources: {}
```

**Note**  
The value of `database.ownerPassword` should not be put in clear in the values. At Mirakl we manage our secrets using Vault, so we can use the [Argo CD Vault Plugin](https://argocd-vault-plugin.readthedocs.io/en/stable/) to fetch the password from Vault.

We can then try to deploy our chart:

```c
helm install cnpg-database ./
```

## Creating PostgreSQL Teleport users

Once the CNPG database is successfully created, the next step is to establish the PostgreSQL users that will be utilized by Teleport to access the database environment. It’s important to note that the user rights configuration outlined in this article serves as a demonstration and should be adjusted to align with your specific requirements.

In our setup, we will create a single schema with a name that matches the owner user of the database. Subsequently, we will grant access rights to this schema to the Teleport users. However, in a real-world scenario, you may have multiple schemas and might want to incorporate triggers to automate the process of updating Teleport user rights when new schemas are created.

CNPG is able to manage database users, let’s use it to create the users.

In our `templates/clusters.yaml` file, we can add a `spec.managed.roles` field:

```c
# file: templates/cluster.yaml
---
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: {{ .Values.dbName }}
spec:
  managed:
    roles:
      - name: teleport_user_read
        ensure: present
        comment: "Teleport user with read-only access"
        login: true
        inherit: true
        connectionLimit: 20
      - name: teleport_user_write
        ensure: present
        comment: "Teleport user with read/write access"
        login: true
        inherit: true
        connectionLimit: 20
        inRoles: 
          - {{ .Values.database.owner }} #  Inherit from the owner, so can read/write data pushed by the application
```

Throughout the remainder of this article, we will utilize `.Values.dbName` to generate unique names for resources related to the CNPG cluster. This is for demonstration purposes. In an actual chart, it is recommended to implement a more centralized method, such as a helper function, to generate names for resources in a consistent and scalable manner.

CNPG will create those roles in the PostgreSQL database, but we didn’t specify any rights for them. We can do it in the bootstrap section.

The drawback of this solution is that the `bootstrap.initdb` section is only executed when the database is created, so if we update the chart and redeploy it, the users won’t be updated. A better solution to this problem may be to use some migration based tool with a to run it, but it’s not the subject of this article.

Let’s change our initdb section to add users rights:

```c
# file: templates/cluster.yaml
---
spec:
  bootstrap:
    initdb:
      postInitApplicationSQL:
        # Create the owner role and schema to be able to reference it later
        - CREATE ROLE {{ .Values.database.owner }};
        - CREATE SCHEMA {{ .Values.database.owner }} AUTHORIZATION {{ .Values.database.owner }};

        # Create the Teleport read user so we can reference it later in this script
        - CREATE ROLE teleport_user_read;

        # Grant read privileges to the Teleport read user
        - GRANT USAGE ON SCHEMA {{ .Values.database.owner }} TO teleport_user_read;
        - GRANT SELECT ON ALL TABLES IN SCHEMA {{ .Values.database.owner }} TO teleport_user_read;
        - GRANT USAGE ON ALL SEQUENCES IN SCHEMA {{ .Values.database.owner }} TO teleport_user_read;
        - ALTER DEFAULT PRIVILEGES IN SCHEMA {{ .Values.database.owner }} GRANT SELECT ON TABLES TO teleport_user_read;
        - ALTER DEFAULT PRIVILEGES IN SCHEMA {{ .Values.database.owner }} GRANT SELECT ON SEQUENCES TO teleport_user_read;

        # Transactions default read for the Teleport read user
        - ALTER USER teleport_user_read SET default_transaction_read_only = on;
```

In order to apply this changes, we have to delete the CNPG cluster and recreate it:

```c
helm delete cnpg-database
helm install cnpg-database ./
```

With the PostgreSQL database now established alongside our Teleport users, it’s important to note that these users do not currently support password authentication. As a result, direct login with these Teleport users is not yet possible.

To enable secure and authenticated connections between Teleport and the PostgreSQL database, it is crucial to set up mutual Transport Layer Security (mTLS) communication. By configuring mTLS, we can establish a trusted and encrypted channel that allows Teleport users to securely connect to the database while ensuring data confidentiality and integrity.

## Setting up mTLS between Teleport and the database

Here comes the first challenge.

Cloudnative-pg already internally uses mTLS to authenticate the connection between master and replica databases, and also between the connection pooler and the databases.

By default, when you create a CNPG cluster, it will generate a CA and put it into Kubernetes secret. This CA is used to sign the certificates for the master and replica databases, and also for the connection pooler.

Thankfully, it also permits us to use our own Certificate Authorities (CA) to generate those client and server certificates.

The problem here is that we also want the PostgreSQL server to trust the Teleport generated certificates. Teleport has its own CA, and we don’t want to rely on it to generate CNPG internal client certificates (and even if we wanted we certainly couldn’t, because the Teleport CA has to be kept secret).

What we want is to trust both CA on the PostgreSQL server side:

- An ‘internal’ CNPG client CA, used to generate master/slave and pooler certificates.
- The ‘external’ Teleport client CA, used to generate Teleport user certificates.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*fE1zYo5dIWpA7r7yk2h-9Q.png)

CNPG provides a way to specify the client CA to trust for the server with the option `spec.certificates.clientCASecret`, but it only accepts a single Kubernetes secret containing the CA certificate stored in PEM format in a `ca.crt` key ([doc](https://cloudnative-pg.io/documentation/1.21/certificates/#client-certificate)).

After digging into the code, I found that the `ca.crt` key is mapped to the `ssl_ca_file` parameter of PostgreSQL’s configuration file. This file can contain multiple CAs ([doc](https://www.postgresql.org/docs/current/ssl-tcp.html#SSL-CLIENT-CERTIFICATES)), separated by a newline, so we need to create a Kubernetes secret containing both CAs.

One important thing to note is that when you specify the `clientCASecret` key in the CNPG cluster, CNPG stops generating client certificates. That implies we have to generate a secret for the field `spec.certificates.replicationTLSSecret` that will contain a certificate and private key for the user `streaming_replica`. It is used by CNPG for the replication process to keep the PostgreSQL replica up-to-date.

First, we will generate a CA for the CNPG client certificates, and then we will see how to merge it with the Teleport CA in a single secret.

## Establishing Secure Client Certificates

To generate client certificates for secure communication, we will rely on [cert-manager](https://cert-manager.io/), a powerful tool for managing certificates within a Kubernetes cluster. Our goal is to establish a Certificate Authority (CA) that will be responsible for signing the replication user’s certificate.

It’s important to note that a valid ***root CA*** is a self-signed certificate, meaning it has been signed with its own private key. On the other hand, a valid ***intermediate CA*** has its certificate signed by a root CA.

In this case, we aim to create a ***root CA***, so we will generate a self-signed certificate. This will serve as the foundation for our certificate infrastructure, ensuring the trustworthiness and integrity of the certificates used for client authentication.

Please make sure that cert-manager is already installed within your Kubernetes cluster before proceeding with the steps outlined below.

```c
# file: templates/selfsigned-issuer.yaml
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: "{{ .Values.dbName }}-selfsigned-issuer"
spec:
  selfSigned: {}
```

Next, let’s create the client CA:

```c
# file: templates/client-ca.yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: "{{ .Values.dbName }}-client-ca"
  labels:
    cnpg.io/reload: "" #  Note this annotation, it tells CNPG to reload the database when this secret change
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: "{{ .Values.dbName }}-client-ca"
spec:
  isCA: true
  commonName: "{{ .Values.dbName }}-client-ca"
  secretName: "{{ .Values.dbName }}-client-ca"
  usages:
    - client auth
  issuerRef:
    name: "{{ .Values.dbName }}-selfsigned-issuer"
    kind: Issuer
    group: cert-manager.io
```

Please note that the label `cnpg.io/reload` serves as an instruction to the CNPG operator, guiding it to reload the database whenever there are changes in the labeled Secrets or ConfigMaps within the Kubernetes cluster. For more detailed information on how to implement this label and its functionality, please refer to the [CNPG documentation](https://cloudnative-pg.io/documentation/1.21/kubectl-plugin/#restart).

Now we have a CA, we can create the corresponding issuer to generate new certificates:

```c
# file: templates/client-ca-issuer.yaml
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: "{{ .Values.dbName }}-client-ca-issuer"
spec:
  ca:
    secretName: "{{ .Values.dbName }}-client-ca"
```

Next, we will create the `streaming_replica` certificate:

```c
# file: templates/replication-user-cert.yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: "{{ .Values.dbName }}-replication-user-cert"
  labels:
    cnpg.io/reload: ""
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: "{{ .Values.dbName}}-replication-user-cert"
spec:
  secretName: "{{ .Values.dbName }}-replication-user-cert"
  usages:
    - client auth
  commonName: streaming_replica
  issuerRef:
    name: "{{ .Values.dbName }}-client-ca-issuer"
    kind: Issuer
    group: cert-manager.io
```

Now we have a secret containing the CA and the replication certificate, we can use them in the CNPG cluster:

```c
# file: templates/cluster.yaml
---
apiVersion: cloudnative.pg/v1
kind: Cluster
spec:
  certificates:
    replicationTLSSecret: "{{ .Values.dbName }}-replication-user-cert"
    clientCASecret: "{{ .Values.dbName }}-client-ca"
```

Our PostgreSQL cluster is now equipped with a custom client CA. However, it currently lacks trust in Teleport certificates. To establish this trust, we must include the Teleport CA within our client CA secret.

To accomplish this, we will proceed with creating a new secret, specifically a CA bundle.

## Creating a Client CA bundle

At Mirakl we deploy our Kubernetes manifests using ArgoCD + Helm + argocd-vault-plugin. As we store the Teleport DB client CA in our Vault, we could easily create a Kubernetes secret containing the Teleport DB CA certificate:

```c
# file: teleport-db-client-ca-secret.yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: "{{ .Values.dbName }}-teleport-db-client-ca"
data:
  ca.crt: {{ .Values.teleport.dbCA | b64enc }}
```

And in values:

```c
teleport:
  # -- Teleport CA to inject into CNPG database to trust Teleport client certificates
  # Retrieve the CA from Vault (path is secret/teleport/ca, key is db)
  dbCA: <path:secret/teleport/ca#db>
```

Previously, deploying the code using Helm was a straightforward process of copy-pasting and deploying. However, with the introduction of the ArgoCD Vault plugin, there is now an additional dependency to consider. To test using Helm, you have the flexibility to replace vault placeholders in the values file (values that resemble `<path:secret/XXX#YYY>`).

The problem is that we need to merge this secret with the CNPG client CA secret, and we can’t do it with Helm + ArgoCD in a reliable way.

Indeed, the client CA is managed by CNPG and may change at runtime, so we need a way to update the bundle secret when the client CA changes.

We need a sort of Kubernetes secret merge operator to generate this bundle secret. I have found 4 existing solutions:

- [trust-manager](https://cert-manager.io/docs/trust/trust-manager/), a side project of cert-manager. It does *almost* exactly what we need: it fetches CA from multiple sources and generates a bundle. The problem is that it only fetches these CA from a ‘trust’ namespace, and pushes them into a secret in all other namespaces. We want it to fetch the secrets in our namespace and push the bundle in the same namespace. Because of this design the [Custom Resource Definition](https://kubernetes.io/docs/tasks/extend-kubernetes/custom-resources/custom-resource-definitions/) (CRD) it uses is not namespaced, so it’s not a viable solution.
- [konfd](https://github.com/kelseyhightower/konfd) is a little Go program able to fetch data from other secrets and generate new ConfigMaps or Secrets. It is really permissive, because we can use a template to generate the new secret. Here the limitation is that it is interval based, and it caches the source secret internally. So if we update the client CA or the Teleport CA, it may never fetch the new data. We could easily fork it and change this behavior, but the project is pretty old and not maintained anymore.
- [konfigurator](https://github.com/stakater/Konfigurator) is an alternative to konfd, well maintained and that should works on our case, but it requires you to set a app field in the KonfiguratorTemplate CRD that reference a deployment/statefulset/daemonset to rollout restart when the secret change. Because we use CNPG we don’t have any deployment/statefulset/daemonset to reference, so we can’t use it (moreover we don’t want to restart the database, CNPG is smart enough to reload PostgreSQL without interruption).

[external-secrets](https://external-secrets.io/) is an operator that fetches secrets from external sources and creates Kubernetes secrets. It can generate new secrets from a template, and retry to render it regularly (interval based). Secret source includes Vault and Kubernetes secrets, so in theory it should be able to do what we want, but we decided to not use it yet (but we certainly will in the future).

Because none of these solutions fits our needs (except maybe external-secrets, but we need to explore this path more deeply, as it may be used in other internal projects), we decided to create a small bash script that will fetch the secrets and merge them in a single secret.

```c
#!/usr/bin/env bash
# file: files/scripts/ca/sync-client-ca.sh
set -euo pipefail

# This script watches changes for the client CA and updates the CA bundle for CNPG.

: "${TARGET_SECRET?Required}"
: "${CLIENT_CA_SECRET?Required}"
: "${TELEPORT_CA?Required}"
: "${NAMESPACE?Required}"

function push_secret() {
  local client_ca=$1
  rendered_ca=$(
    cat <<EOF
$client_ca
$TELEPORT_CA
EOF
  )
  kubectl -n "$NAMESPACE" patch secret "$TARGET_SECRET" --patch-file <(
    cat <<EOF
---
data:
  ca.crt: $(echo -n "$rendered_ca" | base64 -w0)
EOF
  )
}

while read -r line; do
  CA_CRT=$(echo "$line" | base64 -d)
  push_secret "$CA_CRT"
done < <(kubectl -n "$NAMESPACE" get secret "$CLIENT_CA_SECRET" -w -ojsonpath="{.data.ca\.crt}{'\n'}")
```

This script is really simple, it just fetches the client CA secret and the Teleport CA secret, and merges them in a single secret. It uses the watch API, so it will update the secret as soon as the client CA secret changes.

We can put it in a `files/scripts/ca/sync-client-ca.sh` file and use Helm to generate a ConfigMap:

```c
# file: templates/sync-client-ca-scripts.yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: "{{ .Values.dbName }}-sync-client-ca-scripts"
data:
  {{- (.Files.Glob "files/scripts/ca/*").AsConfig | nindent 2 }}
```

This script can now be used in a Pod, and needs to access the Kubernetes API (more particularly Kubernetes secret):

```c
# file: templates/sync-client-ca.yaml
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: "{{ .Values.dbName }}-sync-client-ca"
rules:
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get", "watch", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: "{{ .Values.dbName }}-sync-client-ca"
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: "{{ .Values.dbName }}-sync-client-ca"
subjects:
  - kind: ServiceAccount
    name: "{{ .Values.dbName }}-sync-client-ca"
    namespace: "{{ .Release.Namespace }}"
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: "{{ .Values.dbName }}-sync-client-ca"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: "{{ .Values.dbName }}-sync-client-ca"
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/instance: "{{ .Release.Name }}"
      app.kubernetes.io/component: sync-client-ca
      app.kubernetes.io/name: sync-client-ca
  template:
    metadata:
      labels:
        app.kubernetes.io/instance: "{{ .Release.Name }}"
        app.kubernetes.io/component: sync-client-ca
        app.kubernetes.io/name: sync-client-ca
    spec:
      containers:
        - name: bash
          image: bitnami/kubectl:{{ .Capabilities.KubeVersion.Major }}.{{ .Capabilities.KubeVersion.Minor }}
          command:
            - bash
            - -c
            - cd scripts && ./sync-client-ca.sh
          env:
            - name: TARGET_SECRET
              value: "{{ .Values.dbName }}-cnpg-client-ca-bundle"
            - name: CLIENT_CA_SECRET
              value: "{{ .Values.dbName }}-cnpg-client-ca"
            - name: NAMESPACE
              value: "{{ .Release.Namespace }}"
            - name: TELEPORT_CA
              value: "{{ .Values.teleport.dbCA }}"
          volumeMounts:
            - name: scripts
              mountPath: /scripts
      serviceAccountName: "sync-client-ca"
      volumes:
        - name: scripts
          configMap:
            name: "{{ .Values.dbName }}-sync-client-ca-scripts"
            items:
              - key: sync-client-ca.sh
                path: sync-client-ca.sh
                mode: 0755
```

Now we will have a new secret `{{.Values.dbName}}-cnpg-client-ca-bundle` that contains both CAs.

**Note**  
Also note that we inject the Teleport CA directly in the Pod using the `TELEPORT_CA` environment variable without using the secret. This permits us to make the deployment automatically restart when the Teleport CA changes.

We also could have used an annotation on the Pod to trigger a restart when the secret changed, but to keep the code simple we decided to use this solution. The annotation should have looked like this:

```c
metadata:
  annotations:
    checksum/config-teleport-ca: {{ include (print $.Template.BasePath "/teleport-db-client-ca-secret.yaml") . | sha256sum }}
```

The file `teleport-db-client-ca-secret.yaml` can be deleted, we don’t need it anymore.

We can use it in our CNPG cluster definition:

```c
# file: templates/cluster.yaml
---
apiVersion: cloudnative.pg/v1
kind: Cluster
spec:
  certificates:
    clientCASecret: "{{ .Values.dbName }}-cnpg-client-ca-bundle"
```

PostgreSQL is now configured to trust both the CNPG client certificates and the Teleport client certificates when we try to connect to it using mTLS.

We can now enable mTLS for our Teleport users.

## Implementing mTLS for Teleport users

Now that PostgreSQL is aware of the Teleport CA, we need to tell it to enable mTLS for Teleport users.

This is done using the [pg\_hba.conf](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html) file.

**Important**  
This file lists for each connection type what is the method to use to authenticate. When someone tries to connect to the database, PostgreSQL will look for the **first** matching line in this file and use the corresponding method to authenticate the user, so you may pay attention to the order of the lines.

CNPG manages this file for us, and allows us to add new lines through the array field `spec.postgresql.pg_hba`. The syntax is the same as the `pg_hba.conf` file.

Let’s add a new line to enable mTLS for postgresql user named `teleport_user_read`:

```c
# file: templates/cluster.yaml
---
spec:
  postgresql:
    pg_hba:
      - hostssl all teleport_user_read,teleport_user_write 0.0.0.0/0 cert
```

**Warning**  
The syntax of `pg_hba.conf` depends on the PostgreSQL version. For example, recent versions support regex for users, but older versions don’t. In order to be compatible with all versions of PostgreSQL, we decided to not use regex in the following examples.

If you want to only use recent version of PostgreSQL, you can use regex to match all users that start with `teleport_user_`:  
`hostssl all /^teleport_user_.*$0.0.0.0/0 cert`

Now, with the PostgreSQL cluster configured to trust both the CNPG client CA and the Teleport client CA, our Teleport users can securely log in using mTLS. This means we can now easily reference this database within Teleport and connect to it using tsh, ensuring a seamless and secure connection.

## Registering the database in Teleport

In order to make Teleport aware of our database, we have multiple solutions:

1. We can deploy a new agent in our Kubernetes cluster, and statically configure it to register the database in Teleport. This has the advantage that we can easily test it without impacting other Teleport components. The main drawback is that with this design we need to deploy at least one agent per CNPG database.
2. Each Kubernetes cluster already has a local Teleport agent that is used to register the Kubernetes cluster in Teleport. We can use this agent to access the database in Teleport, and register the database [dynamically](https://goteleport.com/docs/database-access/guides/dynamic-registration/). Here the difficult part is to find a way to register the database dynamically.

Both solutions work, we started with the first one in order to test things, and then switched to the second one which is less resource consuming (but currently has a main drawback).

### Utilizing a Teleport Agent for Static Database Registration

The idea is to deploy a new Teleport agent in the same namespace as the CNPG database, and configure it to register the database in Teleport.

Teleport has a [Helm chart](https://github.com/gravitational/teleport/tree/master/examples/chart/teleport-kube-agent) we can use to deploy the agent.

Let’s add it to our chart’s dependencies:

```c
# file: Chart.yaml
---
dependencies:
  - name: teleport-kube-agent
    version: 13.3.5
    repository: https://charts.releases.teleport.dev
    alias: teleport
```

We can then configure it:

```c
file: values.yaml
---
teleport:
  # Teleport chart parameters
  roles: db
  authToken: <path:secret/teleport/join-tokens/db#token>  # We put our Teleport join token in our Vault so we can easily fetch it from our Helm charts.
  caPin:
    - <path:secret/teleport/ca-pin#ca-pin>  # We put our Teleport CA pin in our Vault so we can easily fetch it from our Helm charts.
  proxyAddr: teleport.mirakl.net:443
  serviceAccount:
    create: true
  rbac:
    create: false
  databases:  # Overridden in mirakl-config, see below
    - name: placeholder
      uri: placeholder
      protocol: postgres
  podSecurityPolicy:
    enabled: false
  extraArgs:
    # NOTE We inject a custom config, because the chart's built in configuration
    # NOTE keys don't support dynamic templating.
    - --config
    - /etc/teleport-mirakl/config.yaml
  extraVolumes:
    - name: mirakl-config
      configMap:
        name: teleport-mirakl-config
  extraVolumeMounts:
    - name: mirakl-config
      mountPath: /etc/teleport-mirakl
      readOnly: true
  resources:
    limits:
      memory: 256Mi
    requests:
      cpu: 50m
      memory: 128Mi
  # End of Teleport chart parameters
  # -- Labels to add to the Teleport database. Support templating.
  dbLabels:
    provisioned_by: cloudnative-pg
    chart_version: "{{ .Chart.Version }}"
    chart_name: "{{ .Chart.Version }}"
    stage: "{{ .Values.stage }}"
    name: "{{ .Values.dbName }}"
    kubernetes_cluster: "clusterXXX" #  This should be overridden by the user
```

Currently, the Teleport chart doesn’t permit us to inject templates in its configuration values, so we need to create a ConfigMap containing the configuration and tell Teleport to use it instead of the chart’s default one. This is why we use `extraVolumes`, `extraVolumeMounts` and `extraArgs`.

**Note**  
Some charts permit injecting templates in their configuration by using Helm [tpl](https://helm.sh/docs/howto/charts_tips_and_tricks/#using-the-tpl-function) function. This is pretty useful to make a chart more customizable.

CNPG creates multiple services to access database:

- One for read/write access (rw) (target the master database)
- One for read access (r) (target the any database instance)
- One for read only access (ro) (target replica databases)

The name of the service is `{{clusterName}}--{{serviceType}}` where serviceType is one of `rw`, `r` or `ro`.

We decided to register both the read/write and read only services in Teleport, so we need to register two databases in Teleport. The only difference between these two databases is the name (without suffix or suffixed by `-ro`), the URI and a Teleport label `sql_type` that indicates if the database is a master `primary`) or a replica (`standby`).

Here is the configuration we use:

```c
# file: templates/teleport-mirakl-config.yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  # NOTE cannot template the name because used in Teleport extraVolumes which is static
  name: teleport-mirakl-config
data:
  # NOTE Teleport doesn't automatically reload when this config file changes (no checksum annotation)
  # NOTE cannot use Reloader because we can't customize Teleport deployment annotations...
  config.yaml: |
    ---
    version: v3
    teleport:
      ca_pin:
        {{- toYaml .Values.teleport.ca_pin | nindent 8 }}
      join_params:
        method: token
        token_name: /etc/teleport-secrets/auth-token
      log:
        output: stderr
        severity: INFO
        format:
          output: text
          extra_fields:
            - timestamp
            - level
            - component
            - caller
      proxy_server: {{ .Values.teleport.proxyAddr }}
    app_service:
      enabled: false
    auth_service:
      enabled: false
    proxy_service:
      enabled: false
    ssh_service:
      enabled: false
    db_service:
      enabled: true
      databases:
        - name: {{ .Values.dbName }}
          protocol: postgres
          uri: {{ .Values.dbName }}-rw.{{ .Release.Namespace }}.svc:5432
          tls:
            mode: insecure
          static_labels:
            sql_type: primary
            {{- tpl (toYaml .Values.teleport.dbLabels) . | nindent 12 }}
        - name: {{ .Values.dbName }}-ro
          protocol: postgres
          uri: {{ .Values.dbName }}-ro.{{ .Release.Namespace }}.svc:5432
          tls:
            mode: insecure
          static_labels:
            sql_type: standby
            {{- tpl (toYaml .Values.teleport.dbLabels) . | nindent 12 }}
```

**Note**  
Please note here we use `insecure` TLS mode in this example. It is possible to configure the Teleport agent to verify the PostgreSQL’s certificate, but it requires to inject the CA certificate in the agent.

The problem is that the agent doesn’t support dynamic templating for `extraVolumes`, so we cannot mount it directly from the secret generated by CNPG, as its name depends on the cluster’s name.

It is possible to customize the Server CA to put it in a static secret and generate the CA using cert-manager, but for now we will use the insecure mode and skip the certificate verification.

Now, when we deploy our chart, ArgoCD will also deploy a Teleport agent that will register itself in Teleport and tell it about its databases.

We can now connect to the database using tsh:

```c
tsh login --proxy=mirakl.teleport.sh
tsh db ls --query='labels["provisioned_by"] == "cloudnative-pg"' # You should see \`cnpg-postgres\` and \`cnpg-postgres-ro\`
tsh db connect --db-user=teleport_user_read --db-name=postgres cnpg-postgres  # Or the value you put in \`.Values.dbName\`.
```

Hurrah, we can now connect to our database using Teleport!

However, we must acknowledge that we currently rely on an insecure TLS mode between the agent and the database. Additionally, we unnecessarily rely on the agent to register the database in Teleport, despite already having a highly available Teleport agent in the Kubernetes cluster.

To optimize our approach, let’s explore the possibility of dynamically registering the database instead.

### Essential Prelude: Unveiling the Server CA

Before going further, we need to change the PostgreSQL Server CA. Indeed, at Mirakl we already have a CA that is used to sign all our PostgreSQL server certificates, and we want to use it instead of the one generated by CNPG. This will permit our applications to trust the database certificates without any additional configuration.

Using a single, centralized CA for this use case has multiple advantages:

- Our applications don’t need to trust multiple CAs,
- We can reference the same CA for all our Teleport Agent / databases (because ultimately we want the agent verify the server certificate),
- ArgoCD will wait for the certificate to be signed by the CA in its health check because it is aware of cert-manager resources (but not CNPG resources).

We use [Hashicorp Vault](https://www.vaultproject.io/) to store this CA, so we can use cert-manager to generate the database certificate.

To keep this article more concise we won’t explain how to set up Vault, but you can find more information in the [official documentation](https://www.vaultproject.io/docs).

So let’s create a Vault issuer using an appRole (cert-manager also supports many [other methods](https://cert-manager.io/docs/configuration/vault/#authenticating)):

```c
# file: templates/server-issuer.yaml
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: "{{ .Values.dbName }}-server-issuer"
spec:
  vault:
    auth:
      appRole:
        path: approle
        roleId: "{{ .Values.certificates.server.certManagerIssuer.roleId }}"
        secretRef:
          key: secretId
          name: "{{ .Values.dbName }}-server-issuer-auth"
    path: {{ .Values.certificates.server.certManagerIssuer.path }}
    server: {{ .Values.certificates.server.certManagerIssuer.server }}
---
apiVersion: v1
kind: Secret
metadata:
  name: "{{ .Values.dbName }}-server-issuer-auth"
data:
  secretId: {{ .Values.certificates.server.certManagerIssuer.secretId | b64enc }}
```

We can add some default values to configure the Vault issuer:

```c
# file: values.yaml
---
certificates:
  server:
    certManagerIssuer:
      roleId: <path:secret/cert-manager#role-id>
      secretId: <path:secret/cert-manager#secret-id>
      path: pki/db-ca/sign/cnpg-database
      server: https://vault-address/
```

And we can now use this issuer to generate the database certificate. The database will be exposed using 3 Kubernetes services (`rw`, `r` or `ro` ), each service can be reached using a different DNS suffixes:

- no suffix, i.e: `SERVICE_NAME`
- with the namespace as suffix: `SERVICE_NAME.NAMESPACE`
- with the NAMESPACE.svc as suffix: `SERVICE_NAME.NAMESPACE.svc`
- with the complete DNS name: `SERVICE_NAME.NAMESPACE.svc.cluster.local`

We will use some loops to generate all these DNS names.

```c
# file: templates/server-certificate.yaml
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: "{{ .Values.dbName }}-cnpg-server-cert"
spec:
  secretName: "{{ .Values.dbName }}-cnpg-server-cert"
  usages:
    - server auth
  dnsNames:
    {{- $suffixes := list "" (printf ".%s" .Release.Namespace) (printf ".%s.svc" .Release.Namespace) (printf ".%s.svc.cluster.local" .Release.Namespace) -}}
    {{- $serviceTypes := list "rw" "r" "ro" -}}
    {{- $name := .Values.dbName -}}
    {{- range $_,$type := $serviceTypes -}}
    {{- range $_,$suffix := $suffixes }}
    - {{ $name }}-{{ $type }}{{ $suffix }}
    {{- end -}}
    {{- end }}
  commonName: {{ $name }}-rw
  issuerRef:
    name: "{{ .Values.dbName }}-server-issuer"
    kind: Issuer
    group: cert-manager.io
---
apiVersion: v1
kind: Secret
metadata:
  name: "{{ .Values.dbName }}-cnpg-server-cert"
  labels:
    cnpg.io/reload: ""
```

All we miss to configure the database to use this new certificate is to retrieve the CA certificate used to sign it:

```c
# file: templates/server-ca-secret.yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: "{{ .Values.dbName }}-mirakl-internal-root-ca"
type: Opaque
data:
  ca.crt: {{ .Values.certificates.server.rootCA | b64enc }}
```

And the corresponding configuration:

```c
# file: values.yaml
---
certificates:
  server:
    rootCA: <path:secret/db-root-certificate#ca>
```

We can now configure our database to use this new certificate:

```c
# file: templates/cluster.yaml
---
spec:
  certificates:
    serverTLSSecret: "{{ .Values.dbName }}-cnpg-server-cert"
    serverCASecret: "{{ .Values.dbName }}-mirakl-internal-root-ca"
```

Now that the database uses our CA, we can try to register it dynamically.

### Streamlining Dynamic database registration

The present state of Teleport does not include automatic database registration functionality. However, there are promising directions for improvement that hold the potential for future implementation. At least two viable solutions have been identified for addressing this limitation.

1. Teleport v14 introduces Kubernetes application discovery, which is able to discover and register Kubernetes services in Teleport. It is not yet able to register databases, but it may be implemented in the future as stated in [their doc](https://goteleport.com/docs/application-access/enroll-kubernetes-applications/reference/#teleportdevdiscovery-type).
2. We could use their Kubernetes Operator, but it doesn’t support registering databases yet. There is [an issue](https://github.com/gravitational/teleport/issues/22476) about that. Having a Kubernetes CRD that represents the database would be really nice, as we could use ArgoCD to deploy it and Teleport would automatically register it.

But for now, we need to find a way to register the database dynamically.

ArgoCD has [hooks](https://argo-cd.readthedocs.io/en/stable/user-guide/resource_hooks/) that can be used to trigger actions when the chart is deployed. The idea is to create a Kubernetes Job that will register the database in Teleport when the chart is deployed, after pods are ready and healthy.

The huge downside of this solution is that ArgoCD doesn’t support hooks for deletion, so when the chart is deleted, the database will not be unregistered. There is [an issue](https://github.com/argoproj/argo-cd/issues/7575) about that, and the proposed workaround is not easy to implement and we can’t use it.

As we really want to go this path, we decided that we will manually unregister the database when we delete the chart’s releases. We’ll be closely monitoring Teleport changelogs to see when solution 1 or 2 will be implemented, and we’ll move on them when they’re ready.

Let’s create a Kubernetes Job that will register the database in Teleport. In order to register a dynamic database, we can simply call the `tctl` CLI tool. It can create or update resources in Teleport from a YAML file:

```c
tctl create --force <file>
```

**Note**

The force options tells `tctl` to update the resource if it already exists.

The database resource is described in the [documentation](https://goteleport.com/docs/database-access/reference/configuration/#database-resource). It accepts almost the same format as for static registration.

We will use a Kubernetes ConfigMap to store the Teleport database objects, with some loops to generate `rw` and `ro` databases:

```c
# file: templates/teleport-register-config.yaml
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: "{{ .Values.dbName }}-teleport-register-config"
data:
  # First we generate the rw database
  {{- $accesses := list (dict "sql_type" "primary" "name" "%s" "type" "rw") -}}
  # Then we generate the ro database if needed
  # RO databases can only be used if we have more than one instance
  {{- if lt 1 (int .Values.instancesCount) -}}
    {{- $accesses = append $accesses (dict "sql_type" "standby" "name" "%s-ro" "type" "ro") -}}
  {{- end -}}

  {{- range $_,$db := $accesses }}
  {{ $db.sql_type }}.yaml: |
    ---
    kind: db
    version: v3
    metadata:
      name: {{ printf $db.name $.Values.dbName }}
      labels:
        # sql_type is either \`primary\` or \`standby\`
        sql_type: {{ $db.sql_type }}
        # We retrieve common labels from the values file
        {{- tpl (toYaml $.Values.teleport.dbLabels) $ | nindent 8 }}
    spec:
      protocol: postgres
      uri: {{ $.Values.dbName }}-{{ $db.type }}.{{ $.Release.Namespace }}.svc:5432
      tls:
        mode: verify-full
      # Here we retrieve the server CA certificate, so the agent can verify the
      # database certificate
      ca_cert: |
        {{- $rootCA := $.Values.certificates.server.rootCA -}}
        {{- if regexMatch "^<path:secret/.*>$" $rootCA -}}
          {{- /* A little hack to have the secret right-indented we it is injected by ArgoCD Vault plugin */ -}}
          {{- printf "%s | indent 4>" (trimSuffix ">" $rootCA) | nindent 8 -}}
        {{- else -}}
          {{- $rootCA | nindent 8 -}}
        {{- end }}
  {{- end }}
```

**Important**  
In order to use `tctl`, we need to provide a Teleport identity. This identity is used to authenticate to the Teleport cluster. It can be generated using `tbot`, but this requires a token or to set up Kubernetes JWKS authentication.  
Also note that [JWKS authentication](https://github.com/gravitational/teleport/blob/master/rfd/0143-external-k8s-joining.md) uses a Kubernetes ServiceAccount, but the name and namespace of this ServiceAccount should be known by Teleport (the `spec.kubernetes.allow.service_account` doesn’t allow to use regex, only exact-match).  
This is not desirable in our case, we want the chart to be deployed in any Kubernetes cluster, any namespace, with any name. We don’t want to hardcode the ServiceAccount name and namespace in the chart, it would cause collisions between our ArgoCD applications.  
We decided to use a static identity that is stored in our Vault with a short TTL, rotated regularly. This token is then retrieved by the ArgoCD Vault plugin each time we deploy changes to our database chart.

We can now use this ConfigMap to register the database using a hook Job:

```c
# file: templates/teleport-register.yaml
---
apiVersion: batch/v1
kind: Job
metadata:
  name: "{{ .Values.dbName }}-register-teleport"
  annotations:
    argocd.argoproj.io/hook: PostSync  # This hook will be executed after the chart is deployed
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation  # This hook will be deleted before the next deployment
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: teleport
          image: public.ecr.aws/gravitational/teleport:{{ .Values.teleport.version }}
          command:
            - /bin/bash
            - -c
            - |
              set -euo pipefail
              for file in /etc/teleport-resources/*.yaml; do
                echo "Registering $file"
                tctl create -i /etc/teleport/identity --auth-server "$AUTH_SERVER" --force "$file"
              done
          env:
            - name: AUTH_SERVER
              value: "{{ .Values.teleport.proxyAddr }}"
          volumeMounts:
            - name: identity
              mountPath: /etc/teleport/
              readOnly: true
            - name: resources
              mountPath: /etc/teleport-resources/
              readOnly: true
      volumes:
        - name: identity
          secret:
            secretName: "{{ .Values.dbName }}-register-teleport"
        - name: resources
          configMap:
            name: "{{ .Values.dbName }}-teleport-register-config"
---
apiVersion: v1
kind: Secret
metadata:
  name: "{{ .Values.dbName }}-register-teleport"
  annotations:
    argocd.argoproj.io/hook: PostSync
    # Don't keep this secret after the hook is done
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
type: Opaque
data:
  identity: {{ .Values.teleport.identity | b64enc }}
```

And in our values we can update the Teleport section, removing previous configuration:

```c
# file: values.yaml
---
teleport:
  # -- Teleport \`tctl\` version to use to register the database
  version: 13.4.1
  # -- Teleport identity file with \`tctl\` to use to register the database
  identity: <path:secret/teleport/cnpg-identity#identity>
  # -- Teleport CA to inject into CNPG database to trust Teleport client certificates
  dbCA: <path:secret/teleport/ca#db>
  # -- Teleport proxy address to use to register the database
  proxyAddr: teleport.mirakl.net:443
  # -- Labels to add to the Teleport database
  dbLabels:
    provisioned_by: cloudnative-pg
    chart_version: "{{ .Chart.Version }}"
    chart_name: "{{ .Chart.Version }}"
    stage: "{{ .Values.stage }}"
    name: "{{ .Values.dbName }}"
    kubernetes_cluster: "clusterXXX" #  This should be overridden by the user
```

Now, when ArgoCD syncs the chart, it will deploy the Job that will register the database in Teleport. We should be able to see it using `tctl get db/`, but not in the Teleport UI, or with `tsh db ls`. This is because the Teleport agent is not aware of the database yet. We need to tell our agents what dynamic databases they should handle.

This is done on the agent’s configuration file, in the [database service](https://goteleport.com/docs/reference/config/#database-service), we should add a `db_service.ressources` section that will tell the agent to handle databases that match the given labels.

**Important**  
We have to carefully choose the labels we use to match the database, because the agent will handle all databases that match the given labels, even if they are not reachable from the agent.  
**Note**  
In this article we use the label `kubernetes_cluster` to match the database. This label has to be fed by the user in this article, but it could be automatically set by ArgoCD in real life.

When we register our database, we add a label `kubernetes_cluster` that contains the name of the Kubernetes cluster where the database is deployed. We can use this label to tell the agent to handle all databases that are deployed in the same cluster.

We deploy our agents using the official’s Teleport Agent Helm chart. It allows you to customize the `db_service.ressources` field through the [databaseResources](https://goteleport.com/docs/reference/helm-reference/teleport-kube-agent/#databaseresources) configuration option.

We can add the following configuration to our agent’s values:

```c
databaseResources:
  - labels:
      kubernetes_cluster: clusterXXX  # Adapt to your needs
      provisioned_by: cloudnative-pg
```

We should now be able to see the database in Teleport UI, and connect to it using `tsh db connect`!

There is only one last thing to do: we want to expose the database to our applications behind PgBouncer, a connection pooler for PostgreSQL.

## Setting up a connection pooler

As previously mentioned, our objective is to enable our applications to access our database via PgBouncer.

With CNPG, we can accomplish this through deploying a PgBouncer instance in front of a PostgreSQL database. This instance will be configured to authenticate using mTLS.

Let’s create a PgBounder pooler that allows our applications to connect to the database and make read/write queries:

```c
# file: templates/pooler.yaml
---
apiVersion: postgresql.cnpg.io/v1
kind: Pooler
metadata:
  name: pooler-{{ .Values.dbName }}-rw
spec:
  cluster:
    name: {{ .Values.dbName }}
  instances: {{ .Values.pooler.replicaCount }}
  type: rw
  pgbouncer:
    poolMode: session
    parameters:
      {{- .Values.pooler.parameters | toYaml | nindent 6 }}
```

And the corresponding values:

```c
# file: values.yaml
---
pooler:
  replicaCount: 1
  parameters:
    default_pool_size: "50"
    server_idle_timeout: "30"
```

**Note**  
You can find allowed parameters for PgBouncer in the [CNPG documentation](https://cloudnative-pg.io/documentation/1.21/connection_pooling/#pgbouncer-configuration-options).

If you try to deploy the chart as-is, you will get an error in the CNPG operator logs telling you that CNPG cannot find a `ca.key` key in some secret. In fact we have the same problem that we had for the `streaming_replica` certificate: CNPG cannot anymore generate it automatically, we have to do it ourselves.

Contrary to the `streaming_replica` certificate, this behavior is not yet documented in [CNPG documentation](https://github.com/cloudnative-pg/cloudnative-pg/issues/2841).

**Note**  
Trying to create a new CNPG cluster from scratch with an attached pooler makes the cluster creation silently fail, without any error message. All you see is that the cluster never goes to the `Ready` Ready state.

This issue was hard to debug, because the error doesn’t appear in the pooler’s status nor the CNPG cluster’s status. It only appears in the CNPG operator’s logs.

What we can do is to generate the right certificate using cert-manager, so CNPG won’t try to generate it.

First we have to generate the certificate:

```c
# file: templates/pooler-certificate.yaml
---
apiVersion: v1
kind: Secret
metadata:
  name: "{{ .Values.dbName }}-cnpg-pooler-cert"
  labels:
    cnpg.io/reload: ""
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: "{{ .Values.dbName }}-cnpg-pooler-cert"
spec:
  secretName: "{{ .Values.dbName }}-cnpg-pooler-cert"
  usages:
    - client auth
  commonName: cnpg_pooler_pgbouncer #  The common name shouldn't be changed
  issuerRef:
    name: "{{ .Values.dbName }}-cnpg-client-ca"
    kind: Issuer
    group: cert-manager.io
```

And now we can use it in the pooler by specifying the secret name in the `spec.pgbouncer.authQuerySecret.name` field.

**Warning**  
Because we specify this field, CNPG will not manage PgBouncer configuration in PostgreSQL anymore. We have to manage it ourselves. This is documented in their [spec](https://cloudnative-pg.io/documentation/1.21/cloudnative-pg.v1/#postgresql-cnpg-io-v1-PgBouncerSpec) and in the [doc](https://cloudnative-pg.io/documentation/1.21/connection_pooling/#authentication).

So we also have to specify the `spec.pgbouncer.authQuery` field, which is the query that PgBouncer will use to authenticate users. We can use the same query that CNPG uses by default.

```c
# file: templates/pooler.yaml
---
spec:
  pgbouncer:
    authQuerySecret:
      name: "{{ .Values.dbName }}-cnpg-pooler-cert"
    authQuery: "SELECT usename, passwd FROM user_search($1)"
```

We can now modify our PostgreSQL cluster configuration to allow the pooler to connect to it:

```c
# file: templates/cluster.yaml
---
spec:
  bootstrap:
    initdb:
      postInitApplicationSQL:
         # PgPooler stuff
        - CREATE ROLE cnpg_pooler_pgbouncer WITH LOGIN;
        - GRANT CONNECT ON DATABASE {{ .Values.database.name }} TO cnpg_pooler_pgbouncer;
        - |
            CREATE OR REPLACE FUNCTION user_search(uname TEXT)
              RETURNS TABLE (usename name, passwd text)
              LANGUAGE sql SECURITY DEFINER AS
              'SELECT usename, passwd FROM pg_shadow WHERE usename=$1;';
        - |
            REVOKE ALL ON FUNCTION user_search(text)
              FROM public;
        - GRANT EXECUTE ON FUNCTION user_search(text) TO cnpg_pooler_pgbouncer;
        # End of PgPooler
        # [...] all the other stuff we put previously
```

And now CNPG is able to start the pooler and the PostgreSQL cluster! You can try to connect to the database using the pooler:

```c
EXPORT dbName=cnpg-postgres #  {{ .Values.dbName }}
EXPORT user=app_user #  {{ .Values.database.owner }}
EXPORT db=database1 #  {{ .Values.database.name }}
# Open a tunnel to the pooler service
kubectl port-forward "svc/pooler-${dbName}-rw" 5432:5432 &
# Connect to the database through the tunnel
psql -h localhost -p 5432 -U "$user" "$db"
```

## Conclusion

In this article, we explored the configuration of CNPG databases for seamless integration with Teleport, utilizing various registration methods.

Throughout the process, we encountered several challenging aspects, including:

- Generating a client CA bundle
- Producing all necessary certificates
- Dynamically registering a database in Teleport
- Configuring the CNPG Pooler

Fortunately, we were able to identify solutions for each of these hurdles. Additionally, we are excited to propose some potential enhancements:

- Implementing the Kubernetes Operator for effortless database registration in Teleport
- Utilizing annotations on database services to facilitate agent handling (a feature yet to be implemented in Teleport)
- Leveraging external-secrets for streamlined client CA bundle generation, replacing our current Bash scripts

We hope that this article has provided valuable insights for seamlessly integrating CNPG and Teleport into your infrastructure. If not, we hope it has sparked innovative ideas and a deeper understanding of how Teleport interacts with self-hosted PostgreSQL databases.

[![Mirakl Tech Blog](https://miro.medium.com/v2/resize:fill:96:96/1*iqi4nkVqH5XcBsWowi0bEw.jpeg)](https://mirakl.tech/?source=post_page---post_publication_info--f768f1c614de---------------------------------------)

[![Mirakl Tech Blog](https://miro.medium.com/v2/resize:fill:128:128/1*iqi4nkVqH5XcBsWowi0bEw.jpeg)](https://mirakl.tech/?source=post_page---post_publication_info--f768f1c614de---------------------------------------)

[Last published Jul 10, 2025](https://mirakl.tech/beats-bytes-and-basslines-an-introduction-to-live-coding-with-strudel-cc-4d378e86d5b7?source=post_page---post_publication_info--f768f1c614de---------------------------------------)

Deep dives with members of the Mirakl engineering, product and data teams who are at the forefront of the enterprise marketplace revolution.

We are the Mirakl Labs Team