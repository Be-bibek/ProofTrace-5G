import re

tex_file = r"d:\flutter_main\Bibek\ProofTrace-5G\pdf-docx\submission_work\main.tex"
out_tex = r"d:\flutter_main\Bibek\ProofTrace-5G\pdf-docx\submission_work\main_for_docx.tex"

with open(tex_file, "r", encoding="utf-8") as f:
    content = f.read()

algo_replacement = r"""
\vspace{10pt}
\noindent\textbf{Algorithm 1: Receiver Verification and Provenance Extraction}

\noindent\textbf{Require:} Datagram $P$; keys $K_{enc}, K_{sec}$; expected metadata $DevID, W_{exp}$; clock $T_{now}$\\
\textbf{Ensure:} Verdict $\in \{\text{Authentic},\,\text{Tampered},\,\text{Stale}\}$

\noindent
1: Parse $\mathcal{N} \parallel C \parallel \text{Tag} \gets P$\\
2: $M \gets \text{ChaCha20-Poly1305-Decrypt}(K_{enc}, \mathcal{N}, C, \text{Tag})$\\
3: \textbf{if} $M = \bot$ \textbf{then return Tampered} (AEAD tag failure)\\
4: Deconstruct $(I_w \parallel \tau \parallel T_s) \gets M$\\
5: \textbf{if} $\vert{}T_{now} - T_s\vert{} > 30\,\text{s}$ \textbf{then return Stale} (Expired freshness window)\\
6: $\tau_{\mathit{calc}} \gets \text{BLAKE3}_{\text{keyed}}(K_{sec}, DevID \parallel \text{Serialize}(I_w) \parallel T_s)$\\
7: \textbf{if} $\tau \neq \tau_{\mathit{calc}}$ \textbf{then return Tampered} (Cryptographic hash mismatch)\\
8: Extract $W_{ext}$ from LSBs of $I_w$\\
9: \textbf{if} $W_{ext} \neq W_{exp}$ \textbf{then return Tampered} (Provenance mismatch)\\
10: \textbf{return Authentic}
\vspace{10pt}
"""

algo_replacement = algo_replacement.replace('\\', '\\\\')

pattern = re.compile(r"\\begin\{algorithm\}.*?\\end\{algorithm\}", re.DOTALL)
new_content = pattern.sub(algo_replacement, content)

with open(out_tex, "w", encoding="utf-8") as f:
    f.write(new_content)
