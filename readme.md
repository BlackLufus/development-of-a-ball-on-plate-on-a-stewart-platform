# Grundlagen: Schritt für Schritt Anleitung zur berechnung der Stewart-Plattform:

## 1. **Geometrie der Plattform definieren**

**Basis (festes Element):**

6 Befestigungspunkte $ B_i $ ($ i = 1, \dots, 6 $) auf einem Kreis mit Radius $ R_b $.
Typische Anordnung: Punkte um $ 60^\circ $ versetzt.
Koordinaten im Basissystem:

$
B_i = \begin{bmatrix} R_b \cos(\theta_{b_i}) \\ R_b \sin(\theta_{b_i}) \\ 0 \end{bmatrix}
$

**Plattform (bewegliches Element):**

6 Befestigungspunkte $ P_i $ auf einem Kreis mit Radius $ R_p $.
Koordinaten im Plattformsystem:

$
P_i = \begin{bmatrix} R_p \cos(\theta_{p_i}) \\ R_p \sin(\theta_{p_i}) \\ 0 \end{bmatrix}
$

## 2. **Position und Orientierung der Plattform festlegen**

**Translation (Verschiebung):**

Verschiebungsvektor $ \mathbf{t} = \begin{bmatrix} x \\ y \\ z \end{bmatrix} $.

**Rotation:**

Rotationsmatrix $ \mathbf{R} $ aus Euler-Winkeln (z. B. Roll-Pitch-Yaw):

$R_B = R_z(ψ) * R_y(θ) * R_x(ϕ) $

**Rotation um die Z-Achse (Yaw, ψ)**

$
R_z(ψ) = \begin{bmatrix}
\cosψ & -sinψ & 0 \\
sinψ & cosψ & 0 \\
0 & 0 & 1
\end{bmatrix}
$

**Rotation um die Y-Achse (Pitch, θ)**

$
R_y(θ) = 
\begin{bmatrix}
cos(θ) & 0 & sin(θ) \\
0 & 1 & 0 \\
-sin(θ) & 0 & cos(θ)
\end{bmatrix}
$

**Rotation um die X-Achse (Roll, ϕ)**

$
R_y(θ) = 
\begin{bmatrix}
1 & 0 & 0 \\
0 & cos(ϕ) & -sin(ϕ) \\
0 & sin(ϕ) & cos(ϕ)
\end{bmatrix}
$

**Beispiel:**

$
R_B =
\begin{bmatrix}
cos(ψ) & -sin(ψ) & 0 \\
sin(ψ) & cos(ψ) & 0 \\
0 & 0 & 1
\end{bmatrix}
\
*
\begin{bmatrix}
cos(θ) & 0 & sin(θ) \\
0 & 1 & 0 \\
-sin(θ) & 0 & cos(θ)
\end{bmatrix}
*
\begin{bmatrix}
1 & 0 & 0 \\
0 & cos(ϕ) & -sin(ϕ) \\
0 & sin(ϕ) & cos(ϕ)
\end{bmatrix}
$

$
R_B =
\begin{bmatrix}
cos(ψ)cos(θ) & -sin(ψ) & cos(ψ)sin(θ) \\
sin(ψ)cos(θ) & cos(ψ) & sin(ψ)sin(θ) \\
-sin(θ) & 0 & cos(θ)
\end{bmatrix}
*
\begin{bmatrix}
1 & 0 & 0 \\
0 & cos(ϕ) & -sin(ϕ) \\
0 & sin(ϕ) & cos(ϕ)
\end{bmatrix}
$

$
R_B =
\begin{bmatrix}
cos(ψ)cos(θ) & -sin(ψ)cos(ϕ)+cos(ψ)sin(θ)sin(ϕ) & sin(ψ)sin(ϕ)+cos(ψ)sin(θ)cos(ϕ) \\
sin(ψ)cos(θ) & cos(ψ)cos(ϕ) + sin(ψ)sin(θ)sin(ϕ) & -cos(ϕ)sin(ϕ)+sin(ψ)sin(θ)cos(ϕ) \\
-sin(θ) & cos(θ)sin(ϕ) & cos(θ)cos(ϕ)
\end{bmatrix}
$

Werte zwischen $-90\degree$ und $90\degree$
$
ψ = 30\degree
$
$
θ = 20\degree
$
$
ϕ = 10\degree
$

## 3. **Plattformpunkte ins Basissystem transformieren**

Jeder Plattformpunkt $ P_i $ wird transformiert:

$
P_{b_i} = \mathbf{R} \cdot P_i + \mathbf{t}
$

**Beispiel:**

Für $ P_1 = \begin{bmatrix} 0.8 \\ 0 \\ 0 \end{bmatrix} $:

$
P_{b_1} = \mathbf{R} \cdot \begin{bmatrix} 0.8 \\ 0 \\ 0 \end{bmatrix} + \begin{bmatrix} 0.1 \\ 0.2 \\ 0.5 \end{bmatrix}
$

## 4. **Beinvektoren berechnen**

Vektor für Bein $ i $:

$
\mathbf{v}_i = P_{b_i} - B_i
$

**Beispiel:**

$
\mathbf{v}_1 = \begin{bmatrix} 0.75 \\ 0.64 \\ 0.34 \end{bmatrix} - \begin{bmatrix} 1.0 \\ 0 \\ 0 \end{bmatrix} = \begin{bmatrix} -0.25 \\ 0.64 \\ 0.34 \end{bmatrix}
$

## 5. **Beinlängen bestimmen**

Länge des Beins $ i $:

$
L_i = \|\mathbf{v}_i\| = \sqrt{v_{i_x}^2 + v_{i_y}^2 + v_{i_z}^2}
$

**Beispiel:**

$
L_1 = \sqrt{(-0.25)^2 + 0.64^2 + 0.34^2} \approx 0.76 \, \text{m}
$

---

### **Wichtige Hinweise**

- **Arbeitsraum prüfen:** Die berechneten Beinlängen müssen im zulässigen Bereich der Aktoren liegen.
- **Numerische Berechnung:** Die Nutzen von Tools wie MATLAB oder Python für präzise Matrizenoperationen.
- **Symmetrie:** Bei symmetrischen Plattformen vereinfachen sich die Winkel $ \theta_{b_i} $ und $ \theta_{p_i} $.

**Formelzusammenfassung:**

$
\boxed{L_i = \sqrt{( \mathbf{R} \cdot P_i + \mathbf{t} - B_i )^\top ( \mathbf{R} \cdot P_i + \mathbf{t} - B_i )}}
$