import pandas as pd

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

from pytorch_tabnet.tab_model import TabNetClassifier

import pickle



# Load dataset

data = pd.read_csv(
    "dataset/soil_data.csv"
)



# Features

X = data[
    [
        "nitrogen",
        "phosphorus",
        "potassium",
        "moisture",
        "temperature"
    ]
]



# Target

y = data["soil_health"]



# Convert labels

encoder = LabelEncoder()

y = encoder.fit_transform(y)



# Split data

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,
    test_size=0.2,
    random_state=42

)



# Create TabNet model

model = TabNetClassifier()



# Train

model.fit(

    X_train.values,
    y_train,

    eval_set=[
        (
            X_test.values,
            y_test
        )
    ],

    max_epochs=50,

    patience=10

)



# Save model

model.save_model(
    "app/ml_models/soil_tabnet_model"
)



# Save encoder

with open(
    "app/ml_models/soil_encoder.pkl",
    "wb"
) as f:

    pickle.dump(
        encoder,
        f
    )



print("Soil TabNet model trained successfully")