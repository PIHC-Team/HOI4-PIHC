# %%
from hoi4dev import *

# %%
# Uprise
print("Uprise")
print(get_num_days("0999.11.11", "1001.02.01") // 7)
print()
# Changeling Retaliation
print("Changeling Retaliation")
print(get_num_days("0999.11.11", "1001.04.06") // 7)
print()
# Appleloosa Trade Agreement
print("Appleloosa Trade Agreement")
print(get_num_days("0999.11.11", "1001.06.01") // 7)
print()
# Crystal Empire Truce
print("Crystal Empire Truce")
print(get_num_days("0999.11.11", "1001.09.01") // 7)
print()
# Canterlot Pact
print("Canterlot Pact")
print(get_num_days("1001.06.01", "1001.12.01") // 7)
print(get_num_days("1001.09.01", "1001.12.01") // 7)
print(get_num_days("1001.04.06", "1001.12.01") // 7)
print(get_num_days("0999.11.11", "1001.12.01") // 7)
print()
# Cozy Glow Coronation
print("Cozy Glow Coronation")
print(get_num_days("1001.12.01", "1002.06.24") // 7)
print(get_num_days("0999.11.11", "1002.06.25") // 7)
print()
# Jahr Null
print("Jahr Null")
print(get_num_days("0999.11.11", "1002.12.25") // 7)
print()
# Sunset Returns
print("Sunset Returns")
print(get_num_days("0999.11.11", "1001.11.01") // 7)
print(get_num_days("1001.11.01", "1002.05.01") // 7)
print(get_num_days("1002.05.01", "1002.12.01") // 7)
print()

# Second Ponyvile Election
print("Second Ponyvile Election")
print(get_end_date("1002.12.01", 1298))
print()

# %%