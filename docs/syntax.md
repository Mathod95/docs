## Header
!!! example

    ```shell 
    ---
    title: "Titre de ton article"
    description: "Courte description pour l’aperçu et le SEO"
    date: 2025-02-10
    hide:
      - tags
    categories:
      - Documentation
    tags:
      - template
    user-defined-values:
      - YOUR_APPNAME
      - YOUR_ENV
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
