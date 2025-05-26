import gc

found_objects = gc.get_objects()
print("Before:", len(found_objects))

import waste_memory

hold_reference = waste_memory.run()

found_objects = gc.get_objects()
print("After: ", len(found_objects))
for obj in found_objects[:3]:
    print(repr(obj)[:100])

print("...")