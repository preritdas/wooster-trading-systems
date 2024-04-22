from . import one, two, three, four, five, six, seven
from . import enforceparams


# ---- Catalog systems ----

systems = {
    1: ("Wooster One", one, one.WoosterOne),
    2: ("Wooster Two", two, two.WoosterTwo),
    3: ("Wooster Three", three, three.WoosterThree),
    4: ("Wooster Four", four, four.WoosterFour),
    5: ("Wooster Five", five, five.WoosterFive),
    6: ("Wooster Six", six, six.WoosterSix),
    7: ("Wooster Seven", seven, seven.WoosterSeven),
}

# Enforce parameters (module enforceparams handles config dictating no checks)

def check_all_systems():
    for idx, tup in systems.items(): 
        enforceparams.check_system(tup[1].Params, idx)

check_all_systems()
