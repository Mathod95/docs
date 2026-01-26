from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

class UserDefinedValues(BasePlugin):

    config_scheme = (
        ("keywords", config_options.Type(dict)),
        (
            "input-placeholder",
            config_options.Type(str, default="{{{user-defined-values}}}"),
        ),
    )

    def on_config(self, config, **kwargs):
        # Sanitize keywords: ensure all values are dictionaries
        self.keywords = {}
        for key, value in self.config["keywords"].items():
            self.keywords[key] = value if isinstance(value, dict) else {}
        return config

    def on_post_page(self, output_content, page, config):
        data_tag = "data-bind-user-defined-values"

        # Récupérer les keywords à afficher pour cette page depuis la meta
        page_keywords = getattr(page, "meta", {}).get("user-defined-values", None)
        if page_keywords is None:
            # Si non spécifié, afficher tous les keywords
            page_keywords = list(self.keywords.keys())

        # Remplacer les keywords dans le texte par des spans
        for keyword in page_keywords:
            if keyword in self.keywords:
                output_content = output_content.replace(
                    keyword, f'<span {data_tag}="{keyword}">{keyword}</span>'
                )

        # Générer les champs input
        input_boxes = """
        <style>
            label.user-defined-values { width: 30%; }
            input.user-defined-values[type=text] {
                width: 100%;
                padding: 12px 20px;
                margin: 8px 0;
                box-sizing: border-box;
                border: 1px solid black;
                display: inline-block;
            }
        </style>
        """

        for keyword in page_keywords:
            if keyword not in self.keywords:
                continue

            values = self.keywords[keyword]
            javascript_variable_name = keyword.lower().replace("-", "_")
            label = values.get("label", keyword)
            placeholder = values.get("placeholder", "")

            input_boxes += f"""
            <label class="user-defined-values" for="{keyword}">{label}</label>
            <input class="user-defined-values" type="text" placeholder="{placeholder}" id="{keyword}" />
            <script>
                const {javascript_variable_name} = document.getElementById('{keyword}');
                {javascript_variable_name}.value = window.localStorage.getItem('{keyword}');
                {javascript_variable_name}.oninput = function(e) {{
                    const value = e.target.value;
                    window.localStorage.setItem('{keyword}', value);
                    document.querySelectorAll('[{data_tag}="{keyword}"]').forEach(function(element) {{
                        element.innerHTML = value == '' ? '{keyword}' : value;
                    }});
                }};
            </script>
            """

        # Remplacer le placeholder par les inputs générés
        output_content = output_content.replace(
            self.config["input-placeholder"], input_boxes
        )

        return output_content
