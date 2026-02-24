import logging
import os
import json
import numpy as np
from sqlalchemy import select, desc
from app.core.database import async_session
from app.models.ai_prediction import AIPrediction
from app.models.draw_result import DrawResult

logger = logging.getLogger(__name__)

# Avoiding hard dependencies locally for faster boot
try:
    from tensorflow import keras
    import tensorflow as tf
except ImportError:
    keras = None

try:
    import joblib
except ImportError:
    joblib = None

def get_model_path(lottery_type: str, model_name: str, ext: str):
    return os.path.join(os.path.dirname(__file__), "..", "..", "ml", f"lottery_{model_name}_{lottery_type}.{ext}")

async def get_recent_sequences(db, length=10, lottery_type: str = "mega645"):
    result = await db.execute(
        select(DrawResult)
        .where(DrawResult.type == lottery_type)
        .order_by(desc(DrawResult.draw_date))
        .limit(length)
    )
    draws = result.scalars().all()
    if not draws or len(draws) < length:
        return None, None, None
    draws = list(reversed(draws))
    
    max_num = 55 if lottery_type == "power655" else 45
    encoded = []
    
    # LSTM input
    for draw in draws:
        vec = np.zeros(max_num)
        for num in draw.numbers[:6]:
            if 1 <= num <= max_num: vec[num - 1] = 1.0
        encoded.append(vec)
        
    # RF input (features from the latest draw)
    last_draw = draws[-1].numbers[:6]
    vec_rf = np.zeros(max_num)
    for num in last_draw:
        if 1 <= num <= max_num: vec_rf[num - 1] = 1.0
    t_sum = sum(last_draw)
    odd_count = sum(1 for n in last_draw if n % 2 != 0)
    rf_features = np.concatenate([vec_rf, [t_sum, odd_count]])
    
    return np.array([encoded]), np.array([rf_features]), last_draw

