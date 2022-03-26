import matplotlib.pyplot as plt

F = 15e9
u_s = 30e6
d_i = 2e6

N = [10, 100, 1000]
u = [300e3, 700e3, 2e6]

def f1(N, u):
    return max(F*N/u_s, F/d_i)

def f2(N, u):
    return max(F/u_s, F/d_i, N*F / (u_s + N*u))

for n in N:
    plt.plot(u, [f2(n, ui) for ui in u])

plt.legend([f"N = {x}" for x in N])
plt.xlabel("u")
plt.ylabel("D")

plt.show()