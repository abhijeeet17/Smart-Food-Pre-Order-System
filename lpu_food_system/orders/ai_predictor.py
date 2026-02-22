"""
AI Demand Prediction Module
Uses Linear Regression to predict food demand based on historical data.
This helps stall owners prepare the right quantity in advance.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import datetime


class DemandPredictor:
    """
    Predicts food demand for a given food item, day, and time slot.

    Features used for prediction:
    - day_of_week: 0=Monday, 6=Sunday
    - time_slot_index: index of the break time slot
    - is_weekend: binary flag
    - week_number: week of the year
    """

    def __init__(self):
        self.model = LinearRegression()
        self.scaler = StandardScaler()
        self.is_trained = False

    def prepare_features(self, day_of_week, time_slot_index, week_number=None):
        """Convert input values into a feature vector for the model"""
        if week_number is None:
            week_number = datetime.date.today().isocalendar()[1]

        is_weekend = 1 if day_of_week >= 5 else 0

        # Feature engineering: interaction between day and slot
        day_slot_interaction = day_of_week * time_slot_index

        return np.array([[
            day_of_week,
            time_slot_index,
            is_weekend,
            week_number,
            day_slot_interaction
        ]])

    def train(self, demand_records):
        """
        Train the model on historical DemandRecord data.

        Args:
            demand_records: QuerySet of DemandRecord objects
        """
        if not demand_records.exists():
            self.is_trained = False
            return False

        # Build pandas DataFrame from queryset
        data = []
        for record in demand_records:
            data.append({
                'day_of_week': record.day_of_week,
                'time_slot_index': record.time_slot.id,
                'week_number': record.date.isocalendar()[1],
                'is_weekend': 1 if record.day_of_week >= 5 else 0,
                'day_slot_interaction': record.day_of_week * record.time_slot.id,
                'quantity': record.quantity_ordered
            })

        df = pd.DataFrame(data)

        if len(df) < 5:
            # Not enough data to train properly
            self.is_trained = False
            return False

        X = df[['day_of_week', 'time_slot_index', 'is_weekend', 'week_number', 'day_slot_interaction']]
        y = df['quantity']

        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        return True

    def predict(self, day_of_week, time_slot_index):
        """
        Predict demand for a specific day and time slot.

        Returns:
            int: Predicted number of orders (minimum 0)
        """
        if not self.is_trained:
            # Fallback: use a simple average estimation
            return self._fallback_prediction(day_of_week, time_slot_index)

        features = self.prepare_features(day_of_week, time_slot_index)
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)[0]
        return max(0, int(round(prediction)))

    def _fallback_prediction(self, day_of_week, time_slot_index):
        """
        Simple rule-based fallback when not enough training data exists.
        Based on typical campus food patterns.
        """
        # Lunch slots (index 2-3) tend to be busiest
        base = 20
        if time_slot_index in [2, 3]:
            base = 45
        elif time_slot_index == 1:
            base = 30

        # Weekdays are busier
        if day_of_week < 5:
            base = int(base * 1.3)

        return base

    def get_peak_slots(self, food_item_id, all_slots):
        """
        Returns slots ordered by predicted demand (highest first).
        Useful for showing peak times on dashboard.
        """
        today = datetime.date.today()
        day_of_week = today.weekday()

        slot_predictions = []
        for i, slot in enumerate(all_slots):
            predicted = self.predict(day_of_week, slot.id)
            slot_predictions.append({
                'slot': slot,
                'predicted_demand': predicted,
                'is_peak': predicted > 35
            })

        # Sort by predicted demand descending
        slot_predictions.sort(key=lambda x: x['predicted_demand'], reverse=True)
        return slot_predictions


def get_weekly_demand_chart_data(food_item):
    """
    Returns data for a Chart.js bar chart showing
    predicted demand across all 7 days of the week.
    """
    from orders.models import BreakTimeSlot

    predictor = DemandPredictor()

    try:
        from orders.models import DemandRecord
        records = DemandRecord.objects.filter(food_item=food_item)
        predictor.train(records)
    except Exception:
        pass

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    slots = list(BreakTimeSlot.objects.all())

    chart_data = {
        'labels': days,
        'datasets': []
    }

    colors = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
    ]

    for i, slot in enumerate(slots[:5]):
        dataset = {
            'label': str(slot),
            'data': [predictor.predict(day, slot.id) for day in range(7)],
            'backgroundColor': colors[i % len(colors)],
        }
        chart_data['datasets'].append(dataset)

    return chart_data


def update_demand_records():
    """
    Called daily (or via cron) to update DemandRecord
    with actual orders placed — feeds the AI training data.
    """
    from orders.models import Order, DemandRecord
    import datetime

    today = datetime.date.today()
    orders_today = Order.objects.filter(order_date=today)

    for order in orders_today:
        for item in order.items.all():
            record, created = DemandRecord.objects.get_or_create(
                food_item=item.food_item,
                date=today,
                time_slot=order.time_slot,
                defaults={
                    'day_of_week': today.weekday(),
                    'quantity_ordered': 0
                }
            )
            record.quantity_ordered += item.quantity
            record.save()
