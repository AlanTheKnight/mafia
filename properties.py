class Properties:
    def __init__(self, filename: str, sep: str = "="):
        with open(filename, "r") as f:
            for line in f.readlines():
                data = line.split(sep)
                setattr(self, data[0].strip(), data[1].strip())