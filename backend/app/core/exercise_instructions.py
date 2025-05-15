class ExerciseInstructions:
    def __init__(self):
        self.instructions = {
            "push-up": {
                "steps": ["Start in plank position", "Lower your body", "Push back up"],
                "tips": ["Keep your back straight", "Elbows at 45 degrees"],
                "common_mistakes": ["Sagging hips", "Flaring elbows"]
            }
        }

    def get_instructions(self, exercise):
        if exercise not in self.instructions:
            raise ValueError(f"No instructions available for {exercise}")
        return self.instructions[exercise] 