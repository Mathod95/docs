---
tags:
  - Crossplane
  - AWS
  - Organization
user-defined-values:
  - REGION
  - ACCOUNT_ID
  - APPNAME
  - ENVIRONMENT
  - COMPANY
  - NAMESPACE
  - TEAM
  - SERVICE
---

!!! example "User Defined Values"
    {{{user-defined-values}}}

## Account

```yaml linenums="1"
apiVersion: organizations.aws.m.upbound.io/v1beta1
kind: Account
metadata:
  annotations:
    meta.upbound.io/example-id: organizations/v1beta1/account
  labels:
    testing.upbound.io/example-name: account
  name: account
  namespace: upbound-system
spec:
  forProvider:
    email: <new-account-email>
    name: my_new_account
```

---

## DelegatedAdministrator

## Organization

```yaml linenums="1"
apiVersion: organizations.aws.m.upbound.io/v1beta1
kind: Organization
metadata:
  name: org
  namespace: upbound-system
spec:
  forProvider:
    awsServiceAccessPrincipals: #(1)!
      - cloudtrail.amazonaws.com
      - config.amazonaws.com
    featureSet: ALL #(2)!
```

1.  List of AWS service principal names for which you want to enable integration with your organization. 

    This is typically in the form of a URL, such as service-abbreviation.amazonaws.com. 
    
    Organization must have feature_set set to ALL. 
    
    Some services do not support enablement via this endpoint, see warning in aws docs.

2.  Specify `ALL` (default) or `CONSOLIDATED_BILLING`.

---

## OrganizationalUnit

```yaml linenums="1"
apiVersion: organizations.aws.m.upbound.io/v1beta1
kind: OrganizationalUnit
metadata:
  annotations:
    meta.upbound.io/example-id: organizations/v1beta1/organizationalunit
  labels:
    testing.upbound.io/example-name: example
  name: example
  namespace: upbound-system
spec:
  forProvider:
    name: example
    parentId: <parent-id>
```

---
## Policy

## PolicyAttachment