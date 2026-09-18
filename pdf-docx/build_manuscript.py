import os
import re
import subprocess
import shutil

def build_pdf():
    print("Building PDF...")
    # Run pdflatex twice for cross-references
    subprocess.run(['pdflatex', '-interaction=nonstopmode', '-jobname=SecureMark-Med', 'main.tex'], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['pdflatex', '-interaction=nonstopmode', '-jobname=SecureMark-Med', 'main.tex'], check=True, stdout=subprocess.DEVNULL)
    print("PDF build complete.")

def build_docx():
    print("Building DOCX...")
    # Read main.tex
    with open('main.tex', 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply formatting fixes for Pandoc (extracting body + fixing citations)
    # Map Citations
    bibitem_pattern = re.compile(r'\\bibitem\{([^}]+)\}')
    bibitems = bibitem_pattern.findall(content)
    cite_map = {key: str(i+1) for i, key in enumerate(bibitems)}

    def repl_cite(match):
        keys = match.group(1).split(',')
        nums = [cite_map.get(k.strip(), '?') for k in keys]
        return '[' + ', '.join(nums) + ']'
    content = re.sub(r'\\cite\{([^}]+)\}', repl_cite, content)

    # Replace thebibliography environment with standard Markdown/Pandoc friendly lists
    content = re.sub(r'\\begin\{thebibliography\}\{.*?\}', r'\\section*{References}', content)
    content = re.sub(r'\\end\{thebibliography\}', '', content)

    def repl_bibitem(match):
        key = match.group(1)
        num = cite_map.get(key, '?')
        return f'\n\n[{num}] '
    content = re.sub(r'\\bibitem\{([^}]+)\}', repl_bibitem, content)

    # Replace class to article to avoid llncs warnings in Pandoc
    content = re.sub(r'\\documentclass\[.*?\]\{llncs\}', r'\\documentclass{article}', content)

    # -------------------------------------------------------------
    # PANDOC ALGORITHM FIX: Replace \begin{algorithm}...\end{algorithm}
    # with a Pandoc-friendly tabular block so Word doesn't drop it.
    # -------------------------------------------------------------
    algo_pattern = re.compile(r'\\begin\{algorithm\}.*?\\end\{algorithm\}', re.DOTALL)
    
    pandoc_friendly_algo = r'''
\begin{table}[htbp]
\centering
\caption{Algorithm 1: Receiver Verification and Provenance Extraction}
\label{alg:verification}
\small
\begin{tabular}{@{}ll@{}}
\toprule
\multicolumn{2}{@{}l}{\textbf{Require:} Datagram $P$; keys $K_{enc}, K_{sec}$; expected metadata $DevID, W_{exp}$; clock $T_{now}$} \\
\multicolumn{2}{@{}l}{\textbf{Ensure:} Verdict $\in \{\text{Authentic},\,\text{Tampered},\,\text{Replay}\}$} \\
\midrule
1:  & Parse $\mathcal{N} \parallel C \parallel \text{Tag} \gets P$ \\
2:  & $M \gets \text{ChaCha20-Poly1305-Decrypt}(K_{enc}, \mathcal{N}, C, \text{Tag})$ \\
3:  & \textbf{if} $M = \bot$ \textbf{then return} \textbf{Tampered} (AEAD tag failure) \\
4:  & Deconstruct $(I_w \parallel \tau \parallel T_s) \gets M$ \\
5:  & \textbf{if} $\vert{}T_{now} - T_s\vert{} > 30\,\text{s}$ \textbf{then return} \textbf{Replay} (Stale packet) \\
6:  & $\tau_{\mathit{calc}} \gets \text{BLAKE3}(DevID \parallel K_{sec} \parallel \text{Serialize}(I_w) \parallel T_s)$ \\
7:  & \textbf{if} $\tau \neq \tau_{\mathit{calc}}$ \textbf{then return} \textbf{Tampered} (Cryptographic hash mismatch) \\
8:  & Extract $W_{ext}$ from LSBs of $I_w$ \\
9:  & \textbf{if} $W_{ext} \neq W_{exp}$ \textbf{then return} \textbf{Tampered} (Provenance mismatch) \\
10: & \textbf{return} \textbf{Authentic} \\
\bottomrule
\end{tabular}
\end{table}
'''
    content = re.sub(algo_pattern, lambda m: pandoc_friendly_algo, content)

    with open('main-pandoc.tex', 'w', encoding='utf-8') as f:
        f.write(content)

    # Run pandoc
    subprocess.run([
        'pandoc', 'main-pandoc.tex',
        '-o', 'SecureMark-Med.docx',
        '--from=latex',
        '--to=docx',
        '--mathjax'
    ], check=True)
    print("DOCX build complete.")

def verify():
    print("\n--- Build Verification ---")
    files = ['SecureMark-Med.pdf', 'SecureMark-Med.docx']
    all_good = True
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"[OK] {file} generated successfully (Size: {size / 1024:.2f} KB)")
        else:
            print(f"[ERROR] {file} is missing!")
            all_good = False
    
    if all_good:
        print("\nSUCCESS: Both documents generated cleanly without errors.")
    else:
        print("\nFAILURE: One or more documents failed to generate.")

if __name__ == '__main__':
    try:
        build_pdf()
        build_docx()
        verify()
    except Exception as e:
        print(f"Build failed: {e}")
