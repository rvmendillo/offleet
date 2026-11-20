"""Turn on-screen text (with code and math symbols) into text-to-speech friendly prose.

Captions keep symbols like O(n), nums[i] or ∫; the iOS speech engine receives the
"say" variant produced here, e.g. "O of n", "nums at i", "the integral of".
"""
import re

_SYMBOLS = [
    ("≤", " less than or equal to "), ("≥", " greater than or equal to "), ("≠", " not equal to "),
    ("≈", " approximately "), ("≡", " is congruent to "), ("∝", " is proportional to "),
    ("→", " to "), ("←", " gets "), ("⇒", " implies "), ("⇔", " if and only if "), ("↦", " maps to "),
    ("×", " times "), ("·", " times "), ("÷", " divided by "), ("±", " plus or minus "), ("∓", " minus or plus "),
    ("∞", " infinity "), ("π", " pi "), ("θ", " theta "), ("λ", " lambda "), ("μ", " mu "), ("σ", " sigma "),
    ("Σ", " sigma "), ("∑", " the sum of "), ("∏", " the product of "), ("∮", " the closed integral of "),
    ("∬", " the double integral of "), ("∭", " the triple integral of "), ("∫", " the integral of "),
    ("∂", " partial "), ("∇", " del "), ("Δ", " delta "), ("δ", " delta "), ("ε", " epsilon "), ("α", " alpha "),
    ("β", " beta "), ("γ", " gamma "), ("ω", " omega "), ("Ω", " omega "), ("φ", " phi "), ("ϕ", " phi "),
    ("ρ", " rho "), ("τ", " tau "), ("η", " eta "), ("κ", " kappa "), ("ξ", " xi "), ("ψ", " psi "), ("χ", " chi "),
    ("ζ", " zeta "), ("ν", " nu "), ("Θ", " theta "), ("Λ", " lambda "), ("Φ", " phi "), ("Ψ", " psi "),
    ("√", " the square root of "), ("∛", " the cube root of "),
    ("∈", " in "), ("∉", " not in "), ("⊆", " is a subset of "), ("⊂", " is a subset of "), ("∪", " union "),
    ("∩", " intersect "), ("∅", " the empty set "), ("∀", " for all "), ("∃", " there exists "), ("¬", " not "),
    ("∧", " and "), ("∨", " or "), ("⊕", " XOR "), ("⊗", " tensor "), ("∘", " composed with "), ("ℝ", " the reals "),
    ("ℕ", " the naturals "), ("ℤ", " the integers "), ("ℚ", " the rationals "), ("ℂ", " the complex numbers "),
    ("⁻¹", " inverse "), ("²", " squared "), ("³", " cubed "), ("⁴", " to the fourth "), ("ⁿ", " to the n "),
    ("ˣ", " to the x "), ("⁺", " plus "), ("⁻", " minus "), ("′′", " double prime "), ("″", " double prime "), ("′", " prime "),
    ("₀", " sub 0 "), ("₁", " sub 1 "), ("₂", " sub 2 "), ("₃", " sub 3 "), ("ₙ", " sub n "), ("ᵢ", " sub i "),
    ("ⱼ", " sub j "), ("ₖ", " sub k "), ("ₜ", " sub t "), ("ₓ", " sub x "),
    ("−", " minus "), ("ₐ", " sub a "), ("ᵃ", " to the a "), ("ᵇ", " to the b "), ("ᵏ", " to the k "),
    ("…", "... "), ("—", ", "), ("⟨", " "), ("⟩", " "), ("‖", " norm "), ("°", " degrees "),
]

_ABBREV = [
    (r"\be\.g\.", "for example"), (r"\bi\.e\.", "that is"), (r"\bvs\.?", "versus"), (r"\betc\.", "et cetera"),
    (r"\bw\.r\.t\.", "with respect to"), (r"\bs\.t\.", "such that"), (r"\biff\b", "if and only if"),
]

_BIGO_INNER = [
    (r"\^2\b", " squared"), (r"\^3\b", " cubed"), (r"\^(\w+)", r" to the \1"), (r"\*", " times "),
    (r"\+", " plus "), (r"(?<=\w)\s*-\s*(?=\w)", " minus "), (r"!", " factorial"), (r"/", " over "),
    (r"·", " times "), (r"×", " times "), (r"²", " squared"), (r"\blog\b", "log"), (r"\b1\b", "one"),
]


def _bigo(m):
    letter, inner = m.group(1), m.group(2)
    for pat, rep in _BIGO_INNER:
        inner = re.sub(pat, rep, inner)
    name = {"O": "O of", "Θ": "theta of", "Ω": "omega of", "o": "little o of"}[letter]
    return f" {name} {inner.strip()} "


