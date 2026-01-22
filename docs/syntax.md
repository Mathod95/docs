
---


## Embed Documentation
<div class="admonition example">
  <p class="admonition-title">Example</p>

```embed
url: https://docs.crossplane.io/latest
```
    ````
    <div class="admonition note">
      <p class="admonition-title">Documentation</p>

    ```embed
    url: https://docs.crossplane.io/latest
    ```
    </div>
    ````
</div>

---

## Embed Documentation Foldable
<details class="admonition note">
  <summary>Documentation</summary>

```embed
url: https://docs.crossplane.io/latest
```
  </details>
</div>


---

## Variables
```
---
user-defined-values:
  - YOUR_APPNAME
  - YOUR_ENV
---
```


!!! Example
    {{{user-defined-values}}}

```
---
apiVersion: v1 
kind: Pod 
metadata: 
  name: APPNAME-pod 
  namespace: NAMESPACE
  labels: 
    app: APPNAME
    env: ENVIRONMENT
  annotations: 
    aws-account: "ACCOUNT_ID"
    maintainer: "dev@mathod.io"
spec: 
  containers: 
  - name: nginx-container
    image: nginx
```

=== "File Path on Saltbox Host"

    !!! warning inline end "Never Edit These Files"
    
        Updates will overwrite your changes. Use the inventory system instead.

    ```shell
    /srv/git/saltbox/roles/<role_name>/defaults/main.yml
    ```

    ```shell
    /opt/sandbox/roles/<role_name>/defaults/main.yml
    ```

    ```shell
    /srv/git/saltbox/inventories/group_vars/all.yml
    ```

!!! warning inline end "Never Edit These Files"

    Updates will banane your changes. Use the inventory system instead.



!!! tip ""
    To determine which apps are included in Authelia by default, you can run this command or a similar one:

    ```shell
    grep -Ril '_traefik_sso_middleware: "{{ traefik_default_sso_middleware }}"' /srv/git/saltbox/roles /opt/sandbox/roles | awk 'BEGIN{RS="roles/"; FS="/defaults"}NF>1{print $1}' | sort -u
    ```