# Calculation of inverse kinematics

The Stewart platform is a parallel kinematic mechanism consisting of a fixed base and a movable platform. These two planes are connected by six adjustable legs that can be changed in length. By precisely controlling the length of these legs, the position and orientation of the upper platform can be precisely controlled in six degrees of freedom (translation and rotation along all axes). This document provides a mathematical description of how to calculate the leg lengths and the angles of the servo motors.

The leg lengths of the Stewart platform are calculated using a mathematical derivation based on the spatial positions and orientations of the two platforms.

## 1. Translation

The translation vector \( \mathbf{t} \) defines the linear displacement of the movable platform relative to the fixed base.

```math
\mathbf{t} = \begin{bmatrix}
x \\ y \\ z
\end{bmatrix}
```

## 2. Rotation

Three Euler angles (roll \( \alpha \), pitch \( \beta \), yaw \( \gamma \)) specify the orientation of the platform. These angles are converted from degrees to radians:

```math
\alpha = \frac{\pi}{180} \cdot \alpha, \quad \beta = \frac{\pi}{180} \cdot \beta, \quad \gamma = \frac{\pi}{180} \cdot \gamma
```
## 3. Rotation matrix

Using Euler angles, three rotation matrices R (as 3 × 3) are defined, which describe the rotations around the individual axes. Each individual matrix thus ensures that the platform rotates in only one direction.

**Rotation around the x-axis (Roll):**
```math
R_x = \begin{bmatrix}
1 & 0 & 0 \\
0 & \cos\alpha & -\sin\alpha \\
0 & \sin\alpha & \cos\alpha
\end{bmatrix}
```

**Rotation around the y-axis (Pitch):**
```math
R_y = \begin{bmatrix}
\cos\beta & 0 & \sin\beta \\
0 & 1 & 0 \\
-\sin\beta & 0 & \cos\beta
\end{bmatrix}
```

**Rotation around the z-axis (Yaw):**
```math
R_z = \begin{bmatrix}
\cos\gamma & -\sin\gamma & 0 \\
\sin\gamma & \cos\gamma & 0 \\
0 & 0 & 1
\end{bmatrix}
```

**Total rotation matrix:**
```math
R = R_z \cdot R_y \cdot R_x
```

## 4. Transformation of platform points

```math
\mathbf{P}_b^{(i)} = R \cdot \mathbf{P}_p^{(i)} + \mathbf{t}, \quad i = 1, \dots, 6
```

## 5. Calculation of vectors and linear actuators:

```math
\mathbf{v}^{(i)} = \mathbf{P}_b^{(i)} - \mathbf{P}_B^{(i)}
```

```math
L_i = \| \mathbf{v}^{(i)} \| = \sqrt{(v_x^{(i)})^2 + (v_y^{(i)})^2 + (v_z^{(i)})^2}, \quad i = 1, \dots, 6
```

# Calculation of servo angles

The angle calculation is based on three known quantities:

- the servo steering arm \( r \)
- the fixed connecting rod \( l \)
- previously calculated length of the actuator \( L_i \)

## 1. Law of cosines

The three sides form an equilateral triangle. The enclosed angle \( \theta_i \) can be determined using the cosine rule

```math
\cos(\theta) = \frac{a^2 + b^2 - c^2}{2ab}
```

## 2. Applied to the system

```math
\cos(\theta_i) = \frac{r^2 + L_i^2 - l^2}{2 \cdot r \cdot L_i}, \quad i = 1, \dots, 6
```

## 3. Angle calculation

```math
\theta_i = \arccos\left(\frac{r^2 + L_i^2 - l^2}{2 \cdot r \cdot L_i}\right) \cdot \frac{180}{\pi}, \quad i = 1, \dots, 6
```

## 4. Validity check of the value range

Only if this range is observed is the configuration valid and mechanically feasible.

```math
|r - l| \leq L_i \leq r + l
```
