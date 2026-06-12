def get_cbc_grade(marks):

    if marks <= 10:
        return "BE2"
    elif marks <= 20:
        return "BE1"
    elif marks <= 30:
        return "AE2"
    elif marks <= 40:
        return "AE1"
    elif marks <= 57:
        return "ME2"
    elif marks <= 74:
        return "ME1"
    elif marks <= 89:
        return "EE2"
    else:
        return "EE1"