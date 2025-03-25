"""
Fingerprint feature extraction model using MobileNetV2.
"""

import tensorflow as tf
from tensorflow.keras import layers, Model
from typing import Tuple, Optional
import numpy as np
from loguru import logger
import cv2

class FingerprintModel:
    def __init__(self,
                 input_shape: Tuple[int, int, int] = (224, 224, 1),
                 feature_dim: int = 512,
                 dropout_rate: float = 0.5):
        """
        Initialize the fingerprint model.
        
        Args:
            input_shape: Input shape (height, width, channels)
            feature_dim: Dimension of the output feature vector
            dropout_rate: Dropout rate for regularization
        """
        self.input_shape = input_shape
        self.feature_dim = feature_dim
        self.dropout_rate = dropout_rate
        self.model = self._build_model()
        
    def _build_model(self) -> Model:
        """
        Build the MobileNetV2-based model for fingerprint feature extraction.
        
        Returns:
            Compiled Keras model
        """
        try:
            # Load pre-trained MobileNetV2
            base_model = tf.keras.applications.MobileNetV2(
                input_shape=self.input_shape,
                include_top=False,
                weights='imagenet'
            )
            
            # Freeze the base model layers
            base_model.trainable = False
            
            # Create the model
            inputs = layers.Input(shape=self.input_shape)
            
            # Preprocess input (normalize to [-1, 1])
            x = layers.Lambda(
                lambda x: (x - 0.5) * 2.0
            )(inputs)
            
            # Apply base model
            x = base_model(x)
            
            # Global average pooling
            x = layers.GlobalAveragePooling2D()(x)
            
            # Add dense layers for feature extraction
            x = layers.Dense(1024, activation='relu')(x)
            x = layers.BatchNormalization()(x)
            x = layers.Dropout(self.dropout_rate)(x)
            
            x = layers.Dense(512, activation='relu')(x)
            x = layers.BatchNormalization()(x)
            x = layers.Dropout(self.dropout_rate)(x)
            
            # Output layer
            outputs = layers.Dense(self.feature_dim, activation='linear')(x)
            
            # Create and compile model
            model = Model(inputs=inputs, outputs=outputs)
            model.compile(
                optimizer='adam',
                loss='mse',
                metrics=['mae']
            )
            
            return model
            
        except Exception as e:
            logger.error(f"Error building model: {str(e)}")
            raise
            
    def extract_features(self, image: np.ndarray) -> np.ndarray:
        """
        Extract features from a preprocessed fingerprint image.
        
        Args:
            image: Preprocessed fingerprint image
            
        Returns:
            Feature vector
        """
        try:
            # Ensure correct shape
            if len(image.shape) == 2:
                image = np.expand_dims(image, axis=-1)
            if len(image.shape) == 3 and image.shape[-1] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                image = np.expand_dims(image, axis=-1)
                
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            
            # Extract features
            features = self.model.predict(image, verbose=0)
            
            # Normalize features
            features = features / np.linalg.norm(features)
            
            return features[0]
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            raise
            
    def compute_similarity(self, 
                          features1: np.ndarray, 
                          features2: np.ndarray) -> float:
        """
        Compute cosine similarity between two feature vectors.
        
        Args:
            features1: First feature vector
            features2: Second feature vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Ensure vectors are normalized
            features1 = features1 / np.linalg.norm(features1)
            features2 = features2 / np.linalg.norm(features2)
            
            # Compute cosine similarity
            similarity = np.dot(features1, features2)
            
            # Convert to [0, 1] range
            similarity = (similarity + 1) / 2
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error computing similarity: {str(e)}")
            raise
            
    def save_model(self, path: str):
        """
        Save the model to disk.
        
        Args:
            path: Path to save the model
        """
        try:
            self.model.save(path)
            logger.info(f"Model saved to {path}")
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
            
    def load_model(self, path: str):
        """
        Load a model from disk.
        
        Args:
            path: Path to the saved model
        """
        try:
            self.model = tf.keras.models.load_model(path)
            logger.info(f"Model loaded from {path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise 