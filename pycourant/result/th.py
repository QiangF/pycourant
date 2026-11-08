from pyradioss.result.RadiossTHReader import RadiossTHReader

# Load the TH file (contains all timesteps)
th = RadiossTHReader("modelT01")

# Inspect available data keys
print(th.array.keys())

# Access data as numpy arrays
time = th.array["time"]
internal_energy = th.array["INTERNAL ENERGY"]

# Example: plot with matplotlib
import matplotlib.pyplot as plt
plt.plot(time, internal_energy)
plt.xlabel("Time")
plt.ylabel("Internal Energy")
plt.show()
