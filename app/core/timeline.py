from typing import Dict

def calculate_timeline_estimate(total_area: float, ai_interpretation: Dict) -> str:
    """
    Calculates the estimated project timeline based on roof area and complexity factors.
    """
    if not total_area or total_area <= 0:
        return "Unable to estimate - no area data"

    if total_area < 2000: base_days = 2
    elif total_area < 5000: base_days = 4
    elif total_area < 10000: base_days = 7
    else: base_days = 10

    if ai_interpretation.get("special_requirements"):
        base_days += len(ai_interpretation["special_requirements"])

    if ai_interpretation.get("damage_assessment", {}).get('severity') == 'high':
        base_days += 2

    return f"{base_days}-{base_days + 2} business days"