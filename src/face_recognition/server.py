import os
import torch
from flask import Flask, request, jsonify
from torchvision import transforms, models, datasets
from PIL import Image
import torch.nn as nn

app = Flask(__name__)

def load_model(model_path, num_classes):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    weights = models.ResNet18_Weights.DEFAULT
    model = models.resnet18(weights=weights)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    model = model.to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model

def preprocess_image(image):
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    image = preprocess(image).unsqueeze(0)
    return image

def predict(model, image_tensor):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    image_tensor = image_tensor.to(device)
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, preds = torch.max(probabilities, 1)
    return confidence.item(), preds.item()

@app.route('/predict', methods=['POST'])
def predict_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file:
        image = Image.open(file.stream)
        image_tensor = preprocess_image(image)
        confidence, prediction = predict(model, image_tensor)

        result = {'prediction': class_names[prediction], 'confidence': confidence}
        return jsonify(result)

if __name__ == '__main__':
    data_dir = 'train_data' 
    data_transforms = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    full_dataset = datasets.ImageFolder(data_dir, transform=data_transforms)
    class_names = full_dataset.classes

    model_path = 'best_model.pth'
    model = load_model(model_path, len(class_names))

    app.run(host='0.0.0.0', port=5000)
