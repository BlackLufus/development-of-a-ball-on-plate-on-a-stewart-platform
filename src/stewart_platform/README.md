# Mathematische Modellierung der Stewart-Plattform

Die Stewart-Plattform ist ein parallelkinematischer Mechanismus, der aus einer festen Basis und einer beweglichen Plattform besteht. Diese beiden Ebenen sind über sechs verstellbare Beine verbunden, die in der Länge verändert werden können. Durch die gezielte Steuerung dieser Beinlängen lässt sich die Position und Orientierung der oberen Plattform in sechs Freiheitsgraden (Translation und Rotation entlang aller Achsen) präzise kontrollieren. In diesem Dokument wird die Berechnung der Beinlängen sowie der Winkel von Servomotoren mathematisch beschrieben.

## Berechnung der Beinlängen

Die Berechnung der Beinlängen der Stewart-Plattform erfolgt durch eine mathematische Herleitung, die auf den räumlichen Positionen und Orientierungen der beiden Plattformen basiert.

Zur eindeutigen Beschreibung der Position und Orientierung der Plattform werden zwei Größen verwendet:

- Ein Translationsvektor \( \mathbf{t} \), der die lineare Verschiebung der beweglichen Plattform bezüglich der festen Basis definiert:

```math
\mathbf{t} = \begin{bmatrix}
x \\ y \\ z
\end{bmatrix}
```

- Drei Winkel, sogenannte Eulerwinkel (Roll \( \alpha \), Pitch \( \beta \), Yaw \( \gamma \)), die die Orientierung der Plattform angeben. Diese Winkel werden von Grad in Radianten umgerechnet:

```math
\alpha = \frac{\pi}{180} \cdot \alpha, \quad \beta = \frac{\pi}{180} \cdot \beta, \quad \gamma = \frac{\pi}{180} \cdot \gamma
```

Die Rotationsmatrizen zur Beschreibung der Drehungen um die jeweiligen Achsen lauten:

**Rotation um die x-Achse (Roll):**
```math
R_x = \begin{bmatrix}
1 & 0 & 0 \\
0 & \cos\alpha & -\sin\alpha \\
0 & \sin\alpha & \cos\alpha
\end{bmatrix}
```

**Rotation um die y-Achse (Pitch):**
```math
R_y = \begin{bmatrix}
\cos\beta & 0 & \sin\beta \\
0 & 1 & 0 \\
-\sin\beta & 0 & \cos\beta
\end{bmatrix}
```

**Rotation um die z-Achse (Yaw):**
```math
R_z = \begin{bmatrix}
\cos\gamma & -\sin\gamma & 0 \\
\sin\gamma & \cos\gamma & 0 \\
0 & 0 & 1
\end{bmatrix}
```

**Gesamtrotationsmatrix:**
```math
R = R_z \cdot R_y \cdot R_x
```

**Transformation der Plattformpunkte:**
```math
\mathbf{P}_b^{(i)} = R \cdot \mathbf{P}_p^{(i)} + \mathbf{t}, \quad i = 1, \dots, 6
```

**Berechnung der Beinvektoren und Beinlängen:**
```math
\mathbf{v}^{(i)} = \mathbf{P}_b^{(i)} - \mathbf{P}_B^{(i)}
```

```math
L_i = \| \mathbf{v}^{(i)} \| = \sqrt{(v_x^{(i)})^2 + (v_y^{(i)})^2 + (v_z^{(i)})^2}, \quad i = 1, \dots, 6
```

---

## Berechnung der Servo-Winkel

Um die Plattform effektiv steuern zu können, ist zusätzlich die Berechnung der entsprechenden Servo-Winkel notwendig. Die Winkelberechnung basiert auf drei bekannten Größen:

- der Servo-Arm-Länge \( r \)
- der festen Beinlänge \( l \)
- den zuvor berechneten Beinlängen \( L_i \)

Diese Formel ergibt sich aus der Betrachtung eines mechanischen Dreiecks, das durch den Servoarm, die feste Verbindungsstange (Pushrod) und die Strecke zwischen dem Servodrehpunkt und dem Befestigungspunkt auf der Plattform gebildet wird.

Dabei bilden:

- \( a = r \) (Servo-Arm)
- \( b = L_i \) (berechnete Beinlänge)
- \( c = l \) (feste Verbindungsstange)

die drei Seiten eines ebenen Dreiecks. Der eingeschlossene Winkel \( \theta_i \) lässt sich mithilfe des Kosinussatzes bestimmen:

**Kosinussatz:**
```math
\cos(\theta) = \frac{a^2 + b^2 - c^2}{2ab}
```

**Angewandt auf das System ergibt sich:**
```math
\cos(\theta_i) = \frac{r^2 + L_i^2 - l^2}{2 \cdot r \cdot L_i}, \quad i = 1, \dots, 6
```

**Winkelberechnung:**
```math
\theta_i = \arccos\left(\frac{r^2 + L_i^2 - l^2}{2 \cdot r \cdot L_i}\right) \cdot \frac{180}{\pi}, \quad i = 1, \dots, 6
```

**Gültigkeitsprüfung des Wertebereichs:**
```math
|r - l| \leq L_i \leq r + l
```

Nur wenn dieser Bereich eingehalten wird, ist die Konfiguration gültig und mechanisch realisierbar.
