# 📰 Fake News Detection System

A machine learning-powered Flask web application that detects fake news using Natural Language Processing (NLP) and Logistic Regression. The system features user authentication, prediction history tracking, and an admin dashboard for analytics.

## 🌟 Features

### Core Functionality
- **Fake News Detection**: Analyzes news articles and classifies them as Real or Fake
- **ML-Powered**: Uses TF-IDF vectorization with Logistic Regression for accurate predictions
- **User Authentication**: Secure login/registration system with session management
- **Prediction History**: Track all predictions with timestamps and results
- **Admin Dashboard**: Monitor system statistics and manage users

### User Features
- Register new account with username/password
- Login with credentials
- Submit news articles for analysis
- View prediction history with confidence metrics
- Personal statistics (total predictions, real vs. fake count)

### Admin Features
- View all registered users
- Add/delete users from system
- View global statistics (total real/fake predictions)
- System-wide analytics dashboard

## 📋 Requirements

- Python 3.8+
- Flask 2.0+
- scikit-learn 1.0+
- pandas
- SQLite3

See `requirements.txt` for all dependencies with versions.

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/10-lalitha/fakenewsdetection.git
   cd fakenewsdetection
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the app**
   - Open browser and navigate to `http://localhost:5000`
   - Default admin credentials: `username: admin, password: admin`

## 🏗️ Project Architecture

```
fakenewsdetection/
├── app.py                          # Main Flask application
├── train.py                        # Model training script
├── requirements.txt                # Python dependencies
├── database.db                     # SQLite database
├── model/
│   ├── model.pkl                   # Trained ML model
│   └── vectorizer.pkl              # TF-IDF vectorizer
├── dataset/
│   ├── True.csv                    # Authentic news articles
│   └── Fake.csv                    # Fake news articles
└── templates/
    ├── index.html                  # Home/prediction page
    ├── login.html                  # Login form
    ├── register.html               # Registration form
    ├── dashboard.html              # User dashboard
    └── admin.html                  # Admin panel
```

## 📁 Directory Structure Details

### Flask Application (app.py)
- **Routes**: Home, Register, Login, Dashboard, Predict, Admin, Add User, Delete User, Logout
- **Database**: SQLite with two tables - `users` and `history`
- **Session Management**: Flask sessions for user authentication

### Model Training (train.py)
- **Data Source**: True.csv (21,417 articles) + Fake.csv (23,481 articles)
- **Vectorization**: TF-IDF (Term Frequency-Inverse Document Frequency)
- **Algorithm**: Logistic Regression
- **Output**: Trained model.pkl and vectorizer.pkl

### Templates
- Responsive HTML pages with CSS styling
- Gradient backgrounds and modern UI
- Form validation and error handling

## 🤖 Machine Learning Model

### Algorithm: Logistic Regression
- **Input**: News article text
- **Processing**: TF-IDF Vectorization with English stop words removal
- **Output**: Binary classification (Real=1, Fake=0)
- **Accuracy**: ~95% on test dataset

### Training Pipeline
1. Load True.csv and Fake.csv datasets
2. Add labels (1 for true, 0 for fake)
3. Combine datasets and split (80% train, 20% test)
4. Vectorize text using TF-IDF
5. Train Logistic Regression model
6. Save model and vectorizer as pickle files

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
```

### History Table
```sql
CREATE TABLE history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    news TEXT,
    result TEXT
)
```

## 📊 API Endpoints

| Method | Route | Purpose |
|--------|-------|---------|
| GET | `/` | Home page |
| GET/POST | `/register` | User registration |
| GET/POST | `/login` | User login |
| GET | `/dashboard` | User dashboard with history |
| POST | `/predict` | Submit news for prediction |
| GET | `/admin` | Admin dashboard |
| POST | `/add_user` | Add new user (admin only) |
| GET | `/delete_user/<id>` | Delete user (admin only) |
| GET | `/logout` | User logout |

## 🔐 Security Considerations

### Current Implementation
- Session-based authentication
- Password storage in database
- Admin panel access control

### ⚠️ Security Issues (TODO)
- **Password Hashing**: Implement bcrypt or werkzeug.security
- **SQL Injection**: Already using parameterized queries ✓
- **CSRF Protection**: Add Flask-WTF for CSRF tokens
- **HTTPS**: Enable SSL/TLS in production
- **Input Validation**: Add data validation on user inputs
- **Rate Limiting**: Implement request rate limiting

## 📦 Dependencies

```
Flask==2.3.2
scikit-learn==1.3.0
pandas==2.0.3
numpy==1.24.3
```

## 🚢 Deployment

### Render Deployment Guide
See `DEPLOYMENT_GUIDE.md` for detailed Render deployment instructions.

### Quick Deployment Steps
1. Push code to GitHub repository
2. Create new Web Service on Render
3. Connect GitHub repository
4. Set environment variables
5. Deploy and monitor logs

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

See `TESTING.md` for comprehensive testing documentation.

## 📝 Usage Examples

### For Users
1. Create an account at `/register`
2. Login with credentials
3. Navigate to home page
4. Enter a news article in the text area
5. Click "Predict" to get classification
6. View your prediction history in dashboard

### For Administrators
1. Login with admin credentials
2. Navigate to `/admin`
3. View system statistics
4. Manage users (add/delete)
5. Monitor prediction trends

## 📈 Model Performance

- **Accuracy**: 95%+ on test dataset
- **Training Time**: < 5 seconds
- **Prediction Time**: < 100ms per article
- **Dataset Size**: 44,898 articles (21,417 true + 23,481 fake)

## 🐛 Known Issues

- [ ] No password hashing implemented
- [ ] No email verification on registration
- [ ] Limited input validation
- [ ] No rate limiting on predictions
- [ ] No logging system

## 🛠️ Development

### Training a New Model
```bash
python train.py
```

This will:
1. Load datasets from `dataset/` folder
2. Train new model on combined data
3. Save updated model.pkl and vectorizer.pkl

### Database Reset
```python
import os
os.remove('database.db')
# Restart app to recreate database
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Testing Documentation](TESTING.md)
- [Architecture Overview](ARCHITECTURE.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

**Lalitha** - [GitHub Profile](https://github.com/10-lalitha)

## 📞 Support

For issues and questions, please open a GitHub issue in the repository.

---

**Last Updated**: June 2026
