import json
import os
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 1. SETUP PATHS
current_dir = os.path.dirname(__file__)
data_path = os.path.join(current_dir, 'training_data.json')
save_dir = os.path.join(current_dir, 'agent')
model_path = os.path.join(save_dir, 'custom_model.pkl')

# 2. LOAD DATA
if not os.path.exists(data_path):
    print(f"❌ Error: Could not find {data_path}")
    exit()

print("📂 Loading Big Data Set...")
with open(data_path, 'r') as f:
    data = json.load(f)

texts = [item['text'] for item in data]
labels = [item['label'] for item in data]
print(f"📊 Found {len(texts)} training examples.")

# 3. SPLIT DATA (Train vs Test)
# We keep 20% of data hidden to test if the model actually learned
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

# 4. BUILD THE BRAIN (Pipeline)
# CountVectorizer: Converts words ("bat", "ball") into numbers
# MultinomialNB: The algorithm that finds patterns in those numbers
model = make_pipeline(CountVectorizer(), MultinomialNB())

# 5. TRAIN!
print("🧠 Training the Custom Module...")
model.fit(X_train, y_train)

# 6. EVALUATE
if len(X_test) > 0:
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"✅ Training Complete! Accuracy on test data: {accuracy * 100:.2f}%")
else:
    print("✅ Training Complete! (Not enough data for test split yet)")

# 7. SAVE THE BRAIN
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print(f"💾 Trained Module saved to: {model_path}")