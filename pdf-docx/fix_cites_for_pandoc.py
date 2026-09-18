import re

with open('Claude-tex-1.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Map Citations
bibitem_pattern = re.compile(r'\\bibitem\{([^}]+)\}')
bibitems = bibitem_pattern.findall(content)
cite_map = {key: str(i+1) for i, key in enumerate(bibitems)}

def repl_cite(match):
    keys = match.group(1).split(',')
    nums = [cite_map.get(k.strip(), '?') for k in keys]
    return '[' + ', '.join(nums) + ']'
content = re.sub(r'\\cite\{([^}]+)\}', repl_cite, content)

content = re.sub(r'\\begin\{thebibliography\}\{.*?\}', r'\\section*{References}', content)
content = re.sub(r'\\end\{thebibliography\}', '', content)

def repl_bibitem(match):
    key = match.group(1)
    num = cite_map.get(key, '?')
    return f'\n\n[{num}] '
content = re.sub(r'\\bibitem\{([^}]+)\}', repl_bibitem, content)


# 2. Fix Algorithm and Table 2 for Pandoc Word Conversion
# Remove original Algorithm 1
algo_pattern = re.compile(r'\\begin\{algorithm\}.*?\\end\{algorithm\}', re.DOTALL)
content = re.sub(algo_pattern, '', content)

# Remove original Table 2
table2_pattern = re.compile(r'\\begin\{table\}.*?tab:fidelity.*?\\end\{table\}', re.DOTALL)
content = re.sub(table2_pattern, '', content)

# Define the exact Pandoc-friendly string to insert before \subsection{Diagnostic Fidelity}
pandoc_friendly_algo_table = r'''
\noindent \textbf{Algorithm 1} Receiver Verification and Provenance Extraction\\
\rule{\textwidth}{0.5pt}\\
\textbf{Require:} Packet $P$; keys $K_{enc}, K_{sec}$; expected $DevID, W_{exp}$; clock $T_{now}$\\
\textbf{Ensure:} Verdict $\in \{\text{Authentic}, \text{Tampered}, \text{Replay}\}$\\
1: Parse $\mathcal{N} \parallel C \parallel \text{Tag} \gets P$\\
2: $M \gets \text{ChaCha20-Poly1305-Decrypt}(K_{enc}, \mathcal{N}, C, \text{Tag})$\\
3: \textbf{if} $M = \bot$ \textbf{then return Tampered} (AEAD failed)\\
4: \textbf{end if}\\
5: Deconstruct $(I_w \parallel \tau \parallel T_s) \gets M$\\
6: \textbf{if} $|T_{now} - T_s| > 30\,\text{s}$ \textbf{then return Replay}\\
7: \textbf{end if}\\
8: $\tau_{calc} \gets \text{BLAKE3}(DevID \parallel K_{sec} \parallel \text{Serialize}(I_w) \parallel T_s)$\\
9: \textbf{if} $\tau \neq \tau_{calc}$ \textbf{then return Tampered} (token mismatch)\\
10: \textbf{end if}\\
11: Extract $W_{ext}$ from LSBs of $I_w$\\
12: \textbf{if} $W_{ext} \neq W_{exp}$ \textbf{then return Tampered} (provenance mismatch)\\
13: \textbf{end if}\\
14: \textbf{return Authentic}\\
\rule{\textwidth}{0.5pt}

\vspace{1em}

\begin{table}[h]
\centering
\caption{Diagnostic fidelity metrics on $512\times512$ DICOM images.}
\label{tab:fidelity}
\begin{tabular}{lcccc}
\toprule
Modality & PSNR (dB) & SSIM & NC & BER (\%) \\
\midrule
Chest X-Ray   & 52.14 & 0.9998 & 1.0000 & 0.00 \\
Cranial CT    & 51.42 & 0.9997 & 1.0000 & 0.00 \\
Abdominal MRI & 53.08 & 0.9999 & 1.0000 & 0.00 \\
\bottomrule
\end{tabular}
\end{table}

'''

content = content.replace(r'\subsection{Diagnostic Fidelity}', pandoc_friendly_algo_table + r'\subsection{Diagnostic Fidelity}')

with open('Claude-tex-1-pandoc.tex', 'w', encoding='utf-8') as f:
    f.write(content)
