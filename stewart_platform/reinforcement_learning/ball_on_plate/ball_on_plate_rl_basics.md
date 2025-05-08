# Ball on Plate System with Stewart Platform

## System Overview
The Ball on Plate system consists of a Stewart platform that can rotate around the X and Y axes to control the position of a ball on a plate. The Z-axis rotation does not affect the ball's movement.

## State Variables
- Ball Position: (x, y)
- Ball Velocity: (vx, vy)
- Ball Acceleration: (ax, ay)
- Platform Rotation: (θx, θy)

## System Dynamics
The ball's movement is influenced by:
1. Gravity (g = 9.81 m/s²)
2. Platform tilt angles
3. Friction (can be initially ignored for basic modeling)

### Motion Equations
For small angles, the ball's acceleration can be approximated as:
```python
ax = g * sin(θy)
ay = -g * sin(θx)
```

## Control Inputs
- θx: Platform rotation around X-axis (-θmax to +θmax)
- θy: Platform rotation around Y-axis (-θmax to +θmax)

## State Tracking
The system tracks:
1. Current Position (x, y)
2. Current Velocity (vx, vy) through position differentiation
3. Current Acceleration (ax, ay) through velocity differentiation
4. Movement Direction: atan2(vy, vx)

## Basic Python Class Structure
```python
class BallOnPlate:
    def __init__(self):
        self.x = 0.0  # Ball x position
        self.y = 0.0  # Ball y position
        self.vx = 0.0  # Ball x velocity
        self.vy = 0.0  # Ball y velocity
        self.theta_x = 0.0  # Platform x rotation
        self.theta_y = 0.0  # Platform y rotation
        self.theta_max = 0.3  # max 30 degree tilt
        self.delta_theta_max = 0.05  # max 5 degree change per step
        
    def update_state(self, dt):
        # Update velocities based on platform tilt
        ax = g * math.sin(self.theta_y)
        ay = -g * math.sin(self.theta_x)
        
        self.vx += ax * dt
        self.vy += ay * dt
        
        # Update positions
        self.x += self.vx * dt
        self.y += self.vy * dt
    
    def get_movement_direction(self):
        return math.atan2(self.vy, self.vx)
    
    def set_platform_rotation(self, theta_x, theta_y):
        self.theta_x = max(min(theta_x, self.theta_max), -self.theta_max)
        self.theta_y = max(min(theta_y, self.theta_max), -self.theta_max)
        
    def apply_continuous_action(self, action):
        """Absolute angle control"""
        theta_x = action[0] * self.theta_max
        theta_y = action[1] * self.theta_max
        self.set_platform_rotation(theta_x, theta_y)
        
    def apply_incremental_action(self, action):
        """Incremental angle changes"""
        delta_x = action[0] * self.delta_theta_max
        delta_y = action[1] * self.delta_theta_max
        new_theta_x = self.theta_x + delta_x
        new_theta_y = self.theta_y + delta_y
        self.set_platform_rotation(new_theta_x, new_theta_y)
```

## Reinforcement Learning Considerations

### State Space
- Ball position (x, y)
- Ball velocity (vx, vy)
- Platform angles (θx, θy)

### Action Space
Es gibt zwei grundlegende Ansätze für den Action Space:

1. **Kontinuierliche Aktionen (Continuous)**
   - Action Space: [-1, 1] für beide Achsen
   - Direkte Winkelsteuerung: Agent bestimmt absolute Winkel
   - Beispiel: action = [0.5, -0.3] → θx = 0.5 * θmax, θy = -0.3 * θmax

2. **Inkrementelle Aktionen (Incremental)**
   - Action Space: [-δθmax, +δθmax] für beide Achsen
   - Schrittweise Winkeländerung: Agent ändert current_angle += delta
   - Beispiel: action = [0.1, -0.1] → θx += 0.1, θy -= 0.1

Empfehlung: Der inkrementelle Ansatz ist oft besser geeignet, weil:
1. Smoother Bewegungen möglich
2. Realistischere Simulation der Plattform-Dynamik
3. Verhindert abrupte Winkeländerungen
4. Ähnlicher zur realen Stewart-Plattform Steuerung

### Reward Function
Possible components:
1. Distance to target position
2. Ball velocity (to encourage stability)
3. Platform angle magnitude (to minimize tilt)

### Terminal Conditions
1. Ball leaves the plate
2. Ball reaches target position and stabilizes
3. Maximum episode steps reached
