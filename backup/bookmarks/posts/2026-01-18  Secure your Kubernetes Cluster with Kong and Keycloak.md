---
title: Secure your Kubernetes Cluster with Kong and Keycloak
date: 2026-01-18
categories:
  - "uncategorized"
tags:
  - untagged
source: https://medium.com/@armeldemarsac/secure-your-kubernetes-cluster-with-kong-and-keycloak-e8aa90f4f4bd
author:
  - "[[Armel de Marsac]]"
---
<!-- more -->

[Sitemap](https://medium.com/sitemap/sitemap.xml)

This article as been inspired by the [dev.to post](https://dev.to/robincher/securing-your-site-via-oidc-powered-by-kong-and-keycloak-2ccc) from Robin Cheer. Thanks to him and Sal Sarrentino for his help on [Kong forum](https://discuss.konghq.com/).

As our Kubernetes cluster grows, authentication and authorization might become a problem. The more dashboards an ui tools we add, the more accounts and credentials we have to manage. The traditional approach to solve this problem is to add Single Sign On with, for example, Keycloak. We create a realm, a client and switch all of our tools to use OAuth2.0. Easy, right? Well, not really. The issue being that not all tools ship with a built in authentication mechanism support OAuth2.0. Even worse, some of them don’t even have authentication at all!

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*CpjhwQyp42yLDKwMJilxEw.png)

### Kong to the rescue

Fortunately, some reverse proxy solutions like [Kong](https://konghq.com/) offer the ability to enable OAuth2.0 at the proxy level! This is done thanks to its vast third plugin ecosystem. In our case the [open source OIDC plugin](https://github.com/revomatico/kong-oidc) handles the process. Unfortunately when I stumbled onto this issue a week ago, I realized that the plugin wasn’t up to date with the latest Kong’s plugin api. Having never contributed to the open source community before I thought it would be a nice opportunity to get me started. So I [forked it](https://github.com/armeldemarsac92/kong-oidc) and brought it up to date. Being a junior dev of course I worked on the main branch. We all have to start somewhere.

![](https://miro.medium.com/v2/resize:fit:640/format:webp/1*2Yxvs3zPfEv1t-i-BtZQ8Q.png)

conceptual view of the proxy approach

### Clarifications on Kong

To my knowledge there are two flavors of Kong. The first one is the traditional approach, using the [Kong Ingress Controller](https://developer.konghq.com/kubernetes-ingress-controller/) and its gigantic helm chart [kong/ingress](https://github.com/Kong/charts/tree/main/charts/ingress). The other one is the newer [Kong Gateway Operator](https://developer.konghq.com/operator/) and its new data/controlplane topology that relies basically on the same components as the older approach. It brings however a third ressource to the table, the Gateway Operator that is supposed to manage the deployment of multiple control and data planes. I won’t elaborate further in this post, just know that the approach described here works with both topologies.

### Installing a custom plugin with Kong

With the newer Kong Gateway Operator comes a new [KongPluginInstallation](https://developer.konghq.com/operator/dataplanes/how-to/deploy-custom-plugins/) ressource that allows us to manage all plugin configuration with Kubernetes objects. This approach however as some crucial limitations: it only supports very basic plugins with no external dependencies that should be constituted only of a schema.lua and the handler.lua. This is not compatible with our OIDC plugin as it has external dependencies, mainly [resty-oidc](https://github.com/zmartzone/lua-resty-openidc) and [jwt-keycloak](https://github.com/armeldemarsac92/kong-plugin-jwt-keycloak). For this plugin to work we have to build a custom Docker image from the [official kong image](https://hub.docker.com/_/kong). The DockerFile is contained inside [my repo](https://github.com/armeldemarsac92/kong-oidc) but you can also directly use the image I created: [armeldemarsac92/kong-oidc:4.0.0](https://hub.docker.com/repository/docker/armeldemarsac/kong-oidc/general). Now that we have our custom Kong image, let’s prepare our Kubernetes objects.

### Deploying the plugin

A functionnal Kong deployment is a prerequisite, check the official tutorial for [KIC](https://developer.konghq.com/kubernetes-ingress-controller/install/) or [KGO](https://developer.konghq.com/operator/dataplanes/get-started/hybrid/install/). As a reference here is the Gateway used in our tutorial:

```c
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: kong
spec:
  gatewayClassName: kong
  listeners:
  - name: global-https
    port: 443
    protocol: HTTPS
    hostname: "otterstack.local"
    tls:
      mode: Terminate
      certificateRefs:
        - kind: Secret
          name: global-cert-secret
    allowedRoutes:
      namespaces:
        from: All
```

If you use Kong Gateway Operator, here is an example GatewayConfiguration file:

```c
kind: GatewayConfiguration
apiVersion: gateway-operator.konghq.com/v1beta1
metadata:
  name: kong
  namespace: kong
spec:
  dataPlaneOptions:
    network:
      services:
        ingress:
          type: LoadBalancer
          name: gateway-lb
          annotations:
            metallb.io/loadBalancerIPs: 192.168.10.20
    deployment:
      podTemplateSpec:
        spec:
          containers:
          - name: proxy
            image: armeldemarsac/kong-oidc:4.0.0
            imagePullPolicy: Always
            env:
              - name: KONG_DATABASE
                value: "off"
              - name: KONG_PLUGINS
                value: "bundled,oidc,jwt-keycloak"
              - name: KONG_LOG_LEVEL
                value: "debug"
  controlPlaneOptions:
    deployment:
      podTemplateSpec:
        spec:
          containers:
          - name: controller
            image: kong/kubernetes-ingress-controller:3.5
            env:
            - name: CONTROLLER_LOG_LEVEL
              value: debug
```

Once your Kong gateway is up and running start by configuring the plugin:

```c
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: my-oidc-grafana
  namespace: monitoring
  annotations:
    konghq.com/ingress.class: kong
  labels:
    global: "false"
config:
  client_id: grafana
  client_secret: your-super-secret-client-secret #NOT IDEAL
  realm: example-realm
  discovery: http://keycloak.keycloak.svc.cluster.local/keycloak/realms/example-realm/.well-known/openid-configuration
  scope: openid
  response_type: code
  token_endpoint_auth_method: client_secret_post
  header_names: 
    - "X-Username"
  header_claims: 
    - "preferred_username"
  redirect_uri: https://otterstack.local/grafana/dashboard #MUST BE DIFFERENT FROM THE ROOT URL OF THE RESSOURCE
  recovery_page_path: https://www.reddit.com/media?url=https%3A%2F%2Fi.redd.it%2Fyj5kmtbgk9k91.jpg  
disabled: false
plugin: oidc
```

All the available config options are in the [readme](https://github.com/armeldemarsac92/kong-oidc/blob/master/README.md). Here you can see we have added the “header\_names” and “header\_claims” options that will be passed to the upstream Grafana instance once we’re logged in. We also have to secure the httproute to the service by referencing our KongPlugin configuration.

```c
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: http-grafana
  namespace: monitoring
spec:
  parentRefs:
  - name: kong
    kind: Gateway
    namespace: default
    sectionName: global-https
  rules:
  - matches:
    - path:
       type: PathPrefix
        value: /grafana
    filters:
    - type: URLRewrite
      urlRewrite:
        path:
          type: ReplacePrefixMatch
          replacePrefixMatch: /
    - type: ExtensionRef
      extensionRef:
        group: configuration.konghq.com
        kind: KongPlugin
        name: my-oidc-grafana
    backendRefs:
    - name: my-grafana
      kind: Service
      port: 80
      namespace: monitoring
```

### Configuring Keycloak

To deploy Keycloak I’ll use its helm chart, the important section are the keycloakConfigCli, which allows use to configure KC directly from the helm chart:

```c
keycloakConfigCli:
  enabled: true
  image:
    registry: docker.io
    repository: bitnami/keycloak-config-cli
    tag: 6.4.0-debian-12-r9
    digest: ""

  configuration:
    example-realm.json: |
      {
        "realm": "example-realm",
        "enabled": true,
        "registrationAllowed": true,
        "clients": [
          {
            "clientId": "grafana",
            "protocol": "openid-connect",
            "publicClient": false,
            "secret": "your-super-secret-client-secret",
            "redirectUris": [
              "https://otterstack.local/grafana"
            ],
            "webOrigins": [
              "+"
            ],
            "standardFlowEnabled": true,
            "implicitFlowEnabled": false,
            "directAccessGrantsEnabled": false,
            "serviceAccountsEnabled": false,
            "clientAuthenticatorType": "client-secret"
          },
          {
            "clientId": "kubewall",
            "protocol": "openid-connect",
            "publicClient": false,
            "secret": "your-super-secret-client-secret",
            "redirectUris": [
              "https://otterstack.local/dashboard"
            ],
            "webOrigins": [
              "+"
            ],
            "standardFlowEnabled": true,
            "implicitFlowEnabled": false,
            "directAccessGrantsEnabled": false,
            "serviceAccountsEnabled": false,
            "clientAuthenticatorType": "client-secret"
          }
        ],
        "users": [
          {
            "username": "basicuser",
            "email": "basicuser@example.com",
            "enabled": true,
            "firstName": "Basic",
            "lastName": "User",
            "credentials": [
              {
                "type": "password",
                "value": "basicpassword"
              }
            ],
            "groups": [
              "basicgroup"
            ]
          }
        ],
        "groups": [
          {
            "name": "basicgroup"
          }
        ]
      }
```

And the extraEnvVars sections:

```c
extraEnvVars:
  - name: KC_HTTP_ENABLED
    value: "true" 
  - name: KC_HOSTNAME 
    value: "https://otterstack.local/keycloak" #SET THE DESIRED BASEPATH HERE
  - name: "KC_HOSTNAME_BACKCHANNEL_DYNAMIC"
    value: "true"
```

The backchannel\_dynamic option is crucial as it will allow KC to advertise and serve its backend endpoint using kubernetes DNS records (keycloak.{namespace}.svc.cluster.local), which is fundamental for the Kong gateway pod to establish connection with it. Once it’s deployed create the httproute we’ll need to access the admin UI and the login page:

```c
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: http-keycloak
  namespace: keycloak
spec:
  parentRefs:
  - name: kong
    kind: Gateway
    namespace: default
    sectionName: global-https
  rules:
  - matches:
    - path:
        type: PathPrefix
        value: /keycloak
    backendRefs:
    - name: keycloak
      kind: Service
      port: 80  
      namespace: keycloak
```

### Upstream app configuration

Are we done? If your upstream app has no authentication mechanism built in, yes! If not however, you’ll have to configure it’s authentication mechanism to rely on proxy auth. In our demo we’ll configure grafana’s helm chart’s auth section as so:

```c
grafana.ini:
  auth.basic:
    enabled: false
  auth.generic_oauth:
    enabled: false
  auth.proxy: 
    enabled: true
    header_name: X-Username
    header_property: username
    auto_sign_up: true
  auth:
    disable_login_form: true
```

As we can see we’ll rely on the auth headers configured in the KongPlugin object above.

### Conclusion

We’re done, thanks for reading! If you have any question please feel free to ask on Kong forums or under this post. Please keep in mind that I’m a junior dev, double check the configurations provided and refer to official Kong documentation.

Software engineering student at Epitech Paris, HOI4 buff and otter maniac. [https://github.com/armeldemarsac92](https://github.com/armeldemarsac92)

## More from Armel de Marsac

## Recommended from Medium

[

See more recommendations

](https://medium.com/?source=post_page---read_next_recirc--e8aa90f4f4bd---------------------------------------)