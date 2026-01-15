import json
from typing import Dict, List, Tuple


def trapezoid_membership(x: float, a: float, b: float, c: float, d: float) -> float:
    if x <= a or x >= d:
        return 0.0
    if b <= x <= c:
        return 1.0
    if a < x < b:
        return (x - a) / (b - a) if b != a else 0.0
    if c < x < d:
        return (d - x) / (d - c) if d != c else 0.0
    return 0.0


def fuzzify_temperature(
    temperature_value: float,
    temp_json: str,
    temp_var_name: str = "температура"
) -> Dict[str, float]:
    data = json.loads(temp_json)
    terms = data[temp_var_name]
    result: Dict[str, float] = {}
    for term in terms:
        pts = term["points"]
        a, b, c, d = pts[0][0], pts[1][0], pts[2][0], pts[3][0]
        mu = trapezoid_membership(temperature_value, a, b, c, d)
        result[term["id"]] = mu
    return result


def build_output_terms(
    heat_json: str,
    heat_var_name: str = "уровень_нагрева"
) -> Dict[str, Tuple[float, float, float, float]]:
    data = json.loads(heat_json)
    idx: Dict[str, Tuple[float, float, float, float]] = {}
    for term in data[heat_var_name]:
        pts = term["points"]
        a, b, c, d = pts[0][0], pts[1][0], pts[2][0], pts[3][0]
        idx[term["id"]] = (a, b, c, d)
    return idx


def apply_rules_mamdani(
    mu_temp: Dict[str, float],
    rules_json: str,
    heat_json: str,
    heat_var_name: str = "уровень_нагрева"
) -> List[Tuple[float, float]]:
    rules = json.loads(rules_json)
    out_terms = build_output_terms(heat_json, heat_var_name)

    all_x: List[float] = []
    for a, b, c, d in out_terms.values():
        all_x.extend([a, b, c, d])
    xs = sorted(set(all_x))
    mu_out = {x: 0.0 for x in xs}

    for in_term, out_term in rules:
        alpha = mu_temp.get(in_term, 0.0)
        if alpha <= 0.0:
            continue
        a, b, c, d = out_terms[out_term]
        for x in xs:
            mu_t = trapezoid_membership(x, a, b, c, d)
            mu_rule = min(alpha, mu_t)
            if mu_rule > mu_out[x]:
                mu_out[x] = mu_rule

    return [(x, mu_out[x]) for x in xs]


def defuzzify_first_maximum(mu_points: List[Tuple[float, float]]) -> float:
    if not mu_points:
        return 0.0
    max_mu = max(mu for _, mu in mu_points)
    if max_mu <= 0.0:
        return 0.0
    for x, mu in sorted(mu_points, key=lambda p: p[0]):
        if mu == max_mu:
            return x
    return 0.0


def main(
    temp_var_json: str,
    heat_var_json: str,
    rules_json: str,
    current_temperature: float
) -> float:
    mu_temp = fuzzify_temperature(current_temperature, temp_var_json, "температура")
    mu_points = apply_rules_mamdani(mu_temp, rules_json, heat_var_json, "уровень_нагрева")
    s_star = defuzzify_first_maximum(mu_points)
    return float(s_star)


if __name__ == "__main__":
    temp_json = """
    {
      "температура": [
        {
          "id": "холодно",
          "points": [
            [0,1],
            [18,1],
            [22,0],
            [50,0]
          ]
        },
        {
          "id": "комфортно",
          "points": [
            [18,0],
            [22,1],
            [24,1],
            [26,0]
          ]
        },
        {
          "id": "жарко",
          "points": [
            [0,0],
            [24,0],
            [26,1],
            [50,1]
          ]
        }
      ]
    }
    """

    heat_json = """
    {
      "уровень_нагрева": [
        {
          "id": "слабый",
          "points": [
            [0,0],
            [0,1],
            [5,1],
            [8,0]
          ]
        },
        {
          "id": "умеренный",
          "points": [
            [5,0],
            [8,1],
            [13,1],
            [16,0]
          ]
        },
        {
          "id": "интенсивный",
          "points": [
            [13,0],
            [18,1],
            [23,1],
            [26,0]
          ]
        }
      ]
    }
    """

    rules = """
    [
      ["холодно", "интенсивный"],
      ["комфортно", "умеренный"],
      ["жарко", "слабый"]
    ]
    """

    t = 21.0
    print(main(temp_json, heat_json, rules, t))
