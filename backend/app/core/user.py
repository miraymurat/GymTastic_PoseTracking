import uuid
from datetime import datetime

class UserManager:
    def __init__(self):
        # In-memory storage (replace with database in production)
        self.users = {}

    def register_user(self, username, email, password):
        """Register a new user."""
        if email in [user["email"] for user in self.users.values()]:
            raise ValueError("Email already registered")
        
        user_id = str(uuid.uuid4())
        self.users[user_id] = {
            "username": username,
            "email": email,
            "password": password,  # In production, hash the password
            "created_at": datetime.now().isoformat()
        }
        return {"user_id": user_id, "username": username}

    def login_user(self, email, password):
        """Login a user."""
        for user_id, user in self.users.items():
            if user["email"] == email and user["password"] == password:
                return {"user_id": user_id, "username": user["username"]}
        raise ValueError("Invalid credentials")

    def get_user_profile(self, user_id):
        """Get user profile."""
        if user_id not in self.users:
            raise ValueError("User not found")
        user = self.users[user_id].copy()
        user.pop("password", None)  # Don't return password
        return user

    def start_workout(self, user_id, exercise_type):
        """Start a new workout session."""
        if user_id not in self.users:
            raise ValueError("User not found")
        
        session_id = str(uuid.uuid4())
        self.workouts[session_id] = {
            "user_id": user_id,
            "exercise_type": exercise_type,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration": 0,
            "reps": 0
        }
        return session_id

    def end_workout(self, user_id, session_id, duration, reps):
        """End a workout session."""
        if session_id not in self.workouts:
            raise ValueError("Workout session not found")
        
        workout = self.workouts[session_id]
        if workout["user_id"] != user_id:
            raise ValueError("Unauthorized")
        
        workout["end_time"] = datetime.now().isoformat()
        workout["duration"] = duration
        workout["reps"] = reps
        
        # Update progress
        if user_id not in self.progress:
            self.progress[user_id] = {}
        
        exercise_type = workout["exercise_type"]
        if exercise_type not in self.progress[user_id]:
            self.progress[user_id][exercise_type] = {
                "total_duration": 0,
                "total_reps": 0,
                "sessions": 0
            }
        
        progress = self.progress[user_id][exercise_type]
        progress["total_duration"] += duration
        progress["total_reps"] += reps
        progress["sessions"] += 1
        
        return workout

    def get_workout_history(self, user_id):
        """Get user's workout history."""
        if user_id not in self.users:
            raise ValueError("User not found")
        
        return [
            workout for workout in self.workouts.values()
            if workout["user_id"] == user_id
        ]

    def get_user_progress(self, user_id):
        """Get user's progress."""
        if user_id not in self.users:
            raise ValueError("User not found")
        
        return self.progress.get(user_id, {})

    def update_user_progress(self, user_id, stats):
        """Update user's progress."""
        if user_id not in self.users:
            raise ValueError("User not found")
        
        if user_id not in self.progress:
            self.progress[user_id] = {}
        
        for exercise_type, exercise_stats in stats.items():
            if exercise_type not in self.progress[user_id]:
                self.progress[user_id][exercise_type] = {
                    "total_duration": 0,
                    "total_reps": 0,
                    "sessions": 0
                }
            
            progress = self.progress[user_id][exercise_type]
            progress.update(exercise_stats)
        
        return self.progress[user_id] 