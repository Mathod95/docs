---
hide:
  - navigation
---

## Header
!!! example

    ```shell title="Code"
    ---
    title: Titre de ton article
    description: "Courte description pour l’aperçu et le SEO"
    date: 2025-02-10
    categories:
      - Documentation
    tags:
      - template
    status:
    sources:
    hide:
      - tags
    ---
    ```

---

## Code Annotate
!!! example

    ```yaml title="Visual"
    theme:
      features:
        - content.code.annotate # (1)
    ```

    1.  :man_raising_hand: I'm a code annotation! I can contain `code`, __formatted
        text__, images, ... basically anything that can be written in Markdown.


    ````title="Code"
    ```yaml
    theme:
      features:
        - content.code.annotate # (1)
    ```

    1.  :man_raising_hand: I'm a code annotation! I can contain `code`, __formatted
        text__, images, ... basically anything that can be written in Markdown.
    ````

---

## Footnotes

!!! example

    https://zensical.org/docs/authoring/footnotes/

    ```
    [^1]: Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    [^2]:
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et euismod
        nulla. Curabitur feugiat, tortor non consequat finibus, justo purus auctor
        massa, nec semper lorem quam in massa.
    ```

---

## Emotes

!!! example

    ```
    📋 Liste
    ✅ Succès/OK
    ❌ Erreur/Échec
    ⚠️ Attention
    ℹ️ Information
    ⏭️ Ignoré/Skip
    🔄 En cours
    ⏸️ Pause
    ▶️ Play/Start
    ➕ Ajouter
    ➖ Retirer
    🔧 Configuration
    🔨 Build
    🚀 Déployer
    📦 Package
    🗑️ Supprimer
    📝 Documenter
    📊 Stats
    📈 Augmentation
    📉 Diminution
    🎯 Objectif
    💡 Idée
    🔍 Recherche
    ```

---

## Admonitions

!!! example

    !!! note

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
        euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
        purus auctor massa, nec semper lorem quam in massa.

    !!! abstract

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
        euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
        purus auctor massa, nec semper lorem quam in massa.

    !!! info

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
        euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
        purus auctor massa, nec semper lorem quam in massa.

    !!! tip

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
        euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
        purus auctor massa, nec semper lorem quam in massa.

    !!! success

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
        euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
        purus auctor massa, nec semper lorem quam in massa.

    !!! question

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
        euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
        purus auctor massa, nec semper lorem quam in massa.

    !!! warning

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
        euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
        purus auctor massa, nec semper lorem quam in massa.

    !!! failure

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
        euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
        purus auctor massa, nec semper lorem quam in massa.

    !!! danger

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
        euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
        purus auctor massa, nec semper lorem quam in massa.

    !!! bug

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
        euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
        purus auctor massa, nec semper lorem quam in massa.

    !!! example

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
        euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
        purus auctor massa, nec semper lorem quam in massa.

    !!! quote

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla et
        euismod nulla. Curabitur feugiat, tortor non consequat finibus, justo
        purus auctor massa, nec semper lorem quam in massa.

---

## Tabbed Admonition
!!! example

    === "Tab1"

        !!! note "Note for Python"
            This is a note inside the Python tab.

    === "Tab2"

        !!! warning "Warning for JavaScript"
            This is a warning inside the JavaScript tab.

    !!! note "Parent Admonition"

        This is the outer admonition content.

        === "Tab 1"

            !!! tip "Tip inside Tab 1"
                This is the first tab's inner admonition.

        === "Tab 2"

            !!! warning "Warning inside Tab 2"
                This is the second tab's inner admonition.
    ```
    === "Tab1"

        !!! note "Note for Python"
            This is a note inside the Python tab.

    === "Tab2"

        !!! warning "Warning for JavaScript"
            This is a warning inside the JavaScript tab.

    !!! note "Parent Admonition"

        This is the outer admonition content.

        === "Tab 1"

            !!! tip "Tip inside Tab 1"
                This is the first tab's inner admonition.

        === "Tab 2"

            !!! warning "Warning inside Tab 2"
                This is the second tab's inner admonition.
    ```

---


---

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

---

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