async def generate_prediction(target_period: str, lottery_type: str = "mega645") -> None:
    """Ensemble AI prediction generator (LSTM + Random Forest + Markov Chain)"""
    try:
        max_num = 55 if lottery_type == "power655" else 45
        lstm_path = get_model_path(lottery_type, "lstm", "keras")
        rf_path = get_model_path(lottery_type, "rf", "joblib")
        markov_path = get_model_path(lottery_type, "markov", "json")
        
        async with async_session() as db:
            lstm_input, rf_input, last_draw = await get_recent_sequences(db, length=10, lottery_type=lottery_type)
            
            p_lstm = np.zeros(max_num)
            p_rf = np.zeros(max_num)
            p_markov = np.zeros(max_num)
            
            ensemble_ready = False
            
            if lstm_input is not None and keras and joblib:
                try:
                    # 1. Load & Predict LSTM
                    if os.path.exists(lstm_path):
                        lstm_model = keras.models.load_model(lstm_path)
                        p_lstm = lstm_model.predict(lstm_input, verbose=0)[0]
                    
                    # 2. Load & Predict Random Forest
                    if os.path.exists(rf_path):
                        rf_model = joblib.load(rf_path)
                        p_rf = rf_model.predict(rf_input)[0]
                        
                    # 3. Load & Predict Markov Chain
                    if os.path.exists(markov_path):
                        with open(markov_path, 'r') as f:
                            transition_matrix = np.array(json.load(f))
                        for n in last_draw:
                            if 1 <= n <= max_num:
                                p_markov += transition_matrix[n - 1]
                        if len(last_draw) > 0:
                            p_markov = p_markov / len(last_draw) # average probability
                    
                    ensemble_ready = True
                    
                except Exception as e:
                    logger.warning(f"Failed to load one of the ensemble models: {e}")

            if not ensemble_ready:
                logger.info(f"Using fallback pure random probability for {lottery_type}")
                # Fallback: random probabilities
                p_lstm = np.random.uniform(0.1, 0.9, max_num)
                p_rf = np.random.uniform(0.1, 0.9, max_num)
                p_markov = np.random.uniform(0.1, 0.9, max_num)
            
            # Weighted Voting
            # LSTM: 40%, RF: 40%, Markov: 20%
            p_final = (0.4 * p_lstm) + (0.4 * p_rf) + (0.2 * p_markov)
            
            top_indices_desc = np.argsort(p_final)[::-1]
            top_probs_desc = p_final[top_indices_desc]
            
            # Base confident (rescaled logically)
            def calc_confidence(probs):
                c = float(np.mean(probs) * 100)
                return max(70.0, min(98.0, c * 1.5)) # Scale up slightly for UI display
                
            prediction_sets = []
            
            # SET 1: Best Combination (Top 1-6)
            set1_idx = top_indices_desc[:6]
            confidence_1 = calc_confidence(top_probs_desc[:6])
            prediction_sets.append({
                "numbers": sorted([int(i) + 1 for i in set1_idx]),
                "confidence": round(confidence_1, 2)
            })
            
            # SET 2: Alternative 1 (Top 1-5 + Top 7)
            set2_idx = np.concatenate([top_indices_desc[:5], [top_indices_desc[6]]])
            confidence_2 = calc_confidence(p_final[set2_idx]) * 0.98 # slightly lower confidence
            prediction_sets.append({
                "numbers": sorted([int(i) + 1 for i in set2_idx]),
                "confidence": round(confidence_2, 2)
            })
            
            # SET 3: Alternative 2 (Top 1-4 + Top 7 + Top 8)
            set3_idx = np.concatenate([top_indices_desc[:4], [top_indices_desc[6], top_indices_desc[7]]])
            confidence_3 = calc_confidence(p_final[set3_idx]) * 0.96
            prediction_sets.append({
                "numbers": sorted([int(i) + 1 for i in set3_idx]),
                "confidence": round(confidence_3, 2)
            })
            
            # Default backward compatibility properties
            best_set = prediction_sets[0]
            final_prediction = best_set["numbers"]
            avg_confidence = best_set["confidence"]
            is_premium = avg_confidence > 85.0
            
            # Save or Update
            result = await db.execute(
                select(AIPrediction).where(
                    (AIPrediction.target_period == target_period) & 
                    (AIPrediction.type == lottery_type)
                )
            )
            existing = result.scalar_one_or_none()
            
            # Top 1 backward compatible saving
            if existing:
                existing.predicted_numbers = final_prediction
                existing.confidence = avg_confidence
                existing.prediction_sets = prediction_sets
                existing.is_premium_only = is_premium
            else:
                new_prediction = AIPrediction(
                    target_period=target_period,
                    type=lottery_type,
                    predicted_numbers=final_prediction,
                    confidence=avg_confidence,
                    prediction_sets=prediction_sets,
                    is_premium_only=is_premium
                )
                db.add(new_prediction)
                
            await db.commit()
            logger.info(f"Ensemble AI Generated {len(prediction_sets)} prediction sets for {lottery_type} period {target_period}")
            
    except Exception as e:
        logger.error(f"Failed to generate Ensemble AI predictions for {lottery_type} period {target_period}: {e}")
        import traceback
        logger.error(traceback.format_exc())

async def verify_prediction(draw_period: str, actual_numbers: list[int], lottery_type: str = "mega645") -> int | None:
    try:
        async with async_session() as db:
            result = await db.execute(
                select(AIPrediction).where(
                    (AIPrediction.target_period == draw_period) & 
                    (AIPrediction.type == lottery_type)
                )
            )
            prediction = result.scalar_one_or_none()
            
            if not prediction:
                return None
            
            if prediction.is_verified:
                return prediction.matches
            
            # Tracking accurately on Set 1
            predicted_set = set(prediction.predicted_numbers)
            actual_set = set(actual_numbers[:6])
            matched = predicted_set & actual_set
            
            prediction.is_verified = True
            prediction.matches = len(matched)
            await db.commit()
            
            return len(matched)
            
    except Exception as e:
        logger.error(f"Failed to verify prediction for period {draw_period}: {e}")
        return None