def speakify(text: str) -> str:
    if not text:
        return text
    s = text
    # markdown and code decoration
    s = re.sub(r"```.*?```", " ", s, flags=re.S)
    s = s.replace("**", "").replace("`", "").replace("__", "")
    s = re.sub(r"^#+\s*", "", s, flags=re.M)
    s = re.sub(r"^\s*[-*•]\s+", "", s, flags=re.M)
    for pat, rep in _ABBREV:
        s = re.sub(pat, rep, s, flags=re.I)
    # complexity notation
    s = re.sub(r"\b([OΘΩ])\(([^()]*(?:\([^()]*\)[^()]*)*)\)", _bigo, s)
    # indexing like dp[i][j] or nums[i]
    s = re.sub(r"\b([A-Za-z_]\w*)\[([^\[\]]+)\]\[([^\[\]]+)\]", r"\1 at \2, \3", s)
    s = re.sub(r"\b([A-Za-z_]\w*)\[([^\[\]:]+)\]", r"\1 at \2", s)
    # limits and single-letter function application: f(x) -> f of x
    s = re.sub(r"\blim\s*_?\{?\s*(\w)\s*(?:→|->|to)\s*([\w∞+\-]+)\}?", r"the limit as \1 approaches \2,", s)
    s = re.sub(r"(?<![\w.])([a-zA-Z])\(([^()]{1,12})\)", r"\1 of \2", s)
    # generics like Map<String, Integer>
    s = re.sub(r"(?<=\w)<(?=[A-Z?])", " of ", s)
    s = re.sub(r"(?<=[\w?])>(?=[\s,;.)>]|$)", " ", s)
    # multi-char operators
    for pat, rep in [("==", " equals "), ("!=", " is not equal to "), ("<=", " is at most "), (">=", " is at least "),
                     ("->", " to "), ("=>", " gives "), ("&&", " and "), ("||", " or "), ("+=", " plus equals "),
                     ("-=", " minus equals "), ("*=", " times equals "), ("//", " integer divided by "),
                     ("**", " to the power of "), ("<<", " shifted left by "), (">>", " shifted right by "), ("::", " ")]:
        s = s.replace(pat, rep)
    for sym, rep in _SYMBOLS:
        s = s.replace(sym, rep)
    # exponents like 10^5 or 2^n
    s = re.sub(r"(\w)\s*\^\s*\(?(-?\w+)\)?", r"\1 to the power of \2", s)
    # ranges like 1–5 (en dash)
    s = re.sub(r"(\d)\s*–\s*(\d)", r"\1 to \2", s)
    s = s.replace("–", ", ")
    # arithmetic
    s = re.sub(r"(?<=[\w)\]])\s*\+\s*(?=[\w(\[])", " plus ", s)
    s = re.sub(r"(?<=\w)\s+-\s+(?=\w)", " minus ", s)
    s = re.sub(r"\b([a-z]\w*)\s*-\s*(\d+)\b", r"\1 minus \2", s)
    s = re.sub(r"(?<=\w)\s*\*\s*(?=\w)", " times ", s)
    s = re.sub(r"(\d)\s*/\s*(\d)", r"\1 over \2", s)
    s = re.sub(r"\)\s*/\s*(\w)", r") over \1", s)
    s = re.sub(r"\s/\s", " divided by ", s)
    s = re.sub(r"(?<=\w)\s+/\s+(?=\w)", " divided by ", s)
    s = re.sub(r"(\d)\s*%", r"\1 percent", s)
    s = re.sub(r"\s%\s", " mod ", s)
    s = re.sub(r"(?<=[\w)\]])\s*=\s*(?=[\w\-\[('\"])", " equals ", s)
    s = re.sub(r"\s<\s", " is less than ", s)
    s = re.sub(r"\s>\s", " is greater than ", s)
    s = s.replace("&", " and ").replace("@", " at ")
    s = re.sub(r"#(\d)", r"number \1", s)
    # brackets and braces become pauses
    s = re.sub(r"[\[\]{}]", " ", s)
    s = re.sub(r"\(\s*\)", "", s)
    # identifiers: snake_case and camelCase
    s = re.sub(r"(?<=[A-Za-z])_(?=[A-Za-z])", " ", s)
    s = re.sub(r"(?<=[a-z])(?=[A-Z][a-z])", " ", s)
    # spoken lists: "1,3,4" -> "1, 3, 4" (content never uses thousands separators)
    s = re.sub(r"(?<=[\w'\"]),(?=[-\w'\"])", ", ", s)
    # tidy
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    s = re.sub(r",\s*,+", ",", s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


if __name__ == "__main__":
    samples = [
        "Time is O(n), space is O(1). Sorting costs O(n log n); brute force is O(n^2).",
        "If nums[l] + nums[r] == target we return [l, r].",
        "dp[i][j] = dp[i-1][j] + dp[i][j-1]",
        "1 ≤ n ≤ 10^5 and -10^9 ≤ nums[i] ≤ 10^9",
        "∫ₐᵇ f(x) dx = F(b) − F(a)",
        "The window is 'abc' (length 3), e.g. maxLen = 3.",
        "Use a HashMap<Character, Integer> to count; k-1 and n - 1.",
        "f′(x) = lim h→0 [f(x+h) − f(x)] / h",
        "Check s.length() and charAt(i) && i < j.",
        "a² + b² = c²; ∑ i = n(n+1)/2",
    ]
    for t in samples:
        print(t, "\n  ->", speakify(t))
