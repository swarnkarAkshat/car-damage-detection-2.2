def get_damage_details(prediction: str):
    if not prediction:
        return {"damage": 0, "cost": 0}
    
    formatted = prediction.lower()
    
    if 'normal' in formatted:
        return {"damage": 0, "cost": 0}
    elif 'breakage' in formatted:
        return {"damage": 40, "cost": 6000}
    elif 'crushed' in formatted:
        return {"damage": 60, "cost": 9000}
    
    return {"damage": 0, "cost": 0}
