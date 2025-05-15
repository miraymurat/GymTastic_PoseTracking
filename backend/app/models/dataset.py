import torch
from torch.utils.data import Dataset
import numpy as np
import cv2
import os
from typing import List, Tuple, Dict

class ExerciseDataset(Dataset):
    def __init__(self, root_dir: str, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.exercises = ['plank', 'squat']
        self.samples = []
        
        # Load dataset samples
        for exercise in self.exercises:
            exercise_dir = os.path.join(root_dir, exercise)
            if os.path.exists(exercise_dir):
                for filename in os.listdir(exercise_dir):
                    if filename.endswith('.mp4'):
                        self.samples.append({
                            'video_path': os.path.join(exercise_dir, filename),
                            'exercise': exercise,
                            'label': 1 if exercise == 'plank' else 0  # 1 for plank, 0 for squat
                        })
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        video_path = sample['video_path']
        
        # Read video frames
        cap = cv2.VideoCapture(video_path)
        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        
        # Convert frames to tensor
        frames = np.array(frames)
        if self.transform:
            frames = self.transform(frames)
        
        return {
            'frames': torch.FloatTensor(frames),
            'label': torch.LongTensor([sample['label']])[0],
            'exercise': sample['exercise']
        }

class RealTimePoseDetector:
    def __init__(self, model_path: str = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._load_model(model_path)
        self.transform = self._get_transform()
        
    def _load_model(self, model_path: str):
        # Load your trained PyTorch model here
        # This is a placeholder - you'll need to implement your actual model architecture
        model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=True)
        model.fc = torch.nn.Linear(model.fc.in_features, 2)  # 2 classes: plank and squat
        if model_path:
            model.load_state_dict(torch.load(model_path))
        model.to(self.device)
        model.eval()
        return model
    
    def _get_transform(self):
        # Define your data transforms here
        return torch.nn.Sequential(
            torch.nn.Linear(224 * 224 * 3, 512),
            torch.nn.ReLU(),
            torch.nn.Linear(512, 2)
        )
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """Process a single frame and return pose detection results"""
        # Preprocess frame
        frame = cv2.resize(frame, (224, 224))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = torch.FloatTensor(frame).permute(2, 0, 1).unsqueeze(0)
        frame = frame.to(self.device)
        
        # Get prediction
        with torch.no_grad():
            output = self.model(frame)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            
        return {
            'exercise_type': 'plank' if probabilities[1] > 0.5 else 'squat',
            'confidence': float(probabilities[1] if probabilities[1] > 0.5 else probabilities[0])
        } 