import re
from pathlib import Path


def test_template_url_for_parameters_match_route_variables():
    project_root = Path(__file__).resolve().parents[1]
    routes_text = (project_root / "app" / "routes.py").read_text()
    template_dir = project_root / "app" / "templates"

    route_pattern = re.compile(
        r'@bp\.route\("([^"]+)"[^\n]*\)\n(?:@[^\n]+\n)*def\s+(\w+)\(([^)]*)\):'
    )
    route_parameters = {}

    for match in route_pattern.finditer(routes_text):
        path, endpoint, _ = match.groups()
        route_parameters[endpoint] = set(
            re.findall(r'<(?:[^:<>]+:)?(\w+)>', path)
        )

    errors = []
    url_pattern = re.compile(
        r"url_for\('main\.(\w+)'\s*(?:,([^)]*))?\)"
    )

    for template in template_dir.glob("*.html"):
        text = template.read_text()
        for match in url_pattern.finditer(text):
            endpoint = match.group(1)
            arguments = match.group(2) or ""
            supplied = set(re.findall(r'(\w+)\s*=', arguments))

            if endpoint not in route_parameters:
                errors.append(f"{template.name}: unknown endpoint {endpoint}")
                continue

            missing = route_parameters[endpoint] - supplied
            if missing:
                errors.append(
                    f"{template.name}: {endpoint} missing {sorted(missing)}"
                )

    assert not errors, "\n".join(errors)
