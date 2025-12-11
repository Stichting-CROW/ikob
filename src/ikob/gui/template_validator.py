class TemplateValidator:
    @staticmethod
    def validate_template(template):
        for key in set(template.keys()):
            t = template[key]
            if key == "label":
                continue
            if type(t) is not dict:
                print("Het 'type' veld mist.")
                return False
            if "type" in t:
                value_type = t["type"]
                if value_type == "checklist" or value_type == "choice":
                    if "items" not in t:
                        print(f"Items is verplicht voor type '{value_type}' in '{key}'.")
                        return False
                    if len(t["items"]) < 1:
                        print(f"Geen opties in 'items' voor type '{value_type}' in '{key}'.")
                        return False
                if "range" in t:
                    value_range = t["range"]
                    if value_type != "number":
                        print(f"De 'range' optie wordt niet ondersteund voor type '{value_type}'.")
                        return False
                    if type(value_range) is not list:
                        print(f"De 'range' moet worden opgegeven als een lijst in '{key}'.")
                        return False
                    if len(value_range) != 2:
                        print(f"De 'range' moet precies twee waarden bevatten in '{key}'.")
                        return False
                if "default" in t:
                    default_value = t["default"]
                    if not TemplateValidator._validate_default_type(type, default_value):
                        print(f"Default waarde '{default_value}' voor '{key}' past niet bij type '{value_type}'.")
                        return False
            else:
                return TemplateValidator.validate_template(template[key])
        return True

    @staticmethod
    def validate_config_with_template(config, template, strict=False):
        """
        Valideert een configuratie gegeven een template.
        Er wordt gekeken naar structuur en waarden van de bladen.
        Indien strict op False staat, dan is het toegestaan om in de config
        extra velden te hebben die niet in het template staan. In dat geval
        garandeert de validatie alleen dus de standaard velden. De overige
        waarden worden klakkeloos overgenomen.
        Resultaat: True - Configuratie klopt.
                False - Configuratie klopt niet.
        """
        template_keys = [key for key in template.keys() if key != "label"]
        if not isinstance(config, dict):
            return False
        if strict and set(config.keys()) != set(template_keys):
            return False
        for key in template_keys:
            if not strict:
                if key not in config:
                    return False
            if "type" in template[key]:
                check = {
                    "text": TemplateValidator._validate_text,
                    "number": TemplateValidator._validate_number,
                    "directory": TemplateValidator._validate_text,
                    "file": TemplateValidator._validate_text,
                    "checkbox": TemplateValidator._validate_box,
                    "checklist": TemplateValidator._validate_items,
                    "choice": TemplateValidator._validate_choice,
                }
                if not check.get(template[key]["type"], TemplateValidator._false)(config[key], template[key]):
                    return False
            elif type(template[key]) is dict:
                if not TemplateValidator.validate_config_with_template(config[key], template[key], strict=strict):
                    return False
        return True

    @staticmethod
    def _validate_default_type(value_type, default_value):
        default_type = type(default_value)
        if default_type is dict:
            return False
        if (
            value_type == "text" or value_type == "file" or value_type == "directory" or value_type == "choice"
        ) and default_type is not str:
            return False
        if value_type == "number" and not (default_type is float or default_type is int):
            return False
        if (value_type == "checklist") and default_type is not list:
            return False
        if (value_type == "checkbox") and default_type is not bool:
            return False
        return True

    @staticmethod
    def _false(value, template):
        return False

    @staticmethod
    def _validate_text(value, template):
        if type(value) is not str:
            return False
        return True

    @staticmethod
    def _validate_number(value, template):
        if not (type(value) is float or type(value) is int):
            return False
        if "range" in template:
            if value < template.range[0] or value > template.range[1]:
                return False
        return True

    @staticmethod
    def _validate_items(values, template):
        if type(values) is not list:
            return False
        for item in values:
            if item not in template["items"]:
                return False
        return True

    @staticmethod
    def _validate_box(value, template):
        return value in [True, False]

    @staticmethod
    def _validate_choice(value, template):
        if value not in template["items"]:
            return False
        return True
