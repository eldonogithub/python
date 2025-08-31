
import math
from math import comb
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import mpmath as mp
    mpmath_available = True
except ImportError:
    mpmath_available = False

def binom_pmf(n, k, p):
    return comb(n, k) * (p ** k) * ((1 - p) ** (n - k))

def binom_cdf_leq(n, k, p):
    return sum(binom_pmf(n, i, p) for i in range(k + 1))

def compute_stats(n, k, p0):
    # Expected value under null hypothesis
    mean = n * p0
    # Variance under null hypothesis
    var = n * p0 * (1 - p0)
    # Standard deviation under null hypothesis
    sd = math.sqrt(var)
    # Z-score for normal approximation to the binomial
    z = (k - mean) / sd
    # Two-sided exact p-value (Clopper-Pearson style tail doubling)
    pmf_k = binom_pmf(n, k, p0)
    two_sided_p = sum(binom_pmf(n, i, p0) for i in range(n + 1) if binom_pmf(n, i, p0) <= pmf_k)
    # One-sided lower-tail probability
    cdf_leq_k = binom_cdf_leq(n, k, p0)
    # 95% confidence interval for true p (Clopper-Pearson exact via beta quantiles)
    alpha = 0.05
    if mpmath_available:
        lower_cp = 0.0 if k == 0 else mp.betaincinv(k, n-k+1, alpha/2, regularized=True)
        upper_cp = 1.0 if k == n else mp.betaincinv(k+1, n-k, 1 - alpha/2, regularized=True)
        cp_interval = (float(lower_cp), float(upper_cp))
    else:
        cp_interval = (None, None)
    # Wilson score interval for binomial proportion
    phat = k/n
    z_ = 1.96
    center = (phat + (z_**2)/(2*n)) / (1 + z_**2/n)
    halfwidth = (z_ * math.sqrt((phat*(1-phat) + (z_**2)/(4*n)) / n)) / (1 + z_**2/n)
    lower_wilson = center - halfwidth
    upper_wilson = center + halfwidth
    # Desired margin of error for estimating p (±5%)
    m = 0.05
    n_margin = (1.96**2 * p0*(1-p0)) / (m**2)
    # One-sample binomial power calculation
    power = 0.80
    p1 = 0.15
    z_alpha2 = 1.96
    if mpmath_available:
        z_power = mp.sqrt(2) * mp.erfinv(2*power - 1)
        z_power = 0.8416212335729143
    else:
        z_power = 0.8416212335729143
    n_power = ((z_alpha2*math.sqrt(p0*(1-p0)) + z_power*math.sqrt(p1*(1-p1)))**2) / ((p0 - p1)**2)
    results = {
        "n": n,
        "k": k,
        "p0": p0,
        "mean_np": mean,
        "sd_sqrt_np1p": sd,
        "z_normal": z,
        "pmf_at_k": pmf_k,
        "P(X <= k | p0)": cdf_leq_k,
        "two_sided_exact_p": two_sided_p,
        "phat": phat,
        "Clopper-Pearson_95%": cp_interval,
        "Wilson_95%": (lower_wilson, upper_wilson),
        "n_for_±5%_margin_at_95%": n_margin,
        "n_for_detecting_20%_vs_15%_80%power_5%alpha": n_power
    }
    return results

def show_results(results):
    # Output will be handled with tags in the Text widget, so return a list of (label, value) pairs
    formatted = []
    for k, v in results.items():
        if isinstance(v, float):
            val = f"{v:.2f}"
        elif isinstance(v, tuple) and all(isinstance(x, float) or x is None for x in v):
            val = f"({v[0]:.2f}, {v[1]:.2f})" if v[0] is not None and v[1] is not None else str(v)
        else:
            val = str(v)
        formatted.append((k, val))
    return formatted

def on_calculate():
    try:
        n = int(entry_n.get())
        k = int(entry_k.get())
        p0 = float(entry_p0.get())
        if not (0 <= p0 <= 1):
            raise ValueError("p0 must be between 0 and 1")
        results = compute_stats(n, k, p0)
        result_text.delete(1.0, tk.END)
        # Insert with tags for color and bold
        for label, value in show_results(results):
            result_text.insert(tk.END, f"{label}: ", "label")
            result_text.insert(tk.END, f"{value}\n", "value")
    except Exception as e:
        messagebox.showerror("Error", str(e))
## Only the new dark theme code below
root = tk.Tk()
root.title("Binomial Stats Calculator")
root.configure(bg="black")

style = ttk.Style()
style.theme_use("default")
style.configure("TFrame", background="black")
style.configure("TLabel", background="black", foreground="white")
style.configure("TButton", background="black", foreground="white")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

label_n = ttk.Label(frame, text="Number of trials (n):")
label_n.grid(row=0, column=0, sticky=tk.W)
entry_n = tk.Entry(frame, bg="black", fg="white", insertbackground="white")
entry_n.grid(row=0, column=1)
entry_n.insert(0, "71")

label_k = ttk.Label(frame, text="Number of successes (k):")
label_k.grid(row=1, column=0, sticky=tk.W)
entry_k = tk.Entry(frame, bg="black", fg="white", insertbackground="white")
entry_k.grid(row=1, column=1)
entry_k.insert(0, "11")

label_p0 = ttk.Label(frame, text="Probability of success (p0):")
label_p0.grid(row=2, column=0, sticky=tk.W)
entry_p0 = tk.Entry(frame, bg="black", fg="white", insertbackground="white")
entry_p0.grid(row=2, column=1)
entry_p0.insert(0, "0.20")

calc_btn = ttk.Button(frame, text="Calculate", command=on_calculate)
calc_btn.grid(row=3, column=0, columnspan=2, pady=5)

result_text = tk.Text(frame, width=60, height=18, bg="black", fg="white", insertbackground="white")
result_text.grid(row=4, column=0, columnspan=2, pady=5)
# Add tags for bold yellow labels and bold white values
result_text.tag_configure("label", foreground="yellow", font=("TkDefaultFont", 10, "bold"))
result_text.tag_configure("value", foreground="white", font=("TkDefaultFont", 10, "bold"))

root.mainloop()
