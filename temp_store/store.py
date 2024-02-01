import requests

class TemperatureRetriever:

    def retrieve(self, lat, long, ts):
        # do api calling
        print("Hey i am the real one")
        return 42
        


class TemperatureStore:


    def __init__(self) -> None:
        self.locations = {}

    def store(self, lat, long, ts, temp):
        """
        This method stores a temperature observation.
        """
        if (lat, long) in self.locations:
            location_map = self.locations[(lat, long)]
        else:
            location_map = {}
            self.locations[(lat, long)] = location_map
        location_map[ts] = temp


    def retrieve(self, lat, long, ts):
        if (lat, long) in self.locations:
            location_map = self.locations[(lat, long)]
            if ts in location_map:
                return location_map[ts]
        return None
