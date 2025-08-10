def decide_action(
    p_incident: float, trust: float, th_hi=0.6, th_lo=0.4, min_trust=0.8
) -> str:
    if trust < min_trust:
        return "no_op"
    if p_incident >= th_hi:
        return "restart_service"
    if p_incident >= th_lo:
        return "scale_up"
    return "no_op"
