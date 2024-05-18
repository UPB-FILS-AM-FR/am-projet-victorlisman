# test.py
import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from model import FaceRecognitionModel

# Hyperparameters
batch_size = 32
num_classes = 10 

# Data transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Datasets and dataloaders
test_dataset = datasets.ImageFolder(root='path/to/test', transform=transform)
test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False)

# Model
model = FaceRecognitionModel(num_classes=num_classes)
model.load_state_dict(torch.load('face_recognition_model.pth'))
model.eval()

# Testing loop
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

correct = 0
total = 0

with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

accuracy = 100 * correct / total
print(f'Accuracy: {accuracy:.2f}%')
