def detect_category(text):

    text = text.lower()

    if any(word in text for word in ["water", "tap", "cooler", "leakage"]):
        return "Water"

    elif any(word in text for word in ["fan", "light", "switch", "socket", "ac", "power"]):
        return "Electrical"

    elif any(word in text for word in ["garbage", "dust", "toilet", "cleaning", "dirty"]):
        return "Sanitation"

    elif any(word in text for word in ["bus", "vehicle", "transport", "driver"]):
        return "Transport"

    elif any(word in text for word in ["computer", "wifi", "internet", "printer", "software"]):
        return "IT Support"

    else:
        return "Other"

def detect_department(category):

    if category == "Water":
        return "Maintenance"

    elif category == "Electrical":
        return "Electrical"

    elif category == "Sanitation":
        return "Sanitation"

    elif category == "Transport":
        return "Transport"

    elif category == "IT Support":
        return "IT Support"

    else:
        return None

def calculate_priority(urgency, affected_students, location_importance, complaint_frequency):

    score = (
        urgency
        + affected_students
        + location_importance
        + complaint_frequency
    )

    if score >= 80:
        level = "High"

    elif score >= 50:
        level = "Medium"

    else:
        level = "Low"

    return score, level