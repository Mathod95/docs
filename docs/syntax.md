!!! example "Header"
    
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

!!! example "Code Annotate"

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

!!! example "Tabbed codeBlocks"

    === "Python"

        !!! note "Note for Python"
            This is a note inside the Python tab.

    === "JavaScript"

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
    === "Python"

        !!! note "Note for Python"
            This is a note inside the Python tab.

    === "JavaScript"

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

<div class="admonition note">
  <p class="admonition-title">Documentation</p>

```embed
url: https://docs.crossplane.io/latest
```
</div>

---

<details class="admonition note">
  <summary>Documentation</summary>

```embed
url: https://docs.crossplane.io/latest
```
  </details>
</div>


---

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
  name: YOUR_APPNAME-pod 
  namespace: app1
  labels: 
    app: YOUR_APPNAME
    env: YOUR_ENV
  annotations: 
    aws-account: "2389849082948"
    maintainer: "dev@mathod.io"
spec: 
  containers: 
  - name: nginx-container
    image: nginx
```

---

!!! example "ADMONITIONS"

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
