def score(e) -> float:
    """
    Simple, deterministic trust scoring:
    - Untrusted sources get low weight.
    - Otherwise weight by how 'clean' the record looks.
    """
    src = e.get("source", "trusted")
    if src != "trusted":
        return 0.1
    # downweight obviously malformed or very noisy errors
    if "forged" in e.get("log", "").lower():
        return 0.1
    return 1.0
