from telemetry_generator import generate_telemetry
from preprocessing import preprocess
from online_model import OnlineModel


def main():
    # Generate telemetry data (no anomalies for baseline)
    telemetry_data = generate_telemetry(num_points=100, anomaly=False)

    # Initialize online model
    model = OnlineModel(target="latency_norm")

    # Stream data one by one
    for i, row in telemetry_data.iterrows():
        x = row.to_dict()
        x_processed = preprocess(x)  # Optional preprocessing

        # Keep original latency value for comparison
        true_value = x_processed["latency_norm"]
        prediction = model.predict(x_processed)

        # Fit model
        model.partial_fit(x_processed)

        # Print info
        print(
            f"[{i}] Predicted: {prediction:.2f}, True: {true_value:.2f}, MAE: {model.score():.3f}"
        )


if __name__ == "__main__":
    main()
