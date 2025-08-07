import time


def stream_data(df, delay=0.01):
    for _, row in df.iterrows():
        yield row.to_dict()
        time.sleep(delay)
