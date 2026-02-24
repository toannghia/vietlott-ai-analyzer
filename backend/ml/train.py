import asyncio
import os
import logging
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from sqlalchemy import select, desc
from app.core.database import async_session
from app.models.draw_result import DrawResult
from app.models.number_stat import NumberStat
import joblib
from sklearn.ensemble import RandomForestRegressor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_model_path(lottery_type: str, model_name: str, ext: str):
    return os.path.join(os.path.dirname(__file__), f"lottery_{model_name}_{lottery_type}.{ext}")

# 1. FETCH DATA
async def fetch_dataset(lottery_type: str, limit=None):
    async with async_session() as db:
        query = select(DrawResult).where(DrawResult.type == lottery_type).order_by(desc(DrawResult.draw_date))
        if limit:
            query = query.limit(limit)
        result = await db.execute(query)
        draws = result.scalars().all()
        logger.info(f"Đã lấy TOÀN BỘ dữ liệu lịch sử ({len(draws)} kỳ quay) cho {lottery_type} để huấn luyện Ensemble.")
    if not draws:
        return []
    draws = list(reversed(draws))
    dataset = [d.numbers[:6] for d in draws]
    return dataset

# 2. LSTM PREDICTOR
class LSTMPredictor:
    def __init__(self, lottery_type="mega645", sequence_length=10):
        self.lottery_type = lottery_type
        self.sequence_length = sequence_length
        self.num_classes = 55 if lottery_type == "power655" else 45
        self.model = None

    def prepare_data(self, dataset):
        X, y = [], []
        encoded_dataset = []
        for draw in dataset:
            vec = np.zeros(self.num_classes)
            for num in draw:
                if 1 <= num <= self.num_classes:
                    vec[num - 1] = 1.0
            encoded_dataset.append(vec)
        encoded_dataset = np.array(encoded_dataset)
        for i in range(len(encoded_dataset) - self.sequence_length):
            X.append(encoded_dataset[i : i + self.sequence_length])
            y.append(encoded_dataset[i + self.sequence_length])
        return np.array(X), np.array(y)

    def build_model(self):
        model = keras.Sequential([
            keras.layers.Input(shape=(self.sequence_length, self.num_classes)),
            keras.layers.LSTM(128, return_sequences=True),
            keras.layers.Dropout(0.3),
            keras.layers.LSTM(64, return_sequences=True),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(64),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(self.num_classes, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        self.model = model
        return model

    def train_model(self, dataset, epochs=50, batch_size=32):
        logger.info(f"Training LSTM for {self.lottery_type}...")
        if len(dataset) < self.sequence_length + 5:
            logger.warning("Not enough data to train LSTM.")
            return False
        X, y = self.prepare_data(dataset)
        if self.model is None:
            self.build_model()
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)
        path = get_model_path(self.lottery_type, "lstm", "keras")
        self.model.save(path)
        logger.info(f"LSTM Model saved to {path}")
        return True

# 3. RANDOM FOREST PREDICTOR
class RandomForestPredictor:
    def __init__(self, lottery_type="mega645"):
        self.lottery_type = lottery_type
        self.num_classes = 55 if lottery_type == "power655" else 45
        self.model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
        
    def prepare_data(self, dataset):
        X, y = [], []
        for i in range(1, len(dataset)):
            prev_draw = dataset[i-1]
            curr_draw = dataset[i]
            
            vec = np.zeros(self.num_classes)
            for num in prev_draw:
                if 1 <= num <= self.num_classes: vec[num - 1] = 1.0
            
            t_sum = sum(prev_draw)
            odd_count = sum(1 for n in prev_draw if n % 2 != 0)
            
            features = np.concatenate([vec, [t_sum, odd_count]])
            X.append(features)
            
            target = np.zeros(self.num_classes)
            for num in curr_draw:
                if 1 <= num <= self.num_classes: target[num - 1] = 1.0
            y.append(target)
            
        return np.array(X), np.array(y)
        
    def train_model(self, dataset):
        logger.info(f"Training Random Forest for {self.lottery_type}...")
        if len(dataset) < 10: return False
        X, y = self.prepare_data(dataset)
        self.model.fit(X, y)
        path = get_model_path(self.lottery_type, "rf", "joblib")
        joblib.dump(self.model, path)
        logger.info(f"Random Forest Model saved to {path}")
        return True

# 4. MARKOV CHAIN PREDICTOR
class MarkovChainPredictor:
    def __init__(self, lottery_type="mega645"):
        self.lottery_type = lottery_type
        self.num_classes = 55 if lottery_type == "power655" else 45
        self.transition_matrix = np.zeros((self.num_classes, self.num_classes))
        
    def train_model(self, dataset):
        logger.info(f"Training Markov Chain for {self.lottery_type}...")
        for i in range(1, len(dataset)):
            prev_draw = dataset[i-1]
            curr_draw = dataset[i]
            for p_num in prev_draw:
                for c_num in curr_draw:
                    if 1 <= p_num <= self.num_classes and 1 <= c_num <= self.num_classes:
                        self.transition_matrix[p_num-1][c_num-1] += 1
                        
        row_sums = self.transition_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        self.transition_matrix = self.transition_matrix / row_sums
        
        path = get_model_path(self.lottery_type, "markov", "json")
        with open(path, 'w') as f:
            json.dump(self.transition_matrix.tolist(), f)
        logger.info(f"Markov Chain Model saved to {path}")
        return True

async def main():
    import sys
    ltype = sys.argv[1] if len(sys.argv) > 1 else "mega645"
    epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    dataset = await fetch_dataset(ltype)
    
    # Train Ensemble
    lstm = LSTMPredictor(lottery_type=ltype)
    lstm.train_model(dataset, epochs=epochs)
    
    rf = RandomForestPredictor(lottery_type=ltype)
    rf.train_model(dataset)
    
    mc = MarkovChainPredictor(lottery_type=ltype)
    mc.train_model(dataset)
    
    logger.info(f"Ensemble training completed for {ltype}.")

if __name__ == "__main__":
    asyncio.run(main())
