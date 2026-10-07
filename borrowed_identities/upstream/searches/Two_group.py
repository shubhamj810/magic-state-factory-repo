"""Asymmetric distillation factory search (Section IV) """
from math import comb
from itertools import product


def f_coefficient(i_O, i_S, k, n_minus_k, w_O, w_S):
    coeff_y = sum(((-1) ** j) * comb(i_O, j) * comb(k - i_O, w_O - j)
                  for j in range(max(0, w_O - (k - i_O)), min(i_O, w_O) + 1))
    coeff_z = sum(((-1) ** j) * comb(i_S, j) * comb(n_minus_k - i_S, w_S - j)
                  for j in range(max(0, w_S - (n_minus_k - i_S)), min(i_S, w_S) + 1))
    return coeff_y * coeff_z


def phi_over_theta_int(i_O, i_S, k, n_minus_k, sigma_dict):
    total = 0
    for (w_O, w_S), sigma in sigma_dict.items():
        if sigma == 0:
            continue
        total -= sigma * f_coefficient(i_O, i_S, k, n_minus_k, w_O, w_S)
    return total


def is_borrowed_identity(l, n, k, sigma_dict):
    n_minus_k = n - k
    for i_O in range(k + 1):
        for i_S in range(n_minus_k + 1):
            if i_O + i_S == 0 or i_O + i_S > l:
                continue
            required_div = 1 << (l - i_O - i_S + 1)
            total = sum(
                sigma * comb(k - i_O, w_O - i_O) * comb(n_minus_k - i_S, w_S - i_S)
                for (w_O, w_S), sigma in sigma_dict.items()
                if w_O >= i_O and w_S >= i_S
            )
            if total % required_div != 0:
                return False
    return True


def n_circuit_count(k, n_minus_k, sigma_dict):
    return sum(comb(k, w_O) * comb(n_minus_k, w_S)
               for (w_O, w_S), sigma in sigma_dict.items() if sigma != 0)


def extract_factory(k, n_minus_k, sigma_dict, W_O, W_total):
    N_circuit = n_circuit_count(k, n_minus_k, sigma_dict)
    intersection = set(W_O) & set(W_total)
    n_removed = sum(comb(k, w) for w in intersection if w >= 1)
    return N_circuit - n_removed


def residual_phase_at_iO(l, k, n_minus_k, sigma_dict, W_O_int_W_total, i_O):
    full_mod = 1 << (l + 1)
    phi_full = phi_over_theta_int(i_O, 0, k, n_minus_k, sigma_dict)
    extracted = 0
    for w in W_O_int_W_total:
        if w < 1:
            continue
        sigma = sigma_dict.get((w, 0), 0)
        if sigma == 0:
            continue
        coeff_y = sum(((-1) ** j) * comb(i_O, j) * comb(k - i_O, w - j)
                      for j in range(max(0, w - (k - i_O)), min(i_O, w) + 1))
        extracted -= -sigma * coeff_y
    return (phi_full + extracted) % full_mod


def classify_output(l, k, n_minus_k, sigma_dict, W_O_int_W_total):
    full_mod = 1 << (l + 1)
    half_mod = full_mod // 2

    def center(x):
        return ((x + half_mod) % full_mod) - half_mod

    phi_residual = [residual_phase_at_iO(l, k, n_minus_k, sigma_dict, W_O_int_W_total, i_O)
                    for i_O in range(k + 1)]
    phi_diff = [center((p - phi_residual[0]) % full_mod) for p in phi_residual]
    if all(p == 0 for p in phi_diff):
        return "trivial", phi_diff
    highest_d = 0
    for d in range(1, k + 1):
        c_d = center(sum(((-1) ** (d - j)) * comb(d, j) * phi_diff[j] for j in range(d + 1)) % full_mod)
        if c_d != 0:
            highest_d = d
    return (f"deg{highest_d}" if highest_d else "trivial"), phi_diff


def W_AP(n, s):
    return [w for w in range(1, n + 1) if (w - 1) % s == 0]


def build_gate_set(k, n_minus_k, s_total, s_O):
    n = k + n_minus_k
    W_total = set(W_AP(n, s_total))
    W_O = set([0] + W_AP(k, s_O))
    W_S = set(range(0, n_minus_k + 1))  # s_S = 1
    pairs = []
    for w_O in W_O:
        if w_O > k:
            continue
        for w_S in W_S:
            if w_S > n_minus_k:
                continue
            if w_O + w_S in W_total and w_O + w_S >= 1:
                pairs.append((w_O, w_S))
    return sorted(pairs), W_total, W_O


def find_valid_signs(l, n, k, pairs):
    valid = []
    sigma_all_pos = {pair: 1 for pair in pairs}
    if is_borrowed_identity(l, n, k, sigma_all_pos):
        valid.append(dict(sigma_all_pos))
    check_only = [p for p in pairs if p[0] == 0]
    if not check_only:
        return valid
    for sign_choice in product([-1, 1], repeat=len(check_only)):
        if all(s == 1 for s in sign_choice):
            continue
        sd = {pair: 1 for pair in pairs}
        for pair, sign in zip(check_only, sign_choice):
            sd[pair] = sign
        if is_borrowed_identity(l, n, k, sd):
            valid.append(dict(sd))
    return valid
