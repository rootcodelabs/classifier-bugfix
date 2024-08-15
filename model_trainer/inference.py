from transformers import XLMRobertaTokenizer, XLMRobertaForSequenceClassification,Trainer, TrainingArguments, DistilBertTokenizer, DistilBertForSequenceClassification, BertForSequenceClassification, BertTokenizer
import pickle
import torch
import os
import torch.nn.functional as F
from transformers import logging
import warnings
warnings.filterwarnings("ignore", message="Some weights of the model checkpoint were not used when initializing")
logging.set_verbosity_error()

class InferencePipeline:
    
    def __init__(self, hierarchy_file, model_name, results_folder):
        
        self.hierarchy_file = hierarchy_file
            
        with open(f"{results_folder}/models_dets.pkl", 'rb') as file:
            self.models = pickle.load(file)
            
        if model_name == 'distil-bert':
            self.base_model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased')
            self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        
        elif model_name == 'roberta':
            self.base_model = XLMRobertaForSequenceClassification.from_pretrained('xlm-roberta-base')
            self.tokenizer = XLMRobertaTokenizer.from_pretrained('xlm-roberta-base')
        
        elif model_name == 'bert':
            self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
            self.base_model = BertForSequenceClassification.from_pretrained('bert-base-uncased')

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        
        label_encoder_names = os.listdir(f"{results_folder}/saved_label_encoders")
        label_encoder_names = sorted(label_encoder_names, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        self.label_encoder_dict = {}
        for i in range(len(label_encoder_names)):
            with open(os.path.join(f"{results_folder}/saved_label_encoders",label_encoder_names[i]), 'rb') as file:
                self.label_encoder_dict[i] = pickle.load(file)

        model_names = os.listdir(f"{results_folder}/saved_models")
        model_names = sorted(model_names, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        self.models_dict = {}
        for i in range(len(model_names)):
            self.models_dict[i] = torch.load(os.path.join(f"{results_folder}/saved_models",model_names[i]))

        classification_model_names = os.listdir(f"{results_folder}/classifiers")
        classification_model_names = sorted(classification_model_names, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        self.classification_models_dict = {}
        for i in range(len(classification_model_names)):
            self.classification_models_dict[i] = torch.load(os.path.join(f"{results_folder}/classifiers",classification_model_names[i]))
    
    def find_index(self, data, search_dict):
        for index, d in enumerate(data):
            if d == search_dict:
                return index
        return None
    
    def predict_class(self,text_input):
        inputs = self.tokenizer(text_input, truncation=True, padding=True, return_tensors='pt')
        inputs.to(self.device)
        inputs = {key: val.to(self.device) for key, val in inputs.items()}
        predicted_classes = []
        probabilities = []
        self.base_model.to(self.device)
        i = 0
        data = self.hierarchy_file['classHierarchy']
        parent = 1
        while data:
            current_classes = {parent: [d['class'] for d in data]}
            model_num = self.find_index(self.models, current_classes)
            if model_num is None:
                break
            label_encoder = self.label_encoder_dict[model_num]
            num_labels = len(label_encoder.classes_)
            
            if self.model_name == 'distil-bert':
                self.base_model.classifier = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased',  num_labels=num_labels).classifier
                self.base_model.distilbert.transformer.layer[-2:].load_state_dict(self.models_dict[model_num])
                
            elif self.model_name == 'roberta':
                self.base_model.classifier = XLMRobertaForSequenceClassification.from_pretrained('xlm-roberta-base', num_labels=num_labels).classifier
                self.base_model.roberta.encoder.layer[-2:].load_state_dict(self.models_dict[model_num])
                
            elif self.model_name == 'bert':
                self.base_model.classifier = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=num_labels).classifier
                self.base_model.base_model.encoder.layer[-2:].load_state_dict(self.models_dict[model_num])
                
            self.base_model.classifier.load_state_dict(self.classification_models_dict[model_num])
            self.base_model.to(self.device)
            with torch.no_grad():
                outputs = self.base_model(**inputs)
                probability = F.softmax(outputs.logits, dim=1)
                predictions = torch.argmax(outputs.logits, dim=1)
                predicted_probabilities = probability.gather(1, predictions.unsqueeze(1)).squeeze()
                if int(predicted_probabilities.cpu().item()*100)<80:
                    return [],[]
                probabilities.append(int(predicted_probabilities.cpu().item()*100))

            predicted_label = label_encoder.inverse_transform(predictions.cpu().numpy())
            predicted_classes.append(predicted_label[0])

            data = next((item for item in data if item['class'] == predicted_label), None)
            parent = predicted_label[0]
            if not data:
                break

            while data['subclasses'] and len(data['subclasses']) <= 1:
                if data['subclasses']:
                    predicted_classes.append(data['subclasses'][0]['class'])
                    parent = data['subclasses'][0]['class']
                    data = data['subclasses'][0]
                else:
                    data = None
                    break

            if not data['subclasses']:
                break

            if not data:
                break

            data = data['subclasses']

        return predicted_classes, probabilities
    
    def user_corrected_probabilities(self, text_input, user_classes):
        inputs = self.tokenizer(text_input, truncation=True, padding=True, return_tensors='pt')
        inputs.to(self.device)
        inputs = {key: val.to(self.device) for key, val in inputs.items()}
        predicted_classes = []
        user_class_probabilities = []
        real_predicted_probabilities = []
        self.base_model.to(self.device)
        i = 0
        data = self.hierarchy_file['classHierarchy']
        parent = 1

        for i in range(len(user_classes)):
            current_classes = {parent: [d['class'] for d in data]}
            model_num = self.find_index(self.models, current_classes)
            if model_num is None:
                break
            label_encoder = self.label_encoder_dict[model_num]
            num_labels = len(label_encoder.classes_)

            if self.model_name == 'distil-bert':
                self.base_model.classifier = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased',  num_labels=num_labels).classifier
                self.base_model.distilbert.transformer.layer[-2:].load_state_dict(self.models_dict[model_num])

            elif self.model_name == 'roberta':
                self.base_model.classifier = XLMRobertaForSequenceClassification.from_pretrained('xlm-roberta-base', num_labels=num_labels).classifier
                self.base_model.roberta.encoder.layer[-2:].load_state_dict(self.models_dict[model_num])

            elif self.model_name == 'bert':
                self.base_model.classifier = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=num_labels).classifier
                self.base_model.base_model.encoder.layer[-2:].load_state_dict(self.models_dict[model_num])

            self.base_model.classifier.load_state_dict(self.classification_models_dict[model_num])
            self.base_model.to(self.device)

            with torch.no_grad():
                outputs = self.base_model(**inputs)
                probability = F.softmax(outputs.logits, dim=1)

                user_class_index = label_encoder.transform([user_classes[i]])[0]

                user_class_probability = probability[:, user_class_index].item()
                user_class_probabilities.append(int(user_class_probability * 100))

                predictions = torch.argmax(outputs.logits, dim=1)
                real_predicted_probabilities.append(int(probability.gather(1, predictions.unsqueeze(1)).squeeze().cpu().item() * 100))

                predicted_label = label_encoder.inverse_transform(predictions.cpu().numpy())
                predicted_classes.append(predicted_label[0])

            data = next((item for item in data if item['class'] == user_classes[i]), None)
            parent = user_classes[i]
            if not data:
                break

            while data['subclasses'] and len(data['subclasses']) <= 1:
                if data['subclasses']:
                    parent = data['subclasses'][0]['class']
                    data = data['subclasses'][0]
                else:
                    data = None
                    break

            if not data['subclasses']:
                break

            if not data:
                break

            data = data['subclasses']

        return user_class_probabilities
