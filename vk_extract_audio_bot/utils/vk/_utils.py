def get_method_params(
    func_locals: dict,
) -> dict:
    exclude = ["self"]
    params = {}
    for key, value in func_locals.items():
        if key in exclude or value is None:
            continue
        format_value = value
        if isinstance(format_value, list):
            format_value = ",".join(map(str, value))
        params[key] = format_value
    return params
