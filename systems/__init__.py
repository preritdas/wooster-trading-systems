from . import one, two, three
from . import enforceparams


# ---- Catalog systems ----

systems = {
    1: ("Wooster One", one, one.WoosterOne),
    2: ("Wooster Two", two, two.WoosterTwo),
    3: ("Wooster Three", three, three.WoosterThree)
}

# Enforce parameters (module enforceparams handles config dictating no checks)

for idx, tup in systems.items(): 
    enforceparams.check_system(tup[1].Params, idx)
