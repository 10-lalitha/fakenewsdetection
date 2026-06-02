import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Load datasets
true_df = pd.read_csv('dataset/True.csv')
fake_df = pd.read_csv('dataset/Fake.csv')

# Add labels
true_df['label'] = 1
fake_df['label'] = 0

# Combine datasets
df = pd.concat([true_df, fake_df])
# Use text column
X = df['text']
y = df['label']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Convert text to numbers
vectorizer = TfidfVectorizer(stop_words='english')
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train model
model = LogisticRegression()
model.fit(X_train_vec, y_train)

# Accuracy
accuracy = model.score(X_test_vec, y_test)
print("Model Accuracy:", accuracy)

# Save model
pickle.dump(model, open('model/model.pkl', 'wb'))
pickle.dump(vectorizer, open('model/vectorizer.pkl', 'wb'))

print("Model trained successfully!")